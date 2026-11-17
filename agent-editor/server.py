#!/usr/bin/env python3
"""Agent Editor server (standard library only).

One shared timeline. Agents (real Claude subagents, scripts, anything that can run curl) change it through
POST /api/op. The server checks every operation against the transcript and a few editing rules and says
OK or NO with a reason. The browser UI listens to /api/events and draws every agent's cursor and edits.

Run:  python3 server.py [--port 8780]
"""
import argparse, json, mimetypes, os, queue, re, threading, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get("AGENT_EDITOR_PROJECT") or os.path.join(HERE, "project")
OUT = os.environ.get("AGENT_EDITOR_OUT") or os.path.join(HERE, "out")
MUSIC_ROOT = os.environ.get("MUSIC_ROOT", os.path.join(HERE, "music"))
if not os.path.exists(os.path.join(PROJ, "ingest.json")):
    raise SystemExit("No video prepared yet. Run:  python3 ingest.py YOUR_VIDEO.mp4 --dur 100   (see README.md)")
ING = json.load(open(os.path.join(PROJ, "ingest.json")))
DUR = ING["media"]["duration"]
WORDS = ING["words"]
LOCK = threading.RLock()
SUBS = []
RENDER = {"state": "idle", "frac": 0.0, "file": None, "error": None}
STATE = {}

def new_state():
    return {"t0": time.time(), "seq": 0, "next": 1, "cuts": [], "captions": [], "fx": [], "graphics": [], "music": None,
            "agents": {}, "log": [], "rejections": []}

def load_state():
    try:
        d = json.load(open(os.path.join(PROJ, "state.json")))
        if d.get("log"):
            return d
    except (OSError, ValueError):
        pass
    return None

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def inside_word(t, margin=0.03):
    for w in WORDS:
        if w["t"] + margin < t < w["e"] - margin:
            return w
    return None

def fresh_id(prefix):
    i = STATE["next"]
    STATE["next"] += 1
    return f"{prefix}{i}"

def live(items):
    return [x for x in items if x["status"] == "ok"]

def num(op, key, lo=None, hi=None):
    try:
        v = float(op[key])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"'{key}' must be a number")
    if lo is not None and v < lo or hi is not None and v > hi:
        raise ValueError(f"'{key}' must be between {lo} and {hi}")
    return round(v, 3)

def op_cut(op, agent):
    a, b = num(op, "start", 0, DUR), num(op, "end", 0, DUR)
    if b - a < 0.4:
        raise ValueError("a cut must be at least 0.4 s long")
    for c in live(STATE["cuts"]):
        if a < c["end"] - 0.001 and b > c["start"] + 0.001:
            raise ValueError(f"overlaps {c['id']} ({c['start']}-{c['end']}); each part of the source can be kept once")
    for label, t in (("start", a), ("end", b)):
        w = inside_word(t)
        if w:
            raise ValueError(f"cut {label} {t} lands inside the word '{w['w']}' ({w['t']}-{w['e']}); use {max(0, w['t'] - 0.06):.2f} or {w['e'] + 0.04:.2f}")
    it = {"id": fresh_id("c"), "start": a, "end": b, "agent": agent, "status": "ok", "note": str(op.get("note", ""))[:120]}
    STATE["cuts"].append(it)
    return "cut", it

def op_caption(op, agent):
    a, b = num(op, "start", 0, DUR), num(op, "end", 0, DUR)
    text = str(op.get("text", "")).strip()
    ws = text.split()
    if not 1 <= len(ws) <= 3 or len(text) > 22:
        raise ValueError("a caption is 1 to 3 words and at most 22 characters")
    if not 0.2 <= b - a <= 3.0:
        raise ValueError("a caption lasts 0.2 to 3 s")
    for c in live(STATE["captions"]):
        if a < c["end"] - 0.05 and b > c["start"] + 0.05:
            raise ValueError(f"overlaps caption {c['id']} ('{c['text']}' {c['start']}-{c['end']})")
    spoken = {norm(w["w"]) for w in WORDS if w["e"] > a - 0.35 and w["t"] < b + 0.35}
    missing = [w for w in ws if norm(w) and norm(w) not in spoken]
    if missing:
        raise ValueError(f"words not spoken between {a} and {b}: {missing}; captions come only from the transcript")
    it = {"id": fresh_id("k"), "start": a, "end": b, "text": text, "agent": agent, "status": "ok"}
    STATE["captions"].append(it)
    return "caption", it

def op_fx(op, agent):
    typ = op.get("type")
    if typ not in ("punch_zoom", "blur_in"):
        raise ValueError("type must be punch_zoom or blur_in")
    at = num(op, "at", 0, DUR)
    d = num(op, "dur", 0.3, 2.5) if "dur" in op else (1.2 if typ == "punch_zoom" else 0.3)
    for f in live(STATE["fx"]):
        if at < f["at"] + f["dur"] and at + d > f["at"]:
            raise ValueError(f"overlaps {f['id']} ({f['type']} at {f['at']})")
        if typ == "punch_zoom" and f["type"] == "punch_zoom" and abs(f["at"] - at) < 4:
            raise ValueError(f"punch zooms must be at least 4 s apart ({f['id']} is at {f['at']})")
    it = {"id": fresh_id("f"), "type": typ, "at": at, "dur": d, "agent": agent, "status": "ok"}
    STATE["fx"].append(it)
    return "fx", it

TEMPLATES = ("stat_card", "lower_third", "chapter_title", "highlight")

def op_graphic(op, agent):
    tpl = op.get("template")
    if tpl not in TEMPLATES:
        raise ValueError(f"template must be one of {list(TEMPLATES)}")
    at = num(op, "at", 0, DUR)
    d = num(op, "dur", 1.5, 4.0) if "dur" in op else 2.5
    text = str(op.get("text", "")).strip()
    if not 1 <= len(text) <= 24:
        raise ValueError("text is 1 to 24 characters")
    spoken = {norm(w["w"]) for w in WORDS if w["e"] > at - 2 and w["t"] < at + d + 2}
    missing = [w for w in text.split() if norm(w) and norm(w) not in spoken]
    if missing:
        raise ValueError(f"words not spoken near {at}: {missing}; graphic text comes only from the transcript")
    live_g = live(STATE["graphics"])
    if len(live_g) >= 10:
        raise ValueError("at most 10 graphics in one video")
    for g in live_g:
        if at < g["at"] + g["dur"] + 0.5 and at + d > g["at"] - 0.5:
            raise ValueError(f"too close to {g['id']} ('{g['text']}' at {g['at']}); keep 0.5 s between graphics")
    it = {"id": fresh_id("g"), "template": tpl, "text": text, "at": at, "dur": d, "agent": agent, "status": "ok"}
    STATE["graphics"].append(it)
    return "graphic", it

def op_music(op, agent):
    rel = str(op.get("file", ""))
    path = os.path.realpath(os.path.join(MUSIC_ROOT, rel))
    if not path.startswith(os.path.realpath(MUSIC_ROOT)) or not os.path.isfile(path):
        raise ValueError("file must be a path inside the music library that exists")
    db = num(op, "volume_db", -30, -14)
    STATE["music"] = {"file": rel, "volume_db": db, "agent": agent, "status": "ok", "id": fresh_id("m")}
    return "music", STATE["music"]

def op_reject(op, agent):
    if STATE["agents"].get(agent, {}).get("role") != "reviewer":
        raise ValueError("only an agent that said hello with role 'reviewer' can reject")
    reason = str(op.get("reason", "")).strip()
    if len(reason) < 8:
        raise ValueError("give a reason of at least 8 characters")
    iid = str(op.get("id", ""))
    for lst in (STATE["cuts"], STATE["captions"], STATE["fx"], STATE["graphics"]):
        for it in lst:
            if it["id"] == iid and it["status"] == "ok":
                it["status"] = "rejected"
                it["reason"] = reason
                STATE["rejections"].append({"id": iid, "owner": it["agent"], "by": agent, "reason": reason, "t": round(time.time() - STATE["t0"], 2)})
                return "reject", it
    raise ValueError(f"no accepted item with id {iid}")

def op_remove(op, agent):
    if STATE["agents"].get(agent, {}).get("role") != "human":
        raise ValueError("only the person at the screen (role 'human') can remove an item")
    iid = str(op.get("id", ""))
    for lst in (STATE["cuts"], STATE["captions"], STATE["fx"], STATE["graphics"]):
        for it in lst:
            if it["id"] == iid and it["status"] == "ok":
                it["status"] = "removed"
                return "remove", it
    raise ValueError(f"no accepted item with id {iid}")

OPS = {"cut": op_cut, "caption": op_caption, "fx": op_fx, "graphic": op_graphic, "music": op_music, "reject": op_reject, "remove": op_remove}

def broadcast(ev):
    STATE["seq"] += 1
    ev["seq"] = STATE["seq"]
    ev["t"] = round(time.time() - STATE["t0"], 2)
    STATE["log"].append(ev)
    del STATE["log"][:-5000]
    for q in list(SUBS):
        q.put(ev)
    save()

def save():
    try:
        json.dump(STATE, open(os.path.join(PROJ, "state.json"), "w"))
    except OSError:
        pass

def handle_op(op):
    with LOCK:
        agent = str(op.get("agent", "")).strip()
        kind = op.get("op")
        if not agent:
            return 400, {"ok": False, "error": "agent is required"}
        if kind == "hello":
            STATE["agents"][agent] = {"role": str(op.get("role", "editor")), "status": "ready", "ops": 0, "no": 0, "claim": None, "done": False, "summary": ""}
            broadcast({"type": "hello", "agent": agent, "role": STATE["agents"][agent]["role"], "ok": True})
            return 200, {"ok": True}
        if agent not in STATE["agents"]:
            return 400, {"ok": False, "error": "say hello first: {\"op\":\"hello\",\"agent\":\"W01\",\"role\":\"cutter\"}"}
        ag = STATE["agents"][agent]
        if kind == "claim":
            ag["claim"] = {k: op.get(k) for k in ("kind", "id", "start", "end")}
            ag["status"] = str(op.get("status", "working"))[:60]
            broadcast({"type": "claim", "agent": agent, "claim": ag["claim"], "status": ag["status"], "ok": True})
            return 200, {"ok": True}
        if kind == "done":
            ag["done"] = True
            ag["summary"] = str(op.get("summary", ""))[:200]
            ag["status"] = "done"
            broadcast({"type": "done", "agent": agent, "summary": ag["summary"], "ok": True})
            return 200, {"ok": True}
        fn = OPS.get(kind)
        if not fn:
            return 400, {"ok": False, "error": f"unknown op '{kind}'. Ops: hello, claim, cut, caption, fx, graphic, music, reject, done"}
        try:
            typ, it = fn(op, agent)
        except ValueError as e:
            ag["no"] += 1
            broadcast({"type": kind, "agent": agent, "ok": False, "error": str(e), "req": {k: op.get(k) for k in ("start", "end", "at", "text", "id")}})
            return 200, {"ok": False, "error": str(e)}
        ag["ops"] += 1
        broadcast({"type": typ, "agent": agent, "ok": True, "item": it})
        return 200, {"ok": True, "id": it.get("id"), "item": it}

def review():
    with LOCK:
        cuts = sorted(live(STATE["cuts"]), key=lambda c: c["start"])
        caps = live(STATE["captions"])
        issues = []
        for c in cuts:
            for s in ING["silences"]:
                a, b = max(s["s"], c["start"]), min(s["e"], c["end"])
                if b - a > 0.35:
                    issues.append({"kind": "pause", "ref": c["id"], "msg": f"{round(b - a, 2)} s of silence inside {c['id']} at {round(a, 2)}"})

        def in_cut(t):
            return any(c["start"] - 0.05 <= t <= c["end"] + 0.05 for c in cuts)

        for k in caps:
            if not in_cut((k["start"] + k["end"]) / 2):
                issues.append({"kind": "orphan_caption", "ref": k["id"], "msg": f"caption '{k['text']}' is outside every kept cut"})
        spoken_kept = [w for w in WORDS if in_cut((w["t"] + w["e"]) / 2)]
        uncaptioned = [w for w in spoken_kept if not any(k["start"] - 0.35 <= w["t"] and w["e"] <= k["end"] + 0.35 for k in caps)]
        if uncaptioned:
            issues.append({"kind": "uncaptioned", "ref": "-", "msg": f"{len(uncaptioned)} kept words have no caption, first at {uncaptioned[0]['t']}"})
        kept = round(sum(c["end"] - c["start"] for c in cuts), 2)
        return {"issues": issues, "stats": {"kept_s": kept, "cuts": len(cuts), "captions": len(caps), "fx": len(live(STATE["fx"])), "graphics": len(live(STATE["graphics"])), "rejections": len(STATE["rejections"])}}

def window(q):
    a, b = float(q.get("start", [0])[0]), float(q.get("end", [DUR])[0])
    return {"start": a, "end": b,
            "words": [w for w in WORDS if w["e"] > a and w["t"] < b],
            "silences": [s for s in ING["silences"] if s["e"] > a and s["s"] < b],
            "sentences": [s for s in ING["sentences"] if s["end"] > a and s["start"] < b],
            "cuts": [c for c in live(STATE["cuts"]) if c["end"] > a and c["start"] < b],
            "captions": [c for c in live(STATE["captions"]) if c["end"] > a and c["start"] < b],
            "fx": [f for f in live(STATE["fx"]) if f["at"] > a - 3 and f["at"] < b + 3],
            "graphics": [g for g in live(STATE["graphics"]) if g["at"] > a - 3 and g["at"] < b + 3]}

def do_render():
    try:
        import render
        RENDER.update(state="rendering", frac=0.0, error=None, file=None)
        out = os.path.join(OUT, f"edit-{int(time.time())}.mp4")
        with LOCK:
            snap = json.loads(json.dumps(STATE))
        render.render(snap, ING, HERE, out, lambda f: RENDER.update(frac=round(f, 3)), MUSIC_ROOT)
        RENDER.update(state="done", frac=1.0, file="out/" + os.path.basename(out))
        with LOCK:
            broadcast({"type": "render", "agent": "server", "ok": True, "file": RENDER["file"]})
    except Exception as e:  # noqa
        RENDER.update(state="error", error=str(e)[:600])
        with LOCK:
            broadcast({"type": "render", "agent": "server", "ok": False, "error": RENDER["error"]})

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def send_json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        path = urlparse(self.path).path
        try:
            body = json.loads(raw or b"{}")
        except ValueError:
            return self.send_json(400, {"ok": False, "error": "body must be JSON"})
        if path == "/api/op":
            code, obj = handle_op(body)
            return self.send_json(code, obj)
        if path == "/api/reset":
            global STATE
            with LOCK:
                if len(STATE["log"]) >= 30:
                    os.makedirs(os.path.join(PROJ, "runs"), exist_ok=True)
                    json.dump(STATE["log"], open(os.path.join(PROJ, "runs", f"run-{int(time.time())}.json"), "w"))
                STATE = new_state()
                broadcast({"type": "reset", "agent": "server", "ok": True})
            return self.send_json(200, {"ok": True})
        if path == "/api/render":
            if RENDER["state"] == "rendering":
                return self.send_json(200, {"ok": False, "error": "already rendering"})
            threading.Thread(target=do_render, daemon=True).start()
            return self.send_json(200, {"ok": True})
        self.send_json(404, {"ok": False})

    def do_GET(self):
        u = urlparse(self.path)
        p, q = u.path, parse_qs(u.query)
        if p == "/api/state":
            with LOCK:
                return self.send_json(200, {k: v for k, v in STATE.items() if k != "log"} | {"render": RENDER})
        if p == "/api/ingest":
            return self.send_json(200, ING)
        if p == "/api/window":
            with LOCK:
                return self.send_json(200, window(q))
        if p == "/api/runlog":
            with LOCK:
                lg = list(STATE["log"])
            if len(lg) < 30:
                d = os.path.join(PROJ, "runs")
                fs = sorted(os.listdir(d)) if os.path.isdir(d) else []
                lg = json.load(open(os.path.join(d, fs[-1]))) if fs else lg
            return self.send_json(200, lg)
        if p == "/api/review":
            return self.send_json(200, review())
        if p == "/api/rejections":
            with LOCK:
                ag = q.get("agent", [None])[0]
                return self.send_json(200, [r for r in STATE["rejections"] if ag is None or r["owner"] == ag])
        if p == "/api/events":
            return self.sse()
        if p == "/":
            p = "/ui/index.html"
        return self.static(p)

    def sse(self):
        qq = queue.Queue()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        with LOCK:
            snap = {k: v for k, v in STATE.items() if k != "log"}
            SUBS.append(qq)
        try:
            self.wfile.write(("data: " + json.dumps({"type": "snapshot", "state": snap}) + "\n\n").encode())
            self.wfile.flush()
            while True:
                try:
                    ev = qq.get(timeout=15)
                    self.wfile.write(("data: " + json.dumps(ev) + "\n\n").encode())
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            if qq in SUBS:
                SUBS.remove(qq)

    def static(self, p):
        rel = p.lstrip("/")
        if not rel.startswith(("ui/", "project/", "out/")) or ".." in rel or rel.endswith(("state.json", "a.wav")):
            return self.send_json(404, {"ok": False})
        f = os.path.join(HERE, rel)
        if not os.path.isfile(f):
            return self.send_json(404, {"ok": False})
        size = os.path.getsize(f)
        ctype = mimetypes.guess_type(f)[0] or "application/octet-stream"
        start, end, code = 0, size - 1, 200
        rng = self.headers.get("Range")
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                if m.group(2):
                    end = min(size - 1, int(m.group(2)))
                code = 206
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "no-store")
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        try:
            with open(f, "rb") as fh:
                fh.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = fh.read(min(65536, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

def main():
    global STATE
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8780)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    try:
        import render
        render.make_templates(PROJ)
    except Exception as e:  # noqa
        print("template previews not made:", e, flush=True)
    STATE = load_state() or new_state()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    srv.daemon_threads = True
    print(f"Agent Editor on http://127.0.0.1:{a.port}  (source {DUR:.1f}s, {len(WORDS)} words)", flush=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
