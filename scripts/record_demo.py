"""Record ScamShield demo footage for the submission video.

Produces four silent 1920x1080 .webm clips with a visible cursor:
  1_app_demo.webm   0:00-1:35  hero + Shots 1-4 (CBI, digital arrest, Kannada, genuine)
  2_terminal.webm   Shot 5     pytest + evaluate.py — real output, captured when you run this
  3_orchestrate.webm 1:35-1:55 Orchestrate Version B — agent.yaml + deploy.py
  4_bob_session.webm Bob story  your Bob recording, cut (no login email) and captioned as a re-run
Add your voiceover in a video editor (e.g. Clipchamp, built into Windows 11).

Prereqs: `python api.py` and `npm run dev` (in web/) are running.
Usage:   python scripts/record_demo.py [--out DIR] [--show] [--only app|terminal|orchestrate|bob]
"""
from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
URL = "http://localhost:5173"
DIGITAL_ARREST = (
    "Your Aadhaar is linked to illegal activity. Stay on video call with our officer "
    "and do not tell anyone. Transfer Rs.50,000 for verification immediately."
)

# Headless video has no OS cursor, so draw one (plus a click ripple).
CURSOR_JS = """
window.addEventListener('DOMContentLoaded', () => {
  document.body.style.zoom = '1.25';  // 125% page zoom; cursor sits outside <body>
  const root = document.documentElement;
  const c = document.createElement('div');
  c.innerHTML = `<svg width="30" height="30" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6-3.6 6.4z"
    fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
  Object.assign(c.style, {position:'fixed', left:'0', top:'0', zIndex:2147483647,
    pointerEvents:'none', transform:'translate(-200px,-200px)'});
  root.appendChild(c);
  document.addEventListener('mousemove', e => {
    c.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`;
  }, true);
  document.addEventListener('mousedown', e => {
    const r = document.createElement('div');
    Object.assign(r.style, {position:'fixed', left:(e.clientX-22)+'px', top:(e.clientY-22)+'px',
      width:'44px', height:'44px', borderRadius:'50%', border:'3px solid rgba(37,99,235,.85)',
      zIndex:2147483646, pointerEvents:'none', transition:'transform .45s ease-out, opacity .45s ease-out'});
    root.appendChild(r);
    requestAnimationFrame(() => { r.style.transform = 'scale(1.8)'; r.style.opacity = '0'; });
    setTimeout(() => r.remove(), 500);
  }, true);
});
"""


class Timeline:
    """Holds each shot to its slot in the shot list."""

    def __init__(self) -> None:
        self.t0 = time.monotonic()
        self.cues: list[str] = []

    def now(self) -> float:
        return time.monotonic() - self.t0

    def until(self, second: float) -> None:
        left = second - self.now()
        if left > 0:
            time.sleep(left)
        elif left < -0.5:
            print(f"  ! {-left:.1f}s behind the {second:.0f}s mark")

    def cue(self, label: str) -> None:
        s = self.now()
        self.cues.append(f"{int(s // 60)}:{s % 60:05.2f}  {label}")
        print(" ", self.cues[-1])


def point(page: Page, selector: str, *, x_frac: float = 0.5, hold: float = 0.0) -> None:
    """Smooth-scroll an element into view and glide the cursor onto it."""
    el = page.locator(selector).first
    scrolled = el.evaluate("e => { const r = e.getBoundingClientRect();"
                           " if (r.top >= 70 && r.bottom <= innerHeight - 40) return false;"
                           " e.scrollIntoView({behavior: 'smooth', block: 'center'}); return true; }")
    if scrolled:
        time.sleep(0.7)
    box = el.bounding_box()
    assert box, f"not visible: {selector}"
    page.mouse.move(box["x"] + box["width"] * x_frac, box["y"] + box["height"] / 2, steps=20)
    time.sleep(hold)


def click(page: Page, selector: str, pause: float = 0.35) -> None:
    point(page, selector)
    time.sleep(pause)
    page.mouse.down()
    page.mouse.up()


def scroll_to(page: Page, y: int) -> None:
    page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'smooth'}})")
    time.sleep(0.9)


def new_context(browser, raw_dir: Path) -> BrowserContext:
    return browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=str(raw_dir),
        record_video_size={"width": 1920, "height": 1080},
        permissions=["clipboard-read", "clipboard-write"],
    )


def finish(ctx: BrowserContext, page: Page, dest: Path) -> Path:
    video = page.video
    ctx.close()
    shutil.move(video.path(), dest)
    return dest


# ---------------------------------------------------------------------------
# Clip 1 — the app
# ---------------------------------------------------------------------------
def record_app(browser, out: Path, raw: Path) -> Path:
    ctx = new_context(browser, raw)
    ctx.add_init_script(CURSOR_JS)
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    page.wait_for_selector(".primary-btn")
    page.mouse.move(1150, 260)
    time.sleep(1.0)  # trim this lead-in in the editor; cues are relative to t0
    tl = Timeline()

    # 0:00-0:20 · The problem — hero
    tl.cue("Problem — home page")
    tl.until(7)
    point(page, ".hero-copy h1", x_frac=0.3)
    tl.until(13)
    point(page, ".steps", x_frac=0.5)
    tl.until(17)
    scroll_to(page, 250)

    # 0:20-0:45 · Shot 1 — fake police / CBI
    tl.until(20)
    tl.cue("Shot 1 — Fake police / CBI")
    click(page, ".sample-chip >> nth=0")
    time.sleep(0.6)
    point(page, ".textarea", x_frac=0.35, hold=1.6)       # the text auto-fills
    click(page, ".primary-btn")
    page.wait_for_selector(".result.risk-high", timeout=10_000)
    time.sleep(1.2)
    point(page, ".verdict-banner", x_frac=0.25, hold=1.4)  # red banner
    point(page, ".meter .seg-high", hold=1.0)              # HIGH lit
    for i in range(page.locator(".why-list li").count()):  # warning signs
        point(page, f".why-list li >> nth={i}", x_frac=0.15, hold=0.9)
    point(page, ".todo-card", x_frac=0.3, hold=2.0)        # what you should do
    point(page, ".family-row", x_frac=0.2, hold=1.8)       # family alert (demo only)
    point(page, ".helpline-btn", x_frac=0.3, hold=1.2)     # Call 1930

    # 0:45-1:05 · Shot 2 — digital arrest, pasted
    tl.until(45)
    tl.cue("Shot 2 — Digital arrest")
    page.evaluate("t => navigator.clipboard.writeText(t)", DIGITAL_ARREST)
    click(page, ".again-btn")
    time.sleep(1.2)
    click(page, ".textarea")
    time.sleep(0.4)
    page.keyboard.press("Control+V")
    time.sleep(0.3)
    if not page.input_value(".textarea"):  # headless paste unsupported → insert as one paste-like edit
        page.keyboard.insert_text(DIGITAL_ARREST)
    time.sleep(1.5)
    click(page, ".primary-btn")
    page.wait_for_selector(".result.risk-high", timeout=10_000)
    time.sleep(1.2)
    point(page, ".verdict-banner", x_frac=0.25, hold=1.2)
    for i in range(page.locator(".why-list li").count()):  # 4 signals
        point(page, f".why-list li >> nth={i}", x_frac=0.15, hold=1.0)

    # 1:05-1:20 · Shot 3 — Kannada
    tl.until(65)
    tl.cue("Shot 3 — Kannada")
    scroll_to(page, 0)
    click(page, ".lang-switch button >> nth=1")
    time.sleep(3.0)  # whole page flips; result re-explains and scrolls into view
    point(page, ".verdict-banner", x_frac=0.25, hold=2.0)
    point(page, ".todo-card", x_frac=0.3, hold=2.0)

    # 1:20-1:35 · Shot 4 — genuine bank SMS (back in English for the judges)
    tl.until(80)
    tl.cue("Shot 4 — Genuine bank SMS")
    scroll_to(page, 0)
    click(page, ".lang-switch button >> nth=0")
    time.sleep(0.8)
    click(page, ".again-btn")
    time.sleep(0.9)
    click(page, ".sample-chip >> nth=2")
    time.sleep(0.9)
    click(page, ".primary-btn")
    page.wait_for_selector(".result.risk-low", timeout=10_000)
    time.sleep(1.2)
    point(page, ".verdict-banner", x_frac=0.25, hold=1.5)  # Looks safe
    point(page, ".meter .seg-low", hold=1.0)
    point(page, ".no-signs", x_frac=0.2, hold=1.2)
    point(page, ".family-row", x_frac=0.2, hold=1.5)       # no family alert
    tl.until(95)
    tl.cue("End of app demo")

    dest = finish(ctx, page, out / "1_app_demo.webm")
    (out / "1_app_demo_cues.txt").write_text("\n".join(tl.cues) + "\n", encoding="utf-8")
    return dest


# ---------------------------------------------------------------------------
# Clip 2 — terminal (real output, replayed in a large terminal-style page)
# ---------------------------------------------------------------------------
def run_cmd(args: list[str]) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    res = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env)
    out = (res.stdout + res.stderr).rstrip()
    if res.returncode != 0:
        sys.exit(f"Command failed ({' '.join(args)}):\n{out}")
    # Keep the home folder (your name) off screen
    return out.replace(str(Path.home()), "~")


def terminal_html(blocks: list[tuple[str, str]]) -> str:
    data = ",".join(f"[{cmd!r},{html.escape(out)!r}]" for cmd, out in blocks)
    return f"""<!doctype html><meta charset="utf-8"><style>
  html,body{{margin:0;height:100%;background:#0c0c0c}}
  body{{font:32px/1.45 'Cascadia Mono',Consolas,monospace;color:#d4d4d4;padding:64px 80px;box-sizing:border-box}}
  .p{{color:#3b9eff}} .ok{{color:#4ec97b}} .cur{{display:inline-block;width:.6em;background:#d4d4d4;animation:b 1s steps(1) infinite}}
  @keyframes b{{50%{{opacity:0}}}} pre{{margin:0;white-space:pre-wrap}}
</style><pre id="t"></pre><script>
const blocks=[{data}], t=document.getElementById('t'), P='<span class="p">PS ~\\\\ibm&gt;</span> ';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const color=s=>s.replace(/(\\d+ passed[^\\n]*|100\\.0%|0\\.0%)/g,'<span class="ok">$1</span>');
(async()=>{{ let done='';
  for(const [cmd,out] of blocks){{
    for(let i=0;i<=cmd.length;i++){{ t.innerHTML=done+P+cmd.slice(0,i)+'<span class="cur">&nbsp;</span>'; await sleep(55); }}
    await sleep(500); done+=P+cmd+'\\n'+color(out)+'\\n\\n'; t.innerHTML=done; await sleep(5500);
  }}
  t.innerHTML=done+P+'<span class="cur">&nbsp;</span>'; window.__done=true;
}})();
</script>"""


def record_terminal(browser, out: Path, raw: Path) -> Path:
    py = str(ROOT / ".venv" / "Scripts" / "python.exe")
    py = py if Path(py).exists() else sys.executable
    blocks = [
        ("pytest tests/ -q", run_cmd([py, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"])),
        ("python evaluate.py", run_cmd([py, "evaluate.py"])),
    ]
    ctx = new_context(browser, raw)
    page = ctx.new_page()
    page.set_content(terminal_html(blocks))
    page.wait_for_function("window.__done === true", timeout=60_000)
    time.sleep(3.0)
    return finish(ctx, page, out / "2_terminal.webm")


# ---------------------------------------------------------------------------
# Clip 3 — watsonx Orchestrate, Version B (code walkthrough, ~31 s)
# ---------------------------------------------------------------------------
ORCH_FILES = [
    ("orchestrate/agent.yaml", "yaml"),
    ("orchestrate/deploy.py", "python"),
]
# (second, file index, first line, last line) — highlighted band, scrolled into view.
# Fits the 1:35-1:55 slot (20 s).
ORCH_STEPS = [
    (0.0, 0, 1, 9),      # agent name + model
    (3.0, 0, 38, 41),    # the same three tools
    (6.0, 0, 29, 30),    # always ends with 1930
    (9.0, 1, 98, 102),   # deploy: env add + activate (key masked)
    (11.0, 1, 104, 114), # tools import from a clean bundle (.env never uploaded)
    (13.0, 1, 116, 117), # agents import
]
ORCH_TYPE_AT, ORCH_END = 15.0, 20.0


def orchestrate_html() -> str:
    import json
    files = [{"name": n, "lang": lang, "code": (ROOT / n).read_text(encoding="utf-8").rstrip("\n")}
             for n, lang in ORCH_FILES]
    data = json.dumps({"files": files, "steps": ORCH_STEPS, "typeAt": ORCH_TYPE_AT, "end": ORCH_END})
    data = data.replace("</", "<\\/")
    return """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
  :root{--lh:34px}
  html,body{margin:0;height:100%;background:#1e1e1e;overflow:hidden;font-family:'Segoe UI',sans-serif}
  .tabs{display:flex;background:#252526;height:56px}
  .tab{padding:0 30px;display:flex;align-items:center;font-size:21px;color:#9d9d9d;border-right:1px solid #1e1e1e}
  .tab.on{background:#1e1e1e;color:#fff;box-shadow:inset 0 3px 0 #3b9eff}
  .ed{position:absolute;top:56px;bottom:250px;left:0;right:0;overflow:hidden}
  .inner{position:absolute;top:24px;left:0;right:0;transition:transform .7s cubic-bezier(.4,0,.2,1)}
  .band{position:absolute;left:0;right:0;background:rgba(59,158,255,.16);border-left:5px solid #3b9eff;
        transition:top .5s,height .5s,opacity .3s}
  .row{display:flex;position:relative}
  pre{margin:0;font:23px/var(--lh) 'Cascadia Mono',Consolas,monospace}
  .gut{width:96px;text-align:right;padding-right:34px;color:#6e7681;flex:none}
  .code{color:#d4d4d4;background:none!important;padding:0!important}
  .term{position:absolute;left:0;right:0;bottom:0;height:250px;background:#0c0c0c;border-top:1px solid #333;
        padding:20px 60px;box-sizing:border-box}
  .term h4{margin:0 0 14px;font:600 17px 'Segoe UI';color:#9d9d9d;letter-spacing:.08em}
  .term pre{font-size:30px;color:#d4d4d4}.p{color:#3b9eff}
  .cur{display:inline-block;width:.6em;background:#d4d4d4;animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}
</style>
<div class="tabs" id="tabs"></div>
<div class="ed"><div class="inner" id="inner"><div class="band" id="band"></div>
  <div class="row"><pre class="gut" id="gut"></pre><pre class="code hljs" id="code"></pre></div></div></div>
<div class="term"><h4>TERMINAL</h4><pre id="t"></pre></div>
<script>
const D = """ + data + """;
const LH = 34, $ = id => document.getElementById(id);
const hl = (c, l) => (window.hljs ? hljs.highlight(c, {language: l}).value
                      : c.replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m])));
$('tabs').innerHTML = D.files.map((f, i) => `<div class="tab" id="tab${i}">${f.name.split('/').pop()}</div>`).join('');
let cur = -1;
function show(i) {
  if (i === cur) return; cur = i;
  D.files.forEach((_, j) => $('tab' + j).classList.toggle('on', j === i));
  const f = D.files[i], n = f.code.split('\\n').length;
  $('code').innerHTML = hl(f.code, f.lang);
  $('gut').textContent = Array.from({length: n}, (_, k) => k + 1).join('\\n');
  $('inner').style.transition = 'none'; $('inner').style.transform = 'translateY(0)';
  $('band').style.transition = 'none'; void $('inner').offsetHeight;
  $('inner').style.transition = ''; $('band').style.transition = '';
}
function focus(i, a, b) {
  show(i);
  const band = $('band'), view = document.querySelector('.ed').clientHeight - 48;
  band.style.top = (a - 1) * LH + 'px'; band.style.height = (b - a + 1) * LH + 'px';
  const total = D.files[i].code.split('\\n').length * LH;
  const mid = ((a + b) / 2 - 0.5) * LH - view / 2;
  const off = Math.max(0, Math.min(mid, total - view));
  $('inner').style.transform = `translateY(${-off}px)`;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const t0 = performance.now(), at = s => sleep(Math.max(0, t0 + s * 1000 - performance.now()));
  $('t').innerHTML = '<span class="p">PS ~\\\\ibm&gt;</span> <span class="cur">&nbsp;</span>';
  for (const [s, i, a, b] of D.steps) { await at(s); focus(i, a, b); }
  await at(D.typeAt);
  const cmd = 'python orchestrate/deploy.py';
  for (let k = 0; k <= cmd.length; k++) {
    $('t').innerHTML = '<span class="p">PS ~\\\\ibm&gt;</span> ' + cmd.slice(0, k) + '<span class="cur">&nbsp;</span>';
    await sleep(60);
  }
  await at(D.end); window.__done = true;
})();
</script>"""


def record_orchestrate(browser, out: Path, raw: Path) -> Path:
    ctx = new_context(browser, raw)
    page = ctx.new_page()
    page.set_content(orchestrate_html(), wait_until="networkidle")
    page.wait_for_function("window.__done === true", timeout=60_000)
    return finish(ctx, page, out / "3_orchestrate.webm")


# ---------------------------------------------------------------------------
# Clip 4 — Bob session, cut + captioned from your own screen recording (~41 s)
# ---------------------------------------------------------------------------
BOB_SRC = ROOT / "Screen Recording 2026-11-16 062106.mp4"
# (start s, end s, label, caption). 0-4 s is skipped: it shows the login email.
# The clip ends before ~50 s, where Bob edits story_log.md.
BOB_SEGMENTS = [
    (4.5, 29.5, "Re-run for this video · 16 Nov 2026",
     "IBM Bob re-running our Task 2 prompt (red-flag rules + tests) in an empty folder. "
     "The original build session was on 14 Nov and is recorded in docs/story_log.md."),
    (34.0, 49.5, "Build log · docs/story_log.md",
     "Every Bob session, the fixes we made, and each post-Bob change written by Claude — all disclosed."),
]


def bob_html(src: Path) -> str:
    import json
    segs = json.dumps(BOB_SEGMENTS)
    return f"""<!doctype html><meta charset="utf-8"><style>
  html,body{{margin:0;height:100%;background:#000;overflow:hidden;font-family:'Segoe UI',sans-serif}}
  video{{position:absolute;top:0;left:0;width:1920px;height:932px;object-fit:contain;background:#000}}
  .cap{{position:absolute;left:0;right:0;bottom:0;height:148px;background:#111827;border-top:3px solid #3b9eff;
        display:flex;align-items:center;gap:28px;padding:0 56px;box-sizing:border-box}}
  .pill{{flex:none;background:#3b9eff;color:#04111f;font:700 22px 'Segoe UI';padding:10px 20px;border-radius:999px}}
  .txt{{color:#f3f4f6;font:500 27px/1.35 'Segoe UI'}}
  .fade{{position:absolute;inset:0;background:#000;opacity:0;transition:opacity .35s;pointer-events:none}}
</style>
<video id="v" src="{src.as_uri()}" muted playsinline preload="auto"></video>
<div class="cap"><span class="pill" id="pill"></span><span class="txt" id="txt"></span></div>
<div class="fade" id="fade"></div>
<script>
const S = {segs}, v = document.getElementById('v'), $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const seek = t => new Promise(r => {{ v.onseeked = () => r(); v.currentTime = t; }});
const reach = t => new Promise(r => {{
  const tick = () => (v.currentTime >= t || v.ended) ? r() : v.requestVideoFrameCallback(tick);
  v.requestVideoFrameCallback(tick);
}});
(async () => {{
  await new Promise(r => v.readyState >= 1 ? r() : v.addEventListener('loadedmetadata', r, {{once: true}}));
  for (let i = 0; i < S.length; i++) {{
    const [a, b, label, text] = S[i];
    await seek(a); $('pill').textContent = label; $('txt').textContent = text;
    if (i === 0) {{ window.__ready = true; await sleep(400); }}
    $('fade').style.opacity = 0; await v.play(); await reach(b); v.pause();
    if (i < S.length - 1) {{ $('fade').style.opacity = 1; await sleep(400); }}
  }}
  await sleep(600); window.__done = true;
}})();
</script>"""


def record_bob(p, out: Path, raw: Path, src: Path) -> Path:
    if not src.exists():
        sys.exit(f"Bob recording not found: {src}")
    browser = p.chromium.launch(channel="chrome")  # Google Chrome decodes H.264 .mp4
    ctx = new_context(browser, raw)
    page = ctx.new_page()
    player = raw / "bob_player.html"
    raw.mkdir(parents=True, exist_ok=True)
    player.write_text(bob_html(src), encoding="utf-8")
    page.goto(player.as_uri())
    page.wait_for_function("window.__done === true", timeout=120_000, polling=500)
    dest = finish(ctx, page, out / "4_bob_session.webm")
    browser.close()
    return dest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "Videos" / "ScamShield"))
    ap.add_argument("--show", action="store_true", help="show the browser while recording")
    ap.add_argument("--bob-src", default=str(BOB_SRC), help="your Bob screen recording (.mp4)")
    ap.add_argument("--only", choices=["app", "terminal", "orchestrate", "bob"])
    args = ap.parse_args()
    out = Path(args.out)
    raw = out / "_raw"
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.show)
        if args.only in (None, "app"):
            print("Recording app demo (~1:40)…")
            print("Saved:", record_app(browser, out, raw))
        if args.only in (None, "terminal"):
            print("Recording terminal shot…")
            print("Saved:", record_terminal(browser, out, raw))
        if args.only in (None, "orchestrate"):
            print("Recording Orchestrate walkthrough…")
            print("Saved:", record_orchestrate(browser, out, raw))
        if args.only in (None, "bob"):
            print("Cutting + captioning the Bob session…")
            print("Saved:", record_bob(p, out, raw, Path(args.bob_src)))
        browser.close()
    shutil.rmtree(raw, ignore_errors=True)


if __name__ == "__main__":
    main()
