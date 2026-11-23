// The inbox relay (a Cloudflare Worker): HC Webhook on his phone POSTs Health Connect data here; this passes the sleep
// on to GitHub as a repository_dispatch ("health"), and .github/workflows/inbox.yml files it in real/inbox.json as
// pending. It keeps no data and decides nothing: it checks the key, sums each session's stages by type (so the
// payload stays small), and forwards. Set-up: relay/README.md.
//
// Settings -> Variables and Secrets:
//   RELAY_KEY     (secret) a long random string; the same value goes in HC Webhook's header X-Relay-Key
//   GITHUB_TOKEN  (secret) a fine-grained token for this one repository: Contents read and write
//   REPO          (text)   owner/name, e.g. bro2jo/leyenda

export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("POST only", { status: 405 });
    if (!env.RELAY_KEY || request.headers.get("X-Relay-Key") !== env.RELAY_KEY) {
      return new Response("unauthorized", { status: 401 });
    }
    let body;
    try {
      body = await request.json();
    } catch {
      return new Response("not JSON", { status: 400 });
    }

    const sleep = (body.sleep || []).map((s) => {
      const stages = {};
      let first = null;
      for (const st of s.stages || []) {
        let sec = Number(st.duration_seconds);
        if (!Number.isFinite(sec)) sec = (Date.parse(st.end_time) - Date.parse(st.start_time)) / 1000;
        if (Number.isFinite(sec)) stages[String(st.stage)] = (stages[String(st.stage)] || 0) + sec;
        if (st.start_time && (first === null || Date.parse(st.start_time) < Date.parse(first))) first = st.start_time;
      }
      const meta = s.metadata || {};
      const origin = meta.data_origin || meta.dataOrigin || "";
      return {
        id: meta.id || null,
        start: s.start_time || s.session_start_time || first,
        end: s.session_end_time || s.end_time,
        duration_s: s.duration_seconds,
        stages,
        origin: typeof origin === "string" ? origin : origin.packageName || origin.package_name || "",
      };
    });
    const deleted = (body.deleted || [])
      .filter((x) => /sleep/i.test(String(x.type || x.record_type || "")))
      .map((x) => x.id);
    if (!sleep.length && !deleted.length) return new Response("nothing to file", { status: 200 });

    const r = await fetch(`https://api.github.com/repos/${env.REPO}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "inbox-relay",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ event_type: "health", client_payload: { timezone: body.timezone || null, sleep, deleted } }),
    });
    return r.ok
      ? new Response(`filed ${sleep.length} sleep session(s)`, { status: 200 })
      : new Response(`GitHub said ${r.status}: ${await r.text()}`, { status: 502 });
  },
};
