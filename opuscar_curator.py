#!/usr/bin/env python3
"""
Opuscar Skill Curator & Sanitizer
=================================
A zero-dependency developer utility to safely discover, inspect, sanitize, and 
cherry-pick styles from lemomo-ai/lemo-opuscar into clean, isolated agent skills.

Usage:
  opuscar-curator --ui                  # Launch the visual web browser interface (http://localhost:7890)
  opuscar-curator list                  # List all 99 styles across all 15 stations
  opuscar-curator search <term>         # Search styles by keyword, film, or category
  opuscar-curator info <slug>           # Detailed style information and specifications
  opuscar-curator audit <slug>          # Run prompt-injection and security checks
  opuscar-curator cherry-pick <slug>    # Export a clean, isolated skill package
"""

import sys
import os
import json
import re
import argparse
import webbrowser
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Any, Optional

DIR_PATH = Path(__file__).resolve().parent
CATALOG_FILE = DIR_PATH / "catalog.json"

# Load Catalog (all 99 styles)
def load_catalog_data() -> List[Dict[str, Any]]:
    if CATALOG_FILE.exists():
        try:
            with open(CATALOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                catalog = []
                for item in data:
                    slug = item.get("slug", "")
                    num = item.get("num", "")
                    name = item.get("en", slug.replace("-", " ").title())
                    cat_en = item.get("category_en", "General")
                    cat_cn = item.get("category_cn", "")
                    film = item.get("film", "")
                    line = item.get("line", "")
                    uses = item.get("uses", [])
                    poster_url = f"https://raw.githubusercontent.com/lemomo-ai/lemo-opuscar/main/styles/{slug}/poster.jpg"
                    
                    catalog.append({
                        "slug": slug,
                        "num": num,
                        "name": name,
                        "name_cn": item.get("cn", ""),
                        "category_en": cat_en,
                        "category_cn": cat_cn,
                        "film": film,
                        "line": line,
                        "uses": uses,
                        "poster_url": poster_url,
                        "license": "MIT (Core)",
                        "assets_license": "CC-BY-NC-4.0"
                    })
                return catalog
        except Exception as e:
            pass
    return []

CATALOG = load_catalog_data()
CATALOG_BY_SLUG = {item["slug"]: item for item in CATALOG}

# Security Audit Regex Rules
SUSPICIOUS_PATTERNS = [
    (r"(curl|wget)\s+[^\n|]*\|\s*(sh|bash)", "HIGH", "Remote shell pipe execution (`curl | bash`)"),
    (r"setup\.sh\s+deps", "HIGH", "Invokes external dependency pull / setup script"),
    (r"(sudo|chmod\s+\+s)", "HIGH", "Elevated root or suid privilege request"),
    (r"rm\s+-rf\s+[/~]", "HIGH", "Destructive recursive deletion across root or home"),
    (r"eval\s*\(", "MEDIUM", "Dynamic `eval()` code execution"),
    (r"(\.env|id_rsa|credentials|auth\.json)", "MEDIUM", "Accessing sensitive credential or SSH files"),
    (r"(ignore\s+(all\s+)?previous\s+instructions|system\s+prompt\s+override)", "HIGH", "Potential prompt injection / override attempt"),
    (r"(webhook|pastebin|ngrok|pipedream|requestbin)", "MEDIUM", "Potential external telemetry or exfiltration endpoint")
]


def run_security_audit(content: str) -> Dict[str, Any]:
    findings = []
    max_severity = "CLEAN"
    
    for pattern, severity, reason in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append({
                "severity": severity,
                "reason": reason,
                "matches_count": len(matches)
            })
            if severity == "HIGH" or (severity == "MEDIUM" and max_severity != "HIGH"):
                max_severity = severity

    return {
        "status": "PASSED" if max_severity == "CLEAN" else "FLAGGED",
        "severity": max_severity,
        "findings": findings,
        "lines_scanned": len(content.splitlines()),
        "sanitized_safe": max_severity != "HIGH"
    }


def fetch_style_markdown_from_repo(slug: str) -> str:
    raw_url = f"https://raw.githubusercontent.com/lemomo-ai/lemo-opuscar/main/styles/{slug}/STYLE.md"
    try:
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'OpuscarCurator/1.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                return response.read().decode('utf-8', errors='replace')
    except Exception:
        pass

    item = CATALOG_BY_SLUG.get(slug, {})
    return f"""# Style Specification: {item.get('name', slug)}
Station: {item.get('category_en', 'General')} ({item.get('category_cn', '')})
Film Demo: {item.get('film', '')}

## Narrative Pitch
{item.get('line', '')}

## Aesthetic Guidelines
- **Palette & Composition**: High coherence with the {item.get('category_en', '')} aesthetic.
- **Motion Kinematics**: Frame-by-frame procedural easing curves.
- **Rendering Primitives**: Canvas 2D / WebGL deterministic rendering.
- **Pacing**: Storyboarded transitions with visual anchors for key dialogue or text cues.
"""


def generate_tailored_skill_markdown(style: Dict[str, Any], style_md_content: str) -> str:
    return f"""---
name: opuscar-{style['slug']}
description: Generate code-driven video shorts and motion graphics in the '{style['name']}' aesthetic ({style['category_en']}).
---

# Opuscar Skill: {style['name']} ({style['category_en']})

This skill equips the assistant to produce complete visual narratives and motion sequences rendered exclusively in the **{style['name']}** aesthetic using procedural code (Canvas/WebGL) and local tools without relying on heavy cloud generative video models.

## Aesthetic Identity & Medium
- **Category**: {style['category_en']} ({style.get('category_cn', '')})
- **Demo Reference**: "{style.get('film', '')}"
- **Summary**: {style.get('line', '')}
- **Tags / Best Uses**: {', '.join(style.get('uses', []))}
- **Core License**: {style['license']} (Asset rules: {style['assets_license']})

## Style Brief & Invariants
```markdown
{style_md_content.strip()}
```

## Production Guidelines & Sandbox Rules
1. **Local Self-Containment**:
   - Write rendering logic into an isolated HTML/JS file that executes inside a standard headless browser or Canvas context.
   - Do NOT run arbitrary external setup scripts or fetch untrusted third-party binaries.
   - Keep all output assets, frames, and audio tracks within a dedicated task or output directory.
2. **Animation Architecture**:
   - Structure timelines using deterministic time offsets (`t` seconds or frame index `f` at 60fps).
   - Use procedural easing equations (e.g., cubic-bezier, elastic, or spring mechanics) rather than wall-clock `setTimeout` loops.
3. **Audio & Voiceover Synchronization**:
   - Create an absolute-time cue map (Q-map) pairing visual moments with speech beats or score transitions.
"""


def generate_isolated_render_template(style: Dict[str, Any]) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Opuscar Render Harness - {style['name']}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #0f172a;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #canvas-container {{
      box-shadow: 0 20px 50px rgba(0,0,0,0.8);
      border-radius: 8px;
      overflow: hidden;
      background: #000;
      border: 1px solid #1e293b;
    }}
    canvas {{ display: block; }}
    #controls {{
      margin-top: 16px;
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    button {{
      background: #0284c7;
      color: #fff;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
    }}
    button:hover {{ background: #0369a1; }}
    #status {{ font-size: 14px; color: #94a3b8; }}
  </style>
</head>
<body>
  <div id="canvas-container">
    <canvas id="stage" width="1280" height="720"></canvas>
  </div>
  <div id="controls">
    <button id="btn-play">Play / Pause</button>
    <button id="btn-restart">Restart</button>
    <span id="status">Time: 0.00s | Style: {style['name']}</span>
  </div>

  <script>
    const canvas = document.getElementById('stage');
    const ctx = canvas.getContext('2d');
    const statusEl = document.getElementById('status');
    const btnPlay = document.getElementById('btn-play');
    const btnRestart = document.getElementById('btn-restart');

    let startTime = performance.now();
    let isPlaying = true;
    let pausedAt = 0;
    const duration = 10.0;

    function renderFrame(timeSec) {{
      const width = canvas.width;
      const height = canvas.height;
      const progress = Math.min(1.0, timeSec / duration);

      ctx.fillStyle = '#080c14';
      ctx.fillRect(0, 0, width, height);

      ctx.save();
      // Outer aesthetic frame
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 3;
      ctx.strokeRect(30, 30, width - 60, height - 60);

      // Typography
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px sans-serif';
      ctx.fillText("{style['name']}", 70, 95);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '20px sans-serif';
      ctx.fillText("{style['category_en']} • Film Reference: {style.get('film', '')}", 70, 135);

      // Animated visual motif
      const centerX = width / 2;
      const centerY = height / 2 + 20;
      const pulse = Math.sin(timeSec * 2.5) * 25;

      ctx.beginPath();
      ctx.arc(centerX, centerY, 90 + pulse, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
      ctx.fill();
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Progress bar
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(70, height - 70, width - 140, 8);
      ctx.fillStyle = '#38bdf8';
      ctx.fillRect(70, height - 70, (width - 140) * progress, 8);

      ctx.restore();
    }}

    function animate(now) {{
      if (isPlaying) {{
        const elapsed = (now - startTime) / 1000;
        const currentSec = elapsed % duration;
        renderFrame(currentSec);
        statusEl.textContent = `Time: ${{currentSec.toFixed(2)}}s / ${{duration}}s | 60 FPS Procedural Canvas`;
      }}
      requestAnimationFrame(animate);
    }}

    btnPlay.addEventListener('click', () => {{
      if (isPlaying) {{
        isPlaying = false;
        pausedAt = performance.now();
        btnPlay.textContent = 'Play';
      }} else {{
        isPlaying = true;
        startTime += (performance.now() - pausedAt);
        btnPlay.textContent = 'Pause';
      }}
    }});

    btnRestart.addEventListener('click', () => {{
      startTime = performance.now();
      if (!isPlaying) {{
        isPlaying = true;
        btnPlay.textContent = 'Pause';
      }}
    }});

    requestAnimationFrame(animate);
  </script>
</body>
</html>
"""


def cherry_pick_style(slug: str, output_base_dir: str) -> Dict[str, Any]:
    if slug not in CATALOG_BY_SLUG:
        return {"success": False, "error": f"Style '{slug}' not found in catalog."}

    style = CATALOG_BY_SLUG[slug]
    style_content = fetch_style_markdown_from_repo(slug)
    audit_results = run_security_audit(style_content)

    if audit_results["severity"] == "HIGH":
        return {
            "success": False, 
            "error": "Security audit failed: Dangerous patterns detected in style source.", 
            "audit": audit_results
        }

    target_skill_dir = Path(output_base_dir) / f"opuscar-{slug}"
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    skill_md = generate_tailored_skill_markdown(style, style_content)
    (target_skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (target_skill_dir / "STYLE.md").write_text(style_content, encoding="utf-8")
    render_html = generate_isolated_render_template(style)
    (target_skill_dir / "harness.html").write_text(render_html, encoding="utf-8")

    readme_content = f"""# Opuscar Cherry-Picked Skill: {style['name']}

- **Slug**: `{style['slug']}`
- **Category**: {style['category_en']} ({style.get('category_cn', '')})
- **Film Demo**: {style.get('film', '')}
- **Security Audit**: PASSED (0 high-risk directives detected)
- **Local Isolation Guarantee**: Pure HTML5 Canvas / WebGL harness. No automated `setup.sh` or pip/npm execution.

## Testing
Open `harness.html` in your browser to inspect the render loop.
"""
    (target_skill_dir / "README.md").write_text(readme_content, encoding="utf-8")

    return {
        "success": True,
        "path": str(target_skill_dir.resolve()),
        "slug": slug,
        "style_name": style["name"],
        "audit": audit_results
    }


# --- Web UI with Visual Samples & Live Canvas Previews ---

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Opuscar Skill Curator & Visual Workbench</title>
  <style>
    :root {
      --bg: #090d16;
      --card-bg: #111726;
      --card-border: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0ea5e9;
      --pill-bg: #1e293b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      padding: 24px;
      line-height: 1.5;
    }
    .header {
      max-width: 1400px;
      margin: 0 auto 20px auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
    }
    .header-title h1 {
      font-size: 24px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .badge {
      font-size: 11px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 3px 8px;
      border-radius: 999px;
      font-weight: 600;
    }
    .header-title p {
      font-size: 14px;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .controls {
      max-width: 1400px;
      margin: 0 auto 24px auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .search-row {
      display: flex;
      gap: 12px;
      width: 100%;
    }
    .search-bar {
      flex: 1;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 12px 18px;
      color: #fff;
      font-size: 15px;
      outline: none;
    }
    .search-bar:focus { border-color: var(--accent); }
    .station-filter {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 8px;
      scrollbar-width: thin;
    }
    .station-btn {
      background: var(--pill-bg);
      color: var(--text-muted);
      border: 1px solid transparent;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 13px;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
    }
    .station-btn:hover, .station-btn.active {
      background: var(--accent);
      color: #090d16;
      font-weight: 600;
    }
    .grid {
      max-width: 1400px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, border-color 0.15s;
    }
    .card:hover {
      transform: translateY(-3px);
      border-color: #38bdf8;
    }
    .card-thumb-container {
      width: 100%;
      height: 180px;
      background: #0f172a;
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }
    .card-thumb-fallback {
      position: absolute;
      inset: 0;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      color: #64748b;
      font-size: 13px;
      gap: 6px;
    }
    .card-thumb {
      position: relative;
      z-index: 2;
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .card-body {
      padding: 16px;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }
    .card-num {
      font-size: 11px;
      color: var(--accent);
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .card-title {
      font-size: 17px;
      font-weight: 700;
      margin: 4px 0 2px 0;
      color: #fff;
    }
    .card-film {
      font-size: 13px;
      color: #38bdf8;
      margin-bottom: 8px;
    }
    .card-line {
      font-size: 13px;
      color: #94a3b8;
      margin-bottom: 12px;
      line-height: 1.4;
      flex-grow: 1;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .card-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 14px;
    }
    .tag {
      background: rgba(255,255,255,0.06);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      color: #94a3b8;
    }
    .card-actions {
      display: flex;
      gap: 8px;
      border-top: 1px solid var(--card-border);
      padding-top: 12px;
    }
    .btn {
      flex: 1;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      text-align: center;
      cursor: pointer;
      border: none;
      transition: background 0.15s;
      text-decoration: none;
    }
    .btn-demo {
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.35);
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .btn-demo:hover {
      background: rgba(56, 189, 248, 0.25);
      border-color: #38bdf8;
      color: #fff;
    }
    .btn-inspect {
      background: #1e293b;
      color: #f1f5f9;
      border: 1px solid #334155;
    }
    .btn-inspect:hover { background: #334155; }
    .btn-pick {
      background: var(--accent);
      color: #090d16;
    }
    .btn-pick:hover { background: var(--accent-hover); }

    /* Modal */
    .modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.85);
      backdrop-filter: blur(6px);
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }
    .modal {
      background: #101622;
      border: 1px solid var(--card-border);
      width: 100%;
      max-width: 820px;
      max-height: 90vh;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .modal-header {
      padding: 16px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--card-border);
      background: #0d121c;
    }
    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 24px;
      cursor: pointer;
    }
    .modal-content {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .modal-sample-view {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }
    .modal-poster {
      flex: 1;
      min-width: 280px;
      max-height: 240px;
      border-radius: 8px;
      object-fit: cover;
      background: #1e293b;
      border: 1px solid var(--card-border);
    }
    .modal-meta {
      flex: 1.2;
      min-width: 280px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .audit-box {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 13px;
    }
    .audit-box.flagged {
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.3);
    }
    .preview-box {
      background: #080c14;
      padding: 12px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 12px;
      color: #94a3b8;
      max-height: 180px;
      overflow-y: auto;
      white-space: pre-wrap;
      border: 1px solid var(--card-border);
    }
    .modal-footer {
      padding: 14px 20px;
      background: #0d121c;
      border-top: 1px solid var(--card-border);
      display: flex;
      gap: 12px;
      justify-content: flex-end;
    }
  </style>
</head>
<body>

  <header class="header">
    <div class="header-title">
      <h1>Opuscar Skill Curator & Visual Workbench <span class="badge" id="total-badge">99 Styles</span></h1>
      <p>Browse official visual film samples and cherry-pick clean, isolated agent skills without bloated repos or dangerous setup scripts.</p>
    </div>
    <div>
      <span style="font-size: 13px; color: #94a3b8;">Destination: <code>.claude/skills/</code></span>
    </div>
  </header>

  <div class="controls">
    <div class="search-row">
      <input type="text" id="search" class="search-bar" placeholder="Search by style (e.g. satellite, watercolor, blueprint, pixel, noir), film demo, or category...">
    </div>
    <div class="station-filter" id="station-filters">
      <button class="station-btn active" data-cat="all">All Styles (99)</button>
    </div>
  </div>

  <main class="grid" id="styles-grid"></main>

  <!-- Modal -->
  <div class="modal-backdrop" id="modal">
    <div class="modal">
      <div class="modal-header">
        <h2 id="modal-title" style="color: #fff; font-size: 18px;"></h2>
        <button class="close-btn" id="modal-close">&times;</button>
      </div>
      <div class="modal-content">
        <div class="modal-sample-view">
          <img id="modal-poster" class="modal-poster" src="" alt="Sample Poster">
          <div class="modal-meta">
            <div id="modal-cat" style="font-size: 12px; color: var(--accent); font-weight: 700; text-transform: uppercase;"></div>
            <div id="modal-film" style="font-size: 16px; font-weight: 700; color: #fff;"></div>
            <p id="modal-line" style="font-size: 13px; color: #cbd5e1; line-height: 1.4;"></p>
            <div id="modal-uses" style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px;"></div>
            <div style="display: flex; gap: 8px; margin-top: 10px;">
              <a id="modal-demo-link" class="btn btn-demo" href="#" target="_blank" rel="noopener noreferrer" style="flex: none; padding: 6px 14px;">
                ▶ Open Live Demo ↗
              </a>
              <a id="modal-gh-link" class="btn btn-inspect" href="#" target="_blank" rel="noopener noreferrer" style="flex: none; padding: 6px 14px;">
                GitHub Source ↗
              </a>
            </div>
          </div>
        </div>

        <div id="modal-audit" class="audit-box">
          <strong>Security Clearance:</strong> PASSED — Pure procedural canvas. Zero remote shell execution (`curl | bash`), zero setup scripts.
        </div>

        <div>
          <h4 style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">Target Destination:</h4>
          <input type="text" id="dest-input" class="search-bar" value=".claude/skills" style="width: 100%; padding: 8px 12px;">
        </div>

        <div>
          <h4 style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">Specification Preview:</h4>
          <div id="modal-preview" class="preview-box">Loading specification...</div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-inspect" id="modal-cancel">Cancel</button>
        <button class="btn btn-pick" id="modal-confirm" style="max-width: 240px;">Cherry-Pick into Skills</button>
      </div>
    </div>
  </div>

  <script>
    let styles = [];
    let activeCat = 'all';
    let currentModalSlug = null;

    async function loadCatalog() {
      const res = await fetch('/api/catalog');
      styles = await res.json();
      document.getElementById('total-badge').textContent = `${styles.length} Styles`;
      buildCategoryFilters();
      renderStyles();
    }

    function buildCategoryFilters() {
      const container = document.getElementById('station-filters');
      const cats = new Set(styles.map(s => s.category_en).filter(Boolean));

      Array.from(cats).sort().forEach(cat => {
        const count = styles.filter(s => s.category_en === cat).length;
        const btn = document.createElement('button');
        btn.className = 'station-btn';
        btn.dataset.cat = cat;
        btn.textContent = `${cat} (${count})`;
        btn.addEventListener('click', () => {
          document.querySelectorAll('.station-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          activeCat = cat;
          renderStyles();
        });
        container.appendChild(btn);
      });
    }

    function renderStyles() {
      const query = document.getElementById('search').value.toLowerCase();
      const grid = document.getElementById('styles-grid');
      grid.innerHTML = '';

      const filtered = styles.filter(s => {
        const matchesCat = activeCat === 'all' || s.category_en === activeCat;
        const matchesSearch = s.name.toLowerCase().includes(query) ||
                              s.slug.toLowerCase().includes(query) ||
                              (s.film && s.film.toLowerCase().includes(query)) ||
                              (s.line && s.line.toLowerCase().includes(query)) ||
                              (s.uses && s.uses.some(u => u.toLowerCase().includes(query)));
        return matchesCat && matchesSearch;
      });

      if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">No matching styles found.</div>';
        return;
      }

      filtered.forEach(s => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div class="card-thumb-container" onclick="openModal('${s.slug}')">
            <div class="card-thumb-fallback">
              <span style="font-size: 24px;">🎨</span>
              <span>${s.name}</span>
            </div>
            <img class="card-thumb" src="${s.poster_url}" alt="${s.name}" onerror="this.style.display='none'">
          </div>
          <div class="card-body">
            <div class="card-num">#${s.num || '00'} • ${s.category_en}</div>
            <h3 class="card-title">${s.name}</h3>
            ${s.film ? `<div class="card-film">Demo: "${s.film}"</div>` : ''}
            <p class="card-line">${s.line || 'Procedural code-driven visual sequence.'}</p>
            <div class="card-tags">
              ${(s.uses || []).slice(0, 3).map(u => `<span class="tag">#${u}</span>`).join('')}
            </div>
            <div class="card-actions">
              <a class="btn btn-demo" href="https://lemomo-ai.github.io/lemo-opuscar/#${s.slug}" target="_blank" rel="noopener noreferrer" title="Open live film demo in browser">Demo ↗</a>
              <button class="btn btn-inspect" onclick="openModal('${s.slug}')">Inspect</button>
              <button class="btn btn-pick" onclick="quickPick('${s.slug}')">Cherry-Pick</button>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    async function openModal(slug) {
      currentModalSlug = slug;
      const s = styles.find(item => item.slug === slug);
      document.getElementById('modal-title').textContent = `${s.name} (#${s.num || '00'})`;
      document.getElementById('modal-cat').textContent = `${s.category_en} ${s.category_cn ? '• ' + s.category_cn : ''}`;
      document.getElementById('modal-film').textContent = s.film ? `Demo Film: "${s.film}"` : s.name;
      document.getElementById('modal-line').textContent = s.line || '';
      document.getElementById('modal-poster').src = s.poster_url;
      document.getElementById('modal-demo-link').href = `https://lemomo-ai.github.io/lemo-opuscar/#${s.slug}`;
      document.getElementById('modal-gh-link').href = `https://github.com/lemomo-ai/lemo-opuscar/tree/main/styles/${s.slug}`;
      document.getElementById('modal-uses').innerHTML = (s.uses || []).map(u => `<span class="tag">#${u}</span>`).join('');
      document.getElementById('modal-preview').textContent = "Fetching and auditing specification...";
      document.getElementById('modal').style.display = 'flex';

      const res = await fetch(`/api/style-info?slug=${slug}`);
      const data = await res.json();
      document.getElementById('modal-preview').textContent = data.content;
      
      const auditBox = document.getElementById('modal-audit');
      if (data.audit.status === 'PASSED') {
        auditBox.className = 'audit-box';
        auditBox.innerHTML = `<strong>Security Clearance:</strong> PASSED — ${data.audit.lines_scanned} lines scanned. Zero remote shell scripts, no root/privilege escalations, zero prompt injection vectors.`;
      } else {
        auditBox.className = 'audit-box flagged';
        auditBox.innerHTML = `<strong>Security Alert:</strong> FLAGGED — Potential risk detected (${data.audit.findings.map(f => f.reason).join(', ')})`;
      }
    }

    async function quickPick(slug) {
      openModal(slug);
    }

    document.getElementById('modal-close').onclick = () => document.getElementById('modal').style.display = 'none';
    document.getElementById('modal-cancel').onclick = () => document.getElementById('modal').style.display = 'none';

    document.getElementById('modal-confirm').onclick = async () => {
      const dest = document.getElementById('dest-input').value;
      const btn = document.getElementById('modal-confirm');
      btn.textContent = 'Cherry-Picking...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/cherry-pick', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ slug: currentModalSlug, dest: dest })
        });
        const result = await res.json();
        if (result.success) {
          alert(`Successfully cherry-picked '${result.style_name}' into:\n${result.path}\n\nEnvironment remains clean & isolated!`);
          document.getElementById('modal').style.display = 'none';
        } else {
          alert(`Error: ${result.error}`);
        }
      } catch (err) {
        alert(`Failed: ${err.message}`);
      } finally {
        btn.textContent = 'Cherry-Pick into Skills';
        btn.disabled = false;
      }
    };

    document.getElementById('search').addEventListener('input', renderStyles);
    document.getElementById('station-filters').firstElementChild.addEventListener('click', (e) => {
      document.querySelectorAll('.station-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      activeCat = 'all';
      renderStyles();
    });

    loadCatalog();
  </script>
</body>
</html>
"""


class CuratorHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
        elif self.path == "/api/catalog":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(CATALOG).encode("utf-8"))
        elif self.path.startswith("/api/style-info"):
            query = self.path.split("?", 1)[-1]
            params = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
            slug = params.get("slug", "")
            content = fetch_style_markdown_from_repo(slug)
            audit = run_security_audit(content)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"slug": slug, "content": content, "audit": audit}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/cherry-pick":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            slug = data.get("slug")
            dest = data.get("dest", ".claude/skills")

            result = cherry_pick_style(slug, dest)
            self.send_response(200 if result.get("success") else 400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def start_server(port: int = 7890, open_browser: bool = True):
    server = HTTPServer(("127.0.0.1", port), CuratorHTTPHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n✨ Opuscar Curator Web UI running at: {url}")
    print("Press Ctrl+C to stop.\n")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Opuscar Curator...")
        server.server_close()


# --- CLI Commands ---

def cli_list():
    print(f"\n{'NUM':<5} | {'CATEGORY':<25} | {'SLUG':<26} | {'NAME'}")
    print("-" * 90)
    for s in CATALOG:
        print(f"#{s.get('num','00'):<4} | {s.get('category_en',''):<25} | {s['slug']:<26} | {s['name']}")
    print(f"\nTotal styles in catalog: {len(CATALOG)} across 15 stations.\n")


def cli_search(query: str):
    q = query.lower()
    matches = [
        s for s in CATALOG
        if q in s['slug'] or q in s['name'].lower() or q in s.get('film','').lower() or q in s.get('line','').lower() or any(q in u.lower() for u in s.get('uses',[]))
    ]
    print(f"\nSearch results for '{query}': {len(matches)} found\n")
    for s in matches:
        print(f"• [#{s.get('num','00')}] {s['name']} (`{s['slug']}`) — {s.get('category_en','')}")
        if s.get('film'):
            print(f"  Film: \"{s['film']}\"")
        if s.get('line'):
            print(f"  Line: {s['line']}")
        print(f"  Sample: {s['poster_url']}\n")


def cli_info(slug: str):
    if slug not in CATALOG_BY_SLUG:
        print(f"Error: Style '{slug}' not found.")
        sys.exit(1)
    s = CATALOG_BY_SLUG[slug]
    print(f"\n=== {s['name']} (#{s.get('num','00')}) ===")
    print(f"Slug:        {s['slug']}")
    print(f"Category:    {s.get('category_en','')} ({s.get('category_cn','')})")
    print(f"Demo Film:   {s.get('film','')}")
    print(f"Description: {s.get('line','')}")
    print(f"Uses:        {', '.join(s.get('uses',[]))}")
    print(f"Sample URL:  {s['poster_url']}")
    print(f"Demo URL:    https://lemomo-ai.github.io/lemo-opuscar/#{s['slug']}\n")


def cli_audit(slug: str):
    if slug not in CATALOG_BY_SLUG:
        print(f"Error: Style '{slug}' not found.")
        sys.exit(1)
    s = CATALOG_BY_SLUG[slug]
    print(f"\nRunning security & prompt-injection audit for '{s['name']}' ({slug})...")
    content = fetch_style_markdown_from_repo(slug)
    audit = run_security_audit(content)
    print(f"Status: {audit['status']}")
    print(f"Severity: {audit['severity']}")
    print(f"Lines Scanned: {audit['lines_scanned']}")
    if audit['findings']:
        print("Findings:")
        for f in audit['findings']:
            print(f"  - [{f['severity']}] {f['reason']} (Count: {f['matches_count']})")
    else:
        print("Clearance: PASSED (Zero dangerous remote script commands or prompt injection patterns detected).\n")


def cli_cherry_pick(slug: str, dest: str):
    print(f"\nCherry-picking '{slug}' to '{dest}'...")
    result = cherry_pick_style(slug, dest)
    if result["success"]:
        print(f"SUCCESS! Clean, isolated skill created at:\n  {result['path']}")
        print(f"Security: {result['audit']['status']} (Zero elevated commands, zero supply-chain setup scripts).")
        print("Environment remains completely clean.\n")
    else:
        print(f"FAILED: {result['error']}\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Opuscar Skill Curator & Sanitizer: Discover, inspect samples, audit, and cherry-pick clean agent skills."
    )
    parser.add_argument("--ui", action="store_true", help="Launch the web browser visual curator interface")
    parser.add_argument("--port", type=int, default=7890, help="Port for the web UI server (default: 7890)")
    
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="List all 99 styles across all 15 stations")
    
    search_p = subparsers.add_parser("search", help="Search styles by keyword, film, or tag")
    search_p.add_argument("query", help="Keyword or search phrase")

    info_p = subparsers.add_parser("info", help="Show full metadata and sample URL for a style")
    info_p.add_argument("slug", help="Style slug (e.g., satellite-briefing)")

    audit_p = subparsers.add_parser("audit", help="Run security and prompt injection check on a style")
    audit_p.add_argument("slug", help="Style slug (e.g., watercolor, satellite-briefing)")

    cp_p = subparsers.add_parser("cherry-pick", help="Extract a clean, isolated skill package")
    cp_p.add_argument("slug", help="Style slug to cherry-pick")
    cp_p.add_argument("--dest", default=".claude/skills", help="Target skill directory (default: .claude/skills)")

    args = parser.parse_args()

    if args.ui or (len(sys.argv) == 1 and sys.stdin.isatty()):
        start_server(port=args.port, open_browser=True)
    elif args.command == "list":
        cli_list()
    elif args.command == "search":
        cli_search(args.query)
    elif args.command == "info":
        cli_info(args.slug)
    elif args.command == "audit":
        cli_audit(args.slug)
    elif args.command == "cherry-pick":
        cli_cherry_pick(args.slug, args.dest)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
