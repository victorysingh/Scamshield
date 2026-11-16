"""Record ScamShield demo footage for the submission video.

Produces two silent 1920x1080 .webm clips with a visible cursor:
  1_app_demo.webm   0:00-1:35  hero + Shots 1-4 (CBI, digital arrest, Kannada, genuine)
  2_terminal.webm   Shot 5     pytest + evaluate.py — real output, captured when you run this
Add your voiceover in a video editor (e.g. Clipchamp, built into Windows 11).

Prereqs: `python api.py` and `npm run dev` (in web/) are running.
Usage:   python scripts/record_demo.py [--out DIR] [--show] [--only app|terminal]
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "Videos" / "ScamShield"))
    ap.add_argument("--show", action="store_true", help="show the browser while recording")
    ap.add_argument("--only", choices=["app", "terminal"])
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
        browser.close()
    shutil.rmtree(raw, ignore_errors=True)


if __name__ == "__main__":
    main()
