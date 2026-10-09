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
  roll LABEL --stat S --dc N [--adv|--dis] [--bonus N] [--prof] [--chapter N | --tier] [--reroll]   prints the chapter's dice line (paste line 1 as is)
  inspire --reason TEXT        spend one Inspiration on a story action
  chapter-close [--date D] [--force]   freeze the last completed week's score/tier as a chapter (D: any day of the week to close)
  knot tie N --date D --evidence TEXT   record a Knot of the Binding
  show daily|nutrition|food|ex|sport|measurements DATE [--session S]   one date's rows as key: value lines (non-empty fields only); never read the CSVs raw
  recap [--date D] [--write]   the weekly checkpoint numbers for the week containing D (default: the last completed week);
                               --write puts them in real/checkpoints/<the Sunday after>.md (creates the file from the template)
  measure add 'JSON'           append rows to real/logs/measurements.csv (metrics from config.json -> measurement_metrics)
  measures [--metric M]        latest value per metric and side, with LSI; --metric M: that metric's full history
  doc state|addon|rules|guide|master|checkpoint|visit|now|PATH [SECTION ...]   one section of a document (number or title words); no SECTION: its outline
  check                        validate the logs
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
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
    "measurements": ROOT / "real/logs/measurements.csv",
    "state_dir": ROOT / "real/state",
    "checkpoints": ROOT / "real/checkpoints",
    "visits": ROOT / "real/visits",
    "addon": ROOT / "real/plan/ACL_Whole_Athlete_AddOn.md",
    "working_rules": ROOT / "real/plan/ACL_Dashboard_Working_Rules.md",
    "guide": ROOT / "real/plan/nutrition_guide.md",
    "master": ROOT / "real/plan/ACL_Reconstruction_Rehab_Master_Plan.md",
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
              "am_swelling", "am_trend", "am_pain", "am_extension", "flexion", "catch", "am_notes",
              "floor_am", "floor_pm", "knee_session", "knee_min", "knee_rpe", "knee_as_planned",
              "pain_session", "pain_pm", "pt", "addon_session", "addon_min", "addon_rpe",
              "conditioning_type", "conditioning_min", "sport_min",
              "hours_on_feet", "gym_min_on_feet", "crutches", "gait_notes", "adjuncts", "sleep_h", "closed", "notes"],
    "exercise": ["date", "dash_week_start", "pod", "session", "block", "exercise", "side",
                 "sets", "reps", "hold_or_duration", "load_or_band", "assist", "notes"],
    "sport": ["date", "session", "skill", "drill", "sets", "reps", "minutes", "rpe",
              "metric", "value", "notes"],
    "measurements": ["date", "source", "metric", "side", "value", "unit", "method", "visit", "notes"],
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


LOG_FILES = ("nutrition", "food", "foods", "daily", "exercise", "sport", "measurements", "deeds", "rolls", "spends", "chapters")


def ensure_files():
    """Create any missing log file with its header. Only sync calls this; views never create files."""
    for key in LOG_FILES:
        if not P[key].exists():
            write_csv(key, [])


def read_csv(key):
    path = P[key]
    if not path.exists():
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
    if os.environ.get("DARROW_TODAY"):  # test hook only: pretend it is this date
        return d(os.environ["DARROW_TODAY"])
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
def rollup(cfg, write=False):
    """Sum food_entries per date into nutrition_log totals and return the rows. Days without item rows are left alone.
    Only sync passes write=True; every view computes the rollup in memory and never touches the file."""
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
    if write:
        write_csv("nutrition", nut)
    return nut


# ---------------------------------------------------------------- facts per day
def floor_rounds(cfg, date):
    """Weighted heel-prop rounds that make a full daily minimum on this date (config.json -> daily_minimum)."""
    need = 2
    for step in sorted(cfg.get("daily_minimum", {}).get("rounds", []), key=lambda x: x["from"]):
        if step["from"] <= str(date):
            need = step["rounds"]
    return need


def gather(cfg, rules, nutrition=None):
    """Merge every log into one record of facts per date. nutrition: rolled-up rows (in memory or as written)."""
    facts = defaultdict(lambda: {
        "kcal": None, "protein": None, "weight": None, "creatine": False,
        "floor": None, "check": False, "knee": None, "as_planned": False, "pt": False,
        "addons": set(), "cond_min": 0.0, "cond_type": "", "sport": 0, "sport_skills": set(),
        "light": "", "closed": False, "logged": False, "tags": set(), "knee_partial": False,
    })
    for r in (nutrition if nutrition is not None else read_csv("nutrition")):
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
        rounds = int(yes(r.get("floor_am"))) + int(yes(r.get("floor_pm")))
        f["floor"] = "full" if rounds >= floor_rounds(cfg, r["date"]) else ("half" if rounds else f["floor"])
        if VALID_SWELLING.match(str(r.get("am_swelling", "")).strip()):
            f["check"] = True
        ks = str(r.get("knee_session", "")).strip()
        if ks.lower().startswith("partial"):  # below the minimum session: not a loaded day (Working Rules)
            f["knee_partial"] = True
        elif ks and ks.lower() not in ("none", "no", "n", "-"):
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
        elif sess.lower() in ("home", "knee", "a", "b") and block in knee_blocks and not f["knee"] and not f["knee_partial"]:
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
    """The planned sessions for a date: the template in force then (weekly_template_history), else the current one."""
    for t in sorted(cfg.get("weekly_template_history", []), key=lambda x: x["until"]):
        if day.isoformat() <= t["until"]:
            return list(t.get(dow(day), []))
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
def compute(cfg, rules, asof=None, write=False):
    """Everything the sheet needs. write=True (sync only) also rewrites nutrition_log.csv from the food entries."""
    facts = gather(cfg, rules, rollup(cfg, write=write))
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
    ensure_files()
    st = compute(cfg, rules, d(args.date) if getattr(args, "date", None) else None, write=True)
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
def week_weights(facts, ws, upto=None):
    """Morning weigh-ins in the week starting ws (through upto, if given): list of (day, lb)."""
    out = []
    for i in range(7):
        day = ws + dt.timedelta(i)
        if upto and day > upto:
            break
        f = facts.get(day.isoformat())
        if f and f["weight"]:
            out.append((day, f["weight"]))
    return out


def weight_compare(facts, ws, upto=None):
    cur, prev = week_weights(facts, ws, upto), week_weights(facts, ws - dt.timedelta(7))
    avg = sum(w for _, w in cur) / len(cur) if cur else None
    pavg = sum(w for _, w in prev) / len(prev) if prev else None
    return {"cur": cur, "prev": prev, "avg": avg, "prev_avg": pavg,
            "delta": (avg - pavg) if avg is not None and pavg is not None else None}


def weight_line(wc, need):
    s = f"{len(wc['cur'])}/{need}"
    if wc["avg"] is not None:
        s += f" · avg {wc['avg']:.1f} lb"
    if wc["prev_avg"] is not None:
        s += f" · last week {wc['prev_avg']:.1f} ({len(wc['prev'])} reading{'s' if len(wc['prev']) != 1 else ''})"
    if wc["delta"] is not None:
        s += f" · {wc['delta']:+.1f} lb" + (" · ⚠ falling" if wc["delta"] < 0 else "")
    return s


def daily_rows():
    return {r["date"]: r for r in read_csv("daily") if r.get("date")}


def grades_line(ws, upto, rows):
    out = []
    for i in range(7):
        day = ws + dt.timedelta(i)
        if day > upto:
            break
        g = str(rows.get(day.isoformat(), {}).get("am_swelling", "")).strip()
        if VALID_SWELLING.match(g):
            out.append(f"{dow(day)} {g}")
    return " · ".join(out) or "none graded"


def real_week_table(st, cfg, rules, ws, summary=True):
    facts = st["facts"]
    t = cfg["nutrition_targets"]
    lines = ["| Day | Plan | kcal | P (g) | Wt | Cr | Floor | Check | Knee | PT | Add-on | Cond | Sport |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    kc, pr = [], []
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
        flo = {"full": "✔✔", "half": "✔"}.get(f["floor"], "")
        lines.append("| " + " | ".join([
            label + (" 🔴" if f["light"] == "red" else " 🟡" if f["light"] == "yellow" else ""), plan,
            fmt(f["kcal"]), fmt(f["protein"]), fmt(f["weight"], 1) if f["weight"] else "",
            "✔" if f["creatine"] else "", flo, "✔" if f["check"] else "",
            f["knee"] or "", "✔" if f["pt"] else "", "+".join(sorted(f["addons"])),
            f"{int(f['cond_min'])}m" if f["cond_min"] else "", str(f["sport"] or "")]) + " |")
    upto = min(ws + dt.timedelta(6), st["asof"])
    sc = week_score(ws, upto, facts, cfg, rules)
    if not summary:
        return "\n".join(lines)
    out = ["\n".join(lines), ""]
    if kc:
        hit_k = sum(1 for x in kc if x >= t["kcal"])
        hit_p = sum(1 for x in pr if x >= t["protein_g"])
        out.append(f"**Nutrition:** avg {fmt(sum(kc)/len(kc))} kcal (target {fmt(t['kcal'])}) · "
                   f"avg {fmt(sum(pr)/len(pr)) if pr else '-'} g protein (target {t['protein_g']}-{t['protein_g_max']}) · "
                   f"at kcal target {hit_k}/{len(kc)} days · at protein target {hit_p}/{len(pr)} days")
    out.append("**Weigh-ins:** " + weight_line(weight_compare(facts, ws, upto), t["weighins_per_week"]))
    out.append("**Morning swelling grades:** " + grades_line(ws, upto, daily_rows()))
    if sc:
        pl, dn = sc["planned"], sc["done"]
        sess = " · ".join(f"{k} {dn.get(k, 0)}/{v}" for k, v in pl.items())
        out.append(f"**Sessions (through {dow(d(sc['through']))}):** {sess or 'none planned yet'} · "
                   f"floor full {sc['floor_full_days']}/{sc['days']} · graded morning checks "
                   f"{sum(1 for i in range(sc['days']) if facts.get((ws + dt.timedelta(i)).isoformat(), {}).get('check'))}/{sc['days']}")
    return "\n".join(out)


def cmd_today(args, cfg, rules):
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
        if f["closed"]:
            done.append("day closed")
        print("Logged: " + (", ".join(done) if done else "nothing yet"))
        need = floor_rounds(cfg, day.isoformat())
        missing = [x for x, ok in [("morning check (grade swelling)", f["check"]),
                                   ("daily minimum (weighted heel prop" + (f" x{need})" if need > 1 else ")"), f["floor"] == "full"),
                                   ("creatine", f["creatine"])] if not ok]
        if missing:
            print("Still open: " + ", ".join(missing))
    else:
        print("Logged: nothing yet. Still open: morning check, daily minimum (weighted heel prop), creatine")


def cmd_week(args, cfg, rules):
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
                  + real_week_table(st, cfg, rules, ws)
                  + "\n\n**Latest measured:** " + latest_measured_line(cfg))
    replace_block(P["real_now"], real_block, "NOW — the Ledger")
    s = st["sheet"]
    saga_block = ("_Engine block, regenerated by `sync`._\n\n```\n" + sheet_text(s) + "\n```\n\n"
                  f"**Chapter {s['chapter_now']['chapter']}, so far (on what's logged):** {s['chapter_now']['tier_so_far']}")
    replace_block(P["saga_now"], saga_block, "NOW — the Chronicle")


# ---------------------------------------------------------------- measurements
def mkey(r):
    """Sort key: 'pre-op' rows come before every dated row."""
    s = str(r.get("date", "")).strip()
    return "0000-00-00" if s == "pre-op" else s


def mdate(s):
    return s if s == "pre-op" else md(d(s))


def metric_specs(cfg):
    return {k: v for k, v in cfg.get("measurement_metrics", {}).items() if not k.startswith("_")}


def mval(metric, v, unit):
    x = num(v)
    if x is None:
        return str(v)
    if unit == "deg":
        return f"{x:+g}°" if metric == "ext_deg" and x else f"{x:g}°"
    return f"{x:g} {unit}"


def measurement_sets(cfg):
    """One record per (date, metric, method) with the L and R values and the LSI where the metric has one."""
    specs = metric_specs(cfg)
    groups = {}
    for r in sorted(read_csv("measurements"), key=mkey):
        m = r.get("metric", "")
        g = groups.setdefault((r.get("date", ""), m, r.get("method", "")), {
            "date": r.get("date", ""), "metric": m, "method": r.get("method", ""), "source": r.get("source", ""),
            "visit": r.get("visit", ""), "unit": r.get("unit") or specs.get(m, {}).get("unit", ""), "L": None, "R": None})
        side = str(r.get("side", "")).strip().upper()
        if side in ("L", "R"):
            g[side] = num(r.get("value"))
    out = sorted(groups.values(), key=mkey)
    for g in out:
        kind, left, right = specs.get(g["metric"], {}).get("lsi"), g["L"], g["R"]
        g["lsi"] = None
        if kind == "lower" and left and right is not None:  # timed tests: the faster right side is the reference
            g["lsi"] = 100 * right / left
        elif kind and kind != "lower" and right and left is not None:
            g["lsi"] = 100 * left / right
    return out


def set_text(g):
    bits = [f"{s} {mval(g['metric'], g[s], g['unit'])}" for s in ("L", "R") if g[s] is not None]
    if g["lsi"] is not None:
        bits.append(f"LSI {g['lsi']:.1f}%")
    return " · ".join(bits)


def metric_label(m, spec):
    return spec.get("label") or m.rsplit("_", 1)[0].replace("_", " ")


def latest_measured_line(cfg):
    """The gate numbers for NOW: the latest left value, or the latest LSI for strength metrics."""
    sets, parts = measurement_sets(cfg), []
    for m, spec in metric_specs(cfg).items():
        ms = [g for g in sets if g["metric"] == m]
        if not spec.get("now") or not ms:
            continue
        name = metric_label(m, spec)
        paired = [g for g in ms if g["lsi"] is not None]
        lefts = [g for g in ms if g["L"] is not None]
        if spec.get("lsi") and paired:
            g = paired[-1]
            txt = f"{name} LSI {g['lsi']:.1f}% ({mdate(g['date'])})"
            if lefts and mkey(lefts[-1]) > mkey(g):
                txt += f", L {mval(m, lefts[-1]['L'], lefts[-1]['unit'])} ({mdate(lefts[-1]['date'])})"
            parts.append(txt)
        elif lefts:
            g = lefts[-1]
            parts.append(f"{name} L {mval(m, g['L'], g['unit'])} ({mdate(g['date'])})")
    return " · ".join(parts) or "nothing yet"


def measures_in(cfg, ws, we):
    return [g for g in measurement_sets(cfg) if g["date"] != "pre-op" and ws.isoformat() <= g["date"] <= we.isoformat()]


def cmd_measures(args, cfg, rules):
    specs, sets = metric_specs(cfg), measurement_sets(cfg)
    if args.metric:
        if args.metric not in specs:
            sys.exit(f"unknown metric '{args.metric}'. Known: {', '.join(specs)}")
        print(f"# {args.metric} ({specs[args.metric].get('unit', '')}): {specs[args.metric].get('about', '')}")
        for g in (g for g in sets if g["metric"] == args.metric):
            print(f"{mdate(g['date']):<7} {g['source']:<8} {set_text(g)}" + (f"  [{g['method']}]" if g["method"] else "")
                  + (f"  ({g['visit']})" if g["visit"] else ""))
        return
    for m, spec in specs.items():
        ms = [g for g in sets if g["metric"] == m]
        bits = []
        for s in ("L", "R"):
            last = [g for g in ms if g[s] is not None]
            if last:
                g = last[-1]
                bits.append(f"{s} {mval(m, g[s], g['unit'])} ({mdate(g['date'])}" + (f", {g['method']}" if g["method"] else "") + ")")
        paired = [g for g in ms if g["lsi"] is not None]
        if paired:
            bits.append(f"LSI {paired[-1]['lsi']:.1f}% ({mdate(paired[-1]['date'])})")
        print(f"{m:<20} " + (" · ".join(bits) or "not measured"))


def cmd_measure(args, cfg, rules):
    specs = metric_specs(cfg)
    rows = read_csv("measurements")
    added = 0
    for item in as_list(args.payload):
        if not item.get("date"):
            sys.exit("each row needs a date (ISO, or 'pre-op')")
        m, side = item.get("metric", ""), str(item.get("side", "")).strip().upper()
        if m not in specs:
            sys.exit(f"unknown metric '{m}'. Add it to config.json -> measurement_metrics first. Known: {', '.join(specs)}")
        if side not in ("L", "R"):
            sys.exit("side must be L or R (one row per side)")
        if num(item.get("value")) is None:
            sys.exit(f"value must be a number, got '{item.get('value')}'")
        date = "pre-op" if str(item.get("date", "")).strip() == "pre-op" else d(item["date"]).isoformat()
        row = {k: item.get(k, "") for k in COLS["measurements"]}
        row.update({"date": date, "side": side, "unit": item.get("unit") or specs[m].get("unit", "")})
        rows.append(row)
        added += 1
    rows.sort(key=mkey)
    write_csv("measurements", rows)
    print(f"measurements: appended {added} row(s)")


# ---------------------------------------------------------------- weekly recap (the checkpoint's numbers)
NUT_LABEL = {"kcal": "kcal", "protein_g": "protein g", "carbs_g": "carbs g", "fat_g": "fat g", "fiber_g": "fiber g",
             "sat_fat_g": "sat fat g", "sugar_g": "sugar g", "sodium_mg": "sodium mg", "potassium_mg": "potassium mg",
             "calcium_mg": "calcium mg", "iron_mg": "iron mg", "magnesium_mg": "magnesium mg", "zinc_mg": "zinc mg",
             "vit_c_mg": "vit C mg", "vit_d_mcg": "vit D mcg", "omega3_mg": "omega-3 mg"}


def nutrient_bounds(cfg):
    """Per nutrient: min/max and how to print it. Targets from nutrition_targets, references from nutrition_reference."""
    t = cfg["nutrition_targets"]
    b = {"kcal": {"min": t["kcal"], "show": fmt(t["kcal"]), "ref": False},
         "protein_g": {"min": t["protein_g"], "show": f"{t['protein_g']}–{t['protein_g_max']}", "ref": False}}
    for k in ("carbs_g", "fat_g"):
        v = t.get(k)
        if isinstance(v, list) and len(v) == 2:
            b[k] = {"min": v[0], "max": v[1], "show": f"{v[0]}–{v[1]}", "ref": False}
    for k, r in cfg.get("nutrition_reference", {}).items():
        if not k.startswith("_"):
            b[k] = {"min": r.get("min"), "max": r.get("max"), "show": r.get("show", ""), "ref": True}
    return b


def in_bounds(v, bd):
    return (bd.get("min") is None or v >= bd["min"]) and (bd.get("max") is None or v <= bd["max"])


def morning_text(row):
    """A next-morning response: grade, pain, light, and the note when ungraded."""
    if not row:
        return "nothing logged"
    g = str(row.get("am_swelling", "")).strip()
    graded = bool(VALID_SWELLING.match(g))
    parts = [g if graded else "not graded"]
    if str(row.get("am_pain", "")).strip():
        parts.append(f"pain {row['am_pain'].strip()}")
    if str(row.get("light", "")).strip().lower() in ("yellow", "red"):
        parts.append(row["light"].strip().lower())
    note = str(row.get("am_notes", "")).strip()
    if note and not graded:
        parts.append(f'"{note[:60]}{"…" if len(note) > 60 else ""}"')
    return ", ".join(parts)


def recap_text(st, cfg, rules, ws):
    facts, asof = st["facts"], st["asof"]
    we = ws + dt.timedelta(6)
    upto = min(we, asof)
    days = [ws + dt.timedelta(i) for i in range(7) if ws + dt.timedelta(i) <= upto]
    t = cfg["nutrition_targets"]

    def fx(day):  # facts is a defaultdict; .get never creates an entry
        return facts.get(day.isoformat()) or {}

    out = [f"_Engine numbers: `python3 engine/darrow.py recap --date {ws.isoformat()} --write` regenerates this block · "
           f"post-op weeks {post_op_week(cfg, ws)}–{post_op_week(cfg, we)} · POD {pod(cfg, ws)}–{pod(cfg, we)} · "
           f"computed {dow(asof)} {asof.isoformat()}"
           + (f" · **week in progress, through {dow(upto)} {md(upto)}**" if upto < we else "") + "_",
           "", real_week_table(st, cfg, rules, ws, summary=False), ""]
    flags = []

    # nutrition
    nut = {r["date"]: r for r in rollup(cfg) if r.get("date")}
    nrows = [nut[x.isoformat()] for x in days if num(nut.get(x.isoformat(), {}).get("kcal")) is not None]
    partial_today = upto == asof and asof.isoformat() in nut
    out += [f"**Nutrition** · {len(nrows)} of {len(days)} days with totals" + (" (today's is partial)" if partial_today else ""),
            "", "| Nutrient | Avg | Target / ref | Days in range | |", "|---|---|---|---|---|"]
    bounds = nutrient_bounds(cfg)
    off, low, high = [], [], []
    for k in NUTRIENTS:
        vals = [v for v in (num(r.get(k)) for r in nrows) if v is not None]
        bd = bounds.get(k, {})
        if not vals:
            out.append(f"| {NUT_LABEL[k]} | – | {bd.get('show', '')} | | not logged |")
            continue
        avg = sum(vals) / len(vals)
        shown = (fmt(avg, 1) if k in ONE_DECIMAL else fmt(avg)) + (f" ({len(vals)} d)" if len(vals) < len(nrows) else "")
        if not bd:
            out.append(f"| {NUT_LABEL[k]} | {shown} | | | |")
            continue
        status = "ok"
        if bd.get("min") is not None and avg < bd["min"]:
            status = "low" if bd["ref"] else "below"
        elif bd.get("max") is not None and avg > bd["max"]:
            status = "high" if bd["ref"] else "above"
        if status in ("below", "above"):
            off.append(f"{NUT_LABEL[k]} {status}")
        elif status == "low":
            low.append(NUT_LABEL[k])
        elif status == "high":
            high.append(NUT_LABEL[k])
        hits = sum(1 for v in vals if in_bounds(v, bd))
        out.append(f"| {NUT_LABEL[k]} | {shown} | {bd['show']} | {hits}/{len(vals)} | {status} |")
    cr = sum(1 for x in days if fx(x).get("creatine"))
    out += ["", f"Creatine {cr}/{len(days)} days. Omega-3 days in range stand in for fish days."]
    if off:
        flags.append("off target: " + ", ".join(off))
    if low:
        flags.append("low vs reference: " + ", ".join(low))
    if high:
        flags.append("high vs reference: " + ", ".join(high))

    # weight
    wc = weight_compare(facts, ws, upto)
    wr = cfg.get("weight_rule", {})
    need = wr.get("min_readings", t["weighins_per_week"])
    out += ["", "**Weight** · " + weight_line(wc, t["weighins_per_week"])]
    if wc["cur"]:
        out.append("Readings: " + " · ".join(f"{dow(x)} {w:.1f}" for x, w in wc["cur"]))
    if wc["delta"] is not None and wc["delta"] < 0:
        out.append("⚠ The weekly average is falling: say so plainly and suggest telling the surgeon/PCP (Golden rule 3).")
        flags.append(f"weight falling ({wc['delta']:+.1f} lb)")
    if wr and len(wc["cur"]) >= need and len(wc["prev"]) >= need:
        dl = wc["delta"]
        if dl < wr["gain_low_lb"]:
            rule = "losing/flat → add 150–250 kcal/day"
        elif dl <= wr["gain_high_lb"]:
            rule = "gaining ~0.25–0.75 lb/week → stay"
        elif dl <= wr["reduce_above_lb"]:
            rule = "between the guide's bands (0.75–1 lb/week) → stay and watch"
        else:
            rule = ">1 lb/week → reduce ~150–200 kcal if it persists after the initial rebound"
        out.append(f"Guide's rule (two weeks of ≥{need} readings): {dl:+.2f} lb/week → {rule}.")
    else:
        out.append(f"Guide's rule: not yet; it needs two weeks of ≥{need} readings (this week {len(wc['cur'])}, last week {len(wc['prev'])}).")

    # rehab
    rows = daily_rows()
    out += ["", "**Rehab**"]
    off_plan = []
    for x in days:
        f = fx(x)
        if not (f.get("knee") or f.get("pt")):
            continue
        what = []
        if f.get("knee"):
            kap = str(rows.get(x.isoformat(), {}).get("knee_as_planned", "")).strip().upper()
            what.append(f"knee {f['knee']}" + {"Y": " (as written)", "N": " (not as written)"}.get(kap, ""))
            if kap == "N":
                off_plan.append(dow(x))
        if f.get("pt"):
            what.append("PT")
        nxt = x + dt.timedelta(1)
        resp = "not yet" if nxt > asof else morning_text(rows.get(nxt.isoformat()))
        out.append(f"- {dow(x)} {md(x)} · {' + '.join(what)}" + (" · 🔴 red day" if f.get("light") == "red" else "")
                   + f" → {dow(nxt)}: {resp}")
    if not any(fx(x).get("knee") or fx(x).get("pt") for x in days):
        out.append("- no loaded days")
    if off_plan:
        flags.append("knee sessions not as written: " + ", ".join(off_plan))
    floors = [fx(x).get("floor") for x in days]
    n_graded = sum(1 for x in days if fx(x).get("check"))
    out.append(f"Floor: full {floors.count('full')}/{len(days)} · half {floors.count('half')} · "
               f"none {len(days) - floors.count('full') - floors.count('half')}")
    out.append(f"Morning swelling graded {n_graded}/{len(days)}: {grades_line(ws, upto, rows)}")
    lights = {c: [f"{dow(x)}" for x in days if fx(x).get("light") == c] for c in ("yellow", "red")}
    if lights["yellow"] or lights["red"]:
        out.append("Lights: " + " · ".join(f"{c} {', '.join(v)}" for c, v in lights.items() if v))
        if lights["red"]:
            flags.append("red-light days " + ", ".join(lights["red"]))

    # sessions and add-on
    sc = week_score(ws, upto, facts, cfg, rules) or {"planned": {}}
    pl = sc["planned"]
    cond_min = sum(fx(x).get("cond_min") or 0 for x in days)
    tag = rules["tags"]["session_tags"]
    did = {
        "knee": sum(1 for x in days if fx(x).get("knee")),
        "pt": sum(1 for x in days if fx(x).get("pt")),
        "upper": sum(1 for x in days if "upper" in {tag.get(a) for a in fx(x).get("addons", ())}),
        "cond": sum(1 for x in days if (fx(x).get("cond_min") or 0) >= rules["daily"]["conditioning"]["min_minutes"]),
        "accessory": sum(1 for x in days if "accessory" in {tag.get(a) for a in fx(x).get("addons", ())}),
        "power": sum(1 for x in days if "power" in {tag.get(a) for a in fx(x).get("addons", ())}),
        "sport": sum(fx(x).get("sport") or 0 for x in days),
    }
    names = {"knee": "knee sessions", "pt": "PT", "upper": "upper", "cond": "conditioning", "accessory": "accessory",
             "power": "power", "sport": "sport drills"}
    parts = []
    for k, label in names.items():
        if k in pl:
            parts.append(f"{label} {did[k]} of {pl[k]}" + (f" ({int(cond_min)} min)" if k == "cond" and cond_min else ""))
        elif did[k]:
            parts.append(f"{label} {did[k]}")
    out += ["", "**Sessions vs plan:** " + " · ".join(parts)]
    if sc.get("excused"):
        out.append("Excused (red light): " + ", ".join(sc["excused"]))

    # measurements
    ms = measures_in(cfg, ws, we)
    specs = metric_specs(cfg)
    out += ["", "**Measured this week:** " + ("; ".join(
        f"{mdate(g['date'])} {g['source']} {metric_label(g['metric'], specs.get(g['metric'], {}))} {set_text(g)}"
        for g in ms) or "nothing")]
    out += ["", "**Flags:** " + (" · ".join(flags) or "none")]
    return "\n".join(out)


CHECKPOINT_SKELETON = """# Checkpoint — Sun {sun} · week Sun {ws} – Sat {we}

*Post-op weeks {w1}–{w2} · Phase {phase}. The archive of this week: what happened and what was decided. The program in force: `{state}`.*

## Numbers (engine)

<!-- engine:start -->
<!-- engine:end -->

## Nutrition

<!-- What the numbers mean: days at target, each flagged micro and the foods behind it, fish, one or two fixes for next week. -->

## Weight

<!-- The trend and the guide's rule. A target change goes to config.json -> nutrition_targets with its source and date. -->

## Rehab

<!-- Loaded days and their mornings, floor, the swelling trend, sessions vs plan, progressions made and whether each kept the one-change rule. -->

## Add-on and conditioning

<!-- Upper 2 of 2? (decides the block), bike, accessory/power. -->

## PT and measurements

<!-- Each visit this week with its real/visits/ file; what was measured; which questions were answered. -->

## Gates

<!-- The next phase gate, criterion by criterion, with evidence. A Knot tied this week: its evidence. -->

## Program — changes and decisions

<!-- What changed in the program or the targets, and why. A changed program means a new state file; an unchanged one gets its "Last reviewed" line updated. -->

## Next week

<!-- Day by day with doses, or a pointer to the state file's program section if nothing changed. -->
"""


def newest(paths):
    paths = sorted(paths)
    return paths[-1] if paths else None


def cmd_recap(args, cfg, rules):
    st = compute(cfg, rules)
    ws = week_start(d(args.date)) if args.date else week_start(st["asof"]) - dt.timedelta(7)
    we = ws + dt.timedelta(6)
    if ws > st["asof"]:
        sys.exit(f"the week of Sun {ws} hasn't started yet (today is {st['asof']})")
    text = recap_text(st, cfg, rules, ws)
    if not args.write:
        print(text)
        return
    if we >= st["asof"] and not args.force:
        sys.exit(f"the week of Sun {ws} – Sat {we} is still in progress; the checkpoint is written after it ends (use --force anyway)")
    sun = ws + dt.timedelta(7)
    path = P["checkpoints"] / f"{sun.isoformat()}.md"
    if not path.exists():
        state = newest(P["state_dir"].glob("ACL_Recovery_State_*.md"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(CHECKPOINT_SKELETON.format(
            sun=sun.isoformat(), ws=md(ws), we=md(we), w1=post_op_week(cfg, ws), w2=post_op_week(cfg, we),
            phase=cfg["rehab"]["current_phase"], state=state.relative_to(ROOT) if state else "real/state/"), encoding="utf-8")
        print(f"created {path.relative_to(ROOT)} from the checkpoint template")
    replace_block(path, text, "")
    print(f"numbers written to {path.relative_to(ROOT)}\n")
    print(text)


# ---------------------------------------------------------------- documents, one section at a time
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def doc_path(name):
    fixed = {"addon": P["addon"], "rules": P["working_rules"], "guide": P["guide"], "master": P["master"], "now": P["real_now"]}
    if name in fixed:
        return fixed[name]
    globs = {"state": (P["state_dir"], "ACL_Recovery_State_*.md"), "checkpoint": (P["checkpoints"], "20*.md"),
             "visit": (P["visits"], "20*.md")}
    if name in globs:
        found = newest(globs[name][0].glob(globs[name][1]))
        if not found:
            sys.exit(f"no {name} file yet")
        return found
    p = Path(name) if Path(name).is_absolute() else ROOT / name
    if not p.exists():
        sys.exit(f"no document '{name}'. Use state, addon, rules, guide, master, checkpoint, visit, now, or a path")
    return p


def doc_headings(lines):
    out, fence = [], False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        m = None if fence else HEADING.match(ln)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def find_section(hs, q):
    q = q.lower().strip()
    if re.fullmatch(r"\d+(\.\d+)*", q):
        return next((k for k, (_, _, t) in enumerate(hs) if re.match(rf"{re.escape(q)}[.):\s]", t + " ")), None)
    phrase = next((k for k, (_, _, t) in enumerate(hs) if q in t.lower()), None)  # the exact phrase first
    if phrase is not None:
        return phrase
    words = q.split()
    return next((k for k, (_, _, t) in enumerate(hs) if all(w in t.lower() for w in words)), None)


def cmd_doc(args, cfg, rules):
    path = doc_path(args.name)
    lines = path.read_text(encoding="utf-8").split("\n")
    hs = doc_headings(lines)
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path

    def end_of(k):
        lvl = hs[k][1]
        return next((i for i, l2, _ in hs[k + 1:] if l2 <= lvl), len(lines))

    if not args.section:
        print(f"{rel} · {len(lines)} lines")
        for k, (i, lvl, title) in enumerate(hs):
            print(f"{'  ' * (lvl - 1)}{title}  ({end_of(k) - i} lines)")
        return
    for q in args.section:
        k = find_section(hs, q)
        if k is None:
            print(f"{rel}: no section matches '{q}'. Outline: python3 engine/darrow.py doc {args.name}\n")
            continue
        print(f"<!-- {rel} · lines {hs[k][0] + 1}–{end_of(k)} -->")
        print("\n".join(lines[hs[k][0]:end_of(k)]).rstrip() + "\n")


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
    pretty = {"CRITICAL SUCCESS": "Critical success", "CRITICAL FAILURE": "Critical failure", "SUCCESS": "Success",
              "PARTIAL (success at a cost)": "Partial: success at a cost", "FAILURE": "Failure"}[result]
    # line 1 is the chapter's dice line, in the style guide's exact form; paste it as it is
    print(f"`[{(args.stat or 'flat').upper()} · DC {args.dc}]` d20 **{shown}** {mod_txt} = **{total}** — *{pretty}*")
    print(f"(roll {label}: {result}; recorded in saga/state/rolls.csv)")


def cmd_inspire(args, cfg, rules):
    st = compute(cfg, rules)
    if st["sheet"]["inspiration"] < 1:
        sys.exit("no Inspiration to spend")
    sp = read_csv("spends")
    sp.append({"date": st["asof"].isoformat(), "what": "inspiration", "reason": args.reason})
    write_csv("spends", sp)
    print(f"Inspiration spent: {args.reason} (left: {st['sheet']['inspiration'] - 1})")


def cmd_chapter_close(args, cfg, rules):
    """Freeze a finished week's score and tier as a chapter.

    Without --date: the most recent fully completed Sun–Sat week that is not already in chapters.csv.
    With --date D: the week containing D. A week still in progress is refused unless --force is given.
    """
    st = compute(cfg, rules)
    today = st["asof"]
    rows = read_csv("chapters")
    closed = {r["chapter"] for r in rows}
    first_ws = week_start(d(cfg["chronicle_start"]))
    if args.date:
        ws = week_start(d(args.date))
    else:
        ws = week_start(today) - dt.timedelta(7)  # the week that ended last Saturday
        while ws >= first_ws and str(chapter_no(cfg, ws)) in closed:
            ws -= dt.timedelta(7)
        if ws < first_ws:
            cur = week_start(today)
            sys.exit(f"nothing to close: every completed week since the chronicle began is already in chapters.csv. "
                     f"The week of Sun {cur} – Sat {cur + dt.timedelta(6)} is still in progress; "
                     f"use --date {cur + dt.timedelta(6)} --force to close it anyway.")
    week_end = ws + dt.timedelta(6)
    if ws < first_ws:
        sys.exit(f"the week of Sun {ws} is before the chronicle began ({cfg['chronicle_start']})")
    if week_end >= today and not args.force:
        sys.exit(f"the week of Sun {ws} – Sat {week_end} is still in progress (today is {today}); use --force to close it anyway")
    sc = week_score(ws, week_end, st["facts"], cfg, rules)
    n = chapter_no(cfg, ws)
    if str(n) in closed and not args.force:
        r = next(r for r in rows if r["chapter"] == str(n))
        print(f"Chapter {n} (Sun {ws} – Sat {week_end}) already closed: score {r['score']} · {r['tier']} (roll mod {r['roll_mod']}). Use --force to redo.")
        return
    print(f"closing chapter {n}: Sun {ws} – Sat {week_end}")
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
    names = {k["n"]: k["short"] for k in rules.get("knots", [])} or {1: "Straightening", 2: "Walking", 3: "Standing", 4: "the Road", 5: "Lightning", 6: "Turning", 7: "the Field"}
    if any(k["knot"] == args.n for k in knots):
        sys.exit(f"Knot {args.n} is already tied")
    if args.n != len(knots) + 1:
        sys.exit(f"Knots tie in order; next is {len(knots) + 1}")
    knots.append({"knot": args.n, "name": names[args.n], "date": d(args.date).isoformat(), "evidence": args.evidence})
    save_json(P["config"], cfg)
    print(f"Knot {roman(args.n)} ({names[args.n]}) tied {args.date}. Run sync.")


def cmd_show(args, cfg, rules):
    """Record view: print the rows for one date as key: value lines, blank fields omitted. Reads only; never writes."""
    key = {"daily": "daily", "nutrition": "nutrition", "food": "food", "ex": "exercise", "exercise": "exercise", "sport": "sport",
           "measurements": "measurements"}[args.log]
    date = "pre-op" if key == "measurements" and args.date == "pre-op" else d(args.date).isoformat()
    rows = rollup(cfg) if key == "nutrition" else read_csv(key)  # nutrition as sync would roll it up, in memory
    rows = [r for r in rows if r.get("date") == date]
    if getattr(args, "session", None):
        rows = [r for r in rows if str(r.get("session", "")).lower() == args.session.lower()]
    if not rows:
        print(f"{P[key].name}: no rows for {date}")
        return
    for i, r in enumerate(rows):
        if i:
            print()
        for k in list(COLS[key]) + [c for c in r if c not in COLS[key]]:
            v = r.get(k)
            if v not in (None, ""):
                print(f"{k}: {v}")
    print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''} in {P[key].name})")


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
    specs = metric_specs(cfg)
    for i, r in enumerate(read_csv("measurements"), 2):
        where = f"measurements.csv line {i}"
        if r.get("date") != "pre-op":
            try:
                d(r.get("date", ""))
            except Exception:
                problems.append(f"{where}: bad date '{r.get('date')}' (ISO date or 'pre-op')")
        if r.get("metric") not in specs:
            problems.append(f"{where}: metric '{r.get('metric')}' is not in config.json -> measurement_metrics")
        if str(r.get("side", "")).strip().upper() not in ("L", "R"):
            problems.append(f"{where}: side '{r.get('side')}' must be L or R")
        if num(r.get("value")) is None:
            problems.append(f"{where}: value '{r.get('value')}' is not a number")
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
    s = sub.add_parser("show"); s.add_argument("log", choices=["daily", "nutrition", "food", "ex", "exercise", "sport", "measurements"]); s.add_argument("date"); s.add_argument("--session")
    s = sub.add_parser("recap"); s.add_argument("--date"); s.add_argument("--write", action="store_true"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("measure"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("measures"); s.add_argument("--metric")
    s = sub.add_parser("doc"); s.add_argument("name"); s.add_argument("section", nargs="*")
    sub.add_parser("check")
    args = ap.parse_args()
    cfg, rules = load_json(P["config"]), load_json(P["rules"])
    {
        "sync": cmd_sync, "today": cmd_today, "week": cmd_week, "sheet": cmd_sheet, "set": cmd_set,
        "food": cmd_food, "roll": cmd_roll, "inspire": cmd_inspire, "chapter-close": cmd_chapter_close,
        "knot": cmd_knot, "check": cmd_check, "show": cmd_show, "recap": cmd_recap,
        "measure": cmd_measure, "measures": cmd_measures, "doc": cmd_doc,
        "ex": lambda a, c, r: cmd_append("exercise", a, c),
        "sport": lambda a, c, r: cmd_append("sport", a, c),
    }[args.cmd](args, cfg, rules)


if __name__ == "__main__":
    main()
