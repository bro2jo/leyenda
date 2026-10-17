#!/usr/bin/env python3
"""THE UNKNEELING - the Ledger's trends page: real/trends.html, one standalone page of what the logs show over time.

Real only. It reads the logs through the engine's own readers (engine/darrow.py: the same facts, plans, week scores,
weight comparisons and measurements that `today`, `week`, `recap` and `measures` print), never a CSV on its own
terms, and never anything under saga/. Nothing of the story goes in: no XP, level, tier, Ember, Art or name.

What it shows, mobile first (he reads it on his phone):
  the streaks (logging, the morning check, the heel prop, creatine, food) with the last 14 days as dots
  the engine's week score, week by week, with its parts
  a calendar of the daily habits (how many of the four each day carried)
  sessions done against the plan, by week and by family (knee, upper, conditioning, sport, PT)
  the knee's mornings: the swelling grade and the morning pain, day by day
  weight with a 7-day average; calories and protein against their targets
  the latest measured numbers (extension, flexion, strength with LSI)
A range control (2, 4, 8 weeks, all) scopes every chart and count below it. Every chart has a table twin.
Gaps stay gaps: an unlogged day is empty, never zero; the day still open is marked and kept out of averages.

Streaks: consecutive days with the habit done, ending today or, while today is still open, yesterday. A red-light
day (the plan said rest) is skipped: it neither breaks nor extends a streak. An unlogged day breaks it (golden
rule 5: not reported, not done). "Done" is the engine's own reading of the day: the morning check needs a swelling
grade, the heel prop the day's full round count (config.json -> daily_minimum), food a kcal total.

Usage: python3 engine/report.py [--out PATH] [--date D]
  Run it when he asks for the trends (CLAUDE.md routes "trends" here); `ship` does not run it, so the page shows
  the logs as of its last build (the footer says when) and the next ship commits that build. The page needs no
  network: no fonts, scripts, styles or images from anywhere; open the file and it works, JavaScript on or off
  (off: the streaks, the measured numbers and this week's table still show).
Standard library only (Python 3.9+).
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import darrow as E  # noqa: E402  (the engine: one reader of the logs, one set of definitions)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "real" / "trends.html"

GRADES = ["0", "trace", "1+", "2+", "3+"]
HABITS = [  # key in the day record, label, what counts
    ("logged", "Logging", "anything recorded for the day"),
    ("check", "Morning check", "the swelling grade recorded"),
    ("floorfull", "Heel prop", "the daily minimum, every round"),
    ("creatine", "Creatine", "taken"),
    ("food", "Food", "the day's total logged"),
]
FAMILIES = [("knee", "Knee"), ("upper", "Upper"), ("cond", "Conditioning"), ("sport", "Sport"), ("pt", "PT"),
            ("accessory", "Accessory"), ("power", "Power")]


# ---------------------------------------------------------------- the data
def grade_of(row):
    g = str(row.get("am_swelling", "")).strip()
    if not E.VALID_SWELLING.match(g):
        return None
    return "0" if g.lower() in ("0", "none") else g.lower()


def day_record(cfg, rules, facts, rows, day):
    iso = day.isoformat()
    f = facts.get(iso)
    r = rows.get(iso, {})
    rec = {"date": iso, "dow": E.dow(day), "pod": E.pod(cfg, day), "planned": E.planned_for(cfg, day),
           "light": "", "logged": False, "closed": False, "kcal": None, "protein": None, "weight": None,
           "creatine": False, "floor": None, "floorfull": False, "food": False, "check": False, "swelling": None,
           "pain": None, "pain_text": "", "trend": "", "catch": "", "wellness": None, "knee": None,
           "knee_partial": False, "as_planned": False, "pt": False, "pt_missed": False, "addons": [],
           "cond_min": 0, "cond_type": "", "sport": 0, "sport_min": None, "together": False, "missed": []}
    if f:
        rec.update(light=f["light"], logged=f["logged"], closed=f["closed"], kcal=f["kcal"], protein=f["protein"],
                   weight=f["weight"], creatine=f["creatine"], floor=f["floor"], floorfull=f["floor"] == "full",
                   food=f["kcal"] is not None, check=f["check"], knee=f["knee"], knee_partial=f["knee_partial"],
                   as_planned=f["as_planned"], pt=f["pt"], pt_missed=f["pt_missed"], addons=sorted(f["addons"]),
                   cond_min=f["cond_min"], cond_type=f["cond_type"], sport=f["sport"], together=f["together"])
    rec["missed"] = E.unlogged_sessions(cfg, day, f)
    rec["swelling"] = grade_of(r)
    rec["pain"] = E.num(r.get("am_pain"))
    rec["pain_text"] = str(r.get("am_pain", "")).strip()
    rec["trend"] = str(r.get("am_trend", "")).strip()
    rec["catch"] = str(r.get("catch", "")).strip()
    rec["wellness"] = E.num(r.get("wellness"))
    rec["sport_min"] = E.num(r.get("sport_min"))
    for k in ("am_extension", "flexion", "pain_session", "pain_pm", "am_notes", "notes", "hours_on_feet", "crutches",
              "gait_notes", "adjuncts", "sleep_h", "knee_min", "knee_rpe", "addon_min", "addon_rpe", "knee_as_planned"):
        rec[k] = str(r.get(k, "")).strip()  # his words, for the day's card
    rec["adjunct_list"] = [a.strip() for a in re.split(r";", rec["adjuncts"]) if a.strip()]  # sauna, Game Ready, laser, ...
    rec["sport_sessions"] = sorted(f["sport_sessions"]) if f else []
    rec["sport_skills"] = sorted(f["sport_skills"]) if f else []
    return rec


DETAIL_COLS = {
    "ex": ("session", "block", "exercise", "side", "sets", "reps", "hold_or_duration", "load_or_band", "assist", "notes"),
    "sport": ("session", "skill", "drill", "sets", "reps", "minutes", "rpe", "metric", "value", "notes"),
    "food": ("meal", "item", "qty", "kcal", "protein_g", "source"),
}


def details(cfg, recs):
    """Everything else the logs hold about a day, for its card: the exercise rows by session, the throwing rows, the
    food items, the day's nutrition note, what was measured, and the project tasks reported done. Days with none of
    it are left out, so the page stays small."""
    out = {r["date"]: {"ex": [], "sport": [], "food": [], "food_notes": "", "measured": [], "tasks": []} for r in recs}
    for key in ("ex", "sport", "food"):
        for r in E.read_csv("exercise" if key == "ex" else key):
            if r.get("date") in out:
                out[r["date"]][key].append({c: str(r.get(c) or "").strip() for c in DETAIL_COLS[key]})
    for r in E.read_csv("nutrition"):
        if r.get("date") in out:
            out[r["date"]]["food_notes"] = str(r.get("notes") or "").strip()
    specs = E.metric_specs(cfg)
    for g in E.measurement_sets(cfg):
        if g["date"] in out:
            out[g["date"]]["measured"].append(f"{E.metric_label(g['metric'], specs.get(g['metric'], {}))} {E.set_text(g)}"
                                              + (f" ({g['source']})" if g.get("source") else ""))
    for p in E.load_projects().get("projects", []):
        for t in p.get("tasks", []):
            if t.get("done") in out:
                out[t["done"]]["tasks"].append({"project": p["title"], "task": f"{t['n']}. {t['text']}"})
        if p.get("done") in out:
            out[p["done"]]["tasks"].append({"project": p["title"], "task": "finished"})
    return {k: v for k, v in out.items() if any(v[x] for x in ("ex", "sport", "food", "food_notes", "measured", "tasks"))}


def streak(recs, key):
    """Current and best run of a daily habit (module docstring: red days skipped, the open day forgiven)."""
    run = best = 0
    start = best_from = best_to = None
    for r in recs:
        if r["light"] == "red":
            continue
        if r[key]:
            if run == 0:
                start = r["date"]
            run += 1
            if run > best:
                best, best_from, best_to = run, start, r["date"]
        else:
            run = 0
    last = recs[-1]
    i = len(recs) - 1
    if last["light"] != "red" and not last[key] and not last["closed"]:
        i -= 1  # today is still open: the streak stands until the day ends
    cur = 0
    while i >= 0:
        r = recs[i]
        i -= 1
        if r["light"] == "red":
            continue
        if r[key]:
            cur += 1
        else:
            break
    return {"current": cur, "best": best, "best_from": best_from, "best_to": best_to, "today": bool(last[key])}


def family_counts(rules, recs):
    """Sessions done in these days, by family, as they happened (the plan's cap is applied in the view)."""
    tags = rules["tags"]["session_tags"]
    did = Counter()
    for r in recs:
        if r["knee"]:
            did["knee"] += 1
        for a in r["addons"]:
            did[tags.get(a, a)] += 1
        if r["cond_min"] >= rules["daily"]["conditioning"]["min_minutes"]:
            did["cond"] += 1
        if r["sport"]:
            did["sport"] += 1
        if r["pt"]:
            did["pt"] += 1
    return dict(did)


def week_records(cfg, rules, facts, recs, asof):
    by_date = {r["date"]: r for r in recs}
    first = E.d(recs[0]["date"])
    t = cfg["nutrition_targets"]
    out = []
    ws = E.week_start(first)
    while ws <= asof:
        upto = min(ws + dt.timedelta(6), asof)
        sc = E.week_score(ws, upto, facts, cfg, rules)
        days = [by_date[(ws + dt.timedelta(i)).isoformat()] for i in range((upto - ws).days + 1)
                if (ws + dt.timedelta(i)).isoformat() in by_date]
        settled = [x for x in days if x["closed"] or x["date"] != asof.isoformat()]  # the open day is not a day's fuel yet
        kc = [x["kcal"] for x in settled if x["kcal"] is not None]
        pr = [x["protein"] for x in settled if x["protein"] is not None]
        wc = E.weight_compare(facts, ws, upto)
        out.append({
            "week_start": ws.isoformat(), "through": upto.isoformat(), "days": sc["days"], "complete": sc["complete"],
            "current": ws == E.week_start(asof), "score": sc["score"], "parts": {k: round(v, 3) for k, v in sc["parts"].items()},
            "planned": sc["planned"], "done": sc["done"], "did": family_counts(rules, days), "excused": sc["excused"],
            "floor_full": sc["floor_full_days"], "checks": sum(1 for x in days if x["check"]),
            "logged": sum(1 for x in days if x["logged"]), "weighins": sc["weighins"],
            "kcal_avg": round(sum(kc) / len(kc)) if kc else None, "kcal_days": len(kc),
            "kcal_hit": sum(1 for v in kc if v >= t["kcal"]),
            "protein_avg": round(sum(pr) / len(pr)) if pr else None, "protein_days": len(pr),
            "protein_hit": sum(1 for v in pr if v >= t["protein_g"]),
            "weight_avg": round(wc["avg"], 1) if wc["avg"] is not None else None, "weight_n": len(wc["cur"]),
            "weight_delta": round(wc["delta"], 1) if wc["delta"] is not None else None,
        })
        ws += dt.timedelta(7)
    return out


def measured(cfg):
    """Latest per metric and side, with the latest LSI, as `measures` prints it, plus every set for the history."""
    specs, sets = E.metric_specs(cfg), E.measurement_sets(cfg)
    out = []
    for m, spec in specs.items():
        ms = [g for g in sets if g["metric"] == m]
        if not ms:
            continue
        rec = {"metric": m, "label": E.metric_label(m, spec), "unit": spec.get("unit", ""), "about": spec.get("about", ""),
               "L": None, "R": None, "lsi": None, "history": []}
        for s in ("L", "R"):
            last = [g for g in ms if g[s] is not None]
            if last:
                g = last[-1]
                rec[s] = {"text": E.mval(m, g[s], g["unit"]), "date": E.mdate(g["date"]), "method": g["method"]}
        paired = [g for g in ms if g["lsi"] is not None]
        if paired:
            rec["lsi"] = {"value": round(paired[-1]["lsi"], 1), "date": E.mdate(paired[-1]["date"])}
        for g in ms:
            rec["history"].append({"date": E.mdate(g["date"]), "text": E.set_text(g), "source": g["source"], "method": g["method"]})
        out.append(rec)
    return out


def food_sources():
    food = [r for r in E.read_csv("food") if r.get("date")]
    mix = Counter()
    for r in food:
        s = str(r.get("source", "")).strip().lower()
        kind = ("estimate" if "estimate" in s else "photo" if "photo" in s else "label" if "label" in s
                else "library" if "library" in s else "other")
        mix[kind] += 1
    return {"items": len(food), "from": min((r["date"] for r in food), default=None), "mix": dict(mix)}


def now_stamp(cfg):
    try:
        from zoneinfo import ZoneInfo
        now = dt.datetime.now(ZoneInfo(cfg.get("timezone", "America/New_York")))
    except Exception:
        now = dt.datetime.now()
    return now.strftime("%a %Y-%m-%d %H:%M")


def collect(asof=None):
    cfg, rules = E.load_json(E.P["config"]), E.load_json(E.P["rules"])
    st = E.compute(cfg, rules, asof=asof)
    facts, asof = st["facts"], st["asof"]
    rows = E.daily_rows()
    dated = sorted(E.d(x) for x in facts if E.d(x) <= asof)
    first = dated[0] if dated else asof
    recs = [day_record(cfg, rules, facts, rows, first + dt.timedelta(i)) for i in range((asof - first).days + 1)]
    today = recs[-1]
    t = cfg["nutrition_targets"]
    reh = cfg["rehab"]
    pt_days = [r["date"] for r in recs if r["pt"]]
    return {
        "generated": now_stamp(cfg), "asof": asof.isoformat(), "asof_dow": E.dow(asof), "today_closed": today["closed"],
        "pod": E.pod(cfg, asof), "post_op_week": E.post_op_week(cfg, asof), "surgery_date": cfg["surgery_date"],
        "phase": reh["current_phase"], "phase_entered": reh.get("phase_entered"), "next_gate": reh.get("next_gate", ""),
        "targets": {"kcal": t["kcal"], "protein_g": t["protein_g"], "protein_g_max": t["protein_g_max"],
                    "weighins_per_week": t["weighins_per_week"]},
        "floor_rounds": E.floor_rounds(cfg, asof.isoformat()),
        "today_open": today["missed"], "project": E.project_line(),
        "weight_week_line": E.weight_line(E.weight_compare(facts, E.week_start(asof), asof), t["weighins_per_week"]),
        "pt": {"visits": len(pt_days), "last": pt_days[-1] if pt_days else None},
        "days": recs, "weeks": week_records(cfg, rules, facts, recs, asof), "detail": details(cfg, recs),
        "streaks": {k: streak(recs, k) for k, _, _ in HABITS},
        "measured": measured(cfg), "food": food_sources(),
        "coverage": {"first": recs[0]["date"], "days": len(recs), "logged": sum(1 for r in recs if r["logged"]),
                     "closed": sum(1 for r in recs if r["closed"]), "red": sum(1 for r in recs if r["light"] == "red")},
        "week_weights": rules["week_score"]["weights"],
        "week_table": E.real_week_table(st, cfg, rules, E.week_start(asof), summary=False),
    }


# ---------------------------------------------------------------- the static parts (JavaScript off still shows them)
def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def md_of(iso):
    return E.md(E.d(iso))


def dow_md(iso):
    day = E.d(iso)
    return f"{E.dow(day)} {E.md(day)}"


def tile(key, label, what, s, strip):
    cur = s["current"]
    best = s["best"]
    best_txt = (f"best {best}" + (f" · {md_of(s['best_from'])}–{md_of(s['best_to'])}" if best and s["best_from"] != s["best_to"]
                                   else f" · {md_of(s['best_to'])}" if best else ""))
    state = "✓ today" if s["today"] else "not yet today"
    return (f'<div class="tile" data-habit="{key}">'
            f'<div class="tile-h"><span class="tile-l">{esc(label)}</span></div>'
            f'<div class="tile-v"><span class="big">{cur}</span><span class="unit">day{"" if cur == 1 else "s"} in a row</span></div>'
            f'<div class="strip" aria-hidden="true">{strip}</div>'
            f'<div class="tile-f"><span>{esc(best_txt)}</span></div>'
            f'<div class="tile-f"><span data-slot="rate-{key}">—</span><span class="tile-s">{esc(state)}</span></div>'
            f'<div class="tile-w">{esc(what)}</div></div>')


def strip_html(recs, key):
    dots = []
    for r in recs[-14:]:
        cls = "on" if r[key] else "red" if r["light"] == "red" else "off"
        if r is recs[-1]:
            cls += " today"
        dots.append(f'<i class="{cls}" title="{esc(dow_md(r["date"]))}"></i>')
    return "".join(dots)


def measured_html(ms):
    if not ms:
        return '<p class="muted">Nothing measured yet.</p>'
    rows = []
    for m in ms:
        def cell(side):
            v = m.get(side)
            return (f'<td><b>{esc(v["text"])}</b><small>{esc(v["date"])}{(" · " + esc(v["method"])) if v["method"] else ""}</small></td>'
                    if v else '<td class="muted">—</td>')
        lsi = m.get("lsi")
        lsi_td = (f'<td><b>{lsi["value"]:.1f}%</b><small>{esc(lsi["date"])}</small></td>' if lsi else '<td class="muted">—</td>')
        hist = " · ".join(f'{esc(h["date"])}: {esc(h["text"])}' for h in m["history"])
        rows.append(f'<tr><th scope="row">{esc(m["label"])}<small>{esc(m["about"])}</small></th>{cell("L")}{cell("R")}{lsi_td}</tr>'
                    f'<tr class="hist"><td colspan="4"><span class="muted">{hist}</span></td></tr>')
    return ('<div class="scroll"><table class="measured"><thead><tr><th>Metric</th><th>Left</th><th>Right</th><th>LSI</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def week_table_html(md_table):
    lines = [ln for ln in md_table.strip().splitlines() if ln.startswith("|")]
    if len(lines) < 3:
        return ""
    cells = lambda ln: [c.strip() for c in ln.strip().strip("|").split("|")]
    head = "".join(f"<th>{esc(c)}</th>" for c in cells(lines[0]))
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in cells(ln)) + "</tr>" for ln in lines[2:])
    return f'<div class="scroll"><table class="plain"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render(data):
    recs = data["days"]
    tiles = "".join(tile(k, label, what, data["streaks"][k], strip_html(recs, k)) for k, label, what in HABITS)
    phase_since = f' since {md_of(data["phase_entered"])}' if data.get("phase_entered") else ""
    open_txt = ", ".join(data["today_open"]) if data["today_open"] else "nothing"
    planned_today = ", ".join(E.SESSION_NAMES.get(p, p) for p in recs[-1]["planned"]) or "the daily minimum only"
    mix = data["food"]["mix"]
    mix_txt = ", ".join(f"{v} {k}" for k, v in sorted(mix.items(), key=lambda kv: -kv[1])) or "none"
    cov = data["coverage"]
    pt = data["pt"]
    pt_txt = f'Last PT visit {dow_md(pt["last"])} · {pt["visits"]} visit{"s" if pt["visits"] != 1 else ""} logged' if pt["last"] else "No PT visit logged yet"
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE
    for k, v in {
        "{{TITLE}}": "The Ledger",
        "{{STATUS}}": f'{data["asof_dow"]} {md_of(data["asof"])} · POD {data["pod"]} · post-op week {data["post_op_week"]} · Phase {data["phase"]}{phase_since}',
        "{{TODAY_PLAN}}": esc(planned_today),
        "{{TODAY_OPEN}}": esc(open_txt),
        "{{PROJECT}}": esc(data["project"].replace("Project: ", "", 1)),
        "{{PT_LINE}}": esc(pt_txt),
        "{{TILES}}": tiles,
        "{{FLOOR_ROUNDS}}": str(data["floor_rounds"]),
        "{{GATE}}": esc(data["next_gate"]),
        "{{WEIGHT_WEEK}}": esc(data["weight_week_line"]),
        "{{KCAL_T}}": f'{data["targets"]["kcal"]:,}',
        "{{PROT_T}}": f'{data["targets"]["protein_g"]}–{data["targets"]["protein_g_max"]}',
        "{{MEASURED}}": measured_html(data["measured"]),
        "{{WEEK_TABLE}}": week_table_html(data["week_table"]),
        "{{COVERAGE}}": esc(f'{cov["logged"]} of {cov["days"]} days logged since {dow_md(cov["first"])} · {cov["closed"]} closed'
                            + (f' · {cov["red"]} rest day{"s" if cov["red"] != 1 else ""} ordered by the plan' if cov["red"] else "")),
        "{{FOOD_MIX}}": esc(f'{data["food"]["items"]} food items since {md_of(data["food"]["from"])}: {mix_txt}' if data["food"]["from"] else "no itemised food yet"),
        "{{GENERATED}}": esc(data["generated"]),
        "{{DATA}}": payload,
    }.items():
        page = page.replace(k, v)
    return page


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<title>{{TITLE}}</title>
<style>
/* Layout: one column, the width of a phone; sections separated by hairlines, cards only for the streak tiles. */
:root {
  color-scheme: light;
  --bg: #f6f6f3;
  --surface: #fcfcfb;
  --ink: #111210;
  --ink-2: #52514e;
  --muted: #898781;
  --grid: #e1e0d9;
  --axis: #c3c2b7;
  --border: rgba(11,11,11,.10);
  --accent: #2a78d6;
  --accent-soft: rgba(42,120,214,.14);
  --dim: #b4b3ad;
  --seq-0: #e6eef9;
  --seq-1: #b7d3f6;
  --seq-2: #6da7ec;
  --seq-3: #2a78d6;
  --seq-4: #184f95;
  --good: #0ca30c;
  --good-text: #006300;
  --warn: #fab219;
  --serious: #ec835a;
  --critical: #d03b3b;
  --c-knee: #2a78d6; --c-upper: #e87ba4; --c-cond: #1baf7a; --c-sport: #eda100; --c-pt: #008300;
  --c-sauna: #e34948; --c-gr: #6250d6; --c-light: #eb6834;
  --tip-bg: #fcfcfb;
  --shadow: 0 6px 24px rgba(11,11,11,.14);
  --radius: 10px;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,.10);
    --accent: #3987e5; --accent-soft: rgba(57,135,229,.22); --dim: #5a5953;
    --seq-0: #22314a; --seq-1: #184f95; --seq-2: #256abf; --seq-3: #3987e5; --seq-4: #86b6ef;
    --good-text: #0ca30c; --tip-bg: #232322; --shadow: 0 6px 24px rgba(0,0,0,.5);
    --c-knee: #3987e5; --c-upper: #d55181; --c-cond: #199e70; --c-sport: #c98500; --c-pt: #008300;
    --c-sauna: #e66767; --c-gr: #9085e9; --c-light: #d95926;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,.10);
  --accent: #3987e5; --accent-soft: rgba(57,135,229,.22); --dim: #5a5953;
  --seq-0: #22314a; --seq-1: #184f95; --seq-2: #256abf; --seq-3: #3987e5; --seq-4: #86b6ef;
  --good-text: #0ca30c; --tip-bg: #232322; --shadow: 0 6px 24px rgba(0,0,0,.5);
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font); font-size: 16px; line-height: 1.45;
  padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px);
}
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); background: var(--bg); z-index: 10; }
.wrap { max-width: 640px; margin: 0 auto; padding-inline: max(16px, env(safe-area-inset-left, 0px)) max(16px, env(safe-area-inset-right, 0px)); padding-block: 8px 48px; }
h1, h2, h3 { margin: 0; text-wrap: balance; font-weight: 600; }
h1 { font-size: 24px; letter-spacing: -.01em; }
h2 { font-size: 18px; }
p { margin: 0; }
small, .muted { color: var(--muted); }
.eyebrow { font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.head { display: grid; gap: 6px; padding-block: 10px 14px; }
.status { color: var(--ink-2); font-size: 14px; }
.now { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; font-size: 14px; margin-top: 6px; }
.now dt { color: var(--muted); }
.now dd { margin: 0; color: var(--ink-2); min-width: 0; overflow-wrap: anywhere; }
.now dd b { color: var(--ink); font-weight: 600; }

/* the range control: one row, sticky, every chart below follows it */
.bar { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg); padding-block: 8px 10px; }
.seg { display: flex; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); padding: 3px; gap: 3px; }
.seg button {
  flex: 1 1 0; min-height: 40px; border: 0; border-radius: 9px; background: transparent; color: var(--ink-2);
  font: inherit; font-size: 15px; font-weight: 500; cursor: pointer; padding: 0 4px;
}
.seg button[aria-pressed="true"] { background: var(--accent); color: #fff; font-weight: 600; }
.seg button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.seg button[hidden] { display: none; }
.range-note { font-size: 13px; color: var(--muted); margin-top: 6px; }

section { padding-block: 18px 22px; border-top: 1px solid var(--grid); }
.sec-h { display: grid; gap: 2px; margin-bottom: 12px; }
.sec-h p { color: var(--ink-2); font-size: 14px; }

/* stat tiles */
.tiles { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
@media (min-width: 560px) { .tiles { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px 12px 10px; display: grid; gap: 6px; min-width: 0; }
.tile-h { display: flex; justify-content: space-between; gap: 6px; align-items: baseline; }
.tile-l { font-size: 14px; font-weight: 600; }
.tile-s { font-size: 12px; color: var(--muted); white-space: nowrap; }
.tile-v { display: flex; align-items: baseline; gap: 6px; }
.big { font-size: 34px; font-weight: 600; line-height: 1; letter-spacing: -.02em; }
.unit { font-size: 12px; color: var(--muted); }
.tile-f { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: var(--ink-2); flex-wrap: wrap; }
.tile-w { font-size: 11px; color: var(--muted); }
.strip { display: flex; gap: 3px; }
.strip i { flex: 1 1 0; height: 8px; border-radius: 2px; background: var(--seq-3); }
.strip i.off { background: transparent; box-shadow: inset 0 0 0 1px var(--axis); }
.strip i.red { background: var(--grid); }
.strip i.today { outline: 2px solid var(--accent); outline-offset: 1px; }
.stats { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
.stat { display: grid; gap: 2px; min-width: 0; }
.stat .k { font-size: 12px; color: var(--muted); }
.stat .v { font-size: 22px; font-weight: 600; line-height: 1.15; letter-spacing: -.01em; }
.stat .v small { font-size: 13px; font-weight: 500; color: var(--ink-2); margin-left: 4px; }
.stat .d { font-size: 12px; color: var(--ink-2); }
.flag { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; }
.flag.good { color: var(--good-text); }
.flag.warn { color: var(--serious); }
.flag svg { width: 12px; height: 12px; }

/* figures */
figure { margin: 0; position: relative; }
.plot { position: relative; min-width: 0; }
.chart { display: block; width: 100%; height: auto; touch-action: pan-y pinch-zoom; -webkit-tap-highlight-color: transparent; overflow: visible; }
.chart:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
.chart:focus:not(:focus-visible) { outline: none; }
.chart text { fill: var(--muted); font-family: var(--font); font-size: 11px; }
.chart text.halo { paint-order: stroke; stroke: var(--bg); stroke-width: 3px; stroke-linejoin: round; }
.chart text.ink { fill: var(--ink); font-weight: 600; }
.chart text.ink2 { fill: var(--ink-2); }
.chart .grid { stroke: var(--grid); stroke-width: 1; }
.chart .axis { stroke: var(--axis); stroke-width: 1; }
.chart .wk { stroke: var(--grid); stroke-width: 1; }
.chart .target { stroke: var(--ink-2); stroke-width: 1; }
.chart .band { fill: var(--accent-soft); }
.chart .col { fill: var(--accent); }
.chart .col.open { fill: var(--accent-soft); stroke: var(--accent); stroke-width: 1.5; }
.chart .col.hi { filter: brightness(1.15); }
.chart .line { fill: none; stroke: var(--accent); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.chart .dot { fill: var(--dim); stroke: var(--surface); stroke-width: 2; }
.chart .dot.hi { fill: var(--accent); r: 5; }
.chart .end { fill: var(--accent); stroke: var(--surface); stroke-width: 2; }
.chart .cross { stroke: var(--axis); stroke-width: 1; }
.chart .hit { fill: transparent; }
figcaption { font-size: 12px; color: var(--muted); margin-top: 6px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12px; color: var(--ink-2); margin-top: 8px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.legend i { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.legend i.none { box-shadow: inset 0 0 0 1px var(--axis); }
.legend i.dot { width: 10px; height: 10px; border-radius: 50%; }

/* the two views */
.tabs { display: flex; border-bottom: 1px solid var(--grid); margin-bottom: 8px; }
.tabs button { flex: 1 1 0; min-height: 44px; border: 0; border-bottom: 2px solid transparent; margin-bottom: -1px; background: transparent; color: var(--ink-2); font: inherit; font-size: 15px; font-weight: 600; cursor: pointer; }
.tabs button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent); }
.tabs button:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
.mnav { display: flex; align-items: center; gap: 6px; }
.mnav button { min-width: 48px; min-height: 40px; border: 1px solid var(--border); background: var(--surface); color: var(--ink); border-radius: 9px; font: inherit; font-size: 20px; line-height: 1; cursor: pointer; }
.mnav button:disabled { opacity: .35; cursor: default; }
.mnav button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.mnav .ml { flex: 1; text-align: center; font-weight: 600; font-size: 16px; }

/* days: chips, the month grid, the cards */
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: var(--surface); border: 1px solid var(--border); font-size: 13px; color: var(--ink); min-height: 28px; max-width: 100%; }
.chip.q { color: var(--ink-2); }
/* the kinds: one colour each; circles are training and the clinic, squares are recovery */
.mk { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: none; background: transparent; }
.mk.sq { border-radius: 2px; }
.mk.knee { background: var(--c-knee); } .mk.upper { background: var(--c-upper); } .mk.cond { background: var(--c-cond); }
.mk.sport { background: var(--c-sport); } .mk.pt { background: var(--c-pt); }
.mk.sauna { background: var(--c-sauna); } .mk.gr { background: var(--c-gr); } .mk.light { background: var(--c-light); }
.legend .mk { width: 12px; height: 12px; }
.mgrid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 3px; margin-top: 12px; }
.mgrid .dh { font-size: 11px; color: var(--muted); text-align: center; }
.mc { min-height: 64px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); padding: 4px 4px 5px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-start; gap: 4px; font: inherit; font-size: 13px; line-height: 1.2; color: var(--ink-2); cursor: pointer; min-width: 0; text-align: left; }
.mc.none { background: transparent; color: var(--muted); }
.mc.red { background: var(--grid); }
.mc.out { background: transparent; border-color: transparent; color: var(--muted); opacity: .45; cursor: default; }
.mc.today { background: var(--accent-soft); }
.mc.today .dn { color: var(--accent); font-weight: 700; }
.mc.sel { outline: 2px solid var(--ink); outline-offset: 1px; }
.mc:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.mc .marks { display: grid; grid-template-columns: repeat(3, 10px); gap: 3px; }
.dnav { margin-left: auto; display: inline-flex; gap: 4px; }
.dnav button { min-width: 40px; min-height: 36px; border: 1px solid var(--border); background: var(--surface); color: var(--ink); border-radius: 8px; font: inherit; font-size: 18px; line-height: 1; cursor: pointer; }
.dnav button:disabled { opacity: .35; cursor: default; }
.dnav button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
#dayview { scroll-margin-top: calc(env(safe-area-inset-top, 0px) + 112px); }
.day { padding: 12px 0; display: grid; gap: 8px; }
.day header { display: grid; gap: 2px; }
.day header .dh1 { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.day header .dh2 { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
.day header b { font-size: 17px; }
.day header .muted { font-size: 12px; }
.tag { font-size: 11px; font-weight: 600; color: var(--accent); background: var(--accent-soft); padding: 2px 8px; border-radius: 999px; }
details.more summary { cursor: pointer; font-size: 13px; color: var(--ink-2); padding: 6px 0; min-height: 36px; display: flex; align-items: center; gap: 6px; list-style: none; }
details.more summary::-webkit-details-marker { display: none; }
details.more summary::before { content: ""; width: 7px; height: 7px; border-right: 1.5px solid var(--muted); border-bottom: 1.5px solid var(--muted); transform: rotate(-45deg); transition: transform .15s; }
details.more[open] summary::before { transform: rotate(45deg); }
.det { display: grid; gap: 8px; font-size: 13px; color: var(--ink-2); padding-bottom: 4px; }
.dl { display: grid; grid-template-columns: 78px minmax(0, 1fr); gap: 8px; }
.dl .k { color: var(--muted); font-size: 12px; padding-top: 1px; }
.dl .v { min-width: 0; overflow-wrap: anywhere; color: var(--ink); }
.dl ul { margin: 0; padding: 0; list-style: none; display: grid; gap: 5px; }
.dl li small { display: block; color: var(--muted); font-size: 12px; }
.dl li.gk { color: var(--muted); font-size: 12px; font-weight: 600; margin-top: 2px; }
.dl li.nd { color: var(--muted); text-decoration: line-through; }

/* tooltips: tap to read; nothing is only in them */
.tip { position: absolute; z-index: 4; pointer-events: none; background: var(--tip-bg); color: var(--ink); border: 1px solid var(--border); border-radius: 8px; box-shadow: var(--shadow); padding: 8px 10px; font-size: 13px; min-width: 120px; max-width: 240px; display: none; }
.tip.on { display: block; }
.tip .th { font-weight: 600; margin-bottom: 4px; }
.tip .tr { display: flex; gap: 8px; align-items: baseline; justify-content: space-between; }
.tip .tr b { font-weight: 600; font-variant-numeric: tabular-nums; }
.tip .tr span { color: var(--ink-2); }
.tip .tn { color: var(--muted); font-size: 12px; margin-top: 3px; }

/* strips and grids */
.rows { display: grid; gap: 6px; }
.row { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 8px; align-items: center; }
.row .rl { font-size: 12px; color: var(--ink-2); }
.cells { display: grid; gap: 2px; }
.cells i { display: block; height: 26px; border-radius: 3px; background: var(--seq-1); min-width: 0; }
.cells i.g0 { background: var(--seq-0); } .cells i.g1 { background: var(--seq-1); } .cells i.g2 { background: var(--seq-2); }
.cells i.g3 { background: var(--seq-3); } .cells i.g4 { background: var(--seq-4); }
.cells i.none { background: transparent; box-shadow: inset 0 0 0 1px var(--grid); }
.cells i.text { background: transparent; box-shadow: inset 0 0 0 1px var(--axis); }
.cells i.hi { outline: 2px solid var(--ink); outline-offset: -2px; }
.xlab { display: grid; gap: 2px; font-size: 11px; color: var(--muted); }
.xlab span { min-width: 0; white-space: nowrap; overflow: visible; }
.cal { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 4px; }
.cal .dh { font-size: 11px; color: var(--muted); text-align: center; padding-bottom: 2px; }
.cal .c { aspect-ratio: 1; border-radius: 6px; display: flex; align-items: flex-start; justify-content: flex-start; padding: 4px 5px; font-size: 11px; color: var(--ink-2); background: var(--seq-0); min-width: 0; }
.cal .c.h1 { background: var(--seq-1); } .cal .c.h2 { background: var(--seq-2); color: #fff; } .cal .c.h3 { background: var(--seq-3); color: #fff; } .cal .c.h4 { background: var(--seq-4); color: #fff; }
.cal .c.none { background: transparent; box-shadow: inset 0 0 0 1px var(--grid); color: var(--muted); }
.cal .c.red { background: transparent; box-shadow: inset 0 0 0 1px var(--axis); color: var(--muted); }
.cal .c.out { visibility: hidden; }
.cal .c.today { outline: 2px solid var(--accent); outline-offset: 1px; }
.cal .c.hi { outline: 2px solid var(--ink); outline-offset: 1px; }
:root[data-theme="dark"] .cal .c.h1, :root[data-theme="dark"] .cal .c.h2 { color: #fff; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .cal .c.h1, :root:not([data-theme="light"]) .cal .c.h2 { color: #fff; }
  :root:not([data-theme="light"]) .cal .c.h4 { color: #0d0d0d; } }
:root[data-theme="dark"] .cal .c.h4 { color: #0d0d0d; }

/* tables */
.scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { border-collapse: collapse; width: 100%; font-size: 13px; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--grid); vertical-align: top; white-space: nowrap; }
th { font-weight: 600; color: var(--ink-2); font-size: 12px; }
td.n, th.n { text-align: right; }
td small, th small { display: block; font-size: 11px; color: var(--muted); font-weight: 400; white-space: normal; }
tr.hist td { border-bottom: 1px solid var(--grid); font-size: 12px; white-space: normal; padding-top: 2px; }
tr.cur td { background: var(--accent-soft); }
table.sessions th, table.sessions td { padding: 7px 4px; }
table.sessions td { text-align: center; }
table.sessions th.fam { padding-left: 0; width: 1%; }
details.twin table { font-size: 12px; }
details.twin th, details.twin td { padding: 5px 6px; }
table.sessions .pips { display: inline-flex; gap: 3px; justify-content: center; margin-bottom: 2px; }
table.sessions .pips i { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); display: inline-block; }
table.sessions .pips i.open { background: transparent; box-shadow: inset 0 0 0 1.5px var(--axis); }
table.sessions .pips i.extra { background: var(--seq-2); }
table.sessions .cnt { display: block; font-size: 12px; color: var(--ink-2); }
details.twin { margin-top: 8px; }
details.twin summary { cursor: pointer; font-size: 13px; color: var(--ink-2); padding: 8px 0; min-height: 40px; display: flex; align-items: center; gap: 6px; list-style: none; }
details.twin summary::-webkit-details-marker { display: none; }
details.twin summary::before { content: ""; width: 7px; height: 7px; border-right: 1.5px solid var(--muted); border-bottom: 1.5px solid var(--muted); transform: rotate(-45deg); transition: transform .15s; }
details.twin[open] summary::before { transform: rotate(45deg); }
.foot { font-size: 13px; color: var(--muted); display: grid; gap: 6px; padding-top: 18px; border-top: 1px solid var(--grid); }
.foot code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: var(--ink-2); }
noscript .scroll { margin-top: 10px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
@media print { .bar { position: static; } .tip { display: none !important; } }
</style>
</head>
<body>
<div class="wrap">
  <header class="head">
    <div class="eyebrow">Real numbers only</div>
    <h1>The Ledger</h1>
    <p class="status">{{STATUS}}</p>
    <dl class="now">
      <dt>Today</dt><dd>planned <b>{{TODAY_PLAN}}</b> · still open: {{TODAY_OPEN}}</dd>
      <dt>Project</dt><dd>{{PROJECT}}</dd>
      <dt>PT</dt><dd>{{PT_LINE}}</dd>
    </dl>
  </header>

  <div class="bar" id="bar">
    <div class="tabs" role="tablist" aria-label="View">
      <button type="button" role="tab" data-tab="trends" aria-selected="true" aria-controls="tab-trends">Trends</button>
      <button type="button" role="tab" data-tab="days" aria-selected="false" aria-controls="tab-days">Days</button>
    </div>
    <div id="range-row">
      <div class="seg" role="group" aria-label="Range">
        <button type="button" data-range="14" aria-pressed="false">2 wk</button>
        <button type="button" data-range="28" aria-pressed="false">4 wk</button>
        <button type="button" data-range="56" aria-pressed="false">8 wk</button>
        <button type="button" data-range="all" aria-pressed="false">All</button>
      </div>
      <div class="range-note" id="range-note">Every chart and count below follows this range.</div>
    </div>
    <div id="month-row" hidden>
      <div class="mnav">
        <button type="button" id="m-prev" aria-label="Earlier month">‹</button>
        <div class="ml" id="m-label"></div>
        <button type="button" id="m-next" aria-label="Later month">›</button>
      </div>
    </div>
  </div>

  <div id="tab-trends" role="tabpanel">
  <section id="streaks">
    <div class="sec-h"><div class="eyebrow">Streaks</div><h2>Days in a row</h2>
      <p>Consecutive days with each habit done. Today is still open, so a streak stands until the day ends; a rest day the plan ordered is skipped. The dots are the last 14 days.</p></div>
    <div class="tiles">{{TILES}}</div>
  </section>

  <section id="weeks">
    <div class="sec-h"><div class="eyebrow">Week score</div><h2>Week by week</h2>
      <p>The engine's 0–100 score of each week (Sun–Sat): floor 20 · sessions 25 · fuel 30 · checks 10 · weigh-ins 5 · logging 10. This week is scored on its days so far.</p></div>
    <div class="stats" id="week-stats"></div>
    <figure>
      <div class="plot" id="week-plot"></div>
      <div class="tip" id="week-tip"></div>
      <details class="twin"><summary>Table</summary><div class="scroll" id="week-table"></div></details>
    </figure>
  </section>

  <section id="habits">
    <div class="sec-h"><div class="eyebrow">Daily habits</div><h2>Coverage</h2>
      <p>How many of the four daily habits each day carried: the morning check, the heel prop ({{FLOOR_ROUNDS}} round{{FLOOR_ROUNDS_S}}), creatine and the day's food total. An empty day was not logged.</p></div>
    <figure>
      <div class="plot" id="cal-plot"></div>
      <div class="tip" id="cal-tip"></div>
      <div class="legend"><span><i class="none"></i>not logged</span><span><i style="background:var(--seq-0)"></i>0</span><span><i style="background:var(--seq-1)"></i>1</span><span><i style="background:var(--seq-2)"></i>2</span><span><i style="background:var(--seq-3)"></i>3</span><span><i style="background:var(--seq-4)"></i>4 of 4</span></div>
      <details class="twin"><summary>Table</summary><div class="scroll" id="cal-table"></div></details>
    </figure>
  </section>

  <section id="sessions">
    <div class="sec-h"><div class="eyebrow">Sessions</div><h2>Done against the plan</h2>
      <p>Each week's planned sessions by family (plan changes the PT or trainer made are already applied), filled when done. A session beyond the plan shows in a lighter dot.</p></div>
    <div class="stats" id="sess-stats"></div>
    <div class="scroll" id="sess-grid"></div>
  </section>

  <section id="knee">
    <div class="sec-h"><div class="eyebrow">The knee</div><h2>Mornings</h2>
      <p>The morning check, day by day: the swelling grade on the clinic's scale (0 · trace · 1+ · 2+ · 3+) and the morning pain (0–10). A day without a grade stays empty.</p></div>
    <div class="stats" id="knee-stats"></div>
    <figure>
      <div class="plot" id="knee-plot"></div>
      <div class="tip" id="knee-tip"></div>
      <div class="legend" id="knee-legend"></div>
      <details class="twin"><summary>Table</summary><div class="scroll" id="knee-table"></div></details>
    </figure>
    <p class="muted" style="font-size:13px;margin-top:12px">Next gate: {{GATE}}</p>
  </section>

  <section id="weight">
    <div class="sec-h"><div class="eyebrow">Weight</div><h2>Morning weigh-ins</h2>
      <p>Each reading as a dot; the line is the 7-day average. The guide reads the weekly average, not the day.</p></div>
    <div class="stats" id="weight-stats"></div>
    <figure>
      <div class="plot" id="weight-plot"></div>
      <div class="tip" id="weight-tip"></div>
      <figcaption>This week: {{WEIGHT_WEEK}}</figcaption>
      <details class="twin"><summary>Table</summary><div class="scroll" id="weight-table"></div></details>
    </figure>
  </section>

  <section id="fuel">
    <div class="sec-h"><div class="eyebrow">Fuel</div><h2>Calories and protein</h2>
      <p>Each day's total against the target ({{KCAL_T}} kcal · {{PROT_T}} g protein). Today is drawn hollow until it is closed and left out of the averages.</p></div>
    <div class="stats" id="kcal-stats"></div>
    <figure>
      <div class="plot" id="kcal-plot"></div>
      <div class="tip" id="kcal-tip"></div>
      <figcaption>Calories, kcal per day</figcaption>
    </figure>
    <div class="stats" id="prot-stats" style="margin-top:18px"></div>
    <figure>
      <div class="plot" id="prot-plot"></div>
      <div class="tip" id="prot-tip"></div>
      <figcaption>Protein, g per day</figcaption>
      <details class="twin"><summary>Table</summary><div class="scroll" id="fuel-table"></div></details>
    </figure>
  </section>

  <section id="measured">
    <div class="sec-h"><div class="eyebrow">Measured</div><h2>Latest clinic numbers</h2>
      <p>The newest value per side, and the limb symmetry index (left as a share of right). The line under each metric is its history.</p></div>
    {{MEASURED}}
  </section>
  </div>

  <div id="tab-days" role="tabpanel" hidden>
    <section id="month">
      <div class="sec-h"><div class="eyebrow">The month</div><h2>What each day carried</h2>
        <p>One colour and one place per kind. Circles are training and the clinic; squares are recovery. A cell without a fill was not logged. Tap a day to see it below.</p></div>
      <div class="chips" id="m-summary"></div>
      <div class="mgrid" id="m-grid"></div>
      <div class="legend" id="m-legend"></div>
    </section>
    <section id="dayview">
      <div class="sec-h"><div class="eyebrow">Selected day</div></div>
      <div id="m-day"></div>
    </section>
  </div>

  <noscript><section><div class="sec-h"><div class="eyebrow">This week</div><h2>The week's table</h2><p>The charts and the day view need JavaScript; the week's rows are here.</p></div>{{WEEK_TABLE}}</section></noscript>

  <footer class="foot">
    <span>{{COVERAGE}}</span>
    <span>{{FOOD_MIX}}</span>
    <span>From the logs only, through the engine (<code>python3 engine/report.py</code>, run when you ask for it). Built {{GENERATED}}.</span>
  </footer>
</div>

<script type="application/json" id="data">{{DATA}}</script>
<script>
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var D = DATA.days;
  var W = DATA.weeks;
  var T = DATA.targets;
  var ASOF = DATA.asof;
  var OPEN = !DATA.today_closed;
  var DOWS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  var GRADES = ['0', 'trace', '1+', '2+', '3+'];
  var SVG = 'http://www.w3.org/2000/svg';
  var FAMS = [['knee', 'Knee'], ['upper', 'Upper'], ['cond', 'Cond.'], ['sport', 'Sport'], ['pt', 'PT'], ['accessory', 'Access.'], ['power', 'Power']];

  // ---- small helpers
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function svg(tag, attrs, parent) { var e = document.createElementNS(SVG, tag); for (var k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }
  function stext(parent, x, y, str, cls, anchor) { var t = svg('text', { x: x, y: y, 'text-anchor': anchor || 'start' }, parent); if (cls) t.setAttribute('class', cls); t.textContent = str; return t; }
  function md(iso) { var p = iso.split('-'); return (+p[1]) + '/' + (+p[2]); }
  function dowmd(iso) { var i = D.length ? indexOf(iso) : -1; return (i >= 0 ? D[i].dow : DOWS[new Date(iso + 'T12:00:00').getDay()]) + ' ' + md(iso); }
  var INDEX = {}; D.forEach(function (r, i) { INDEX[r.date] = i; });
  function indexOf(iso) { return INDEX[iso] == null ? -1 : INDEX[iso]; }
  function fmtInt(n) { return n == null ? '–' : Math.round(n).toLocaleString('en-US'); }
  function fmt1(n) { return n == null ? '–' : (Math.round(n * 10) / 10).toFixed(1); }
  function signed(n, dec) { if (n == null) return '–'; var s = dec ? fmt1(Math.abs(n)) : fmtInt(Math.abs(n)); return (n > 0 ? '+' : n < 0 ? '−' : '±') + s; }
  function compact(n) { return n >= 1000 ? (n / 1000).toFixed(n % 1000 ? 1 : 0) + 'K' : String(n); }
  function mean(a) { return a.length ? a.reduce(function (s, v) { return s + v; }, 0) / a.length : null; }
  function isOpen(r) { return r.date === ASOF && OPEN; }
  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { } }
  function load(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function niceStep(range, count) { var rough = range / Math.max(1, count); var p = Math.pow(10, Math.floor(Math.log(rough) / Math.LN10)); var r = rough / p; return (r >= 5 ? 10 : r >= 2 ? 5 : r >= 1 ? 2 : 1) * p; }
  function ticks(lo, hi, count) { var st = niceStep(hi - lo, count), out = []; for (var v = Math.ceil(lo / st) * st; v <= hi + 1e-9; v += st) out.push(+v.toFixed(6)); return out; }
  function table(container, head, rows, curRow) {
    var t = el('table', 'plain'), th = el('thead'), tr = el('tr');
    head.forEach(function (h) { var c = el('th', typeof h === 'object' ? h.cls : '', typeof h === 'object' ? h.t : h); tr.appendChild(c); });
    th.appendChild(tr); t.appendChild(th);
    var tb = el('tbody');
    rows.forEach(function (r, i) {
      var row = el('tr', curRow === i ? 'cur' : '');
      r.forEach(function (v, j) { row.appendChild(el('td', typeof head[j] === 'object' ? head[j].cls : '', v == null ? '' : String(v))); });
      tb.appendChild(row);
    });
    t.appendChild(tb); container.replaceChildren(t);
  }
  function stat(k, v, small, d, flag) {
    var s = el('div', 'stat'); s.appendChild(el('div', 'k', k));
    var vv = el('div', 'v', v); if (small) vv.appendChild(el('small', '', small)); s.appendChild(vv);
    if (d) s.appendChild(el('div', 'd', d));
    if (flag) s.appendChild(flag);
    return s;
  }
  function flagEl(kind, text) {
    var f = el('span', 'flag ' + kind);
    var ic = svg('svg', { viewBox: '0 0 12 12', 'aria-hidden': 'true' });
    if (kind === 'good') svg('path', { d: 'M2 6.5l2.5 2.5L10 3.5', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, ic);
    else svg('path', { d: 'M6 1.5l5 9H1z M6 5v2.6 M6 8.8v.2', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.4', 'stroke-linejoin': 'round' }, ic);
    f.appendChild(ic); f.appendChild(document.createTextNode(text)); return f;
  }

  // ---- range
  var RANGES = { '14': 14, '28': 28, '56': 56, 'all': 0 };
  var range = load('ledger.range') || '28';
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.seg button'));
  buttons.forEach(function (b) {
    var n = RANGES[b.getAttribute('data-range')];
    if (n && n >= D.length && n !== 14) b.hidden = true;  // a range longer than the logs is just "All"
    b.addEventListener('click', function () { range = b.getAttribute('data-range'); store('ledger.range', range); renderAll(); });
  });
  if (!buttons.some(function (b) { return b.getAttribute('data-range') === range && !b.hidden; })) range = 'all';
  function slice() { var n = RANGES[range]; return n ? D.slice(-n) : D; }

  // ---- tooltip (one per figure; tap or hover; arrow keys when the chart has focus)
  function tipOf(id) { return document.getElementById(id); }
  function showTip(tip, fig, x, html_rows, title, note, prefer) {
    tip.replaceChildren();
    tip.appendChild(el('div', 'th', title));
    html_rows.forEach(function (r) { var d = el('div', 'tr'); d.appendChild(el('b', '', r[0])); d.appendChild(el('span', '', r[1])); tip.appendChild(d); });
    if (note) tip.appendChild(el('div', 'tn', note));
    tip.classList.add('on');
    var fw = fig.clientWidth, tw = tip.offsetWidth;
    var left = prefer === 'right' ? x + 12 : x - tw - 12;
    if (left + tw > fw) left = x - tw - 12;
    if (left < 0) left = Math.min(Math.max(0, x + 12), fw - tw);
    tip.style.left = Math.max(0, left) + 'px';
    tip.style.top = '0px';
  }
  function hideTip(tip) { tip.classList.remove('on'); }
  var TIPS = [];
  document.addEventListener('pointerdown', function (e) {
    TIPS.forEach(function (t) { if (!t.fig.contains(e.target)) { hideTip(t.tip); if (t.clear) t.clear(); } });
  });
  function attach(fig, tip, target, n, locate, onIndex, clear) {
    var cur = -1;
    function at(e) {
      var rect = target.getBoundingClientRect();
      var i = locate(e.clientX - rect.left, e.clientY - rect.top, rect);
      if (i == null || i < 0 || i >= n) return;
      cur = i; onIndex(i, e.clientX - fig.getBoundingClientRect().left);
    }
    target.addEventListener('pointerdown', function (e) { at(e); e.preventDefault(); });  // read, never focus: keyboard focus keeps its ring
    target.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse' || e.buttons) at(e); });
    target.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') { hideTip(tip); clear(); cur = -1; } });
    target.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { cur = Math.max(0, Math.min(n - 1, (cur < 0 ? n - 1 : cur) + (e.key === 'ArrowRight' ? 1 : -1))); onIndex(cur, null); e.preventDefault(); }
      if (e.key === 'Escape') { hideTip(tip); clear(); cur = -1; }
    });
    TIPS.push({ fig: fig, tip: tip, clear: clear });
  }

  // ---- shared chart frame: x = days, y = values; Sundays labeled; week boundaries ruled
  function frame(container, days, height, yDomain, opts) {
    opts = opts || {};
    var Wd = Math.max(240, container.clientWidth || 320);
    var m = { t: 12, r: 8, b: 22, l: 8 };
    var s = svg('svg', { viewBox: '0 0 ' + Wd + ' ' + height, width: Wd, height: height, role: 'img', tabindex: '0', 'aria-label': opts.label || '' });
    s.setAttribute('class', 'chart');
    container.replaceChildren(s);
    var n = days.length, pw = Wd - m.l - m.r, slot = pw / n, ph = height - m.t - m.b;
    var y0 = yDomain[0], y1 = yDomain[1];
    function xc(i) { return m.l + slot * (i + 0.5); }
    function y(v) { return m.t + ph * (1 - (v - y0) / (y1 - y0)); }
    var g = svg('g', {}, s);
    var tk = opts.ticks || ticks(y0, y1, 4);
    tk.forEach(function (v) {
      if (v < y0 || v > y1) return;
      svg('line', { x1: m.l, x2: Wd - m.r, y1: y(v), y2: y(v), class: v === y0 ? 'axis' : 'grid' }, g);
      if (v !== y0 || opts.labelZero) stext(g, m.l + 2, y(v) - 3, opts.fmtTick ? opts.fmtTick(v) : String(v), 'halo', 'start');
    });
    var firstSun = -1;
    days.forEach(function (r, i) {
      if (r.dow === 'Sun') {
        if (firstSun < 0) firstSun = i;
        if (i > 0) svg('line', { x1: m.l + slot * i, x2: m.l + slot * i, y1: m.t, y2: height - m.b, class: 'wk' }, g);
        var lbl = slot * 7 >= 110 ? 'Sun ' + md(r.date) : md(r.date);
        if (m.l + slot * i + 50 <= Wd) stext(g, m.l + slot * i + 3, height - 7, lbl, '', 'start');
      }
    });
    if (days[0].dow !== 'Sun' && (firstSun < 0 || firstSun * slot >= 48)) stext(g, m.l + 1, height - 7, md(days[0].date), '', 'start');
    return { svg: s, W: Wd, H: height, m: m, n: n, slot: slot, xc: xc, y: y, base: y(y0), g: g, locate: function (px) { return Math.max(0, Math.min(n - 1, Math.floor((px - m.l) / slot))); } };
  }
  function crosshair(F) { var c = svg('line', { class: 'cross', x1: 0, x2: 0, y1: F.m.t, y2: F.base, visibility: 'hidden' }, F.svg); return { show: function (i) { c.setAttribute('x1', F.xc(i)); c.setAttribute('x2', F.xc(i)); c.setAttribute('visibility', 'visible'); }, hide: function () { c.setAttribute('visibility', 'hidden'); } }; }
  function colPath(x, yTop, yBase, w, r) {
    var h = yBase - yTop; if (h <= 0) return '';
    r = Math.min(r, w / 2, h);
    return 'M' + (x - w / 2) + ' ' + yBase + ' V' + (yTop + r) + ' a' + r + ' ' + r + ' 0 0 1 ' + r + ' -' + r + ' h' + (w - 2 * r) + ' a' + r + ' ' + r + ' 0 0 1 ' + r + ' ' + r + ' V' + yBase + ' Z';
  }

  // ---- streaks: the rate within the range
  function renderStreakRates(days) {
    var counted = days.filter(function (r) { return r.light !== 'red'; });
    ['logged', 'check', 'floorfull', 'creatine', 'food'].forEach(function (k) {
      var slot = document.querySelector('[data-slot="rate-' + k + '"]');
      if (!slot) return;
      var done = counted.filter(function (r) { return r[k]; }).length;
      slot.textContent = done + ' of ' + counted.length + ' days';
    });
  }

  // ---- week score
  function renderWeeks(days) {
    var first = days[0].date;
    var weeks = W.filter(function (w) { return w.through >= first; });
    var fig = document.getElementById('week-plot').parentNode, tip = tipOf('week-tip');
    var cur = W[W.length - 1], prev = W.length > 1 ? W[W.length - 2] : null;
    var stats = document.getElementById('week-stats');
    stats.replaceChildren(
      stat('This week so far', String(cur.score), '/ 100', cur.days + ' of 7 days scored'),
      stat('Last week', prev ? String(prev.score) : '–', prev ? '/ 100' : '', prev ? 'week of ' + md(prev.week_start) : 'no completed week yet'));
    var container = document.getElementById('week-plot');
    var Wd = Math.max(240, container.clientWidth || 320), H = 150, m = { t: 14, r: 8, b: 22, l: 8 };
    var s = svg('svg', { viewBox: '0 0 ' + Wd + ' ' + H, width: Wd, height: H, role: 'img', tabindex: '0', 'aria-label': 'Week score by week' });
    s.setAttribute('class', 'chart'); container.replaceChildren(s);
    var n = weeks.length, slot = (Wd - m.l - m.r) / n, ph = H - m.t - m.b;
    function y(v) { return m.t + ph * (1 - v / 100); }
    [0, 50, 100].forEach(function (v) { svg('line', { x1: m.l, x2: Wd - m.r, y1: y(v), y2: y(v), class: v === 0 ? 'axis' : 'grid' }, s); if (v) stext(s, m.l + 2, y(v) - 3, String(v)); });
    var bw = Math.min(24, slot * 0.6), cols = [];
    weeks.forEach(function (w, i) {
      var x = m.l + slot * (i + 0.5);
      var p = svg('path', { d: colPath(x, y(w.score), y(0), bw, 4), class: 'col' + (w.current ? ' open' : '') }, s);
      cols.push(p);
      if (i === n - 1 || i === n - 2) stext(s, x, y(w.score) - 5, String(w.score), 'ink', 'middle');
      stext(s, x, H - 7, md(w.week_start), '', 'middle');
    });
    function show(i, px) {
      cols.forEach(function (c, j) { c.classList.toggle('hi', j === i); });
      var w = weeks[i], P = w.parts, rows = [[String(w.score), w.current ? 'so far' : 'score']];
      [['floor', 'floor'], ['sessions', 'sessions'], ['fuel', 'fuel'], ['checks', 'checks'], ['weighins', 'weigh-ins'], ['ledger', 'logging']].forEach(function (k) { if (P[k[0]] != null) rows.push([Math.round(P[k[0]] * 100) + '%', k[1]]); });
      showTip(tip, fig, px == null ? m.l + slot * (i + 0.5) : px, rows, 'Week of ' + md(w.week_start) + (w.current ? ' (this week)' : ''), w.excused.length ? w.excused.length + ' rest day(s) excused' : '', i < n / 2 ? 'right' : 'left');
    }
    attach(fig, tip, s, n, function (px) { return Math.max(0, Math.min(n - 1, Math.floor((px - m.l) / slot))); }, show, function () { cols.forEach(function (c) { c.classList.remove('hi'); }); });
    table(document.getElementById('week-table'),
      ['Week', { t: 'Score', cls: 'n' }, { t: 'Floor', cls: 'n' }, { t: 'Sessions', cls: 'n' }, { t: 'Fuel', cls: 'n' }, { t: 'Checks', cls: 'n' }, { t: 'Weigh-ins', cls: 'n' }, { t: 'Logged', cls: 'n' }],
      weeks.map(function (w) {
        var P = w.parts, pl = Object.keys(w.planned).reduce(function (a, k) { return a + w.planned[k]; }, 0), dn = Object.keys(w.done).reduce(function (a, k) { return a + w.done[k]; }, 0);
        return [md(w.week_start) + (w.current ? ' (so far)' : ''), w.score, w.floor_full + '/' + w.days, dn + '/' + pl, P.fuel != null ? Math.round(P.fuel * 100) + '%' : '–', w.checks + '/' + w.days, w.weighins + '/' + T.weighins_per_week, w.logged + '/' + w.days];
      }), weeks.length - 1);
  }

  // ---- the calendar of daily habits
  function habitsOf(r) { return [['check', 'morning check'], ['floorfull', 'heel prop'], ['creatine', 'creatine'], ['food', 'food logged']].filter(function (h) { return r[h[0]]; }).map(function (h) { return h[1]; }); }
  function renderCalendar(days) {
    var plot = document.getElementById('cal-plot'), fig = plot.parentNode, tip = tipOf('cal-tip');
    var grid = el('div', 'cal');
    DOWS.forEach(function (d) { grid.appendChild(el('div', 'dh', d[0])); });
    var lead = DOWS.indexOf(days[0].dow);
    for (var i = 0; i < lead; i++) grid.appendChild(el('div', 'c out'));
    var cells = [];
    days.forEach(function (r, i) {
      var k = habitsOf(r).length;
      var c = el('div', 'c ' + (r.light === 'red' ? 'red' : !r.logged ? 'none' : 'h' + k) + (r.date === ASOF ? ' today' : ''), String(+r.date.slice(8)));
      c.setAttribute('data-i', String(i));
      c.setAttribute('role', 'img');
      c.setAttribute('aria-label', dowmd(r.date) + ': ' + (r.logged ? k + ' of 4' : 'not logged'));
      grid.appendChild(c); cells.push(c);
    });
    plot.replaceChildren(grid);
    function show(i, px) {
      cells.forEach(function (c, j) { c.classList.toggle('hi', j === i); });
      var r = days[i], hs = habitsOf(r);
      var rows = r.logged ? [[hs.length + ' of 4', 'habits']] : [['not logged', '']];
      if (r.light === 'red') rows.unshift(['rest', 'the plan said stop']);
      var cell = cells[i].getBoundingClientRect(), fr = fig.getBoundingClientRect();
      showTip(tip, fig, cell.left - fr.left + cell.width / 2, rows, dowmd(r.date) + (isOpen(r) ? ' · today, open' : ''), hs.length ? hs.join(', ') : (r.logged ? 'none of the four' : ''), (cell.left - fr.left) < fr.width / 2 ? 'right' : 'left');
      tip.style.top = (cell.top - fr.top + cell.height + 6) + 'px';
    }
    attach(fig, tip, grid, days.length, function (x, y) {
      var e = document.elementFromPoint(x + grid.getBoundingClientRect().left, y + grid.getBoundingClientRect().top);
      return e && e.hasAttribute && e.hasAttribute('data-i') ? +e.getAttribute('data-i') : null;
    }, show, function () { cells.forEach(function (c) { c.classList.remove('hi'); }); });
    table(document.getElementById('cal-table'), ['Day', 'Check', 'Heel prop', 'Creatine', 'Food', 'Logged'],
      days.map(function (r) { return [dowmd(r.date), r.check ? '✓' : '', r.floorfull ? '✓' : r.floor === 'half' ? 'half' : '', r.creatine ? '✓' : '', r.food ? '✓' : '', r.logged ? '✓' : r.light === 'red' ? 'rest' : '']; }), days.length - 1);
  }

  // ---- sessions against the plan, by week
  function renderSessions(days) {
    var first = days[0].date;
    var weeks = W.filter(function (w) { return w.through >= first; });
    var planned = 0, done = 0;
    weeks.forEach(function (w) { Object.keys(w.planned).forEach(function (k) { planned += w.planned[k]; done += Math.min(w.did[k] || 0, w.planned[k]); }); });
    var cur = W[W.length - 1], cp = Object.keys(cur.planned).reduce(function (a, k) { return a + cur.planned[k]; }, 0), cd = Object.keys(cur.planned).reduce(function (a, k) { return a + Math.min(cur.did[k] || 0, cur.planned[k]); }, 0);
    document.getElementById('sess-stats').replaceChildren(
      stat('In range', done + ' of ' + planned, '', 'planned sessions done'),
      stat('This week', cd + ' of ' + cp, '', 'through ' + dowmd(cur.through)));
    var fams = FAMS.filter(function (f) { return weeks.some(function (w) { return (w.planned[f[0]] || 0) + (w.did[f[0]] || 0) > 0; }); });
    var t = el('table', 'sessions'), th = el('thead'), tr = el('tr');
    tr.appendChild(el('th', 'fam', ''));
    weeks.forEach(function (w) { var c = el('th', '', w.current ? 'this wk' : md(w.week_start)); c.style.textAlign = 'center'; tr.appendChild(c); });
    th.appendChild(tr); t.appendChild(th);
    var tb = el('tbody');
    fams.forEach(function (f) {
      var row = el('tr'); var h = el('th', 'fam', f[1]); h.setAttribute('scope', 'row'); row.appendChild(h);
      weeks.forEach(function (w) {
        var p = w.planned[f[0]] || 0, d = w.did[f[0]] || 0, td = el('td');
        if (!p && !d) { td.appendChild(el('span', 'muted', '–')); row.appendChild(td); return; }
        var pips = el('div', 'pips');
        for (var i = 0; i < Math.max(p, d); i++) pips.appendChild(el('i', i < Math.min(p, d) ? '' : i < p ? 'open' : 'extra'));
        td.appendChild(pips);
        td.appendChild(el('span', 'cnt', p ? d + '/' + p : d + ' done'));
        td.setAttribute('aria-label', f[1] + ', week of ' + md(w.week_start) + ': ' + d + ' of ' + p);
        row.appendChild(td);
      });
      tb.appendChild(row);
    });
    t.appendChild(tb);
    var box = document.getElementById('sess-grid');
    box.replaceChildren(t);
    box.scrollLeft = box.scrollWidth;  // the current week first; earlier weeks by scrolling left
  }

  // ---- the knee: swelling and pain, as strips
  function renderKnee(days) {
    var plot = document.getElementById('knee-plot'), fig = plot.parentNode, tip = tipOf('knee-tip');
    var graded = days.filter(function (r) { return r.swelling != null; });
    var last = graded.length ? graded[graded.length - 1] : null;
    var run = 0; for (var i = days.length - 1; i >= 0; i--) { var r = days[i]; if (r.swelling == null) { if (r.date === ASOF && OPEN) continue; break; } if (GRADES.indexOf(r.swelling) <= 1) run++; else break; }
    var pains = days.filter(function (r) { return r.pain != null; }), zero = pains.filter(function (r) { return r.pain === 0; }).length;
    var lastPain = pains.length ? pains[pains.length - 1] : null;
    document.getElementById('knee-stats').replaceChildren(
      stat('Swelling', last ? last.swelling : '–', last ? dowmd(last.date) : 'not graded', graded.length + ' of ' + days.length + ' mornings graded' + (run > 1 ? ' · ' + run + ' in a row at trace or less' : '')),
      stat('Morning pain', lastPain ? (lastPain.pain_text || String(lastPain.pain)) : '–', lastPain ? dowmd(lastPain.date) : 'not recorded', pains.length ? '0 on ' + zero + ' of ' + pains.length + ' mornings' : 'no readings in range'));
    var wrap = el('div', 'rows'), n = days.length, cols = 'repeat(' + n + ', minmax(0, 1fr))';
    function row(label, cls) { var rw = el('div', 'row'); rw.appendChild(el('div', 'rl', label)); var cells = el('div', 'cells ' + (cls || '')); cells.style.gridTemplateColumns = cols; rw.appendChild(cells); wrap.appendChild(rw); return cells; }
    var sw = row('Swelling'), pn = row('Pain'), swc = [], pnc = [];
    days.forEach(function (r, i) {
      var g = r.swelling == null ? 'none' : 'g' + GRADES.indexOf(r.swelling);
      var a = el('i', g); a.setAttribute('data-i', String(i)); sw.appendChild(a); swc.push(a);
      var pc = r.pain == null ? (r.pain_text ? 'text' : 'none') : 'g' + Math.min(4, Math.ceil(r.pain));
      var b = el('i', pc); b.setAttribute('data-i', String(i)); pn.appendChild(b); pnc.push(b);
    });
    var xl = el('div', 'row'); xl.appendChild(el('div', 'rl', '')); var xs = el('div', 'xlab'); xs.style.gridTemplateColumns = cols;
    days.forEach(function (r, i) { var s = el('span', '', r.dow === 'Sun' && (n - i) * (1 / n) * 300 > 36 ? md(r.date) : ''); xs.appendChild(s); });
    xl.appendChild(xs); wrap.appendChild(xl);
    plot.replaceChildren(wrap);
    var legend = document.getElementById('knee-legend'); legend.replaceChildren();
    GRADES.forEach(function (g, i) { var s = el('span'); var sw2 = el('i'); sw2.style.background = 'var(--seq-' + i + ')'; s.appendChild(sw2); s.appendChild(document.createTextNode(g)); legend.appendChild(s); });
    var ng = el('span'); ng.appendChild(el('i', 'none')); ng.appendChild(document.createTextNode('not graded')); legend.appendChild(ng);
    var pl = el('span'); pl.appendChild(document.createTextNode('pain: 0 lightest, 4+ darkest')); legend.appendChild(pl);
    function show(i, px) {
      swc.forEach(function (c, j) { c.classList.toggle('hi', j === i); }); pnc.forEach(function (c, j) { c.classList.toggle('hi', j === i); });
      var r = days[i], rows = [[r.swelling == null ? 'not graded' : r.swelling, 'swelling'], [r.pain != null ? String(r.pain) : (r.pain_text || '–'), 'pain']];
      if (r.trend) rows.push([r.trend, 'vs yesterday']);
      if (r.catch) rows.push([r.catch.length > 26 ? r.catch.slice(0, 26) + '…' : r.catch, 'catch']);
      var cell = swc[i].getBoundingClientRect(), fr = fig.getBoundingClientRect();
      showTip(tip, fig, cell.left - fr.left + cell.width / 2, rows, dowmd(r.date), r.light === 'red' ? 'rest day' : '', i < n / 2 ? 'right' : 'left');
      tip.style.top = (pn.getBoundingClientRect().bottom - fr.top + 6) + 'px';
    }
    attach(fig, tip, wrap, n, function (x) { var rect = sw.getBoundingClientRect(), wr = wrap.getBoundingClientRect(); return Math.floor((x + wr.left - rect.left) / rect.width * n); }, show, function () { swc.concat(pnc).forEach(function (c) { c.classList.remove('hi'); }); });
    table(document.getElementById('knee-table'), ['Day', 'Swelling', 'Pain', 'Trend', 'Catch'],
      days.map(function (r) { return [dowmd(r.date), r.swelling == null ? '' : r.swelling, r.pain_text, r.trend, r.catch]; }), days.length - 1);
  }

  // ---- weight: dots and the 7-day average
  var ROLL = D.map(function (r, i) { var w = []; for (var j = Math.max(0, i - 6); j <= i; j++) if (D[j].weight != null) w.push(D[j].weight); return w.length >= 2 ? mean(w) : null; });
  function renderWeight(days) {
    var plot = document.getElementById('weight-plot'), fig = plot.parentNode, tip = tipOf('weight-tip');
    var off = indexOf(days[0].date);
    var pts = days.filter(function (r) { return r.weight != null; });
    var last = pts.length ? pts[pts.length - 1] : null;
    var n = D.length, now7 = ROLL[n - 1], before = n > 7 ? ROLL[n - 8] : null;
    var flag = null;
    if (now7 != null && before != null) { var dlt = now7 - before; flag = dlt < 0 ? flagEl('warn', 'falling ' + fmt1(Math.abs(dlt)) + ' lb vs the prior 7 days') : flagEl('good', signed(dlt, true) + ' lb vs the prior 7 days'); }
    document.getElementById('weight-stats').replaceChildren(
      stat('Latest', last ? fmt1(last.weight) : '–', last ? 'lb' : '', last ? dowmd(last.date) : 'no weigh-in in range'),
      stat('7-day average', now7 != null ? fmt1(now7) : '–', now7 != null ? 'lb' : '', null, flag));
    var vals = pts.map(function (r) { return r.weight; }).concat(days.map(function (r, i) { return ROLL[off + i]; }).filter(function (v) { return v != null; }));
    if (!vals.length) { plot.replaceChildren(el('p', 'muted', 'No weigh-ins in this range.')); document.getElementById('weight-table').replaceChildren(); return; }
    var lo = Math.floor(Math.min.apply(null, vals) - 1), hi = Math.ceil(Math.max.apply(null, vals) + 1);
    var F = frame(plot, days, 190, [lo, hi], { label: 'Weight by day', ticks: ticks(lo, hi, 4), fmtTick: function (v) { return v + ' lb'; } });
    var d = '', pen = false, lastRoll = null;
    days.forEach(function (r, i) { var v = ROLL[off + i]; if (v == null) { pen = false; return; } d += (pen ? ' L' : ' M') + F.xc(i).toFixed(1) + ' ' + F.y(v).toFixed(1); pen = true; lastRoll = { i: i, v: v }; });
    if (d) svg('path', { d: d.trim(), class: 'line' }, F.g);
    var dots = [];
    days.forEach(function (r, i) { if (r.weight != null) dots.push(svg('circle', { cx: F.xc(i), cy: F.y(r.weight), r: 4, class: 'dot' }, F.g)); else dots.push(null); });
    if (lastRoll) {
      var ex = F.xc(lastRoll.i), ey = F.y(lastRoll.v);
      svg('circle', { cx: ex, cy: ey, r: 4, class: 'end' }, F.g);
      stext(F.g, ex + 20 > F.W - F.m.r ? ex + 4 : ex, ey - 9, fmt1(lastRoll.v), 'ink halo', ex + 20 > F.W - F.m.r ? 'end' : 'middle');
    }
    var ch = crosshair(F);
    function show(i, px) {
      ch.show(i); dots.forEach(function (c, j) { if (c) c.classList.toggle('hi', j === i); });
      var r = days[i], v = ROLL[off + i], rows = [];
      if (r.weight != null) rows.push([fmt1(r.weight) + ' lb', 'weigh-in']); else rows.push(['no weigh-in', '']);
      if (v != null) rows.push([fmt1(v) + ' lb', '7-day average']);
      showTip(tip, fig, px == null ? F.xc(i) : px, rows, dowmd(r.date), '', i < F.n / 2 ? 'right' : 'left');
    }
    attach(fig, tip, F.svg, F.n, F.locate, show, function () { ch.hide(); dots.forEach(function (c) { if (c) c.classList.remove('hi'); }); });
    table(document.getElementById('weight-table'), ['Day', { t: 'Weigh-in', cls: 'n' }, { t: '7-day avg', cls: 'n' }],
      days.map(function (r, i) { return [dowmd(r.date), r.weight != null ? fmt1(r.weight) : '', ROLL[off + i] != null ? fmt1(ROLL[off + i]) : '']; }), days.length - 1);
  }

  // ---- fuel: columns against the target
  function last7(key) {
    var settled = D.filter(function (r) { return !isOpen(r); });
    var a = settled.slice(-7).filter(function (r) { return r[key] != null; }).map(function (r) { return r[key]; });
    var b = settled.slice(-14, -7).filter(function (r) { return r[key] != null; }).map(function (r) { return r[key]; });
    return { now: mean(a), n: a.length, before: mean(b) };
  }
  function columns(plotId, tipId, days, key, domainTop, target, band, unit, fmtTick) {
    var plot = document.getElementById(plotId), fig = plot.parentNode, tip = tipOf(tipId);
    var F = frame(plot, days, 200, [0, domainTop], { label: key + ' by day', fmtTick: fmtTick });
    if (band) { svg('rect', { x: F.m.l, y: F.y(band[1]), width: F.W - F.m.l - F.m.r, height: F.y(band[0]) - F.y(band[1]), class: 'band' }, F.g); }
    else { svg('line', { x1: F.m.l, x2: F.W - F.m.r, y1: F.y(target), y2: F.y(target), class: 'target' }, F.g); }
    var bw = Math.max(3, Math.min(24, F.slot - 2)), cols = [];
    days.forEach(function (r, i) {
      var v = r[key]; if (v == null) { cols.push(null); return; }
      cols.push(svg('path', { d: colPath(F.xc(i), F.y(Math.min(v, domainTop)), F.base, bw, Math.min(4, bw / 2)), class: 'col' + (isOpen(r) ? ' open' : '') }, F.g));
    });
    if (band) stext(F.g, F.W - F.m.r - 2, F.y(band[1]) - 3, band[0] + '–' + band[1] + ' target', 'ink2 halo', 'end');
    else stext(F.g, F.W - F.m.r - 2, F.y(target) - 4, fmtInt(target) + ' target', 'ink2 halo', 'end');
    var ch = crosshair(F);
    function show(i, px) {
      ch.show(i); cols.forEach(function (c, j) { if (c) c.classList.toggle('hi', j === i); });
      var r = days[i], v = r[key], rows = [];
      if (v == null) rows.push(['not logged', '']); else { rows.push([fmtInt(v) + ' ' + unit, isOpen(r) ? 'so far' : 'total']); rows.push([signed(v - target), 'vs target']); }
      showTip(tip, fig, px == null ? F.xc(i) : px, rows, dowmd(r.date) + (isOpen(r) ? ' · today, open' : ''), '', i < F.n / 2 ? 'right' : 'left');
    }
    attach(fig, tip, F.svg, F.n, F.locate, show, function () { ch.hide(); cols.forEach(function (c) { if (c) c.classList.remove('hi'); }); });
  }
  function renderFuel(days) {
    var settled = days.filter(function (r) { return !isOpen(r); });
    var k7 = last7('kcal'), p7 = last7('protein');
    var kd = settled.filter(function (r) { return r.kcal != null; }), pd = settled.filter(function (r) { return r.protein != null; });
    var kh = kd.filter(function (r) { return r.kcal >= T.kcal; }).length, ph = pd.filter(function (r) { return r.protein >= T.protein_g; }).length;
    document.getElementById('kcal-stats').replaceChildren(
      stat('Calories, last 7 days', k7.now != null ? fmtInt(k7.now) : '–', 'avg', k7.before != null ? signed(k7.now - k7.before) + ' vs the 7 before' : k7.n + ' days with totals'),
      stat('At target', kh + ' of ' + kd.length, 'days', 'in range, today left out'));
    document.getElementById('prot-stats').replaceChildren(
      stat('Protein, last 7 days', p7.now != null ? fmtInt(p7.now) : '–', 'g avg', p7.before != null ? signed(p7.now - p7.before) + ' g vs the 7 before' : p7.n + ' days with totals'),
      stat('At target', ph + ' of ' + pd.length, 'days', T.protein_g + ' g or more'));
    var kmax = Math.max(T.kcal, Math.max.apply(null, days.map(function (r) { return r.kcal || 0; })));
    var pmax = Math.max(T.protein_g_max, Math.max.apply(null, days.map(function (r) { return r.protein || 0; })));
    columns('kcal-plot', 'kcal-tip', days, 'kcal', Math.ceil(kmax * 1.12 / 500) * 500, T.kcal, null, 'kcal', function (v) { return compact(v); });
    columns('prot-plot', 'prot-tip', days, 'protein', Math.ceil(pmax * 1.12 / 50) * 50, T.protein_g, [T.protein_g, T.protein_g_max], 'g', function (v) { return v + ' g'; });
    table(document.getElementById('fuel-table'), ['Day', { t: 'kcal', cls: 'n' }, { t: 'vs target', cls: 'n' }, { t: 'Protein g', cls: 'n' }, { t: 'vs target', cls: 'n' }],
      days.map(function (r) { return [dowmd(r.date) + (isOpen(r) ? ' (open)' : ''), r.kcal != null ? fmtInt(r.kcal) : '', r.kcal != null ? signed(r.kcal - T.kcal) : '', r.protein != null ? fmtInt(r.protein) : '', r.protein != null ? signed(r.protein - T.protein_g) : '']; }), days.length - 1);
  }

  // ---- Days: the month as a grid, and one card per day with everything logged
  // the kinds, in the places they keep in a day's cell (3 x 3; null is an empty place): circles, then the recovery squares
  var KINDS = [['knee', 'Knee', 'o', 'knee'], ['upper', 'Upper', 'o', 'upper'], ['cond', 'Conditioning', 'o', 'conditioning'],
               ['sport', 'Sport (throwing)', 'o', 'throwing'], ['pt', 'PT', 'o', 'PT'], null,
               ['sauna', 'Sauna', 'sq', 'sauna'], ['gr', 'Game Ready', 'sq', 'Game Ready'], ['light', 'Light therapy', 'sq', 'light therapy']];
  var KIND_LIST = KINDS.filter(function (k) { return k; });
  var SHAPE = {}; KIND_LIST.forEach(function (k) { SHAPE[k[0]] = k[2]; });
  function adjKind(a) { return /sauna/i.test(a) ? 'sauna' : /game ?ready|go ready/i.test(a) ? 'gr' : /lllt|laser|red light|light therap/i.test(a) ? 'light' : null; }
  function mark(kind) { return el('i', 'mk ' + (SHAPE[kind] === 'sq' ? 'sq ' : '') + kind); }
  var PLAN_NAMES = { knee: 'knee session', kneeA: 'knee Session A', kneeB: 'knee Session B', upper: 'upper session', upperA: 'Upper A', upperB: 'Upper B', cond: 'conditioning', pt: 'PT visit', sport: 'sport session', accessory: 'accessory', power: 'power' };
  var ADDON_NAMES = { upperA: 'Upper A', upperB: 'Upper B', accessory: 'accessory', power: 'power & mobility', arms: 'arms' };
  var SESSION_LABELS = { home: 'Knee (home)', knee: 'Knee', A: 'Session A', B: 'Session B', PT: 'PT', HEP: 'HEP', floor: 'Floor', upperA: 'Upper A', upperB: 'Upper B', accessory: 'Accessory', power: 'Power', arms: 'Arms', conditioning: 'Conditioning' };
  var MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var DETAIL = DATA.detail || {};
  function catsOf(r) {
    var c = { knee: !!(r.knee || r.knee_partial), upper: r.addons.length > 0, cond: r.cond_min > 0, sport: r.sport > 0 || r.sport_min != null, pt: !!r.pt, sauna: false, gr: false, light: false };
    r.adjunct_list.forEach(function (a) { var k = adjKind(a); if (k) c[k] = true; });
    return c;
  }
  var MONTHS = (function () { var seen = {}; D.forEach(function (r) { seen[r.date.slice(0, 7)] = true; }); return Object.keys(seen).sort(); })();
  var month = load('ledger.month'); if (MONTHS.indexOf(month) < 0) month = MONTHS[MONTHS.length - 1];
  function monthLabel(ym) { var p = ym.split('-'); return MONTH_NAMES[+p[1] - 1] + ' ' + p[0]; }
  function stepMonth(by) { var i = MONTHS.indexOf(month) + by; if (i < 0 || i >= MONTHS.length) return; month = MONTHS[i]; store('ledger.month', month); renderDays(); }
  document.getElementById('m-prev').addEventListener('click', function () { stepMonth(-1); });
  document.getElementById('m-next').addEventListener('click', function () { stepMonth(1); });
  function chip(text, kind, quiet) { var c = el('span', 'chip' + (quiet ? ' q' : '')); if (kind) c.appendChild(mark(kind)); c.appendChild(document.createTextNode(text)); return c; }
  function mins(v) { var n = parseFloat(v); return isNaN(n) ? '' : ' ' + (n % 1 ? n : Math.round(n)) + ' min'; }
  function rpe(v) { return v ? ' · RPE ' + v : ''; }
  var selDay = load('ledger.day');
  function selectDay(iso, scroll) {
    selDay = iso; store('ledger.day', iso);
    if (iso.slice(0, 7) !== month) { month = iso.slice(0, 7); store('ledger.month', month); }
    renderDays();
    if (scroll) { var view = document.getElementById('dayview'); if (view) view.scrollIntoView({ block: 'start' }); }
  }
  function renderDays() {
    var days = D.filter(function (r) { return r.date.slice(0, 7) === month; });
    var mi = MONTHS.indexOf(month);
    document.getElementById('m-label').textContent = monthLabel(month);
    document.getElementById('m-prev').disabled = mi <= 0;
    document.getElementById('m-next').disabled = mi >= MONTHS.length - 1;
    if (!selDay || selDay.slice(0, 7) !== month || INDEX[selDay] == null) selDay = ASOF.slice(0, 7) === month ? ASOF : days[days.length - 1].date;
    var logged = days.filter(function (r) { return r.logged; }).length, counts = {};
    KIND_LIST.forEach(function (k) { counts[k[0]] = 0; });
    days.forEach(function (r) { var c = catsOf(r); KIND_LIST.forEach(function (k) { if (c[k[0]]) counts[k[0]]++; }); });
    var sum = document.getElementById('m-summary'); sum.replaceChildren();
    sum.appendChild(chip(logged + ' of ' + days.length + ' day' + (days.length === 1 ? '' : 's') + ' logged', null, true));
    KIND_LIST.forEach(function (k) { if (counts[k[0]]) sum.appendChild(chip(k[3] + ' ' + counts[k[0]], k[0])); });
    var grid = document.getElementById('m-grid'); grid.replaceChildren();
    DOWS.forEach(function (d) { grid.appendChild(el('div', 'dh', d[0])); });
    var p = month.split('-'), y = +p[0], m = +p[1];
    var lead = new Date(y, m - 1, 1).getDay(), n = new Date(y, m, 0).getDate();
    for (var i = 0; i < lead; i++) grid.appendChild(el('div', 'mc out'));
    for (var d = 1; d <= n; d++) {
      var iso = month + '-' + (d < 10 ? '0' : '') + d, r = D[INDEX[iso]];
      if (!r) { grid.appendChild(el('div', 'mc out', String(d))); continue; }
      var cell = el('button', 'mc' + (r.light === 'red' ? ' red' : !r.logged ? ' none' : '') + (r.date === ASOF ? ' today' : '') + (r.date === selDay ? ' sel' : ''));
      cell.type = 'button'; cell.appendChild(el('span', 'dn', String(d)));
      var c = catsOf(r), marks = el('span', 'marks'), on = [];
      KINDS.forEach(function (k) { if (k && c[k[0]]) { marks.appendChild(mark(k[0])); on.push(k[1]); } else marks.appendChild(el('i', 'mk')); });
      cell.appendChild(marks);
      cell.setAttribute('aria-label', dowmd(r.date) + ': ' + (r.logged ? (on.join(', ') || 'no session') : 'not logged'));
      cell.setAttribute('aria-pressed', r.date === selDay ? 'true' : 'false');
      cell.addEventListener('click', (function (iso) { return function () { selectDay(iso, true); }; })(iso));
      grid.appendChild(cell);
    }
    var legend = document.getElementById('m-legend'); legend.replaceChildren();
    KIND_LIST.forEach(function (k) { var s = el('span'); s.appendChild(mark(k[0])); s.appendChild(document.createTextNode(k[1] + (k[0] === 'light' ? ' (LLLT, red light)' : ''))); legend.appendChild(s); });
    document.getElementById('m-day').replaceChildren(dayCard(D[INDEX[selDay]]));
  }
  function dayCard(r) {
    var a = el('article', 'day'); a.id = 'd-' + r.date;
    var h = el('header'), top = el('div', 'dh1'), meta = el('div', 'dh2');
    top.appendChild(el('b', '', dowmd(r.date)));
    var nav = el('div', 'dnav'), i = INDEX[r.date];
    var prev = el('button', '', '‹'), next = el('button', '', '›');
    prev.type = next.type = 'button'; prev.setAttribute('aria-label', 'The day before'); next.setAttribute('aria-label', 'The day after');
    prev.disabled = i <= 0; next.disabled = i >= D.length - 1;
    prev.addEventListener('click', function () { selectDay(D[i - 1].date, false); });
    next.addEventListener('click', function () { selectDay(D[i + 1].date, false); });
    nav.appendChild(prev); nav.appendChild(next); top.appendChild(nav);
    var plan = r.planned.map(function (p) { return PLAN_NAMES[p] || p; }).join(', ');
    meta.appendChild(el('span', 'muted', 'POD ' + r.pod + (plan ? ' · plan: ' + plan : ' · no session planned')));
    if (r.date === ASOF) meta.appendChild(el('span', 'tag', OPEN ? 'today, open' : 'today'));
    if (r.light === 'red') meta.appendChild(el('span', 'tag', 'rest day, by the plan')); else if (r.light === 'yellow') meta.appendChild(el('span', 'tag', 'yellow'));
    h.appendChild(top); h.appendChild(meta); a.appendChild(h);
    if (!r.logged) { a.appendChild(el('p', 'muted', 'Nothing logged.')); return a; }
    var dt = DETAIL[r.date] || { ex: [], sport: [], food: [], food_notes: '', measured: [], tasks: [] };
    var chips = el('div', 'chips');
    if (r.swelling != null) chips.appendChild(chip('check ' + r.swelling, null, true));
    else if (r.pain_text || r.trend || r.am_notes || r.am_extension) chips.appendChild(chip('check, not graded', null, true));
    if (r.floor === 'full') chips.appendChild(chip('heel prop', null, true)); else if (r.floor === 'half') chips.appendChild(chip('heel prop, one round', null, true));
    if (r.creatine) chips.appendChild(chip('creatine', null, true));
    if (r.weight != null) chips.appendChild(chip(fmt1(r.weight) + ' lb', null, true));
    if (r.kcal != null) chips.appendChild(chip(fmtInt(r.kcal) + ' kcal · ' + fmtInt(r.protein) + ' g', null, true));
    if (r.knee) chips.appendChild(chip('knee ' + r.knee + mins(r.knee_min) + rpe(r.knee_rpe) + (r.knee_as_planned === 'Y' ? ' · as written' : r.knee_as_planned === 'N' ? ' · changed' : ''), 'knee'));
    else if (r.knee_partial) chips.appendChild(chip('knee, partial' + mins(r.knee_min), 'knee'));
    r.addons.forEach(function (ad) { chips.appendChild(chip((ADDON_NAMES[ad] || ad) + mins(r.addon_min) + rpe(r.addon_rpe), 'upper')); });
    if (r.cond_min > 0) chips.appendChild(chip((r.cond_type || 'conditioning') + mins(r.cond_min), 'cond'));
    if (r.sport > 0 || r.sport_min != null) chips.appendChild(chip((r.sport_sessions.indexOf('FILM') >= 0 && r.sport_sessions.length === 1 ? 'film' : 'throwing') + (r.sport_sessions.length ? ' ' + r.sport_sessions.join('+') : '') + mins(r.sport_min) + (r.sport_skills.length ? ' · ' + r.sport_skills.join(', ') : ''), 'sport'));
    if (r.pt) chips.appendChild(chip('PT visit', 'pt'));
    if (r.pt_missed) chips.appendChild(chip('PT visit missed', null, true));
    r.adjunct_list.forEach(function (ad) { var k = adjKind(ad); chips.appendChild(chip(ad, k, !k)); });
    if (r.together) chips.appendChild(chip('together', null, true));
    dt.tasks.forEach(function (t) { chips.appendChild(chip(t.task === 'finished' ? 'project finished: ' + t.project : 'task done: ' + t.task, null, true)); });
    if (dt.measured.length) chips.appendChild(chip('measured', null, true));
    a.appendChild(chips);
    var det = el('details', 'more'), body = el('div', 'det');
    det.open = true;  // the one card on the page: its details are the point
    det.appendChild(el('summary', '', 'Details'));
    function line(k, v) { if (!v) return; var dl = el('div', 'dl'); dl.appendChild(el('span', 'k', k)); var vv = el('span', 'v'); if (typeof v === 'string') vv.textContent = v; else vv.appendChild(v); dl.appendChild(vv); body.appendChild(dl); }
    var morning = ['swelling ' + (r.swelling == null ? 'not graded' : r.swelling)];
    if (r.trend) morning.push('trend ' + r.trend); if (r.pain_text) morning.push('pain ' + r.pain_text);
    if (r.am_extension) morning.push('extension ' + r.am_extension); if (r.flexion) morning.push('flexion ' + r.flexion);
    if (r.catch) morning.push('catch ' + r.catch); if (r.wellness != null) morning.push('wellness ' + r.wellness + '/5');
    if (r.am_notes) morning.push('"' + r.am_notes + '"');
    if (morning.length > 1 || r.swelling != null) line('Morning', morning.join(' · '));
    var groups = [], byKey = {};
    dt.ex.forEach(function (x) { var k = x.session || 'other'; if (!byKey[k]) { byKey[k] = []; groups.push(k); } byKey[k].push(x); });
    groups.forEach(function (k) {
      var ul = el('ul');
      byKey[k].forEach(function (x) {
        var li = el('li', /^\s*(not done|skipped)/i.test(x.notes) ? 'nd' : ''), parts = [x.exercise];
        if (x.side) parts.push(x.side);
        if (x.sets && x.reps) parts.push(x.sets + ' × ' + x.reps); else if (x.sets && x.sets !== '1') parts.push(x.sets + ' sets'); else if (x.reps) parts.push(x.reps + ' reps');
        if (x.hold_or_duration) parts.push(x.hold_or_duration);
        if (x.load_or_band) parts.push(x.load_or_band);
        if (x.assist) parts.push('assist: ' + x.assist);
        li.textContent = parts.join(' · ');
        if (x.notes) li.appendChild(el('small', '', x.notes));
        ul.appendChild(li);
      });
      line(SESSION_LABELS[k] || k, ul);
    });
    if (dt.sport.length) {
      var su = el('ul');
      dt.sport.forEach(function (s) {
        var parts = [s.skill + (s.drill ? ': ' + s.drill : '')];
        if (s.sets && s.reps) parts.push(s.sets + ' × ' + s.reps); else if (s.reps) parts.push(s.reps + ' reps');
        if (s.minutes) parts.push(s.minutes + ' min'); if (s.rpe) parts.push('RPE ' + s.rpe);
        if (s.metric) parts.push(s.metric + (s.value ? ' ' + s.value : ''));
        var li = el('li', '', parts.join(' · ')); if (s.notes) li.appendChild(el('small', '', s.notes)); su.appendChild(li);
      });
      line('Throwing', su);
    }
    if (dt.food.length) {
      var fu = el('ul'), meals = [], byMeal = {};
      dt.food.forEach(function (f) { var k = f.meal || 'food'; if (!byMeal[k]) { byMeal[k] = []; meals.push(k); } byMeal[k].push(f); });
      meals.forEach(function (k) {
        fu.appendChild(el('li', 'gk', k));
        byMeal[k].forEach(function (f) {
          fu.appendChild(el('li', '', f.item + (f.qty ? ' (' + f.qty + ')' : '') + (f.kcal ? ' · ' + fmtInt(+f.kcal) + ' kcal' : '') + (f.protein_g ? ' · ' + fmtInt(+f.protein_g) + ' g' : '') + (/estimate|photo/i.test(f.source) ? ' · est.' : '')));
        });
      });
      line('Food', fu);
    }
    if (dt.food_notes) line(dt.food.length ? 'Food note' : 'Food', dt.food_notes);
    var pain = []; if (r.pain_session) pain.push('in session ' + r.pain_session); if (r.pain_pm) pain.push('evening ' + r.pain_pm);
    line('Pain', pain.join(' · '));
    var feet = []; if (r.hours_on_feet) feet.push('on feet: ' + r.hours_on_feet); if (r.crutches) feet.push('crutches: ' + r.crutches); if (r.gait_notes) feet.push('gait: ' + r.gait_notes);
    line('On feet', feet.join(' · '));
    line('Adjuncts', r.adjuncts);
    if (r.sleep_h) line('Sleep', r.sleep_h + ' h');
    if (dt.measured.length) line('Measured', dt.measured.join(' · '));
    if (dt.tasks.length) line('Project', dt.tasks.map(function (t) { return t.project + ' · ' + t.task; }).join(' · '));
    if (r.missed.length) line(r.date === ASOF && OPEN ? 'Still open' : 'Not done', r.missed.join(', '));
    line('Notes', r.notes);
    if (r.closed) line('Ledger', 'day closed');
    det.appendChild(body); a.appendChild(det);
    return a;
  }

  // ---- the two views
  var TABS = Array.prototype.slice.call(document.querySelectorAll('.tabs button'));
  var tab = (location.hash === '#days' || location.hash === '#trends') ? location.hash.slice(1) : (load('ledger.tab') || 'trends');
  function showTab(name, byTap) {
    tab = name; store('ledger.tab', name);
    TABS.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-tab') === name ? 'true' : 'false'); });
    document.getElementById('tab-trends').hidden = name !== 'trends';
    document.getElementById('tab-days').hidden = name !== 'days';
    document.getElementById('range-row').hidden = name !== 'trends';
    document.getElementById('month-row').hidden = name !== 'days';
    if (byTap) { try { history.replaceState(null, '', '#' + name); } catch (e) { } window.scrollTo(0, 0); }
    if (name === 'trends') renderAll(); else renderDays();
  }
  TABS.forEach(function (b) { b.addEventListener('click', function () { showTab(b.getAttribute('data-tab'), true); }); });

  // ---- all together
  function renderAll() {
    var days = slice();
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-range') === range ? 'true' : 'false'); });
    document.getElementById('range-note').textContent = dowmd(days[0].date) + ' – ' + dowmd(days[days.length - 1].date) + ' · ' + days.length + ' days · every chart and count below follows this range.';
    TIPS.length = 0;
    renderStreakRates(days); renderWeeks(days); renderCalendar(days); renderSessions(days); renderKnee(days); renderWeight(days); renderFuel(days);
  }
  var tmr = null, lastW = window.innerWidth;
  window.addEventListener('resize', function () { if (window.innerWidth === lastW) return; lastW = window.innerWidth; clearTimeout(tmr); tmr = setTimeout(function () { if (tab === 'trends') renderAll(); }, 150); });
  showTab(tab, false);
})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", help=f"where to write (default {OUT.relative_to(ROOT)})")
    ap.add_argument("--date", help="render as of this date (default: today, America/New_York)")
    args = ap.parse_args()
    data = collect(E.d(args.date) if args.date else None)
    page = render(data).replace("{{FLOOR_ROUNDS_S}}", "" if data["floor_rounds"] == 1 else "s")
    out = Path(args.out) if args.out else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    cov = data["coverage"]
    print(f"trends: {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} · as of {data['asof']} · "
          f"{cov['logged']}/{cov['days']} days logged · {len(data['weeks'])} weeks · {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
