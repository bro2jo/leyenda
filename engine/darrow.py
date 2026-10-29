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
  set nutrition|daily DATE k=v ...   upsert fields on a day's row (notes+=text appends; an unknown column is refused).
                               e.g. set daily D am_swelling=trace am_pain=0 floor_am=Y knee_session=A knee_as_planned=Y;
                               set daily D together=Y (time together on purpose: the Tether's practice; sync reports
                               TETHER TIED / DRAWN); set nutrition D weight_lb=156.2 creatine=Y "notes+=shake missed"
  close DATE [--force]         close a day in one step: closed=Y, sync, then saga.py brief --date DATE (what the day's scene must carry);
                               refuses a missed day (nothing logged), a day already closed, and a new week whose last chapter is unclosed
  food add 'JSON' | food list DATE | food rm ID | food lib TEXT
                               add: an object or a list {date, time, meal, item, qty, kcal, protein_g, … every nutrient
                               column you can estimate, source (label|library|photo|estimate|library+estimate), notes};
                               refused for dates before config.json -> food_itemised_from. rm ID: DATE#N (from food list)
  ex add 'JSON'                append exercise-log rows (list or object)
  sport add 'JSON'             append sport-log rows
  roll LABEL --stat S --dc N [--adv|--dis] [--bonus N] [--prof] [--art ID ...] [--chapter N | --tier] [--reroll [--paid]]
                               prints the chapter's dice line (paste line 1 as is); --art adds an Art's rank (Insight = --stat resolve --prof --art wardens_eye);
                               --reroll spends one Inspiration on a second cast (--paid: the *[Inspiration]* option that offered it already spent it);
                               a climax check that fails outright is cast again on his Inspiration, again and again, until it succeeds or he has none
                               (rules.json -> inspiration.auto_reroll_on_fail): every line it prints goes on the page, in order, as one block
  odds [--stat S] [--prof] [--art ID ...] [--chapter N | --tier] [--adv|--dis] [--bonus N] [--dc N | --target P] [--json]
                               what a DC means for him: the chance of a full success, a partial and an outright failure with the
                               modifiers roll would carry (DC 8-20, or one DC); --target P names the DC nearest that chance of a
                               full success. The climax's brief prints it: the week's tier sets the DC (rules.json -> target_odds)
  inspire --reason TEXT       spend one Inspiration on a bold option or a reroll (earned: a week with the daily minimum
                               every day, a Triumph week, every level from 5 on)
  chapter-close [--date D] [--partial-ok] [--force]   Sundays: freeze the week's score and tier as a chapter (pass last
                               Saturday as D). Refuses while that Saturday looks unfinished (nothing logged, no food, or
                               under 60% of the kcal target with no dinner) until he says that was all (--partial-ok).
                               Without --date: the most recent completed, unclosed week; an in-progress week, or redoing
                               a closed one, needs --force. The dice (--chapter N), the road and the XP bonus read the
                               frozen tier from then on
  knot tie N --date D --evidence TEXT   record a Knot of the Binding (a gate in config.json -> rehab.knot_gates passed
                               with PT/surgeon clearance or measured criteria; never a future date); saga.py now then
                               prints the KNOT line: when the Book's transition falls due
  project open TITLE --tasks T1 T2 ... [--id slug] [--date D] [--due D]
                               the week's work: one real goal outside the knee, in 2-5 tasks, one project live at a time
                               (real/projects.json); `today` names its next task. Due the Saturday of the week it opens
                               (--due moves it). `saga.py tale bind ID` binds the tale it tells
  project done TASK [--date D] a task reported (its number, or a few of its words): the tale it is bound to owes a piece
                               (`saga.py now` says so); the last task finishes the project: WORKS +1 on the sheet, +1 Inspiration.
                               Finished after its due day, the project is late: its tale ends on the lesser keepsake
  project show [--all] | project drop --why TEXT   the live projects (every project with --all); set one aside, no shame.
                               Several may be live side by side, each with its own tale: `done` matches a task's words across
                               them; a task's number, or `drop`, takes --id ID when more than one is live
  show daily|nutrition|food|ex|sport|measurements DATE [--session S]   one date's rows as key: value lines (non-empty fields only); never read the CSVs raw
  recap [--date D] [--write]   the weekly checkpoint numbers for the week containing D (default: the last completed week):
                               macros, micros vs reference, weight vs last week, loaded days -> next mornings, sessions vs
                               plan, measured, flags;
                               --write puts them in real/checkpoints/<the Sunday after>.md (creates the file from the template)
  measure add 'JSON'           append rows to real/logs/measurements.csv, one per side: {date (or pre-op), source, metric,
                               side, value, unit, method, visit, notes}; metrics from config.json -> measurement_metrics
  measures [--metric M]        latest value per metric and side, with LSI; --metric M: that metric's full history
  doc state|rules|addon|master|offseason|sport|sportguide|guide|ptnotes|index|now|checkpoint|PATH [SECTION ...]
                               one section of a document (number or title words); no SECTION: its outline
  check                        validate the logs
  ship -m MESSAGE [--no-push]  the end of every change, in one step: check the logs, sync, saga.py check, build the site,
                               commit everything, push to main (pull --rebase and retry when the push is rejected; never
                               force), then push the session's own branch too when it isn't main. Stops at the first
                               failing step and says which. MESSAGE is reader-safe: he reads it (CLAUDE.md)
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
import re
import secrets
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = {
    "config": ROOT / "real/config.json",
    "rules": ROOT / "engine/rules.json",
    "nutrition": ROOT / "real/logs/nutrition_log.csv",
    "food": ROOT / "real/logs/food_entries.csv",
    "foods": ROOT / "real/logs/food_library.csv",
    "daily": ROOT / "real/logs/daily_log.csv",
    "exercise": ROOT / "real/logs/exercise_log.csv",
    "sport": ROOT / "real/logs/sport_log.csv",
    "measurements": ROOT / "real/logs/measurements.csv",
    "state_dir": ROOT / "real/state",
    "state": ROOT / "real/state/recovery_state.md",
    "checkpoints": ROOT / "real/checkpoints",
    "visits": ROOT / "real/visits",
    "addon": ROOT / "real/plan/whole_athlete_addon.md",
    "working_rules": ROOT / "real/plan/working_rules.md",
    "guide": ROOT / "real/plan/nutrition_guide.md",
    "master": ROOT / "real/plan/rehab_master_plan.md",
    "offseason": ROOT / "real/plan/offseason_program_24_week.md",
    "index": ROOT / "real/README.md",
    "sport_plan": ROOT / "real/plan/sport_plan.md",
    "sport_guide": ROOT / "real/plan/ultimate_offseason_guide.md",
    "ptnotes": ROOT / "real/visits/pt_notes.md",
    "projects": ROOT / "real/projects.json",
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
              "am_swelling", "am_trend", "am_pain", "am_extension", "flexion", "catch", "wellness", "am_notes",
              "floor_am", "floor_pm", "knee_session", "knee_min", "knee_rpe", "knee_as_planned",
              "pain_session", "pain_pm", "pt", "addon_session", "addon_min", "addon_rpe",
              "conditioning_type", "conditioning_min", "sport_min",
              "hours_on_feet", "gym_min_on_feet", "crutches", "gait_notes", "adjuncts", "sleep_h", "together", "closed", "notes"],
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
NOT_DONE = re.compile(r"^\s*(not done|skipped)\b", re.I)  # exercise-log notes that mark a planned item as not done


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
    first_itemised = cfg.get("food_itemised_from")
    for date, items in by_date.items():
        if first_itemised and date < first_itemised:
            continue  # a dashboard-era day: its total is the record; `food add` refuses item rows for it
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
        "addons": set(), "cond_min": 0.0, "cond_type": "", "sport": 0, "sport_skills": set(), "sport_sessions": set(),
        "light": "", "closed": False, "logged": False, "tags": set(), "knee_partial": False,
        "together": False, "pt_missed": False, "knee_unpaid": "", "addons_unpaid": set(),
        "knee_tags": set(), "other_tags": set(),
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

    # a daily row counts as logging only if it records something; a row holding nothing but `together` (the
    # Tether's practice, never scored) or the `closed` mark earns no ledger credit in the week score
    quiet_cols = {"date", "dow", "pod", "post_op_week", "dash_week_start", "together", "closed"}
    for r in read_csv("daily"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        if any(str(v or "").strip() for k, v in r.items() if k not in quiet_cols):
            f["logged"] = True
        rounds = int(yes(r.get("floor_am"))) + int(yes(r.get("floor_pm")))
        if VALID_SWELLING.match(str(r.get("am_swelling", "")).strip()):
            f["check"] = True
        need = floor_rounds(cfg, r["date"])
        if need == 0:
            # the heel prop is a weekly check now (Working Rules): the daily minimum is the graded morning check,
            # which pays its own deed, so the floor shows full without paying the floor deed a second time
            f["floor"] = "full" if f["check"] else f["floor"]
            f["floor_is_check"] = True
        else:
            f["floor"] = "full" if rounds >= need else ("half" if rounds else f["floor"])
        ks = str(r.get("knee_session", "")).strip()
        if ks.lower().startswith("partial"):  # below the minimum session: not a loaded day (Working Rules)
            f["knee_partial"] = True
        elif ks and ks.lower() not in ("none", "no", "n", "-"):
            f["knee"] = ks
        f["as_planned"] = yes(r.get("knee_as_planned"))
        if yes(r.get("pt")):
            f["pt"] = True
        elif str(r.get("pt") or "").strip().lower() in ("missed", "skipped", "no-show", "noshow"):
            f["pt_missed"] = True  # a booked visit he did not go to: the only way an appointment counts against the week
        for a in re.split(r"[+,/ ]+", str(r.get("addon_session", ""))):
            if a and a.lower() not in ("none", "no", "n", "-"):
                f["addons"].add(a)
        cm = num(r.get("conditioning_min"))
        if cm:
            f["cond_min"] = max(f["cond_min"], cm)
            f["cond_type"] = str(r.get("conditioning_type", "")).strip().lower()
        f["light"] = str(r.get("light", "")).strip().lower()
        f["closed"] = yes(r.get("closed"))
        if yes(r.get("together")):  # time together on purpose: the Tether's practice (never XP, never scored)
            f["together"] = True

    block_tags = rules["tags"]["block_tags"]
    session_tags = rules["tags"]["session_tags"]
    knee_blocks = {"knee", "single-leg", "posterior", "calf", "hip", "balance", "quad"}
    for r in read_csv("exercise"):
        if not r.get("date"):
            continue
        f = facts[r["date"]]
        f["logged"] = True
        if NOT_DONE.match(str(r.get("notes") or "")):
            continue  # a planned item recorded as not done ("NOT DONE ...", "SKIPPED ..."): a record, never a deed
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
            # which session gave the tag: an unpaid knee session's own rows give no Art practice
            is_knee_row = sess.lower() in ("home", "knee", "a", "b") and block in knee_blocks
            (f["knee_tags"] if is_knee_row else f["other_tags"]).add(block_tags[block])
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
        f["sport_sessions"].add(str(r.get("session", "")).strip().upper() or "-")  # one session, several skill rows
        sk = str(r.get("skill", "")).strip()
        if sk:
            f["sport_skills"].add(sk)
            if sk in sport_map:
                f["tags"].add("sport:" + sk)

    mark_overshoot(facts, cfg, rules)

    for date, f in facts.items():  # derived tags
        f["sport"] = len(f["sport_sessions"])  # XP and temper pay per session a day (per_day_cap), never per skill row
        for a in f["addons"]:
            if a in session_tags and session_tags[a] not in f["addons_unpaid"]:
                f["tags"].add(session_tags[a])
        if f["knee_unpaid"]:
            f["tags"] -= (f["knee_tags"] - f["other_tags"])
        if f["knee"] and not f["knee_unpaid"]:
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


def mark_overshoot(facts, cfg, rules):
    """Golden rule 6: work past the plan is logged truthfully and pays nothing (no XP, no temper, no Art practice).
    From rules.json -> overshoot.from on: a knee session the day after another knee session (the plan never runs
    them back to back), knee or upper sessions beyond the week's planned count, and the optional add-ons beyond
    once a week or before their start date (weekly_template.optional_from). Earlier days are left as they were,
    so the sheet the page has already shown never changes."""
    start = (rules.get("overshoot") or {}).get("from")
    if not start:
        return
    session_tags = rules["tags"]["session_tags"]
    weeks = defaultdict(list)
    for date in list(facts):
        if date >= start:
            weeks[week_start(d(date))].append(date)
    for ws, dates in weeks.items():
        plan, optional = week_plan(cfg, ws)
        opt_from = template_for(cfg, ws).get("optional_from") or cfg["weekly_template"].get("optional_from") or {}
        paid = defaultdict(int)
        for date in sorted(dates):
            f = facts[date]
            if f["knee"]:
                planned_today = any(session_key(p) == "knee" for p in planned_for(cfg, d(date)))
                prev = facts.get((d(date) - dt.timedelta(1)).isoformat())
                if not planned_today and prev is not None and prev["knee"]:
                    # an unplanned session the day after a session: the plan never runs them back to back. A session
                    # the plan put on this day is never the overshoot, even after an extra one the day before.
                    f["knee_unpaid"] = "back-to-back with the day before"
                elif paid["knee"] >= plan.get("knee", 0):
                    f["knee_unpaid"] = "beyond the week's planned knee sessions"
                else:
                    paid["knee"] += 1
            for kind in sorted({session_tags[a] for a in f["addons"] if a in session_tags}):
                if kind == "upper":
                    cap = plan.get("upper", 0)
                elif opt_from.get(kind) and date < opt_from[kind]:
                    cap = 0
                else:
                    cap = max(plan.get(kind, 0), 1 if kind in optional else 0)
                if paid[kind] >= cap:
                    f["addons_unpaid"].add(kind)
                else:
                    paid[kind] += 1


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

    if f["floor"] == "full" and not f.get("floor_is_check"):
        add("floor_full")
    elif f["floor"] == "half":
        add("floor_half")
    if f["check"]:
        add("morning_check")
    def unpaid(label, why):  # work past the plan: kept in the audit trail at zero (mark_overshoot)
        out.append({"date": date, "kind": "daily", "deed": f"{label} (logged; past the plan, not paid)",
                    "xp": 0, **{a: 0 for a in ATTRS}, "note": why})

    if f["knee"]:
        if f["knee_unpaid"]:
            unpaid(R["knee_session"]["label"], f"{f['knee']}: {f['knee_unpaid']}")
        else:
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
            if tag in f["addons_unpaid"]:
                unpaid(R[kind]["label"], f"{a}: beyond the week's plan, or before its start date")
            else:
                add(kind, note=a)
    c = R["conditioning"]
    if f["cond_min"] >= c["min_minutes"]:
        start = (rules.get("overshoot") or {}).get("from")
        cap_min = (cfg.get("conditioning") or {}).get("cap_min")
        paid_min = min(f["cond_min"], cap_min) if (start and cap_min and date >= start) else f["cond_min"]
        xp = min(c["xp_cap"], int(round(paid_min * c["xp_per_min"])))
        tv = min(c["temper_cap"], int(paid_min // 10))
        note = f"{int(f['cond_min'])} min {f['cond_type']}".strip()
        if paid_min < f["cond_min"]:
            note += f" (paid to the plan's {int(cap_min)} min)"
        add("conditioning", xp=xp, temper={"vigor": tv}, note=note)
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
    if f["closed"] and f["logged"]:  # a day holding only `together` earns nothing: the Tether is never scored
        add("day_closed")
    return out


def template_for(cfg, day):
    """The weekly template in force on a date: the weekly_template_history entry that covers it, else the current one."""
    for t in sorted(cfg.get("weekly_template_history", []), key=lambda x: x["until"]):
        if day.isoformat() <= t["until"]:
            return t
    return cfg["weekly_template"]


def session_key(p):
    """A plan code's family for counting: kneeA/kneeB -> knee, upper/upperA/upperB -> upper, the rest as they are."""
    return "knee" if p in ("kneeA", "kneeB", "knee") else ("upper" if p in ("upper", "upperA", "upperB") else p)


def planned_for(cfg, day):
    """The planned sessions for a date: the template in force then (weekly_template_history), else the current one,
    then real/config.json -> plan_changes for that date. A plan change is a session a PT, surgeon or trainer moved or
    cancelled ({"date", "drop": [codes], "add": [codes], "source"}): what the plan itself moves is never a miss."""
    base = list(template_for(cfg, day).get(dow(day), []))
    for ch in cfg.get("plan_changes", []):
        if ch.get("date") != day.isoformat():
            continue
        for p in as_codes(ch.get("drop")):
            hit = p if p in base else next((b for b in base if session_key(b) == session_key(p)), None)
            if hit:
                base.remove(hit)
        base += as_codes(ch.get("add"))
    return base


PLAN_CODES = ("knee", "kneeA", "kneeB", "upper", "upperA", "upperB", "cond", "pt", "sport", "accessory", "power")


def as_codes(v):
    """A plan_changes drop/add value as a list of codes (a lone string is one code, never its letters)."""
    if not v:
        return []
    return [v] if isinstance(v, str) else list(v)


SESSION_NAMES = {"knee": "knee session", "kneeA": "knee Session A", "kneeB": "knee Session B",
                 "upper": "upper session (next of A/B)", "upperA": "Upper A",
                 "upperB": "Upper B", "cond": "conditioning", "pt": "PT visit", "sport": "sport session",
                 "accessory": "accessory", "power": "power"}


def unlogged_sessions(cfg, day, f):
    """The day's planned sessions (plan_changes applied) with nothing recorded for them yet. Any outcome is a record:
    a partial knee session, a ride under the paid minimum, a booked PT visit missed. A rest day the plan ordered
    (light=red) owes none. Knee sessions match as a family (A and B alternate whatever the day), and so does the
    generic `upper` code (the next upper session in the A/B rotation); upperA/upperB and the other add-ons by code."""
    if f and f["light"] == "red":
        return []
    out = []
    for p in planned_for(cfg, day):
        k = session_key(p)
        if not f:
            hit = False
        elif k == "knee":
            hit = bool(f["knee"] or f["knee_partial"])
        elif k == "pt":
            hit = f["pt"] or f["pt_missed"]
        elif k == "cond":
            hit = f["cond_min"] > 0
        elif k == "sport":
            hit = bool(f["sport_sessions"])
        elif p == "upper":
            hit = any(a in ("upperA", "upperB") for a in f["addons"])
        else:
            hit = p in f["addons"]
        if not hit:
            out.append(SESSION_NAMES.get(p, p))
    return out


def week_plan(cfg, ws):
    """The week's planned sessions by family (knee, upper, cond, pt, sport, ...) and its optional add-ons."""
    counts = defaultdict(int)
    for i in range(7):
        for p in planned_for(cfg, ws + dt.timedelta(i)):
            counts[session_key(p)] += 1
    return counts, set(template_for(cfg, ws).get("optional", []))


def week_score(ws, upto, facts, cfg, rules):
    """Score the week starting ws (Sunday) over days ws..upto inclusive.

    Red-light days (the plan said stop) are excused: they are left out of every part. A week that is all red-light
    is scored on what rest still asks for (fuel, weigh-ins, the ledger) over those days, never on training it was
    told not to do. A planned PT visit counts only when he went or when a booked visit was missed (pt=missed):
    an appointment that was never booked is not his to miss."""
    W = rules["week_score"]["weights"]
    days = [ws + dt.timedelta(i) for i in range(7) if ws + dt.timedelta(i) <= upto]
    if not days:
        return None
    floor = checks = ledger = fuel = 0.0
    red_fuel = red_ledger = 0.0
    counted = 0
    floor_full_nonred = 0
    planned = defaultdict(int)
    done = defaultdict(int)
    pt_missed = 0
    weighins = 0
    excused = []
    for day in days:
        f = facts.get(day.isoformat())
        red = bool(f and f["light"] == "red")
        if red:
            excused.append(day.isoformat())
            red_fuel += day_fuel(f, cfg, rules) or 0
            red_ledger += 1 if f["logged"] else 0
        else:
            counted += 1
            for p in planned_for(cfg, day):
                planned[session_key(p)] += 1
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
        if f["knee"] and not f["knee_unpaid"]:  # a back-to-back session is logged, never counted as the plan's
            done["knee"] += 1
        if f["pt"]:
            done["pt"] += 1
        if f["pt_missed"]:
            pt_missed += 1
        tags = {rules["tags"]["session_tags"].get(a) for a in f["addons"]}
        if "upper" in tags:
            done["upper"] += 1
        if f["cond_min"] >= rules["daily"]["conditioning"]["min_minutes"]:
            done["cond"] += 1
        if f["sport"]:
            done["sport"] += 1
        if f["weight"]:
            weighins += 1
    for day in days:
        f = facts.get(day.isoformat())
        if f and f["light"] == "red" and f["weight"]:
            weighins += 1
    if planned.get("pt"):
        planned["pt"] = min(planned["pt"], done["pt"] + pt_missed)
        if not planned["pt"]:
            del planned["pt"]
    need_w = cfg["nutrition_targets"]["weighins_per_week"]
    total_planned = sum(planned.values())
    sess_done = sum(min(done[k], v) for k, v in planned.items())
    if counted == 0:
        # every day excused: score what rest still asks for, over the excused days
        nr = len(excused)
        parts = {"fuel": red_fuel / nr, "weighins": min(weighins, need_w) / need_w, "ledger": red_ledger / nr}
        score = round(100 * sum(W[k] * parts[k] for k in parts) / sum(W[k] for k in parts))
    else:
        n = counted
        sessions = (sess_done / total_planned) if total_planned else 1.0
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
    """The rolling 7-day fuel score as of `day`. A day still being eaten is not a day's fuel yet: `day` itself counts
    only once it is closed; until then the window is the seven days before it. So Ember does not dip at breakfast
    and climb back at dinner, and the glimpses and dice read a settled number."""
    vals = []
    today = facts.get(day.isoformat())
    first = 0 if (today is not None and today["closed"]) else 1
    for i in range(first, first + 7):
        f = facts.get((day - dt.timedelta(i)).isoformat())
        if f:
            fu = day_fuel(f, cfg, rules)
            if fu is not None:
                vals.append(fu)
    if not vals:
        return None
    return max(10, round(100 * sum(vals) / len(vals)))


def tether_at(asof, facts, rules):
    """The Tether: days logged as time together on purpose (daily_log.csv -> together=Y), staged like an Art's
    ranks by rules.json -> tether.stages. It only ever climbs. Nothing else about those days is read."""
    t = rules.get("tether")
    if not t:
        return None
    days = sorted(x for x, f in facts.items() if f.get("together") and d(x) <= asof)
    n = len(days)
    stages = t["stages"]
    stage = sum(1 for k in stages if n >= k)
    names = t.get("names") or []
    return {"days": n, "stage": stage, "of": len(stages),
            "name": names[stage - 1] if stage and stage <= len(names) else None,
            "next_at": next((k for k in stages if n < k), None),
            "first": days[0] if days else None, "last": days[-1] if days else None,
            "with": t.get("with")}


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
    tier_notes = []
    frozen = {r["week_start"]: r for r in read_csv("chapters") if r.get("week_start")}  # chapter-close freezes a week's tier
    if dates:
        ws = week_start(dates[0])
        while ws + dt.timedelta(6) < asof:
            sc = week_score(ws, ws + dt.timedelta(6), facts, cfg, rules)
            fr = frozen.get(ws.isoformat())
            tier = fr["tier"] if fr else sc["tier"]
            sc["frozen_tier"] = fr["tier"] if fr else None
            if fr and fr["tier"] != sc["tier"]:
                tier_notes.append(f"chapter {fr['chapter']} stays {fr['tier']} (frozen by chapter-close); the logs now score {sc['tier']} ({sc['score']})")
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
            bonus = Wk["tier_bonus"].get(tier, 0)
            if bonus and ws >= d(cfg["chronicle_start"]):
                wadd(f"Chapter tier: {tier}", bonus,
                     note=(f"frozen by chapter-close (score {fr['score']})" if fr else f"week score {sc['score']}"))
            if tier == "Triumph" and ws >= d(cfg["chronicle_start"]):
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

    # inspiration: chronological earn/spend, capped. A level gained from inspiration.per_level_from on brings
    # per_level Inspiration, dated the day the XP crossed it.
    per_level = rules["inspiration"].get("per_level", 0)
    if per_level:
        lv_from = rules["inspiration"].get("per_level_from", 2)
        by_date = defaultdict(int)
        for x in deeds:
            by_date[x["date"]] += int(x["xp"])
        run, lv = 0, 1
        for date in sorted(by_date):
            run += by_date[date]
            reached = level_of(run)
            for L in range(lv + 1, reached + 1):
                if L >= lv_from:
                    insp_events.append((date, +per_level, f"level {L}"))
            lv = max(lv, reached)
    works = works_at(asof)
    per_work = (rules.get("works") or {}).get("inspiration_per_finished", 0)
    if per_work:
        for when in works["finished_dates"]:
            insp_events.append((when, +per_work, "a work finished"))
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

    tether = tether_at(asof, facts, rules)
    try:  # the Tether only climbs: a stage the saved sheet already reached is held, in every view
        saved = (load_json(P["sheet"]).get("tether") or {}) if P["sheet"].exists() else {}
    except (OSError, ValueError):
        saved = {}
    if tether and saved.get("stage", 0) > tether["stage"]:
        t_ = rules.get("tether") or {}
        stage = saved["stage"]
        names_, stages_ = t_.get("names") or [], t_.get("stages") or []
        tether = {**tether, "stage": stage, "name": names_[stage - 1] if stage <= len(names_) else saved.get("name"),
                  "next_at": stages_[stage] if stage < len(stages_) else None, "held": True}

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
        "tether": tether,
        "works": {"finished": works["finished"], "tasks_done": works["tasks_done"], "late": works["late"]},
        "chapter_now": {"week_start": cur["week_start"], "through": cur["through"],
                        "tier_so_far": cur["tier"], "chapter": chapter_no(cfg, d(cur["week_start"]))},
        "fell": {a: rules["attributes"][a]["fell"] for a in ATTRS},
    }
    return {"facts": facts, "deeds": deeds, "sheet": sheet, "weeks": weeks, "current_week": cur, "asof": asof,
            "tier_notes": tier_notes}


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
    for n in st.get("tier_notes", []):
        print("  note: " + n)
    if old:
        notes = diff_sheets(old, s)
        if notes:
            print("RECKONING CHANGES:")
            for n in notes:
                print("  " + n)
            line = reckoning_line(old, s)
            if line:
                print("RECKONING LINE (paste it as the reply's bracketed line, nothing explained):")
                print("  " + line)


def diff_sheets(old, new):
    notes = []
    if new["xp"] != old.get("xp"):
        notes.append(f"XP {old.get('xp', 0):,} -> {new['xp']:,} ({new['xp'] - old.get('xp', 0):+,})")
    if new["level"] > old.get("level", 0):
        bits = [f"LEVEL UP: {old.get('level')} -> {new['level']} ({new['rank']})"]
        if old.get("hp_max") is not None and new.get("hp_max") != old.get("hp_max"):
            bits.append(f"HP {old['hp_max']} -> {new['hp_max']}")
        if old.get("proficiency") is not None and new.get("proficiency") != old.get("proficiency"):
            bits.append(f"Proficiency +{old['proficiency']} -> +{new['proficiency']}")
        notes.append(" · ".join(bits))
        if old.get("rank") and new.get("rank") != old.get("rank"):
            notes.append(f"RANK: {old['rank']} -> {new['rank']} (a rank crossing: one prose beat in the next scene, style.md §3; `saga.py now` shows it owed)")
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
            was = prev.get("rank", 0)
            notes.append(f"ART LEARNED: {a['name']} {roman(a['rank'])}" if was == 0
                         else f"ART RANKED UP: {a['name']} {roman(was)} -> {roman(a['rank'])}")
    if new["inspiration"] > old.get("inspiration", 0):
        notes.append(f"INSPIRATION +{new['inspiration'] - old.get('inspiration', 0)} (now {new['inspiration']})")
    if new["knots_count"] > old.get("knots_count", 0):
        notes.append(f"KNOT TIED: {new['knots_count']} of VII")
    oe = (old.get("ember") or {}).get("tier")
    if oe and new["ember"]["tier"] != oe:
        notes.append(f"EMBER {oe} -> {new['ember']['tier']}")
    ot, nt = (old.get("tether") or {}).get("stage", 0), (new.get("tether") or {}).get("stage", 0)
    names = (load_json(P["rules"]).get("tether") or {}).get("names") or []
    of = (new.get("tether") or {}).get("of", 5)
    for k in range(ot + 1, nt + 1):  # every stage crossed gets its own line: each one is a scene, and stage I explains them
        nm = names[k - 1] if k <= len(names) else ""
        notes.append(f"TETHER {'TIED' if k == 1 else 'DRAWN'}: {roman(k)} of {roman(of)} · {nm}"
                     + (" (its scene waits for the next free quest slot)" if nt - ot > 1 else ""))
    ow, nw = old.get("works") or {}, new.get("works") or {}
    if nw.get("tasks_done", 0) > ow.get("tasks_done", 0):
        notes.append(f"WORK: a task done ({nw['tasks_done']} in all); its tale owes a piece (`saga.py now`, then `saga.py brief --tale`)")
    if nw.get("finished", 0) > ow.get("finished", 0):
        late = nw.get("late", 0) > ow.get("late", 0)
        notes.append(f"WORK FINISHED: {nw['finished']} in all; the tale's last piece brings " + ("the lesser keepsake (finished after its week)" if late else "its keepsake"))
    return notes


def roman(n):
    return ["-", "I", "II", "III", "IV", "V", "VI", "VII"][n] if 0 <= n <= 7 else str(n)


def reckoning_line(old, new):
    """The bracketed Reckoning line a reply carries when the sheet moved: the XP gained with the bar to the next
    level, then everything that changed as before -> after (attributes, Arts, Ember, Inspiration, Knots, the Tether,
    the works). The level itself is not here: a level-up has its own block in the reply (the /log reply shape).
    Empty when nothing moved. Only the engine builds it, so no number in a reply is ever worked out by hand."""
    bits = []
    dx = new["xp"] - old.get("xp", 0)
    if dx:
        bar = progress_bar(new["xp"] - new["xp_this_level"], new["xp_next_level"] - new["xp_this_level"])
        bits.append(f"{dx:+,} XP · {new['xp']:,} {bar} {new['xp_next_level']:,}")
    for a in ATTRS:
        o = old.get("attributes", {}).get(a, {}).get("score")
        n = new["attributes"][a]["score"]
        if o is not None and n != o:
            bits.append(f"{a.capitalize()} {o} → {n}")
    oa = {a["id"]: a for a in old.get("arts", [])}
    for a in new["arts"]:
        was = oa.get(a["id"], {}).get("rank", 0)
        if a["rank"] > was:
            bits.append(f"{a['name']} {roman(was) if was else 'new'} → {roman(a['rank'])}")
    oe = (old.get("ember") or {}).get("tier")
    if oe and new["ember"]["tier"] != oe:
        bits.append(f"Ember {oe} → {new['ember']['tier']}")
    if new["inspiration"] > old.get("inspiration", 0):
        bits.append(f"Inspiration {old.get('inspiration', 0)} → {new['inspiration']}")
    if new["knots_count"] > old.get("knots_count", 0):
        bits.append(f"Knots {roman(old.get('knots_count', 0))} → {roman(new['knots_count'])} of VII")
    ot, nt = (old.get("tether") or {}).get("stage", 0), (new.get("tether") or {}).get("stage", 0)
    if nt > ot:
        t = new.get("tether") or {}
        bits.append(f"The Tether: {t.get('name', '')}".rstrip(": ") + f" ({roman(nt)} of {roman(t.get('of', 5))})")
    ow, nw = old.get("works") or {}, new.get("works") or {}
    if nw.get("finished", 0) > ow.get("finished", 0):
        bits.append(f"Works {ow.get('finished', 0)} → {nw['finished']}")
    return "⟦ " + " · ".join(bits) + " ⟧" if bits else ""


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
    lines = ["| Day | Plan | kcal | P (g) | Wt | Cr | Floor | Check | Knee | PT | Add-on | Cond | Sport | Together |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    kc, pr = [], []
    for i in range(7):
        day = ws + dt.timedelta(i)
        f = facts.get(day.isoformat())
        plan = ", ".join(planned_for(cfg, day)) or "floor"
        label = f"{dow(day)} {md(day)}"
        if not f:
            lines.append(f"| {label} | {plan} |" + " |" * 12)
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
            f"{int(f['cond_min'])}m" if f["cond_min"] else "", str(f["sport"] or ""), "✔" if f["together"] else ""]) + " |")
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
    tpl = template_for(cfg, day)
    opt_from = tpl.get("optional_from") or cfg["weekly_template"].get("optional_from") or {}
    optional = [o + (f" (from {opt_from[o]})" if opt_from.get(o, "") > day.isoformat() else "")
                for o in tpl.get("optional", [])]
    print(f"Planned today (template): {', '.join(planned_for(cfg, day)) or 'rest / floor minimum only'}"
          f" · optional this week: {', '.join(optional)}")
    items = [r for r in read_csv("food") if r.get("date") == day.isoformat()]
    if f and f["kcal"] is not None:
        k, p = f["kcal"], f["protein"] or 0
        print(f"Nutrition: {fmt(k)} / {fmt(t['kcal'])} kcal ({fmt(max(0, t['kcal'] - k))} to go) · "
              f"{fmt(p)} / {t['protein_g']} g protein ({fmt(max(0, t['protein_g'] - p))} to go) · {len(items)} items")
    else:
        print(f"Nutrition: nothing logged yet · targets {fmt(t['kcal'])} kcal / {t['protein_g']}-{t['protein_g_max']} g protein")
    if f:
        done = []
        if f["light"] == "red":
            done.append("red light")
        if f["check"]:
            done.append("morning check")
        if f["floor"]:
            done.append(f"floor ({f['floor']})")
        if f["knee"]:
            done.append(f"knee session {f['knee']}")
        elif f["knee_partial"]:
            done.append("knee session partial")
        if f["pt"]:
            done.append("PT")
        elif f["pt_missed"]:
            done.append("PT missed")
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
        if f["together"]:
            done.append("together")
        if f["closed"]:
            done.append("day closed")
        print("Logged: " + (", ".join(done) if done else "nothing yet"))
        need = floor_rounds(cfg, day.isoformat())
        missing = [x for x, ok in [("morning check (grade swelling)", f["check"]),
                                   ("daily minimum (weighted heel prop" + (f" x{need})" if need > 1 else ")"), f["floor"] == "full" or need == 0)]
                   if not ok]
        missing += unlogged_sessions(cfg, day, f) + ([] if f["creatine"] else ["creatine"])
        if missing:
            print(("Not logged" if f["closed"] else "Still open") + ": " + ", ".join(missing))
    else:
        print("Logged: nothing yet. Still open: " + ", ".join(
            ["morning check"] + (["daily minimum (weighted heel prop)"] if floor_rounds(cfg, day.isoformat()) else []) + unlogged_sessions(cfg, day, None) + ["creatine"]))
    print(project_line())


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
    print("\n" + works_week_line(ws))


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
    t = s.get("tether")
    if t and t.get("stage"):  # shown only once it is tied; the stage names are the page's words, never the Ledger's
        lines.append(f"THE TETHER · {roman(t['stage'])} of {roman(t['of'])} · {t['name']}")
    w = s.get("works") or {}
    if w.get("finished"):  # the works: counts only; what they were stays in the Ledger
        lines.append(f"WORKS · {w['finished']} finished")
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
                  + "\n\n**Latest measured:** " + latest_measured_line(cfg)
                  + "\n\n" + "\n".join("**" + line.replace(": ", ":** ", 1) for line in project_lines()))
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
    past = [f"{dow(x)} knee ({fx(x).get('knee_unpaid')})" for x in days if fx(x).get("knee_unpaid")]
    past += [f"{dow(x)} {k}" for x in days for k in sorted(fx(x).get("addons_unpaid") or ())]
    if past:
        flags.append("work past the plan (logged, not paid): " + ", ".join(past))
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
        "sport": sum(1 for x in days if fx(x).get("sport")),
    }
    names = {"knee": "knee sessions", "pt": "PT", "upper": "upper", "cond": "conditioning", "accessory": "accessory",
             "power": "power", "sport": "sport sessions"}
    parts = []
    for k, label in names.items():
        if k in pl:
            parts.append(f"{label} {did[k]} of {pl[k]}" + (f" ({int(cond_min)} min)" if k == "cond" and cond_min else ""))
        elif did[k]:
            parts.append(f"{label} {did[k]}")
    out += ["", "**Sessions vs plan:** " + " · ".join(parts)]
    if sc.get("excused"):
        out.append("Excused (red light): " + ", ".join(sc["excused"]))
    tog = [dow(x) for x in days if fx(x).get("together")]
    out.append(f"**Together:** {len(tog)} day{'s' if len(tog) != 1 else ''}" + (" (" + ", ".join(tog) + ")" if tog else ""))

    # measurements
    ms = measures_in(cfg, ws, we)
    specs = metric_specs(cfg)
    out += ["", "**Measured this week:** " + ("; ".join(
        f"{mdate(g['date'])} {g['source']} {metric_label(g['metric'], specs.get(g['metric'], {}))} {set_text(g)}"
        for g in ms) or "nothing")]
    out += ["", "**Works:** " + works_week_line(ws)[len("Works: "):]]
    out += ["", "**Flags:** " + (" · ".join(flags) or "none")]
    return "\n".join(out)


CHECKPOINT_SKELETON = """# Checkpoint — Sun {sun} · week Sun {ws} – Sat {we}

*Post-op weeks {w1}–{w2} · Phase {phase}. The archive of this week: what happened and what was decided. The program in force: {state}.*

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

## Sport

<!-- Throwing sessions vs plan, the stage and any clearance, the week's question; every fourth week the month check (ratings, the seven review questions). -->

## PT and measurements

<!-- Each PT or surgeon entry this week in real/visits/pt_notes.md (doc ptnotes DATE) and any other real/visits/ file; what was measured; which questions were answered. -->

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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(CHECKPOINT_SKELETON.format(
            sun=sun.isoformat(), ws=md(ws), we=md(we), w1=post_op_week(cfg, ws), w2=post_op_week(cfg, we),
            phase=cfg["rehab"]["current_phase"], state=state_reference()), encoding="utf-8")
        print(f"created {path.relative_to(ROOT)} from the checkpoint template")
    replace_block(path, text, "")
    print(f"numbers written to {path.relative_to(ROOT)}\n")
    print(text)


def state_reference():
    """How a checkpoint names the program its week ran: the current Recovery State by the Sunday in its title, with the
    archive path it moves to when the next one replaces it (real/state/archive/recovery_state_<that Sunday>.md)."""
    if not P["state"].exists():
        return "`real/state/` (no Recovery State yet)"
    first = P["state"].read_text(encoding="utf-8").split("\n", 1)[0]
    m = re.search(r"\d{4}-\d{2}-\d{2}", first)
    if not m:
        return f"`{P['state'].relative_to(ROOT)}`"
    return (f"the Recovery State of Sun {m.group(0)} (`{P['state'].relative_to(ROOT)}`; once replaced, "
            f"`real/state/archive/recovery_state_{m.group(0)}.md`)")


# ---------------------------------------------------------------- documents, one section at a time
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def doc_path(name):
    fixed = {"state": P["state"], "addon": P["addon"], "rules": P["working_rules"], "guide": P["guide"], "master": P["master"],
             "now": P["real_now"], "offseason": P["offseason"], "index": P["index"], "ptnotes": P["ptnotes"],
             "sport": P["sport_plan"], "sportguide": P["sport_guide"]}
    if name in fixed:
        return fixed[name]
    globs = {"checkpoint": (P["checkpoints"], "20*.md")}  # the newest week's review
    if name in globs:
        found = newest(globs[name][0].glob(globs[name][1]))
        if not found:
            sys.exit(f"no {name} file yet")
        return found
    p = Path(name) if Path(name).is_absolute() else ROOT / name
    if not p.exists():
        sys.exit(f"no document '{name}'. Use state, rules, addon, master, offseason, sport, sportguide, guide, ptnotes, index, "
                 f"now, checkpoint, or a path")
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


def vocab_problems(cfg, key, row, where):
    """The row's scoring fields against config.json -> vocabulary (a misspelt code must never pay or cost silently)."""
    v = (cfg.get("vocabulary") or {}).get(key) or {}
    probs = []
    for col, allowed in v.items():
        if col.startswith("_") or not isinstance(allowed, list):
            continue
        raw = str(row.get(col) or "").strip()
        if not raw:
            continue
        tokens = [t for t in re.split(r"[+,/]+", raw) if t.strip()] if col == "addon_session" else [raw]
        for t in tokens:
            t = t.strip()
            ok = (t in allowed
                  or (col == "knee_session" and t.lower().startswith("partial"))
                  or (key == "sport" and col == "session" and t.upper() in {a.upper() for a in allowed}))
            if not ok:
                probs.append(f"{where}: {col} '{t}' is not one of {', '.join(allowed)} (config.json -> vocabulary.{key}.{col}; add it there if it is a new code)")
    return probs


def upsert_row(key, date, kv, cfg):
    """Upsert one day's row in nutrition_log or daily_log. kv maps a column to ("set"|"append", value). Returns the row."""
    rows = read_csv(key)
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
    for k, (op, v) in kv.items():
        if k not in allowed:
            sys.exit(f"unknown column '{k}' for {key}. Allowed: {', '.join(COLS[key])}")
        if op == "append" and row.get(k):
            row[k] = row[k].rstrip() + " " + v
        else:
            row[k] = v
    probs = vocab_problems(cfg, key, row, f"{key} {date}")
    if probs:
        sys.exit("refused, nothing written:\n  " + "\n  ".join(probs))
    rows.sort(key=lambda r: r.get("date", ""))
    write_csv(key, rows)
    return row


def cmd_set(args, cfg, rules):
    key = {"nutrition": "nutrition", "daily": "daily"}[args.log]
    date = d(args.date).isoformat()
    row = upsert_row(key, date, parse_kv(args.fields), cfg)
    print(f"{key} {date}: " + ", ".join(f"{k}={row.get(k)}" for k in COLS[key] if row.get(k) not in (None, "") and k != "notes"))


def day_has_logs(date):
    """The Ledger's open-day test: a daily_log row, a nutrition_log row with data, or a food_entries row for the date."""
    if any(r.get("date") == date for r in read_csv("daily")):
        return True
    data = NUTRIENTS + ["weight_lb", "creatine", "shake", "notes"]
    if any(r.get("date") == date and any(str(r.get(k) or "").strip() for k in data) for r in read_csv("nutrition")):
        return True
    return any(r.get("date") == date for r in read_csv("food"))


def cmd_close(args, cfg, rules):
    """The first half of the day-close procedure in one command (the /log skill, "Close day"): closed=Y -> sync ->
    saga.py now -> saga.py plan next --date D --full. It refuses a day that has not happened, a missed day (nothing
    logged: no row, no scene), a day already closed (it has its scene), and a day in a new week while an earlier
    week's chapter is still unclosed (the checkpoint comes first)."""
    day = d(args.date)
    date = day.isoformat()
    today = today_local(cfg)
    if day > today:
        sys.exit(f"{date} has not happened yet (today is {today})")
    if not day_has_logs(date):
        sys.exit(f"{date} has nothing logged: a missed day gets no row and no scene. Record it with "
                 f"`python3 engine/saga.py plan done N --skipped` (N: its slot) and carry its world move into the next scene.")
    row = daily_rows().get(date)
    if row and yes(row.get("closed")):
        sys.exit(f"{date} is already closed: it has its scene. A late log for it updates the Ledger only; no second scene.")
    closed = {r["chapter"] for r in read_csv("chapters")}
    w, ws = week_start(d(cfg["chronicle_start"])), week_start(day)
    unclosed = []
    while w < ws:
        if str(chapter_no(cfg, w)) not in closed:
            unclosed.append(w)
        w += dt.timedelta(7)
    if unclosed and not args.force:
        sys.exit(f"the week of Sun {unclosed[0]} is not closed as a chapter yet: run /checkpoint first "
                 f"(its first engine step is `python3 engine/darrow.py chapter-close --date {unclosed[0] + dt.timedelta(6)}`), "
                 f"then close {date}. --force closes the day anyway.")
    saga = ROOT / "engine/saga.py"
    pre = subprocess.run([sys.executable, str(saga), "plan", "next", "--date", date], cwd=ROOT, capture_output=True, text=True)
    if pre.returncode and not args.force:  # never a closed day without a slot to write its scene into
        sys.exit(f"not closed: the story has no slot for {date} yet ({(pre.stderr or pre.stdout).strip()}). "
                 f"Open its chapter first (a new week: /checkpoint and `saga.py plan chapter open`), then close {date}.")
    upsert_row("daily", date, {"closed": ("set", "Y")}, cfg)
    print(f"daily {date}: closed=Y")
    cmd_sync(argparse.Namespace(date=None), cfg, rules)
    print(f"\n$ python3 engine/saga.py brief --date {date}")
    r = subprocess.run([sys.executable, str(saga), "brief", "--date", date], cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode:
        sys.stdout.write(r.stderr)
        sys.exit(f"saga.py brief failed: the day is closed and synced, but its slot is not known; "
                 f"fix the plan (a new week needs /checkpoint and `plan chapter open` first), then `saga.py brief --date {date}`")
    print("\nnext: write the scene to the brief (style.md: the wall, the craft, the reread), then `saga.py record '<the skeleton, filled>'`, then `darrow.py ship -m \"close DATE: …\"`")


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
            first_itemised = cfg.get("food_itemised_from")
            if first_itemised and date < first_itemised:
                sys.exit(f"{date} is before itemised food logging began ({first_itemised}): its day total in "
                         f"nutrition_log.csv came from the dashboard and stands as it is. To add a forgotten item, add its "
                         f"numbers to that total with `set nutrition {date} kcal=… protein_g=…`; an item row would replace it.")
            seq = 1 + max([int(r["id"].split("#")[1]) for r in rows
                           if r.get("date") == date and "#" in r.get("id", "")] or [0])
            row = {"id": f"{date}#{seq}", **{k: item.get(k, "") for k in COLS["food"] if k != "id"}}
            row["date"] = date
            rows.append(row)
            added.append(row)
        write_csv("food", rows)
        for r in added:
            shown = lambda v: "?" if v in (None, "") else v  # a zero is a value, not a blank
            print(f"+ {r['id']} {r['item']}: {shown(r.get('kcal'))} kcal, {shown(r.get('protein_g'))} g P")
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
        date = args.payload.split("#")[0]
        if not any(r.get("date") == date for r in keep) and date >= (cfg.get("food_itemised_from") or "0"):
            # the day's totals were rolled up from its items: with none left, clear them, or the old sum stays behind
            nut = read_csv("nutrition")
            for r in nut:
                if r.get("date") == date:
                    for k in NUTRIENTS:
                        r[k] = ""
            write_csv("nutrition", nut)
            print(f"{date}: no food entries left; its rolled-up totals cleared (weight, creatine and notes kept)")
    elif args.action == "lib":
        q = args.payload.lower()
        for r in read_csv("foods"):
            hay = (r.get("name", "") + " " + r.get("aliases", "")).lower()
            if all(w in hay for w in q.split()):
                print(json.dumps({k: v for k, v in r.items() if v not in ("", None)}))


def cmd_append(key, args, cfg):
    rows = read_csv(key)
    probs = []
    for i, item in enumerate(as_list(args.payload), 1):
        day = d(item["date"])
        unknown = [k for k in item if k not in COLS[key]]
        if unknown:
            probs.append(f"{key} row {i}: unknown column(s) {', '.join(unknown)}; columns: {', '.join(COLS[key])}")
        row = {k: item.get(k, "") for k in COLS[key]}
        row["date"] = day.isoformat()
        if key == "exercise":
            row["dash_week_start"] = row["dash_week_start"] or week_start(day).isoformat()
            row["pod"] = row["pod"] or str(pod(cfg, day))
        probs += vocab_problems(cfg, key, row, f"{key} row {i} ({row['date']})")
        rows.append(row)
    if probs:
        sys.exit("refused, nothing written:\n  " + "\n  ".join(probs))
    rows.sort(key=lambda r: r.get("date", ""))
    write_csv(key, rows)
    print(f"{key}: appended {len(as_list(args.payload))} row(s)")


# ---------------------------------------------------------------- dice
def check_result(nat, total, dc):
    """The one rule `roll` and `odds` share: a natural 20 is a critical success and a natural 1 a critical failure
    whatever the total; otherwise success at the DC, a partial (success at a cost) within 3 under it, failure below."""
    if nat == 20:
        return "CRITICAL SUCCESS"
    if nat == 1:
        return "CRITICAL FAILURE"
    if total >= dc:
        return "SUCCESS"
    if total >= dc - 3:
        return "PARTIAL (success at a cost)"
    return "FAILURE"


def roll_mods(args, st, cfg, rules):
    """The modifiers a check carries, in the dice line's order: the stat, proficiency, each Art's rank, the chapter's
    frozen tier (--chapter N) or the live one (--tier), the Ember's effect (a climax reads the Ember its week ended on,
    whatever today's logs say), a bonus. `roll` and `odds` share it, so the odds printed before a climax are the odds
    of the die then cast."""
    s = st["sheet"]
    mods = []
    if args.stat:
        mods.append((args.stat, s["attributes"][args.stat]["mod"]))
    if args.prof:
        mods.append(("proficiency", s["proficiency"]))
    for art_id in (args.art or []):  # an Art's rank rides the check: --art wardens_eye (Insight), --art menders_patience
        art = next((a for a in s["arts"] if a["id"] == art_id), None)
        if not art:
            sys.exit(f"unknown Art '{art_id}'; ids: " + ", ".join(a["id"] for a in s["arts"]))
        if art["rank"] < 1:
            sys.exit(f"{art['name']} is not learned yet"
                     + (f" (sealed until Knot {roman(art['sealed_until_knot'])})" if art.get("sealed_until_knot") else "")
                     + "; roll without --art")
        mods.append((f"{art['name']} {roman(art['rank'])}", art["rank"]))
    ch = None
    if args.chapter:
        ch = next((r for r in read_csv("chapters") if r["chapter"] == str(args.chapter)), None)
        if not ch:
            sys.exit(f"chapter {args.chapter} is not closed yet; run chapter-close first")
        mods.append((f"chapter {args.chapter} {ch['tier']}", int(ch["roll_mod"])))
    elif args.tier:
        cur = st["current_week"]
        mods.append((f"chapter so far {cur['tier']}", cur["roll_mod"]))
    et = s["ember"]["tier"]
    if ch:
        we = d(ch["week_end"]) if ch.get("week_end") else d(ch["week_start"]) + dt.timedelta(6)
        ev = ember_at(we, st["facts"], cfg, rules)
        et = tier_of(ev, rules["ember"]["tiers"])["name"] if ev is not None else None
    if et == "Blazing":
        mods.append(("Ember Blazing", 1))
    elif et == "Bright" and args.stat == "vigor":
        mods.append(("Ember Bright", 1))
    elif et == "Guttering" and args.stat in ("might", "vigor"):
        mods.append(("Ember Guttering", -1))
    if args.bonus:
        mods.append(("bonus", args.bonus))
    return mods


def check_odds(total_mod, dc, mode=""):
    """Exact odds of a full success, a partial and an outright failure for d20 + total_mod against dc, by
    `check_result`'s rule, over every natural (every pair of naturals with advantage or disadvantage)."""
    nats = [max(a, b) if mode == "adv" else min(a, b) for a in range(1, 21) for b in range(1, 21)] if mode else list(range(1, 21))
    out = {"success": 0, "partial": 0, "failure": 0}
    for nat in nats:
        r = check_result(nat, nat + total_mod, dc)
        out["success" if r in ("SUCCESS", "CRITICAL SUCCESS") else "partial" if r.startswith("PARTIAL") else "failure"] += 1
    return {k: v / len(nats) for k, v in out.items()}


def cmd_odds(args, cfg, rules):
    """What a DC means for him now, or at a chapter's climax (--chapter N): the chance of a full success, a partial and
    an outright failure, with the modifiers `roll` would carry. --target P names the DC whose chance of a full success
    lands nearest P (ties go to the harder DC). The brief prints this before a climax, so the week's tier sets the DC."""
    st = compute(cfg, rules)
    mods = roll_mods(args, st, cfg, rules)
    total = sum(m for _, m in mods)
    mod_txt = " ".join(f"{m:+d} {n}" for n, m in mods) or "+0"
    mode = "adv" if args.adv else "dis" if args.dis else ""
    rows = {dc: check_odds(total, dc, mode) for dc in ([args.dc] if args.dc else range(8, 21))}
    target_dc = None
    if args.target is not None:
        if not 0 < args.target < 1:
            sys.exit("--target is a probability between 0 and 1, e.g. 0.8")
        cands = {dc: check_odds(total, dc, mode) for dc in range(5, 31)}
        target_dc = min(cands, key=lambda dc: (abs(cands[dc]["success"] - args.target), -dc))
        rows.setdefault(target_dc, cands[target_dc])
    if args.json:
        print(json.dumps({"stat": args.stat or "flat", "mods": total, "mods_text": mod_txt, "mode": mode,
                          "rows": {str(dc): {k: round(v, 4) for k, v in r.items()} for dc, r in sorted(rows.items())},
                          "target": args.target, "target_dc": target_dc}))
        return
    print(f"[{(args.stat or 'flat').upper()}] {mod_txt} = {total:+d}" + (f" ({mode})" if mode else "") + " · partial = within 3 of the DC (success at a cost)")
    for dc in sorted(rows):
        r = rows[dc]
        print(f"  DC {dc:>2}: success {r['success']:4.0%} · partial {r['partial']:4.0%} · fail {r['failure']:4.0%}" + ("  ← use this" if dc == target_dc else ""))
    if target_dc is not None:
        print(f"use DC {target_dc} for a {args.target:.0%} chance of a full success")


def spend_inspiration(st, reason):
    sp = read_csv("spends")
    sp.append({"date": st["asof"].isoformat(), "what": "inspiration", "reason": reason})
    write_csv("spends", sp)


def cast(args, mods, label, note):
    """Cast one d20 under `label` with these modifiers, record it in rolls.csv and print its dice line (line 1 is the
    chapter's, in the style guide's exact form; paste it as it is). Returns the result."""
    rows = read_csv("rolls")
    a = secrets.randbelow(20) + 1
    b = secrets.randbelow(20) + 1 if (args.adv or args.dis) else None
    mode = "adv" if args.adv else "dis" if args.dis else ""
    nat = max(a, b) if args.adv else min(a, b) if args.dis else a
    total = nat + sum(m for _, m in mods)
    result = check_result(nat, total, args.dc)
    mod_txt = " ".join(f"{m:+d} {n}" for n, m in mods)
    rows.append({"when": dt.datetime.now().isoformat(timespec="seconds"), "label": label, "stat": args.stat or "",
                 "dc": args.dc, "d20": a, "d20_b": b or "", "mode": mode, "mods": mod_txt, "total": total,
                 "result": result, "note": note or ""})
    write_csv("rolls", rows)
    shown = f"{a}/{b} ({mode})" if b else f"{a}"
    pretty = {"CRITICAL SUCCESS": "Critical success", "CRITICAL FAILURE": "Critical failure", "SUCCESS": "Success",
              "PARTIAL (success at a cost)": "Partial: success at a cost", "FAILURE": "Failure"}[result]
    print(f"`[{(args.stat or 'flat').upper()} · DC {args.dc}]` d20 **{shown}** {mod_txt} = **{total}** — *{pretty}*")
    print(f"(roll {label}: {result}; recorded in saga/state/rolls.csv)")
    return result


def cmd_roll(args, cfg, rules):
    rows = read_csv("rolls")
    label = args.label + ("#reroll" if args.reroll else "")
    prior = next((r for r in rows if r["label"] == label), None)
    if prior:
        print(f"ALREADY ROLLED (no takebacks): {prior['label']} → d20 {prior['d20']}"
              f"{'/' + prior['d20_b'] if prior['d20_b'] else ''} {prior['mods']} = {prior['total']} vs DC {prior['dc']} → {prior['result']}")
        return
    if args.paid and not args.reroll:
        sys.exit("--paid goes with --reroll: the choice that offered the reroll spent the Inspiration")
    st = compute(cfg, rules)
    s = st["sheet"]
    note = args.note or ""
    insp = int(s["inspiration"])
    if args.reroll:
        if not any(r["label"] == args.label for r in rows):
            sys.exit("nothing to reroll under that label")
        if args.paid:  # an *[Inspiration]* option in the choice: saga.py choose spent it already
            note = (note + "; " if note else "") + "paid by the choice"
            print("`[INSPIRATION]` spent at the choice · cast again")
        else:
            if insp < 1:
                sys.exit("no Inspiration to spend")
            spend_inspiration(st, f"reroll {args.label}")
            print(f"`[INSPIRATION]` {insp} → {insp - 1} · cast again")
            insp -= 1
    mods = roll_mods(args, st, cfg, rules)
    result = cast(args, mods, label, note)
    # a climax check that fails outright is cast again on his Inspiration, and again, until it succeeds or he has none left
    # (rules.json -> inspiration.auto_reroll_on_fail); the dice lines and the Inspiration lines between them go on the page
    # together, in order, as one block, and the Reckoning box shows the spend
    if args.chapter and not args.reroll and rules["inspiration"].get("auto_reroll_on_fail"):
        lab = label
        while (result in ("FAILURE", "CRITICAL FAILURE") and insp >= 1
               and not any(r["label"] == lab + "#reroll" for r in read_csv("rolls"))):
            spend_inspiration(st, f"cast again on a failed climax check: {args.label}")
            print(f"`[INSPIRATION]` {insp} → {insp - 1} · cast again")
            insp -= 1
            lab += "#reroll"
            result = cast(args, mods, lab, "Inspiration spent on a failed climax check")
        if lab != label:
            print("(every dice and Inspiration line above goes on the page, in order, as one block; the Reckoning box shows the spend)")


def cmd_inspire(args, cfg, rules):
    st = compute(cfg, rules)
    if st["sheet"]["inspiration"] < 1:
        sys.exit("no Inspiration to spend")
    spend_inspiration(st, args.reason)
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
    week_empty = not any(day_has_logs((ws + dt.timedelta(i)).isoformat()) for i in range(7))
    if str(n) not in closed and not (args.partial_ok or args.force or week_empty):
        # the freeze is final: make sure the week's last day is in before it, so a Saturday dinner sent on Sunday
        # morning is never scored as not eaten (late logs move totals, never a frozen tier)
        last = week_end.isoformat()
        f = st["facts"].get(last)
        meals = {str(r.get("meal") or "").strip().lower() for r in read_csv("food") if r.get("date") == last}
        kcal = (f or {}).get("kcal") if f else None
        why = None
        if not day_has_logs(last):
            why = f"nothing is logged for {dow(week_end)} {last}"
        elif kcal is None:
            why = f"no food is logged for {dow(week_end)} {last}"
        elif kcal < 0.6 * cfg["nutrition_targets"]["kcal"] and "dinner" not in meals:
            why = f"{dow(week_end)} {last} shows {int(kcal):,} kcal and no dinner"
        if why:
            sys.exit(f"not frozen: {why}. If anything from that day is still to come, log it first (the Sunday "
                     f"message's own Saturday items go in before this step). If that really is all, rerun with --partial-ok.")
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
    try:
        when = d(args.date)
    except ValueError:
        sys.exit(f"--date {args.date}: not a date (YYYY-MM-DD)")
    if when > today_local(cfg):
        sys.exit(f"--date {when} has not happened yet: a Knot ties on the day its evidence exists, never ahead of it")
    knots.append({"knot": args.n, "name": names[args.n], "date": d(args.date).isoformat(), "evidence": args.evidence})
    save_json(P["config"], cfg)
    print(f"Knot {roman(args.n)} ({names[args.n]}) tied {args.date}. Run sync; `saga.py now` shows the Book's transition as due.")


# ---------------------------------------------------------------- projects: the works (real/projects.json)
PROJECT_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PROJECT_STATUS = ("live", "done", "dropped")
PROJECTS_ABOUT = ("The works: one real goal at a time outside the knee, in 2-5 tasks (clean it, park it, list it). "
                  "`darrow.py project open|done|show|drop`; `today` names the next task. Each task reported pays one piece of the tale "
                  "bound to the project (`saga.py tale bind`, then `saga.py brief --tale`), the last piece its keepsake; a finished project "
                  "counts in the sheet's WORKS and brings one Inspiration. A project is due the Saturday of the week it opens (`due`); "
                  "finished after that day it is `late`, and its tale ends on the lesser keepsake instead of the full one. Titles and tasks "
                  "are real-world words: they never reach the Chronicle or the site, only the counts do. Dates are the days the tasks were reported.")


def load_projects():
    if not P["projects"].exists():
        return {"_about": PROJECTS_ABOUT, "projects": []}
    return load_json(P["projects"])


def save_projects(data):
    out = {"_about": data.get("_about") or PROJECTS_ABOUT}
    out.update({k: v for k, v in data.items() if k != "_about"})
    save_json(P["projects"], out)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s[:40].rstrip("-") or "project"


def live_projects(data):
    """Every live project, in the order they opened. Several may run side by side (his call, 10/29); each binds its own tale."""
    return [p for p in data.get("projects", []) if p.get("status") == "live"]


def pick_project(data, pid=None):
    """The live project a done/drop acts on: the one named by --id, or the only live one. None when several are live and
    none is named (the caller decides: done matches the task's words across them; drop asks for --id)."""
    live = live_projects(data)
    if pid:
        p = next((q for q in live if q.get("id") == pid), None)
        if not p:
            sys.exit(f"no live project {pid!r}; live: " + (", ".join(q["id"] for q in live) or "none"))
        return p
    if not live:
        sys.exit("no project is open (`project open` first)")
    return live[0] if len(live) == 1 else None


def works_at(asof, data=None):
    """The counts the sheet shows as of a date: projects finished, tasks done, and the finish dates (one Inspiration each)."""
    data = data or load_projects()
    asof_s = asof.isoformat() if hasattr(asof, "isoformat") else str(asof)
    done = [p for p in data.get("projects", []) if p.get("status") == "done" and p.get("done") and p["done"] <= asof_s]
    finished = sorted(p["done"] for p in done)
    tasks = sum(1 for p in data.get("projects", []) for t in p.get("tasks", []) if t.get("done") and t["done"] <= asof_s)
    return {"finished": len(finished), "tasks_done": tasks, "finished_dates": finished, "late": sum(1 for p in done if p.get("late"))}


def project_lines(data=None):
    """One line per live project for today's view and the Ledger's NOW: how far it is, its next task, its due day."""
    live = live_projects(data or load_projects())
    if not live:
        return ["Project: none open (`darrow.py project open \"Title\" --tasks …` starts the week's)"]
    return [_project_line(p) for p in live]


def project_line(data=None):
    """The live projects, one line each (joined with newlines when several run side by side)."""
    return "\n".join(project_lines(data))


def _project_line(p):
    done = sum(1 for t in p["tasks"] if t.get("done"))
    nxt = next((t for t in p["tasks"] if not t.get("done")), None)
    due = f" · due {dow(d(p['due']))} {md(d(p['due']))}" if p.get("due") else ""
    resumes = (p.get("deferred") or {}).get("resumes")
    if resumes and today_local(load_json(P["config"])).isoformat() < resumes:
        # set aside by his own call until a later week: named, never pressed as today's next task
        return f"Project: {p['title']} · {done}/{len(p['tasks'])} done · resting until the week of {md(d(resumes))}" + due
    return f"Project: {p['title']} · {done}/{len(p['tasks'])} done" + (f" · next: {nxt['n']}. {nxt['text']}" if nxt else "") + due


def works_week_line(ws):
    """The week's works, for `week`: tasks done and projects finished in it, and the live project."""
    data = load_projects()
    we = ws + dt.timedelta(6)
    inw = lambda x: x and ws.isoformat() <= x <= we.isoformat()
    tasks = [(p, t) for p in data.get("projects", []) for t in p.get("tasks", []) if inw(t.get("done"))]
    fin = [p for p in data.get("projects", []) if p.get("status") == "done" and inw(p.get("done"))]
    bits = [f"{len(tasks)} task{'s' if len(tasks) != 1 else ''} done this week"]
    if fin:
        bits.append("finished: " + ", ".join(p["title"] for p in fin))
    return "Works: " + " · ".join(bits) + " · " + " · ".join(project_lines(data))


def project_problems(cfg):
    """Validation for `check`: ids, statuses, dates, task numbering, and a done project with every task done."""
    probs = []
    try:
        data = load_projects()
    except (OSError, ValueError) as e:
        return [f"projects.json: unreadable ({e})"]
    today = today_local(cfg).isoformat()
    seen = {}
    for i, p in enumerate(data.get("projects", [])):
        where = f"projects.json projects[{i}]"
        pid = str(p.get("id") or "")
        if not PROJECT_ID_RE.match(pid):
            probs.append(f"{where}: id {pid!r} must be lowercase words joined by hyphens")
        seen[pid] = seen.get(pid, 0) + 1
        if not str(p.get("title") or "").strip():
            probs.append(f"{where}: no title")
        if p.get("status") not in PROJECT_STATUS:
            probs.append(f"{where}: status {p.get('status')!r} is live, done or dropped")
        for k in ("opened", "due", "done", "dropped"):
            v = p.get(k)
            if k == "due" and v:
                try:
                    d(v)
                except ValueError:
                    probs.append(f"{where}: due {v!r} is not a date")
                continue
            if v:
                try:
                    if d(v).isoformat() > today:
                        probs.append(f"{where}: {k} {v} has not happened yet")
                except ValueError:
                    probs.append(f"{where}: {k} {v!r} is not a date")
        tasks = p.get("tasks") or []
        if not 2 <= len(tasks) <= 5:
            probs.append(f"{where}: {len(tasks)} tasks; a project has 2 to 5")
        for j, t in enumerate(tasks, 1):
            if t.get("n") != j:
                probs.append(f"{where}: task {j} is numbered {t.get('n')!r}")
            if not str(t.get("text") or "").strip():
                probs.append(f"{where}: task {j} has no text")
            if t.get("done"):
                try:
                    if d(t["done"]).isoformat() > today:
                        probs.append(f"{where}: task {j} done {t['done']} has not happened yet")
                except ValueError:
                    probs.append(f"{where}: task {j} done {t['done']!r} is not a date")
        if p.get("status") == "done":
            if not p.get("done"):
                probs.append(f"{where}: done without a date")
            if any(not t.get("done") for t in tasks):
                probs.append(f"{where}: finished with a task still open")
            if p.get("done") and p.get("due") and bool(p.get("late")) != (p["done"] > p["due"]):
                probs.append(f"{where}: late is {p.get('late')!r} but it finished {p['done']} against a due day of {p['due']}")
        if p.get("status") == "live" and tasks and all(t.get("done") for t in tasks):
            probs.append(f"{where}: every task is done but the project is still live")
    probs += [f"projects.json: id {k!r} appears {v} times" for k, v in seen.items() if v > 1]
    return probs


def cmd_project(args, cfg, rules):
    data = load_projects()
    today = today_local(cfg)
    when = today
    if getattr(args, "date", None):
        try:
            when = d(args.date)
        except ValueError:
            sys.exit(f"--date {args.date}: not a date (YYYY-MM-DD)")
        if when > today:
            sys.exit(f"--date {when} has not happened yet")
    live = live_projects(data)
    if args.action == "show":
        rows = data.get("projects", []) if args.all else live
        if not rows:
            print(project_line(data))
            return
        for q in rows:
            print(f"{q['id']} · {q['title']} · {q['status']} · opened {q.get('opened')}" + (f" · due {q['due']}" if q.get("due") else "")
                  + (f" · finished {q['done']}" + (" (late: the lesser keepsake)" if q.get("late") else " (in its week)") if q.get("done") else "")
                  + (f" · set aside {q['dropped']} ({q.get('why', '')})" if q.get("dropped") else ""))
            for t in q.get("tasks", []):
                print(f"  {'✓' if t.get('done') else '·'} {t['n']}. {t['text']}" + (f"  ({t['done']})" if t.get("done") else ""))
        w = works_at(today, data)
        print(f"works: {w['finished']} finished · {w['tasks_done']} tasks done in all")
        return
    if args.action == "open":
        title = str(args.what or "").strip()
        tasks = [str(t).strip() for t in (args.tasks or []) if str(t).strip()]
        if not title:
            sys.exit('project open needs a title: project open "Sell the cart" --tasks "Clean it" "Park it" "List it"')
        if not 2 <= len(tasks) <= 5:
            sys.exit(f"{len(tasks)} tasks: a project has 2 to 5, each one thing he can report done")
        pid = args.id or slugify(title)
        if not PROJECT_ID_RE.match(pid):
            sys.exit(f"--id {pid!r}: lowercase words joined by hyphens")
        if any(q.get("id") == pid for q in data.get("projects", [])):
            sys.exit(f"id {pid!r} is taken; pass --id")
        due = week_start(when) + dt.timedelta(6)  # the Saturday of the week it opens: the week he first planned it
        if args.due:
            try:
                due = d(args.due)
            except ValueError:
                sys.exit(f"--due {args.due}: not a date (YYYY-MM-DD)")
            if due < when:
                sys.exit(f"--due {due} is before the day it opens ({when})")
        data.setdefault("projects", []).append({"id": pid, "title": title, "status": "live", "opened": when.isoformat(), "due": due.isoformat(),
                                                "done": None, "late": False, "tasks": [{"n": i, "text": t, "done": None} for i, t in enumerate(tasks, 1)]})
        save_projects(data)
        print(f"project {pid} open: {title} · {len(tasks)} tasks · due {dow(due)} {due.isoformat()} (after that day, the lesser keepsake)\n"
              + "\n".join(f"  {i}. {t}" for i, t in enumerate(tasks, 1)))
        if live:
            print("alongside: " + ", ".join(f"{q['id']} ({q['title']})" for q in live)
                  + f" · with several live, `project done` matches a task's words across them; a task's number, or `drop`, takes --id")
        print(f"next: `python3 engine/saga.py tale bind {pid}` binds the tale its tasks will tell ({len(tasks)} pieces)")
        return
    if args.action == "drop":
        p = pick_project(data, args.id)
        if p is None:
            sys.exit("several projects are live; name the one to set aside with --id: " + ", ".join(f"{q['id']} ({q['title']})" for q in live))
        if not str(args.why or "").strip():
            sys.exit("project drop --why TEXT: a line on why it is set aside (no shame; the pieces told stay told)")
        p.update({"status": "dropped", "dropped": when.isoformat(), "why": args.why.strip()})
        save_projects(data)
        print(f"project {p['id']} set aside: {p['title']} ({sum(1 for t in p['tasks'] if t.get('done'))}/{len(p['tasks'])} tasks were done)")
        # its tale, if one is bound, rests (told in part): the story's projections carry that, so they are rebuilt now
        r = subprocess.run([sys.executable, str(ROOT / "engine/saga.py"), "project"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            print("note: `python3 engine/saga.py project` did not run cleanly; run it before shipping:\n" + (r.stdout + r.stderr).strip()[-400:])
        return
    # done
    p = pick_project(data, args.id)
    what = str(args.what or "").strip()
    if not what:
        sys.exit("project done TASK: its number, or a few of its words")
    t = None
    if what.isdigit():
        if p is None:
            sys.exit(f"several projects are live; a task number needs --id (or give a few of the task's words): "
                     + ", ".join(f"{q['id']} ({q['title']})" for q in live))
        t = next((x for x in p["tasks"] if x["n"] == int(what)), None)
        if t is None:
            sys.exit(f"no task {what}; the project has {len(p['tasks'])}")
    else:
        pool = [p] if p else live
        # open tasks first, so a word shared with a task already done never blocks the one he means
        hits = [(q, x) for q in pool for x in q["tasks"] if not x.get("done") and what.lower() in x["text"].lower()]
        if not hits:
            hits = [(q, x) for q in pool for x in q["tasks"] if what.lower() in x["text"].lower()]
        if len(hits) != 1:
            sys.exit(f"{len(hits)} tasks match {what!r}: " + "; ".join(f"{q['id']} {x['n']}. {x['text']}" for q in pool for x in q["tasks"]))
        p, t = hits[0]
    if t.get("done"):
        sys.exit(f"task {t['n']} ({t['text']}) was already reported done on {t['done']}")
    t["done"] = when.isoformat()
    done = sum(1 for x in p["tasks"] if x.get("done"))
    finished = done == len(p["tasks"])
    if finished:
        p["status"], p["done"] = "done", when.isoformat()
        p["late"] = bool(p.get("due")) and when.isoformat() > p["due"]
    save_projects(data)
    print(f"task {t['n']}/{len(p['tasks'])} done: {t['text']} ({when.isoformat()})" + (f" · project {p['id']}" if len(live) > 1 else ""))
    if finished:
        print(f"project finished: {p['title']} · works {works_at(today, data)['finished']} in all (sync shows it; one Inspiration)"
              + (f" · LATE: finished after its due day ({p['due']}); the tale ends on the lesser keepsake" if p.get("late") else f" · in its week (due {p.get('due')}): the full keepsake"))
    else:
        nxt = next((x for x in p["tasks"] if not x.get("done")), None)
        print(f"next task: {nxt['n']}. {nxt['text']}")
    print(f"the tale owes piece {done}: `python3 engine/saga.py brief --tale` (run `sync` first)")


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
    for key in ("daily", "nutrition", "exercise", "sport"):  # the scoring vocabulary: a misspelt code never pays or costs silently
        for i, r in enumerate(read_csv(key), 2):
            problems += vocab_problems(cfg, key, r, f"{key}_log.csv line {i}")
    skills = cfg.get("sport", {}).get("skills") or []
    for i, r in enumerate(read_csv("sport"), 2):
        if skills and r.get("skill") not in skills:
            problems.append(f"sport_log.csv line {i}: skill '{r.get('skill')}' is not one of {', '.join(skills)} (config.json -> sport.skills)")
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
    for i, ch in enumerate(cfg.get("plan_changes", [])):
        where = f"config.json plan_changes[{i}]"
        try:
            day = d(ch.get("date", ""))
        except Exception:
            problems.append(f"{where}: bad date '{ch.get('date')}'")
            continue
        for k in ("drop", "add"):
            if ch.get(k) is not None and not isinstance(ch.get(k), list):
                problems.append(f"{where}: {k} must be a list of codes, e.g. [\"upperB\"]")
            for code in as_codes(ch.get(k)):
                if code not in PLAN_CODES:
                    problems.append(f"{where}: {k} code '{code}' is not one of {', '.join(PLAN_CODES)}")
        base = list(template_for(cfg, day).get(dow(day), []))
        for code in as_codes(ch.get("drop")):
            if code not in base and not any(session_key(b) == session_key(code) for b in base):
                problems.append(f"{where}: drop '{code}' matches nothing planned on {dow(day)} {day} ({', '.join(base) or 'no sessions'})")
        if not ch.get("source"):
            problems.append(f"{where}: no source (who moved it, and where it is filed)")
    problems += project_problems(cfg)
    print("\n".join(problems) if problems else "all logs look clean")


# ---------------------------------------------------------------- ship: the end of every change
def run(cmd, quiet=False):
    """Run a command from the repo root; returns (returncode, combined output)."""
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out and not quiet:
        print(out)
    return r.returncode, out


def cmd_ship(args, cfg, rules):
    """check -> sync -> saga.py check -> picture copies -> build -> commit -> push to main. Every step must pass before the next runs, so
    nothing broken is committed, and the push never forces: a rejected push pulls --rebase, rebuilds and tries again."""
    py = sys.executable
    gates = [("logs", [py, "engine/darrow.py", "check"]), ("sync", [py, "engine/darrow.py", "sync"]),
             ("story", [py, "engine/saga.py", "check"]), ("thumbs", [py, "engine/thumbs.py"]), ("site", [py, "engine/build_site.py"])]

    def gate():
        for name, cmd in gates:
            print(f"── {name}: {' '.join(cmd[1:])}")
            code, out = run(cmd)
            if code != 0 or (name == "logs" and out and out != "all logs look clean"):
                sys.exit(f"ship stopped at {name}: fix the above, then ship again (nothing was committed)")

    def commit(msg):
        run(["git", "add", "-A"], quiet=True)
        if run(["git", "diff", "--cached", "--quiet"], quiet=True)[0] == 0:
            print("── commit: nothing new to commit")
            return
        code, _ = run(["git", "commit", "-q", "-m", msg])
        if code != 0:
            sys.exit("ship stopped at commit")
        print("── commit: " + run(["git", "log", "--oneline", "-1"], quiet=True)[1])

    if not args.message.strip():
        sys.exit("ship needs -m with a reader-safe message")
    gate()
    commit(args.message.strip())
    if args.no_push:
        return
    for attempt in range(3):
        code, out = run(["git", "push", "-q", "origin", "HEAD:main"])
        if code == 0:
            print("── push: main is up to date with this commit")
            break
        if attempt == 2:
            sys.exit("ship stopped at push: still rejected after three tries (nothing was forced)")
        print("── push rejected: pulling main (rebase) and rebuilding")
        if run(["git", "pull", "--rebase", "-q", "origin", "main"])[0] != 0:
            sys.exit("ship stopped at pull --rebase: resolve the conflict (generated files: take either side, then "
                     "sync and build again), `git rebase --continue`, then ship again")
        gate()
        commit("sync and site after pulling main")
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], quiet=True)[1]
    if branch not in ("main", "HEAD"):
        if run(["git", "push", "-q", "-u", "origin", "HEAD"], quiet=True)[0] == 0:
            print(f"── push: {branch} too")
        else:
            print(f"── push: {branch} not pushed (main has the commit)")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync"); s.add_argument("--date")
    s = sub.add_parser("today"); s.add_argument("--date")
    s = sub.add_parser("week"); s.add_argument("--date"); s.add_argument("--score", action="store_true")
    s = sub.add_parser("sheet"); s.add_argument("--json", action="store_true")
    s = sub.add_parser("set"); s.add_argument("log", choices=["nutrition", "daily"]); s.add_argument("date"); s.add_argument("fields", nargs="+")
    s = sub.add_parser("close"); s.add_argument("date"); s.add_argument("--force", action="store_true", help="close the day even while an earlier week's chapter is unclosed")
    s = sub.add_parser("food"); s.add_argument("action", choices=["add", "list", "rm", "lib"]); s.add_argument("payload")
    s = sub.add_parser("ex"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("sport"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("roll"); s.add_argument("label"); s.add_argument("--stat", choices=ATTRS); s.add_argument("--dc", type=int, required=True)
    g = s.add_mutually_exclusive_group(); g.add_argument("--adv", action="store_true"); g.add_argument("--dis", action="store_true")
    s.add_argument("--bonus", type=int, default=0); s.add_argument("--art", action="append", help="add an Art's rank by its rules.json id, e.g. --art wardens_eye for an Insight check")
    s.add_argument("--prof", action="store_true"); s.add_argument("--tier", action="store_true"); s.add_argument("--chapter", type=int)
    s.add_argument("--reroll", action="store_true"); s.add_argument("--paid", action="store_true", help="with --reroll: the choice that offered the reroll spent the Inspiration (saga.py choose); no second spend"); s.add_argument("--note")
    s = sub.add_parser("odds"); s.add_argument("--stat", choices=ATTRS); s.add_argument("--dc", type=int); s.add_argument("--target", type=float, help="the chance of a full success you want, e.g. 0.8: prints the DC nearest it")
    g = s.add_mutually_exclusive_group(); g.add_argument("--adv", action="store_true"); g.add_argument("--dis", action="store_true")
    s.add_argument("--bonus", type=int, default=0); s.add_argument("--art", action="append"); s.add_argument("--prof", action="store_true")
    s.add_argument("--tier", action="store_true"); s.add_argument("--chapter", type=int); s.add_argument("--json", action="store_true")
    s = sub.add_parser("inspire"); s.add_argument("--reason", required=True)
    s = sub.add_parser("chapter-close"); s.add_argument("--date"); s.add_argument("--force", action="store_true")
    s.add_argument("--partial-ok", action="store_true", help="freeze even though the week's last day looks unfinished (he said that was all)")
    s = sub.add_parser("knot"); s.add_argument("action", choices=["tie"]); s.add_argument("n", type=int); s.add_argument("--date", required=True); s.add_argument("--evidence", required=True)
    s = sub.add_parser("project"); s.add_argument("action", choices=["open", "done", "show", "drop"]); s.add_argument("what", nargs="?", help="open: the title; done: the task's number or a few of its words")
    s.add_argument("--tasks", nargs="+", help="open: 2-5 tasks, each one thing he can report done"); s.add_argument("--id", help="open: the new project's short id; done/drop: which live project, when more than one is"); s.add_argument("--date"); s.add_argument("--due", help="open: the day it is due (default: the Saturday of the week it opens)"); s.add_argument("--why"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("show"); s.add_argument("log", choices=["daily", "nutrition", "food", "ex", "exercise", "sport", "measurements"]); s.add_argument("date"); s.add_argument("--session")
    s = sub.add_parser("recap"); s.add_argument("--date"); s.add_argument("--write", action="store_true"); s.add_argument("--force", action="store_true")
    s = sub.add_parser("measure"); s.add_argument("action", choices=["add"]); s.add_argument("payload")
    s = sub.add_parser("measures"); s.add_argument("--metric")
    s = sub.add_parser("doc"); s.add_argument("name"); s.add_argument("section", nargs="*")
    sub.add_parser("check")
    s = sub.add_parser("ship"); s.add_argument("-m", "--message", required=True); s.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    cfg, rules = load_json(P["config"]), load_json(P["rules"])
    {
        "sync": cmd_sync, "today": cmd_today, "week": cmd_week, "sheet": cmd_sheet, "set": cmd_set, "close": cmd_close,
        "food": cmd_food, "roll": cmd_roll, "odds": cmd_odds, "inspire": cmd_inspire, "chapter-close": cmd_chapter_close,
        "knot": cmd_knot, "check": cmd_check, "show": cmd_show, "recap": cmd_recap, "project": cmd_project,
        "measure": cmd_measure, "measures": cmd_measures, "doc": cmd_doc, "ship": cmd_ship,
        "ex": lambda a, c, r: cmd_append("exercise", a, c),
        "sport": lambda a, c, r: cmd_append("sport", a, c),
    }[args.cmd](args, cfg, rules)


if __name__ == "__main__":
    main()
