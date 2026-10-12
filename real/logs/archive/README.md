# Imported originals

Logs brought in from the old ACL dashboard (retired 10/12), kept exactly as uploaded. They are history, not working files: nothing writes here except a re-import of the same file (git keeps every version). The working logs are one level up.

| File | Covers | Merged into |
|---|---|---|
| `ACL_Daily_Log.csv` | 9/10–10/12 (uploaded 10/9; replaced by its audited final copy 10/12) | `../daily_log.csv` |

## `ACL_Daily_Log.csv` → `daily_log.csv`

A merge fills only blank fields; it never overwrites what the repo already holds. The exception is a loaded-day correction, made by hand and named in the commit.

| Dashboard column | `daily_log.csv` |
|---|---|
| `weekday`, `pod`, `postop_week`, `dash_week_start` | `dow`, `pod`, `post_op_week`, `dash_week_start` (computed) |
| `swelling_am` | `am_swelling` (the grade only: 0 / trace / 1+ / 2+ / 3+; "not graded" or blank is no grade); descriptors are in `swelling_trend_vs_prev` from 10/10 |
| `swelling_trend_vs_prev` | `am_trend` (trend words; its descriptors to `am_notes` when they say more) |
| `wellness_1to5` | `wellness` (1 = poor, 5 = great; from 10/11) |
| `conditioning_min` | `conditioning_min` (off-day bike minutes, from 10/9) |
| `pain_am`, `pain_session`, `pain_pm` | `am_pain`, `pain_session`, `pain_pm` |
| `extension_L` | `am_extension` (clinic numbers also go to `measurements.csv`) |
| `flexion_L_active`, `flexion_L_passive` | `flexion` ("A / P") |
| `patellar_sticking` | `catch` |
| `crutches`, `gait_notes`, `adjuncts`, `hours_on_feet`, `gym_min_on_feet` | same names |
| `knee_session_min`, `knee_session_rpe` | `knee_min`, `knee_rpe` |
| `session_type` | `knee_session` (A / B / min / partial) and `pt=Y` by hand; the label itself to `notes` |
| `loaded_day` | not stored: Y = a knee session or PT; `N (partial)` = `knee_session=partial` |
| `floor_done` | `floor_am` / `floor_pm` (one Y per heel-prop round) |
| `addon_session` | only sessions that ran (`upperA`, …); "planned - not done" is not a session |
| `body_mass_lb` | `nutrition_log.csv → weight_lb` |
| `notes` | stays here; the narrative is too long for a cell |
