#!/usr/bin/env python3
"""THE UNKNEELING - the engine.

Turns the real logs (real/logs/*.csv) into Darrow's sheet (saga/state/darrow.json).
Everything is recomputed from the logs on every `sync`, so a corrected log fixes
the sheet automatically and nothing is ever counted twice. Standard library only.

Commands (run from the repo root):
  sync                         recompute everything, rewrite sheet + dashboards
  today [--date D]             real-side view of one day
  week [--date D]              real-side view of the week (Sun-Sat) containing D
  sheet                        saga-side character sheet (no real numbers)
  set nutrition|daily DATE k=v ...   upsert fields on a day's row (notes+=text appends)
  food add 'JSON' | food list DATE | food rm ID | food lib TEXT
  ex add 'JSON'                append exercise-log rows (list or object)
  sport add 'JSON'             append sport-log rows
  roll LABEL --stat S --dc N [--adv|--dis] [--bonus N] [--prof] [--chapter N | --tier] [--reroll]
  inspire --reason TEXT        spend one Inspiration on a story action
  chapter-close [--date D]     freeze the finished week's score/tier for the chapter
  knot tie N --date D --evidence TEXT   record a Knot of the Binding
  check                        validate the logs
"""
import argparse
import csv
import datetime as dt
import json
import math
import re
import secrets
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = {
    "config": ROOT / "real/config.json",
    "rules": ROOT / "engine/rules.json",
    "nutrition": ROOT / "real/logs/nutrition_log.csv",
    "food": ROOT / "real/logs/food_entries.csv",
    "foods": ROOT / "real/logs/foods.csv",
    "daily": ROOT / "real/logs/daily_log.csv",
    "exercise": ROOT / "real/logs/ACL_Exercise_Log.csv",
    "sport": ROOT / "real/logs/sport_log.csv",
    "deeds": ROOT / "engine/deeds.csv",
    "sheet": ROOT / "saga/state/darrow.json",
    "rolls": ROOT / "saga/state/rolls.csv",
    "spends": ROOT / "saga/state/spends.csv",
    "chapters": ROOT / "saga/state/chapters.csv",
    "real_now": ROOT / "real/NOW.md",
    "saga_now": ROOT / "saga/NOW.md",
}

NUTRIENTS = ["kcal", "protein_g", "carbs_g", "fat_g", "fiber_g", "sat_fat_g", "sugar_g",
             "sodium_mg", "potassium_mg", "calcium_mg", "iron_mg", "magnesium_mg",
             "zinc_mg", "vit_c_mg", "vit_d_mcg", "omega3_mg"]
ONE_DECIMAL = {"iron_mg", "zinc_mg", "vit_d_mcg"}
COLS = {
    "nutrition": ["date", "day", "week", "wk_post_op", "weight_lb"] + NUTRIENTS
                 + ["shake", "creatine", "training", "notes"],
    "food": ["id", "date", "time", "meal", "item", "qty"] + NUTRIENTS + ["source", "notes"],
    "foods": ["name", "aliases", "serving"] + NUTRIENTS + ["source", "confidence", "notes"],
    "daily": ["date", "dow", "pod", "post_op_week", "dash_week_start", "light",
              "am_swelling", "am_pain", "am_extension", "am_notes",
              "floor_am", "floor_pm", "knee_session", "knee_min", "knee_rpe", "knee_as_planned",
              "pt", "addon_session", "addon_min", "addon_rpe",
              "conditioning_type", "conditioning_min", "sport_min",
              "hours_on_feet", "gym_min_on_feet", "sleep_h", "closed", "notes"],
    "exercise": ["date", "dash_week_start", "pod", "session", "block", "exercise", "side",
                 "sets", "reps", "hold_or_duration", "load_or_band", "assist", "notes"],
    "sport": ["date", "session", "skill", "drill", "sets", "reps", "minutes", "rpe",
              "metric", "value", "notes"],
    "deeds": ["date", "kind", "deed", "xp", "might", "vigor", "finesse", "resolve", "note"],
    "rolls": ["when", "label", "stat", "dc", "d20", "d20_b", "mode", "mods", "total", "result", "note"],
    "spends": ["date", "what", "reason"],
    "chapters": ["chapter", "week_start", "week_end", "score", "tier", "roll_mod", "week_xp", "closed_on"],
}
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ATTRS = ["might", "vigor", "finesse", "resolve"]
VALID_SWELLING = re.compile(r"^(0|none|trace|1\+|2\+|3\+)$", re.I)
YES = {"y", "yes", "true", "1", "done", "full"}


# ---------------------------------------------------------------- io helpers
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_csv(key):
    path = P[key]
    if not path.exists():
        write_csv(key, [])
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = [dict(r) for r in csv.DictReader(f)]
    # drop blank/whitespace-only lines (e.g. a trailing ' ' line)
    return [r for r in rows if any(str(v or "").strip() for k, v in r.items() if k is not None)]


def write_csv(key, rows):
    path = P[key]
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = list(COLS[key])
    if path.exists():  # keep any extra columns the user added
        with open(path, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f), [])
        cols += [c for c in header if c and c not in cols]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        m = re.match(r"^~?\s*(-?\d+(?:\.\d+)?)", s)
        return float(m.group(1)) if m else None


def yes(v):
    return str(v or "").strip().lower() in YES


def d(s):
    return dt.date.fromisoformat(str(s).strip()[:10])


def today_local(cfg):
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo(cfg.get("timezone", "America/New_York"))).date()
    except Exception:  # no tz database: approximate US Eastern (DST roughly Mar-Oct)
        utc = dt.datetime.now(dt.timezone.utc)
        return (utc - dt.timedelta(hours=4 if 3 <= utc.month <= 10 else 5)).date()


def week_start(day):  # Sunday-start weeks
    return day - dt.timedelta(days=(day.weekday() + 1) % 7)


def dow(day):
    return DOW[day.weekday()]


def pod(cfg, day):
    return (day - d(cfg["surgery_date"])).days


def post_op_week(cfg, day):
    p = pod(cfg, day)
    return max(1, math.ceil(p / 7)) if p > 0 else 0


def md(day):
    return f"{day.month}/{day.day}"


def fmt(n, dec=0):
    if n is None:
        return "-"
    return f"{n:,.{dec}f}"


# ---------------------------------------------------------------- nutrition rollup
def rollup(cfg):
    """Sum food_entries per date into nutrition_log totals. Days without item rows are left alone."""
    food = read_csv("food")
    by_date = defaultdict(list)
    for r in food:
        if r.get("date"):
            by_date[r["date"]].append(r)
    nut = read_csv("nutrition")
    idx = {r["date"]: r for r in nut}
    first = min([d(r["date"]) for r in nut] or [d(cfg["chronicle_start"])])
    for date, items in by_date.items():
        row = idx.get(date)
        if row is None:
            row = {"date": date}
            nut.append(row)
            idx[date] = row
        day = d(date)
        row["day"] = dow(day)
        row["week"] = str((week_start(day) - week_start(first)).days // 7 + 1)
        row["wk_post_op"] = str(post_op_week(cfg, day))
        for k in NUTRIENTS:
            vals = [num(i.get(k)) for i in items]
            vals = [v for v in vals if v is not None]
            if not vals:
                row[k] = ""
                continue
            t = sum(vals)
            row[k] = f"{t:.1f}" if k in ONE_DECIMAL else str(int(round(t)))
    nut.sort(key=lambda r: r["date"])
    write_csv("nutrition", nut)
    return nut


# ---------------------------------------------------------------- facts per day
def gather(cfg, rules):
    """Merge every log into one record of facts per date."""
    facts = defaultdict(lambda: {
        "kcal": None, "protein": None, "weight": None, "creatine": False,
        "floor": None, "check": False, "knee": None, "as_planned": False, "pt": False,
        "addons": set(), "cond_min": 0.0, "cond_type": "", "sport": 0, "sport_skills": set(),
        "light": "", "closed": False, "logged": False, "tags": set(),
    })
    for r in read_csv("nutrition"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        f["kcal"] = num(r.get("kcal"))
        f["protein"] = num(r.get("protein_g"))
        f["weight"] = num(r.get("weight_lb"))
        f["creatine"] = yes(r.get("creatine"))
        if f["kcal"] is not None:
            f["logged"] = True

    for r in read_csv("daily"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        f["logged"] = True
        am, pm = yes(r.get("floor_am")), yes(r.get("floor_pm"))
        f["floor"] = "full" if (am and pm) else ("half" if (am or pm) else f["floor"])
        if VALID_SWELLING.match(str(r.get("am_swelling", "")).strip()):
            f["check"] = True
        ks = str(r.get("knee_session", "")).strip()
        if ks and ks.lower() not in ("none", "no", "n", "-"):
            f["knee"] = ks
        f["as_planned"] = yes(r.get("knee_as_planned"))
        if yes(r.get("pt")):
            f["pt"] = True
        for a in re.split(r"[+,/ ]+", str(r.get("addon_session", ""))):
            if a and a.lower() not in ("none", "no", "n", "-"):
                f["addons"].add(a)
        cm = num(r.get("conditioning_min"))
        if cm:
            f["cond_min"] = max(f["cond_min"], cm)
            f["cond_type"] = str(r.get("conditioning_type", "")).strip().lower()
        f["light"] = str(r.get("light", "")).strip().lower()
        f["closed"] = yes(r.get("closed"))

    block_tags = rules["tags"]["block_tags"]
    session_tags = rules["tags"]["session_tags"]
    knee_blocks = {"knee", "single-leg", "posterior", "calf", "hip", "balance", "quad"}
    for r in read_csv("exercise"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        f["logged"] = True
        sess = str(r.get("session", "")).strip()
        block = str(r.get("block", "")).strip().lower()
        if sess == "PT":
            f["pt"] = True
        elif sess in session_tags:
            f["addons"].add(sess)
        elif sess.lower() in ("floor", "hep") and f["floor"] is None:
            f["floor"] = "half"
        elif sess.lower() in ("home", "knee", "a", "b") and block in knee_blocks and not f["knee"]:
            f["knee"] = "home"
        if block in block_tags:
            f["tags"].add(block_tags[block])
        if block == "conditioning":
            m = num(r.get("hold_or_duration"))
            if m:
                f["cond_min"] = max(f["cond_min"], m)
                f["cond_type"] = f["cond_type"] or str(r.get("exercise", "")).lower()

    sport_map = {a["skill"]: a for a in rules.get("sport_arts", {}).get("arts", [])}
    for r in read_csv("sport"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        f["logged"] = True
        f["sport"] += 1
        sk = str(r.get("skill", "")).strip()
        if sk:
            f["sport_skills"].add(sk)
            if sk in sport_map:
                f["tags"].add("sport:" + sk)

    for date, f in facts.items():  # derived tags
        for a in f["addons"]:
            if a in session_tags:
                f["tags"].add(session_tags[a])
        if f["knee"]:
            f["tags"].add("lower")
            if f["knee"].upper() in ("A", "B", "HOME"):
                f["tags"].add("balance")
        if f["cond_min"] >= rules["daily"]["conditioning"]["min_minutes"]:
            f["tags"].add("conditioning")
            if "run" in f["cond_type"] or "jog" in f["cond_type"]:
                f["tags"].add("run")
        if f["floor"] == "full":
            f["tags"].add("floor")
        if f["check"]:
            f["tags"].add("check")
    return facts


# ---------------------------------------------------------------- scoring
def day_fuel(f, cfg, rules):
    if f["kcal"] is None:
        return None
    e = rules["ember"]
    t = cfg["nutrition_targets"]
    kr = min(1.0, (f["kcal"] or 0) / t["kcal"]) ** e["exponent"]
    pr = min(1.0, (f["protein"] or 0) / t["protein_g"]) ** e["exponent"]
    return e["kcal_weight"] * kr + e["protein_weight"] * pr


def deeds_for_day(date, f, cfg, rules):
    R = rules["daily"]
    out = []

    def add(key, xp=None, temper=None, note=""):
        rule = R[key]
        out.append({"date": date, "kind": "daily", "deed": rule["label"],
                    "xp": rule.get("xp", 0) if xp is None else xp,
                    **{a: (temper if temper is not None else rule.get("temper", {})).get(a, 0) for a in ATTRS},
                    "note": note})

    if f["floor"] == "full":
        add("floor_full")
    elif f["floor"] == "half":
        add("floor_half")
    if f["check"]:
        add("morning_check")
    if f["knee"]:
        add("knee_session", note=f["knee"])
        if f["as_planned"]:
            add("knee_as_planned")
    if f["pt"]:
        add("pt_visit")
    addon_kinds = set()
    for a in f["addons"]:
        tag = rules["tags"]["session_tags"].get(a)
        kind = {"upper": "upper_session", "accessory": "accessory_session", "power": "power_session"}.get(tag)
        if kind and kind not in addon_kinds:
            addon_kinds.add(kind)
            add(kind, note=a)
    c = R["conditioning"]
    if f["cond_min"] >= c["min_minutes"]:
        xp = min(c["xp_cap"], int(round(f["cond_min"] * c["xp_per_min"])))
        tv = min(c["temper_cap"], int(f["cond_min"] // 10))
        add("conditioning", xp=xp, temper={"vigor": tv}, note=f"{int(f['cond_min'])} min {f['cond_type']}".strip())
    for _ in range(min(f["sport"], R["sport_session"]["per_day_cap"])):
        add("sport_session", note=",".join(sorted(f["sport_skills"])))
    if f["weight"]:
        add("weigh_in")
    if f["creatine"]:
        add("creatine")
    t = cfg["nutrition_targets"]
    if f["kcal"] is not None:
        r = f["kcal"] / t["kcal"]
        if r >= 1:
            add("kcal_hit")
        elif r >= R["kcal_near"]["threshold"]:
            add("kcal_near")
    if f["protein"] is not None:
        r = f["protein"] / t["protein_g"]
        if r >= 1:
            add("protein_hit")
        elif r >= R["protein_near"]["threshold"]:
            add("protein_near")
    if f["closed"]:
        add("day_closed")
    return out


def planned_for(cfg, day):
    return list(cfg["weekly_template"].get(dow(day), []))


def week_score(ws, upto, facts, cfg, rules):
    """Score the week starting ws (Sunday) over days ws..upto inclusive."""
    W = rules["week_score"]["weights"]
    days = [ws + dt.timedelta(i) for i in range(7) if ws + dt.timedelta(i) <= upto]
    if not days:
        return None
    floor = checks = ledger = fuel = 0.0
    counted = 0
    floor_full_nonred = 0
    planned = defaultdict(int)
    done = defaultdict(int)
    weighins = 0
    excused = []
    for day in days:
        f = facts.get(day.isoformat())
        red = bool(f and f["light"] == "red")
        if red:
            excused.append(day.isoformat())
        else:
            counted += 1
            for p in planned_for(cfg, day):
                key = "knee" if p in ("kneeA", "kneeB") else ("upper" if p in ("upperA", "upperB") else p)
                planned[key] += 1
        if not f:
            continue
        if red:
            continue
        floor += 1 if f["floor"] == "full" else 0.5 if f["floor"] == "half" else 0
        floor_full_nonred += 1 if f["floor"] == "full" else 0
        checks += 1 if f["check"] else 0
        ledger += 1 if f["logged"] else 0
        fu = day_fuel(f, cfg, rules)
        fuel += fu or 0
        if f["knee"]:
            done["knee"] += 1
        if f["pt"]:
            done["pt"] += 1
        tags = {rules["tags"]["session_tags"].get(a) for a in f["addons"]}
        if "upper" in tags:
            done["upper"] += 1
        if f["cond_min"] >= rules["daily"]["conditioning"]["min_minutes"]:
            done["cond"] += 1
        if f["weight"]:
            weighins += 1
    for day in days:
        f = facts.get(day.isoformat())
        if f and f["light"] == "red" and f["weight"]:
            weighins += 1
    n = max(counted, 1)
    total_planned = sum(planned.values())
    sess_done = sum(min(done[k], v) for k, v in planned.items())
    sessions = (sess_done / total_planned) if total_planned else 1.0
    need_w = cfg["nutrition_targets"]["weighins_per_week"]
    parts = {
        "floor": floor / n, "sessions": sessions, "fuel": fuel / n,
        "checks": checks / n, "weighins": min(weighins, need_w) / need_w, "ledger": ledger / n,
    }
    score = round(sum(W[k] * parts[k] for k in W))
    tier = next(t for t in rules["week_score"]["tiers"] if score >= t["min"])
    return {
        "week_start": ws.isoformat(), "through": days[-1].isoformat(), "days": len(days),
        "score": score, "tier": tier["name"], "roll_mod": tier["roll_mod"], "parts": parts,
        "planned": dict(planned), "done": {k: min(done[k], v) for k, v in planned.items()},
        "floor_full_days": sum(1 for day in days if facts.get(day.isoformat(), {}).get("floor") == "full"),
        "floor_complete": counted > 0 and floor_full_nonred == counted,
        "weighins": weighins, "excused": excused, "complete": len(days) == 7,
    }


def ember_at(day, facts, cfg, rules):
    vals = []
    for i in range(7):
        f = facts.get((day - dt.timedelta(i)).isoformat())
        if f:
            fu = day_fuel(f, cfg, rules)
            if fu is not None:
                vals.append(fu)
    if not vals:
        return None
    return max(10, round(100 * sum(vals) / len(vals)))


def tier_of(value, tiers):
    return next(t for t in tiers if value >= t["min"])


def level_of(xp):
    L = 1
    while 50 * (L + 1) * L <= xp:
        L += 1
    return L


def rank_of(level, rules):
    name = rules["levels"]["ranks"][0]["name"]
    for r in rules["levels"]["ranks"]:
        if level >= r["from"]:
            name = r["name"]
    return name


# ---------------------------------------------------------------- sync
def compute(cfg, rules, asof=None):
    facts = gather(cfg, rules)
    asof = asof or today_local(cfg)
    deeds = []
    for date in sorted(facts):
        if d(date) <= asof:
            deeds += deeds_for_day(date, facts[date], cfg, rules)

    # weekly bonuses for completed weeks
    dates = sorted(d(x) for x in facts if d(x) <= asof)
    weeks = []
    insp_events = []
    if dates:
        ws = week_start(dates[0])
        while ws + dt.timedelta(6) < asof:
            sc = week_score(ws, ws + dt.timedelta(6), facts, cfg, rules)
            weeks.append(sc)
            Wk = rules["weekly"]
            end = (ws + dt.timedelta(6)).isoformat()

            def wadd(label, xp, temper=None, note=""):
                deeds.append({"date": end, "kind": "weekly", "deed": label, "xp": xp,
                              **{a: (temper or {}).get(a, 0) for a in ATTRS}, "note": note})

            if sc["floor_complete"]:
                wadd(Wk["floor_7_of_7"]["label"], Wk["floor_7_of_7"]["xp"], Wk["floor_7_of_7"]["temper"])
                if ws >= d(cfg["chronicle_start"]):
                    insp_events.append((end, +1, "floor 7/7"))
            if sc["weighins"] >= Wk["scouted"]["min_weighins"]:
                wadd(Wk["scouted"]["label"], Wk["scouted"]["xp"])
            if sc["planned"] and all(sc["done"].get(k, 0) >= v for k, v in sc["planned"].items()):
                wadd(Wk["all_sessions"]["label"], Wk["all_sessions"]["xp"], Wk["all_sessions"]["temper"])
            bonus = Wk["tier_bonus"].get(sc["tier"], 0)
            if bonus and ws >= d(cfg["chronicle_start"]):
                wadd(f"Chapter tier: {sc['tier']}", bonus, note=f"week score {sc['score']}")
            if sc["tier"] == "Triumph" and ws >= d(cfg["chronicle_start"]):
                insp_events.append((end, +Wk["triumph_inspiration"], "Triumph week"))
            ws += dt.timedelta(7)

    xp = sum(int(x["xp"]) for x in deeds)
    temper = {a: sum(int(x[a]) for x in deeds) for a in ATTRS}
    knots = sorted(k["knot"] for k in cfg["rehab"].get("knots", []))
    n_knots = len(knots)
    level = level_of(xp)
    attrs = {}
    for a in ATTRS:
        spec = rules["attributes"][a]
        raw = spec["base"] + int(math.floor(math.sqrt(temper[a] / spec["divisor"])))
        cap_tbl = rules["caps_by_knots"].get(a)
        cap = cap_tbl.get(str(n_knots)) if cap_tbl else None
        val = min(raw, cap) if cap else raw
        nxt = spec["divisor"] * (raw - spec["base"] + 1) ** 2
        attrs[a] = {"score": val, "raw": raw, "cap": cap, "mod": (val - 10) // 2,
                    "temper": temper[a], "next_at": nxt, "fell": spec["fell"],
                    "banked": raw > val}

    # inspiration: chronological earn/spend, capped
    for s in read_csv("spends"):
        if s.get("what") == "inspiration":
            insp_events.append((s["date"], -1, s.get("reason", "")))
    insp = 0
    cap = rules["inspiration"]["cap"]
    for _, delta, _ in sorted(insp_events, key=lambda e: (e[0], -e[1])):
        insp = max(0, min(cap, insp + delta))

    # arts
    practice = defaultdict(int)
    for date, f in facts.items():
        if d(date) <= asof:
            for t in f["tags"]:
                practice[t] += 1
    thresholds = rules["art_ranks"]
    arts = []
    all_arts = list(rules["arts"]) + [
        {**a, "tag": "sport:" + a["skill"]} for a in rules.get("sport_arts", {}).get("arts", [])]
    for a in all_arts:
        n = practice.get(a["tag"], 0)
        rank = sum(1 for t in thresholds if n >= t)
        sealed = n_knots < a.get("knot", 0)
        nxt = next((t for t in thresholds if n < t), None)
        arts.append({"id": a["id"], "name": a["name"], "tree": a["tree"], "rank": 0 if sealed else rank,
                     "banked_rank": rank if sealed else 0, "practice": n, "next_at": nxt,
                     "sealed_until_knot": a.get("knot", 0) if sealed else None, "effect": a["effect"]})

    ember = ember_at(asof, facts, cfg, rules)
    ember_t = tier_of(ember, rules["ember"]["tiers"]) if ember is not None else None
    vig = attrs["vigor"]["score"]
    hp = max(10, 20 + 4 * level + 2 * (vig - 10))
    cur = week_score(week_start(asof), asof, facts, cfg, rules)
    sheet = {
        "asof": asof.isoformat(),
        "name": "Ser Darrow of Edgemoor",
        "level": level, "rank": rank_of(level, rules), "xp": xp,
        "xp_this_level": 50 * level * (level - 1), "xp_next_level": 50 * (level + 1) * level,
        "proficiency": 2 + (level - 1) // 4, "hp_max": hp,
        "attributes": attrs,
        "ember": {"value": ember, "tier": ember_t["name"] if ember_t else None,
                  "effect": ember_t["effect"] if ember_t else None},
        "inspiration": insp, "inspiration_cap": cap,
        "knots_tied": knots, "knots_count": n_knots,
        "soft_season": 6 <= post_op_week(cfg, asof) <= 12,
        "arts": arts,
        "chapter_now": {"week_start": cur["week_start"], "through": cur["through"],
                        "tier_so_far": cur["tier"], "chapter": chapter_no(cfg, d(cur["week_start"]))},
        "fell": {a: rules["attributes"][a]["fell"] for a in ATTRS},
    }
    return {"facts": facts, "deeds": deeds, "sheet": sheet, "weeks": weeks, "current_week": cur, "asof": asof}


def chapter_no(cfg, ws):
    return (ws - week_start(d(cfg["chronicle_start"]))).days // 7 + 1


def cmd_sync(args, cfg, rules):
    rollup(cfg)
    st = compute(cfg, rules, d(args.date) if getattr(args, "date", None) else None)
    write_csv("deeds", st["deeds"])
    old = load_json(P["sheet"]) if P["sheet"].exists() else None
    save_json(P["sheet"], st["sheet"])
    write_dashboards(st, cfg, rules)
    # report what changed, for the Reckoning notifications
    s = st["sheet"]
    print(f"synced through {s['asof']}: Level {s['level']} {s['rank']} | XP {s['xp']:,} | "
          f"Ember {s['ember']['value']} {s['ember']['tier']} | Inspiration {s['inspiration']}")
    if old:
        notes = diff_sheets(old, s)
        if notes:
            print("RECKONING CHANGES:")
            for n in notes:
                print("  " + n)


def diff_sheets(old, new):
    notes = []
    if new["xp"] != old.get("xp"):
        notes.append(f"XP {old.get('xp', 0):,} -> {new['xp']:,} ({new['xp'] - old.get('xp', 0):+,})")
    if new["level"] > old.get("level", 0):
        notes.append(f"LEVEL UP: {old.get('level')} -> {new['level']} ({new['rank']})")
    for a in ATTRS:
        o = old.get("attributes", {}).get(a, {}).get("score")
        n = new["attributes"][a]["score"]
        if o is not None and n != o:
            notes.append(f"{a.upper()} {o} -> {n}")
        if o is not None and o <= new["fell"][a] < n:
            notes.append(f"{a.upper()} has passed the Knight Who Fell ({new['fell'][a]})")
    oa = {a["id"]: a for a in old.get("arts", [])}
    for a in new["arts"]:
        prev = oa.get(a["id"], {})
        if a["rank"] > prev.get("rank", 0):
            notes.append(f"ART {'LEARNED' if prev.get('rank', 0) == 0 else 'RANKED UP'}: {a['name']} {roman(a['rank'])}")
    if new["inspiration"] > old.get("inspiration", 0):
        notes.append(f"INSPIRATION +{new['inspiration'] - old.get('inspiration', 0)} (now {new['inspiration']})")
    if new["knots_count"] > old.get("knots_count", 0):
        notes.append(f"KNOT TIED: {new['knots_count']} of VII")
    oe = (old.get("ember") or {}).get("tier")
    if oe and new["ember"]["tier"] != oe:
        notes.append(f"EMBER {oe} -> {new['ember']['tier']}")
    return notes


def roman(n):
    return ["-", "I", "II", "III", "IV", "V", "VI", "VII"][n] if 0 <= n <= 7 else str(n)


# ---------------------------------------------------------------- views
def real_week_table(st, cfg, rules, ws):
    facts = st["facts"]
    t = cfg["nutrition_targets"]
    lines = ["| Day | Plan | kcal | P (g) | Wt | Cr | Floor | Check | Knee | PT | Add-on | Cond | Sport |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    kc, pr, wts = [], [], []
    for i in range(7):
        day = ws + dt.timedelta(i)
        f = facts.get(day.isoformat())
        plan = ", ".join(planned_for(cfg, day)) or "floor"
        label = f"{dow(day)} {md(day)}"
        if not f:
            lines.append(f"| {label} | {plan} |" + " |" * 11)
            continue
        if f["kcal"] is not None:
            kc.append(f["kcal"])
        if f["protein"] is not None:
            pr.append(f["protein"])
        if f["weight"]:
            wts.append(f["weight"])
        flo = {"full": "✔✔", "half": "✔"}.get(f["floor"], "")
        lines.append("| " + " | ".join([
            label + (" 🔴" if f["light"] == "red" else " 🟡" if f["light"] == "yellow" else ""), plan,
            fmt(f["kcal"]), fmt(f["protein"]), fmt(f["weight"], 1) if f["weight"] else "",
            "✔" if f["creatine"] else "", flo, "✔" if f["check"] else "",
            f["knee"] or "", "✔" if f["pt"] else "", "+".join(sorted(f["addons"])),
            f"{int(f['cond_min'])}m" if f["cond_min"] else "", str(f["sport"] or "")]) + " |")
    sc = week_score(ws, min(ws + dt.timedelta(6), st["asof"]), facts, cfg, rules)
    out = ["\n".join(lines), ""]
    if kc:
        hit_k = sum(1 for x in kc if x >= t["kcal"])
        hit_p = sum(1 for x in pr if x >= t["protein_g"])
        out.append(f"**Nutrition:** avg {fmt(sum(kc)/len(kc))} kcal (target {fmt(t['kcal'])}) · "
                   f"avg {fmt(sum(pr)/len(pr)) if pr else '-'} g protein (target {t['protein_g']}-{t['protein_g_max']}) · "
                   f"at kcal target {hit_k}/{len(kc)} days · at protein target {hit_p}/{len(pr)} days")
    w_need = t["weighins_per_week"]
    out.append(f"**Weigh-ins:** {len(wts)}/{w_need}" + (f" · avg {sum(wts)/len(wts):.1f} lb" if wts else ""))
    if sc:
        pl, dn = sc["planned"], sc["done"]
        sess = " · ".join(f"{k} {dn.get(k, 0)}/{v}" for k, v in pl.items())
        out.append(f"**Sessions (through {dow(d(sc['through']))}):** {sess or 'none planned yet'} · "
                   f"floor full {sc['floor_full_days']}/{sc['days']} · graded morning checks "
                   f"{sum(1 for i in range(sc['days']) if facts.get((ws + dt.timedelta(i)).isoformat(), {}).get('check'))}/{sc['days']}")
    return "\n".join(out)


def cmd_today(args, cfg, rules):
    rollup(cfg)
    st = compute(cfg, rules)
    day = d(args.date) if args.date else st["asof"]
    f = st["facts"].get(day.isoformat())
    t = cfg["nutrition_targets"]
    print(f"# {dow(day)} {day.isoformat()} · POD {pod(cfg, day)} · post-op week {post_op_week(cfg, day)} · "
          f"Phase {cfg['rehab']['current_phase']}")
    print(f"Planned today (template): {', '.join(planned_for(cfg, day)) or 'rest / floor minimum only'}"
          f" · optional this week: {', '.join(cfg['weekly_template'].get('optional', []))}")
    items = [r for r in read_csv("food") if r.get("date") == day.isoformat()]
    if f and f["kcal"] is not None:
        k, p = f["kcal"], f["protein"] or 0
        print(f"Nutrition: {fmt(k)} / {fmt(t['kcal'])} kcal ({fmt(max(0, t['kcal'] - k))} to go) · "
              f"{fmt(p)} / {t['protein_g']} g protein ({fmt(max(0, t['protein_g'] - p))} to go) · {len(items)} items")
    else:
        print(f"Nutrition: nothing logged yet · targets {fmt(t['kcal'])} kcal / {t['protein_g']}-{t['protein_g_max']} g protein")
    if f:
        done = []
        if f["check"]:
            done.append("morning check")
        if f["floor"]:
            done.append(f"floor ({f['floor']})")
        if f["knee"]:
            done.append(f"knee session {f['knee']}")
        if f["pt"]:
            done.append("PT")
        if f["addons"]:
            done.append("add-on " + "+".join(sorted(f["addons"])))
        if f["cond_min"]:
            done.append(f"conditioning {int(f['cond_min'])} min")
        if f["sport"]:
            done.append(f"sport x{f['sport']}")
        if f["weight"]:
            done.append(f"weigh-in {f['weight']:.1f}")
        if f["creatine"]:
            done.append("creatine")
        print("Logged: " + (", ".join(done) if done else "nothing yet"))
        missing = [x for x, ok in [("morning check (grade swelling)", f["check"]),
                                   ("floor minimum AM+PM", f["floor"] == "full"),
                                   ("creatine", f["creatine"])] if not ok]
        if missing:
            print("Still open: " + ", ".join(missing))
    else:
        print("Logged: nothing yet. Still open: morning check, floor minimum AM+PM, creatine")


def cmd_week(args, cfg, rules):
    rollup(cfg)
    st = compute(cfg, rules)
    day = d(args.date) if args.date else st["asof"]
    ws = week_start(day)
    print(f"# Week of Sun {ws.isoformat()} – Sat {(ws + dt.timedelta(6)).isoformat()} "
          f"(post-op weeks {post_op_week(cfg, ws)}–{post_op_week(cfg, ws + dt.timedelta(6))})\n")
    print(real_week_table(st, cfg, rules, ws))
    sc = week_score(ws, min(ws + dt.timedelta(6), st["asof"]), st["facts"], cfg, rules)
    if sc and args.score:
        print(f"\n(score {sc['score']} · {sc['tier']} · parts " +
              ", ".join(f"{k} {v:.2f}" for k, v in sc["parts"].items()) + ")")


def sheet_text(s):
    a = s["attributes"]
    bar_xp = progress_bar(s["xp"] - s["xp_this_level"], s["xp_next_level"] - s["xp_this_level"])
    lines = [
        "⟦ THE RECKONING ⟧",
        f"{s['name']} · Level {s['level']} · {s['rank']}",
        f"XP {s['xp']:,} {bar_xp} {s['xp_next_level']:,}",
        f"HP {s['hp_max']} · " + (f"Ember {s['ember']['value']} ({s['ember']['tier']})" if s["ember"]["value"] is not None else "Ember unlit")
        + f" · Inspiration {s['inspiration']}/{s['inspiration_cap']} · Proficiency +{s['proficiency']}",
        "",
    ]
    for k in ATTRS:
        x = a[k]
        cap = f" · capped by the Binding (true {x['raw']})" if x["banked"] else ""
        lines.append(f"{k.upper():<8} {x['score']:>2} ({x['mod']:+d})   the Knight Who Fell: {x['fell']}{cap}")
    knots = s["knots_count"]
    lines += ["", f"THE BINDING · Knots tied {roman(knots)} of VII" + (" · the soft season (do not trust the quiet)" if s.get("soft_season") else "")]
    learned = [x for x in s["arts"] if x["rank"] > 0]
    sealed = [x for x in s["arts"] if x["sealed_until_knot"] and x["practice"] > 0]
    lines.append("ARTS · " + (" · ".join(f"{x['name']} {roman(x['rank'])}" for x in learned) or "none yet"))
    if sealed:
        lines.append("SEALED (practice banked) · " + " · ".join(f"{x['name']} (Knot {roman(x['sealed_until_knot'])})" for x in sealed))
    return "\n".join(lines)


def progress_bar(have, need, width=10):
    need = max(need, 1)
    filled = max(0, min(width, int(width * have / need)))
    return "▰" * filled + "▱" * (width - filled)


def cmd_sheet(args, cfg, rules):
    rollup(cfg)
    st = compute(cfg, rules)
    print(sheet_text(st["sheet"]))
    if args.json:
        print(json.dumps(st["sheet"], indent=2))


def replace_block(path, block, title):
    start, end = "<!-- engine:start -->", "<!-- engine:end -->"
    text = path.read_text(encoding="utf-8") if path.exists() else f"# {title}\n\n{start}\n{end}\n"
    if start not in text:
        text = text.rstrip() + f"\n\n{start}\n{end}\n"
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    path.write_text(pre + start + "\n" + block.strip() + "\n" + end + post, encoding="utf-8")


def write_dashboards(st, cfg, rules):
    asof = st["asof"]
    ws = week_start(asof)
    real_block = (f"_Engine block, regenerated by `sync` · as of {dow(asof)} {asof.isoformat()} · "
                  f"POD {pod(cfg, asof)} · post-op week {post_op_week(cfg, asof)} · Phase {cfg['rehab']['current_phase']}_\n\n"
                  f"### This week (Sun {md(ws)} – Sat {md(ws + dt.timedelta(6))})\n\n"
                  + real_week_table(st, cfg, rules, ws))
    replace_block(P["real_now"], real_block, "NOW — the Ledger")
    s = st["sheet"]
    saga_block = ("_Engine block, regenerated by `sync`._\n\n```\n" + sheet_text(s) + "\n```\n\n"
                  f"**Chapter {s['chapter_now']['chapter']}, so far (on what's logged):** {s['chapter_now']['tier_so_far']}")
    replace_block(P["saga_now"], saga_block, "NOW — the Chronicle")


# ---------------------------------------------------------------- editing commands
def parse_kv(pairs):
    out = {}
    for p in pairs:
        if "+=" in p:
            k, v = p.split("+=", 1)
            out[k.strip()] = ("append", v)
        elif "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = ("set", v)
        else:
            sys.exit(f"bad field '{p}', use key=value or notes+=text")
    return out


def cmd_set(args, cfg, rules):
    key = {"nutrition": "nutrition", "daily": "daily"}[args.log]
    rows = read_csv(key)
    date = d(args.date).isoformat()
    row = next((r for r in rows if r.get("date") == date), None)
    if row is None:
        row = {"date": date}
        rows.append(row)
    day = d(date)
    if key == "daily":
        row.update({"dow": dow(day), "pod": str(pod(cfg, day)), "post_op_week": str(post_op_week(cfg, day)),
                    "dash_week_start": week_start(day).isoformat()})
    else:
        first = min([d(r["date"]) for r in rows if r.get("date")] + [day])
        row["day"] = row.get("day") or dow(day)
        row["week"] = row.get("week") or str((week_start(day) - week_start(first)).days // 7 + 1)
        row["wk_post_op"] = row.get("wk_post_op") or str(post_op_week(cfg, day))
    allowed = set(COLS[key])
    for k, (op, v) in parse_kv(args.fields).items():
        if k not in allowed:
            sys.exit(f"unknown column '{k}' for {key}. Allowed: {', '.join(COLS[key])}")
        if op == "append" and row.get(k):
            row[k] = row[k].rstrip() + " " + v
        else:
            row[k] = v
    rows.sort(key=lambda r: r.get("date", ""))
    write_csv(key, rows)
    print(f"{key} {date}: " + ", ".join(f"{k}={row.get(k)}" for k in COLS[key] if row.get(k) not in (None, "") and k != "notes"))


def as_list(js):
    obj = json.loads(js)
    return obj if isinstance(obj, list) else [obj]


def cmd_food(args, cfg, rules):
    if args.action == "add":
        rows = read_csv("food")
        added = []
        for item in as_list(args.payload):
            if "date" not in item or "item" not in item:
                sys.exit("each food needs at least 'date' and 'item'")
            date = d(item["date"]).isoformat()
            seq = 1 + max([int(r["id"].split("#")[1]) for r in rows
                           if r.get("date") == date and "#" in r.get("id", "")] or [0])
            row = {"id": f"{date}#{seq}", **{k: item.get(k, "") for k in COLS["food"] if k != "id"}}
            row["date"] = date
            rows.append(row)
            added.append(row)
        write_csv("food", rows)
        for r in added:
            print(f"+ {r['id']} {r['item']}: {r.get('kcal') or '?'} kcal, {r.get('protein_g') or '?'} g P")
    elif args.action == "list":
        for r in read_csv("food"):
            if r.get("date") == d(args.payload).isoformat():
                print(f"{r['id']:<14} {r.get('time',''):<6} {r['item']:<40} {r.get('kcal',''):>5} kcal {r.get('protein_g',''):>4} P")
    elif args.action == "rm":
        rows = read_csv("food")
        keep = [r for r in rows if r.get("id") != args.payload]
        if len(keep) == len(rows):
            sys.exit(f"no food entry {args.payload}")
        write_csv("food", keep)
        print(f"removed {args.payload}")
    elif args.action == "lib":
        q = args.payload.lower()
        for r in read_csv("foods"):
            hay = (r.get("name", "") + " " + r.get("aliases", "")).lower()
            if all(w in hay for w in q.split()):
                print(json.dumps({k: v for k, v in r.items() if v not in ("", None)}))


def cmd_append(key, args, cfg):
    rows = read_csv(key)
    for item in as_list(args.payload):
        day = d(item["date"])
        row = {k: item.get(k, "") for k in COLS[key]}
        row["date"] = day.isoformat()
        if key == "exercise":
            row["dash_week_start"] = row["dash_week_start"] or week_start(day).isoformat()
            row["pod"] = row["pod"] or str(pod(cfg, day))
        rows.append(row)
    rows.sort(key=lambda r: r.get("date", ""))
    write_csv(key, rows)
    print(f"{key}: appended {len(as_list(args.payload))} row(s)")


# ---------------------------------------------------------------- dice
def cmd_roll(args, cfg, rules):
    rows = read_csv("rolls")
    label = args.label + ("#reroll" if args.reroll else "")
    prior = next((r for r in rows if r["label"] == label), None)
    if prior:
        print(f"ALREADY ROLLED (no takebacks): {prior['label']} → d20 {prior['d20']}"
              f"{'/' + prior['d20_b'] if prior['d20_b'] else ''} {prior['mods']} = {prior['total']} vs DC {prior['dc']} → {prior['result']}")
        return
    st = compute(cfg, rules)
    s = st["sheet"]
    if args.reroll:
        if not any(r["label"] == args.label for r in rows):
            sys.exit("nothing to reroll under that label")
        if s["inspiration"] < 1:
            sys.exit("no Inspiration to spend")
        sp = read_csv("spends")
        sp.append({"date": st["asof"].isoformat(), "what": "inspiration", "reason": f"reroll {args.label}"})
        write_csv("spends", sp)
    mods = []
    if args.stat:
        m = s["attributes"][args.stat]["mod"]
        mods.append((args.stat, m))
    if args.prof:
        mods.append(("proficiency", s["proficiency"]))
    if args.chapter:
        ch = next((r for r in read_csv("chapters") if r["chapter"] == str(args.chapter)), None)
        if not ch:
            sys.exit(f"chapter {args.chapter} is not closed yet; run chapter-close first")
        mods.append((f"chapter {args.chapter} {ch['tier']}", int(ch["roll_mod"])))
    elif args.tier:
        cur = st["current_week"]
        mods.append((f"chapter so far {cur['tier']}", cur["roll_mod"]))
    et = s["ember"]["tier"]
    if et == "Blazing":
        mods.append(("Ember Blazing", 1))
    elif et == "Bright" and args.stat == "vigor":
        mods.append(("Ember Bright", 1))
    elif et == "Guttering" and args.stat in ("might", "vigor"):
        mods.append(("Ember Guttering", -1))
    if args.bonus:
        mods.append(("bonus", args.bonus))
    a = secrets.randbelow(20) + 1
    b = secrets.randbelow(20) + 1 if (args.adv or args.dis) else None
    mode = "adv" if args.adv else "dis" if args.dis else ""
    nat = max(a, b) if args.adv else min(a, b) if args.dis else a
    total = nat + sum(m for _, m in mods)
    if nat == 20:
        result = "CRITICAL SUCCESS"
    elif nat == 1:
        result = "CRITICAL FAILURE"
    elif total >= args.dc:
        result = "SUCCESS"
    elif total >= args.dc - 3:
        result = "PARTIAL (success at a cost)"
    else:
        result = "FAILURE"
    mod_txt = " ".join(f"{m:+d} {n}" for n, m in mods)
    rows.append({"when": dt.datetime.now().isoformat(timespec="seconds"), "label": label, "stat": args.stat or "",
                 "dc": args.dc, "d20": a, "d20_b": b or "", "mode": mode, "mods": mod_txt, "total": total,
                 "result": result, "note": args.note or ""})
    write_csv("rolls", rows)
    shown = f"{a}/{b} ({mode})" if b else f"{a}"
    print(f"🎲 {label} · {(args.stat or 'flat').upper()} check DC {args.dc}: d20 {shown} {mod_txt} = {total} → {result}")


def cmd_inspire(args, cfg, rules):
    st = compute(cfg, rules)
    if st["sheet"]["inspiration"] < 1:
        sys.exit("no Inspiration to spend")
    sp = read_csv("spends")
    sp.append({"date": st["asof"].isoformat(), "what": "inspiration", "reason": args.reason})
    write_csv("spends", sp)
    print(f"Inspiration spent: {args.reason} (left: {st['sheet']['inspiration'] - 1})")


def cmd_chapter_close(args, cfg, rules):
    st = compute(cfg, rules)
    day = d(args.date) if args.date else st["asof"]
    ws = week_start(day)
    if day.weekday() == 6 and not args.date:  # on Sunday, close the week that just ended
        ws -= dt.timedelta(7)
    sc = week_score(ws, ws + dt.timedelta(6), st["facts"], cfg, rules)
    n = chapter_no(cfg, ws)
    rows = read_csv("chapters")
    if any(r["chapter"] == str(n) for r in rows) and not args.force:
        r = next(r for r in rows if r["chapter"] == str(n))
        print(f"Chapter {n} already closed: score {r['score']} · {r['tier']} (roll mod {r['roll_mod']}). Use --force to redo.")
        return
    week_xp = sum(int(x["xp"]) for x in st["deeds"] if ws.isoformat() <= x["date"] <= (ws + dt.timedelta(6)).isoformat())
    rows = [r for r in rows if r["chapter"] != str(n)]
    rows.append({"chapter": n, "week_start": ws.isoformat(), "week_end": (ws + dt.timedelta(6)).isoformat(),
                 "score": sc["score"], "tier": sc["tier"], "roll_mod": sc["roll_mod"], "week_xp": week_xp,
                 "closed_on": st["asof"].isoformat()})
    rows.sort(key=lambda r: int(r["chapter"]))
    write_csv("chapters", rows)
    print(json.dumps({"chapter": n, **sc}, indent=2))


def cmd_knot(args, cfg, rules):
    knots = cfg["rehab"].setdefault("knots", [])
    names = {1: "Straightening", 2: "Walking", 3: "Standing", 4: "the Road", 5: "Lightning", 6: "Turning", 7: "the Field"}
    if any(k["knot"] == args.n for k in knots):
        sys.exit(f"Knot {args.n} is already tied")
    if args.n != len(knots) + 1:
        sys.exit(f"Knots tie in order; next is {len(knots) + 1}")
    knots.append({"knot": args.n, "name": names[args.n], "date": d(args.date).isoformat(), "evidence": args.evidence})
    save_json(P["config"], cfg)
    print(f"Knot {roman(args.n)} ({names[args.n]}) tied {args.date}. Run sync.")


def cmd_check(args, cfg, rules):
    problems = []
    for key in ("nutrition", "daily", "exercise", "sport", "food"):
        rows = read_csv(key)
        for i, r in enumerate(rows, 2):
            try:
                d(r.get("date", ""))
            except Exception:
                problems.append(f"{key}.csv line {i}: bad date '{r.get('date')}'")
        if key in ("nutrition", "daily"):
            seen = defaultdict(int)
            for r in rows:
                seen[r.get("date")] += 1
            problems += [f"{key}.csv: {k} appears {v} times" for k, v in seen.items() if v > 1]
    for r in read_csv("daily"):
        s = str(r.get("am_swelling", "")).strip()
        if s and not VALID_SWELLING.match(s):
            problems.append(f"daily_log {r['date']}: am_swelling '{s}' is not a grade (0/trace/1+/2+/3+); no check credit")
    print("\n".join(problems) if problems else "all logs look clean")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync"); s.add_argument("--date")
    s = sub.add_parser("today"); s.add_argument("--date")
    s = sub.add_parser("week"); s.add_argument("--date"); s.add_argument("--score", action="store_true")
    s = sub.add_parser("sheet"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("set"); s.add_argument("log", choices=["nutrition", "daily"]); s.add_argument("date"); s.add_argument("fields", nargs="+")
    s = sub.add_parser("food"); s.add_argument("action", choices=["add", "list", "rm", "lib"]); s.add_argument("payload")
    s = sub.add_parser("ex"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("sport"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("roll"); s.add_argument("label"); s.add_argument("--stat", choices=ATTRS); s.add_argument("--dc", type=int, required=True)
    s.add_argument("--adv", action="store_true"); s.add_argument("--dis", action="store_true"); s.add_argument("--bonus", type=int, default=0)
    s.add_argument("--prof", action="store_true"); s.add_argument("--tier", action="store_true"); s.add_argument("--chapter", type=int)
    s.add_argument("--reroll", action="store_true"); s.add_argument("--note")
    s = sub.add_parser("inspire"); s.add_argument("--reason", required=True)
    s = sub.add_parser("chapter-close"); s.add_argument("--date"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("knot"); s.add_argument("action", choices=["tie"]); s.add_argument("n", type=int); s.add_argument("--date", required=True); s.add_argument("--evidence", required=True)
    sub.add_parser("check")
    args = ap.parse_args()
    cfg, rules = load_json(P["config"]), load_json(P["rules"])
    {
        "sync": cmd_sync, "today": cmd_today, "week": cmd_week, "sheet": cmd_sheet, "set": cmd_set,
        "food": cmd_food, "roll": cmd_roll, "inspire": cmd_inspire, "chapter-close": cmd_chapter_close,
        "knot": cmd_knot, "check": cmd_check,
        "ex": lambda a, c, r: cmd_append("exercise", a, c),
        "sport": lambda a, c, r: cmd_append("sport", a, c),
    }[args.cmd](args, cfg, rules)


if __name__ == "__main__":
    main()
