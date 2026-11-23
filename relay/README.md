# The inbox relay: the ring's sleep, into the Ledger by itself

```
RingConn app ──► Health Connect ──► HC Webhook (phone) ──► relay/worker.js (Cloudflare) ──► GitHub repository_dispatch
                                                                                              │
   a session starts: the hook prints INBOX, Claude asks ◄── real/inbox.json (pending) ◄── .github/workflows/inbox.yml
   "yes" → darrow.py inbox confirm → daily_log.csv sleep_min
```

Health Connect lives only on the phone, so an app there has to send the data out. HC Webhook does that on a schedule,
but its JSON is fixed and GitHub only takes its own shape, so a small Worker sits between them: it checks a key, sums each
night's stages, and passes the sleep on. The workflow files it with `darrow.py inbox ingest`; nothing is logged until he
says yes in a session.

## One-time set-up (about 20 minutes)

### 1. GitHub: a token the relay can use
github.com → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
- Name `inbox relay`, expiry as long as you like (a year; it stops working when it expires).
- Repository access: **Only select repositories** → this repository.
- Permissions → Repository permissions → **Contents: Read and write** (Metadata: Read-only comes with it).
- Copy the token (`github_pat_…`). It goes into Cloudflare only, never into this repo or a chat.

### 2. Cloudflare: the Worker (free plan)
dash.cloudflare.com (sign up if needed) → **Workers & Pages** → Create → **Create Worker** → name it `inbox-relay` →
Deploy → **Edit code** → replace everything with `relay/worker.js` → Deploy.
Then the Worker's **Settings → Variables and Secrets**:
- `REPO` (Text): `bro2jo/leyenda`
- `GITHUB_TOKEN` (Secret): the token from step 1
- `RELAY_KEY` (Secret): a long random string you make up (a password manager's generator: 32+ characters)

Note the Worker's URL: `https://inbox-relay.<your-subdomain>.workers.dev`.

### 3. The phone: HC Webhook
- Install **HC Webhook** from the Play Store (`com.hcwebhook.app`).
- Give it Health Connect access for **Sleep** only (nothing else is needed), and let it read in the background when asked.
- Add a webhook: the Worker's URL; add a header `X-Relay-Key` with the `RELAY_KEY` value. Format: JSON.
- Data types: **Sleep** only.
- Sync: **Interval, 60 minutes** (or Scheduled at, say, 08:30 and 10:30). Each sync sends only what is new, so
  frequent syncs cost nothing.
- Samsung: Settings → Apps → HC Webhook → Battery → **Unrestricted**, or Android may stop it running in the background.
- RingConn: make sure its Health Connect permissions include Sleep (RingConn → Me/Settings → Health Connect).
  Open RingConn in the morning so the ring syncs; HC Webhook picks up the night on its next run.

### 4. Test it
- In HC Webhook, tap **Sync Now** (the first sync may only start tracking; a manual sync with a time range of the last
  2 days sends the last nights). Its log should show a 2xx from the Worker.
- GitHub → Actions → **inbox**: a run per payload with sleep in it; it commits `real/inbox.json`.
- A test from GitHub's side alone: Actions → inbox → Run workflow, with a payload such as
  `{"sleep":[{"id":"test-1","start":"2026-01-01T04:40:00Z","end":"2026-01-01T12:30:00Z","stages":{"LIGHT":15000,"DEEP":5000,"REM":6000,"AWAKE":2200}}]}`
  (a night long before the logs, so it never mixes with a real one); the next session asks about `sleep-2026-01-01`:
  tell it "that was the test" and it is dismissed (`darrow.py inbox dismiss sleep-2026-01-01`).
- The next session prints `INBOX` at its start and asks.

## When it stops
- Nothing in Actions: the Worker never called GitHub. HC Webhook's log shows the Worker's reply: 401 = the
  `X-Relay-Key` header doesn't match `RELAY_KEY`; 502 "GitHub said 401/403/404" = the token is wrong, expired, lacks
  Contents write, or `REPO` is misspelt.
- An Actions run failed: open it; the "File the payload" step prints what `inbox ingest` said.
- A night that never arrived: RingConn hadn't synced the ring yet, or Android stopped HC Webhook (battery setting).
  He can always just say the minutes, as before.

## What counts
The minutes **asleep** (light + deep + REM; Health Connect's plain "sleeping" too), not the time in bed. A night goes
to the day he woke (the session's middle between 18:00 and 14:00); a session whose middle falls 14:00–18:00 is a nap
and is left out. A night already in the log, or one he answered, is never filed again. Working Rules → `sleep_min`.
