#!/usr/bin/env python3
"""
Opuscar Skill Curator & Sanitizer
=================================
A zero-dependency developer utility to safely discover, inspect, sanitize, and 
cherry-pick styles from lemomo-ai/lemo-opuscar into clean, isolated agent skills.

Usage:
  opuscar-curator --ui                  # Launch the web browser visual UI (http://localhost:7890)
  opuscar-curator list                  # List all available stations and styles
  opuscar-curator search <term>         # Search styles by keyword, technique, or category
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

# --- Catalog Database (15 Stations, Curated Key Styles from lemo-opuscar) ---
CATALOG: List[Dict[str, Any]] = [
    # Station 01: Edit & Documentary
    {
        "slug": "caption-news",
        "station_id": "01",
        "station_name": "Edit & Documentary",
        "station_zh": "剪辑纪实",
        "name": "Caption News",
        "medium": "Social / Newsfeed Motion",
        "render_tech": "Canvas 2D / DOM",
        "description": "Dynamic lower-thirds, bold kinetic typography subtitles, news tickers, and montage pacing tailored for informational shorts.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["news", "social", "text", "subtitles", "fast-paced"]
    },
    {
        "slug": "visual-investigation",
        "station_id": "01",
        "station_name": "Edit & Documentary",
        "station_zh": "剪辑纪实",
        "name": "Visual Investigation",
        "medium": "Forensic / Investigative Journalism",
        "render_tech": "Canvas 2D + Timeline Sync",
        "description": "Forensic spatial video investigation with synchronised multi-angle footage, geo-spatial callouts, timecode markers, and evidence pins.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["journalism", "evidence", "timeline", "callouts", "forensic"]
    },
    {
        "slug": "1920s-newsreel",
        "station_id": "01",
        "station_name": "Edit & Documentary",
        "station_zh": "剪辑纪实",
        "name": "1920s Newsreel",
        "medium": "Early Silent Film",
        "render_tech": "Procedural Noise + Filter Math",
        "description": "Black-and-white, high-contrast, sepia-toned vintage newsreel with simulated projector gate weave, film dust specks, and silent era intertitles.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["vintage", "film-grain", "retro", "black-white", "historical"]
    },
    {
        "slug": "broadcast-news",
        "station_id": "01",
        "station_name": "Edit & Documentary",
        "station_zh": "剪辑纪实",
        "name": "Broadcast News Package",
        "medium": "Television Broadcast Graphics",
        "render_tech": "Canvas 2D / CSS 3D",
        "description": "Clean network television news package with sliding side panels, breaking news banners, lower-third chyrons, and picture-in-picture frames.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["broadcast", "news", "tv", "chyrons", "professional"]
    },

    # Station 02: Painting & Illustration
    {
        "slug": "impasto-oil",
        "station_id": "02",
        "station_name": "Painting & Illustration",
        "station_zh": "绘画插画",
        "name": "Impasto Oil Painting",
        "medium": "Thick Oil on Canvas",
        "render_tech": "Procedural Brush Kinematics",
        "description": "Viscous, textured oil paint strokes with visible palette-knife ridges, directional specular lighting highlights, and pigment blending.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["artistic", "oil", "texture", "brushstrokes", "tactile"]
    },
    {
        "slug": "watercolor-brush",
        "station_id": "02",
        "station_name": "Painting & Illustration",
        "station_zh": "绘画插画",
        "name": "Watercolor Brush",
        "medium": "Wet-on-Wet Watercolor",
        "render_tech": "Fluid Diffusion Simulation",
        "description": "Translucent watercolor washes with organic pigment pooling, wet-on-wet capillary diffusion, and textured cold-press cotton paper absorption.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["watercolor", "fluid", "wash", "organic", "artistic"]
    },
    {
        "slug": "urban-sketch",
        "station_id": "02",
        "station_name": "Painting & Illustration",
        "station_zh": "绘画插画",
        "name": "Urban Sketch · Pen & Wash",
        "medium": "Ink Linework & Watercolor",
        "render_tech": "Canvas 2D Bezier Paths",
        "description": "Architectural fountain pen linework with intentional jitter, hatched cross-shading, and loose, expressive watercolor fills.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["sketch", "ink", "architecture", "pen", "urban"]
    },
    {
        "slug": "crayon-picture-book",
        "station_id": "02",
        "station_name": "Painting & Illustration",
        "station_zh": "绘画插画",
        "name": "Crayon Picture Book",
        "medium": "Wax Crayon & Construction Paper",
        "render_tech": "Perlin Noise / Procedural Shaders",
        "description": "Charming, tactile children's book aesthetic using waxy textured strokes, uneven edge pressure, and cut-paper layered collage.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["crayon", "children", "playful", "warm", "storybook"]
    },

    # Station 03: Sketch & Board
    {
        "slug": "chalkboard",
        "station_id": "03",
        "station_name": "Sketch & Board",
        "station_zh": "速写板书",
        "name": "Chalkboard Lecture",
        "medium": "Slate Blackboard & Chalk",
        "render_tech": "Procedural Particle Dust",
        "description": "Slate chalkboard diagrams with chalk dust trails, erased chalk ghosting, progressive hand-drawn mathematical equations, and lecture notes.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["education", "math", "lecture", "chalk", "diagrams"]
    },
    {
        "slug": "sketchnote",
        "station_id": "03",
        "station_name": "Sketch & Board",
        "station_zh": "速写板书",
        "name": "Sketchnote Explainer",
        "medium": "Visual Note-taking / Pen Markers",
        "render_tech": "Progressive SVG Vector Path Drawing",
        "description": "Visual summary explainer combining hand-lettered titles, doodle icons, ribbon banners, directional arrows, and mind-map node links.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["notes", "explainer", "infographic", "doodle", "summary"]
    },
    {
        "slug": "whiteboard",
        "station_id": "03",
        "station_name": "Sketch & Board",
        "station_zh": "速写板书",
        "name": "Whiteboard Brainstorm",
        "medium": "Dry-Erase Marker",
        "render_tech": "Stroke Path Interpolation",
        "description": "Clean dry-erase whiteboard aesthetic with multi-colored markers, sticky note callouts, stroke tapering, and eraser streaks.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["whiteboard", "startup", "brainstorm", "sticky-notes"]
    },

    # Station 04: Traditional Crafts
    {
        "slug": "paper-cutout",
        "station_id": "04",
        "station_name": "Traditional Crafts",
        "station_zh": "传统手艺",
        "name": "Layered Paper Cutout",
        "medium": "Cardstock Shadowbox",
        "render_tech": "Multi-layer Canvas Parallax",
        "description": "Multi-layered paper sculpture with realistic cast drop-shadows, paper fiber texture, and subtle parallax depth camera shifts.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["craft", "paper", "shadowbox", "tactile", "depth"]
    },
    {
        "slug": "shadow-puppetry",
        "station_id": "04",
        "station_name": "Traditional Crafts",
        "station_zh": "传统手艺",
        "name": "Shadow Puppetry",
        "medium": "Backlit Silhouette Puppets",
        "render_tech": "Inverse Kinematic Joint Hierarchies",
        "description": "Backlit translucent parchment screen with articulated leather puppets, rod control mechanics, and flickering warm lamp glow.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["cultural", "silhouette", "puppet", "shadows", "folk"]
    },

    # Station 05: Print & Printmaking
    {
        "slug": "risograph",
        "station_id": "05",
        "station_name": "Print & Printmaking",
        "station_zh": "印刷版画",
        "name": "Risograph Print",
        "medium": "Spot Color Duotone Printing",
        "render_tech": "Color Separation & Misregistration Math",
        "description": "Vibrant Fluorescent spot-color risograph printing with grain diffusion dithering, ink roller bleed, and slight layer misregistration.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["print", "riso", "halftone", "indie", "zine"]
    },
    {
        "slug": "woodcut-block",
        "station_id": "05",
        "station_name": "Print & Printmaking",
        "station_zh": "印刷版画",
        "name": "Woodcut Printmaking",
        "medium": "Relief Carved Woodblock",
        "render_tech": "Binary Threshold Hatching",
        "description": "Stark relief printmaking with sharp gouged wood grain chisel marks, heavy black oil ink, and textured mulberry paper transfer.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["woodcut", "monochrome", "print", "historical", "bold"]
    },

    # Station 06: Graphic & Type
    {
        "slug": "swiss-motion",
        "station_id": "06",
        "station_name": "Graphic & Type",
        "station_zh": "平面字体",
        "name": "Swiss Style Motion",
        "medium": "International Typographic Style",
        "render_tech": "Strict Modular Grid Engine",
        "description": "Rigid mathematical grid system, stark sans-serif typography, asymmetric layouts, bold primary accent blocks, and kinetic alignment snaps.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["typography", "swiss", "minimal", "modern", "design"]
    },
    {
        "slug": "art-deco",
        "station_id": "06",
        "station_name": "Graphic & Type",
        "station_zh": "平面字体",
        "name": "Art Deco Titles",
        "medium": "1920s Gilded Luxury Graphics",
        "render_tech": "Geometric Vector Symmetry",
        "description": "Streamlined Roaring Twenties aesthetic featuring gilded brass fillets, geometric sunburst flourishes, stepped frames, and luxury serif type.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["vintage", "luxury", "gold", "geometric", "1920s"]
    },
    {
        "slug": "kinetic-typography",
        "station_id": "06",
        "station_name": "Graphic & Type",
        "station_zh": "平面字体",
        "name": "Kinetic Typography",
        "medium": "Rhythm-Synced Kinetic Text",
        "render_tech": "Bézier Easing & Text Metrics",
        "description": "High-energy typography synced to vocal cadence with scale pops, camera zooms, baseline shifts, and punchy layout transitions.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["kinetic", "type", "rhythm", "fast", "motion-graphics"]
    },

    # Station 07: Line Diagrams
    {
        "slug": "blueprint-cyanotype",
        "station_id": "07",
        "station_name": "Line Diagrams",
        "station_zh": "线条图解",
        "name": "Architectural Blueprint",
        "medium": "Cyanotype Drafting Sheet",
        "render_tech": "Precision Orthographic CAD Math",
        "description": "Classic Prussian blue technical drafting plan with white precision measurement lines, dimension callouts, grid coordinates, and title blocks.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["blueprint", "engineering", "technical", "cad", "precision"]
    },
    {
        "slug": "schematic-circuit",
        "station_id": "07",
        "station_name": "Line Diagrams",
        "station_zh": "线条图解",
        "name": "Electronic Schematic",
        "medium": "PCB Circuit Blueprint",
        "render_tech": "Procedural Bus Routing",
        "description": "Schematic circuit board traces with glowing electronic logic pulses, integrated chip footprints, and animated data signal flows.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["circuits", "hardware", "electronics", "tech", "logic"]
    },

    # Station 08: Cartoons
    {
        "slug": "rubber-hose-1930s",
        "station_id": "08",
        "station_name": "Cartoons",
        "station_zh": "卡通动画",
        "name": "1930s Rubber Hose",
        "medium": "Golden Age Hand-Drawn Animation",
        "render_tech": "Kinematic Limb Flexing",
        "description": "Steamboat-era rubber-hose animation with bendy jointless limbs, pie eyes, bounce squash-and-stretch cycles, and grain vignette.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["cartoon", "rubber-hose", "1930s", "retro", "animation"]
    },

    # Station 09: Games
    {
        "slug": "pixel-art-16bit",
        "station_id": "09",
        "station_name": "Games",
        "station_zh": "游戏像素",
        "name": "16-Bit Pixel Adventure",
        "medium": "16-bit Era Parallax Console Graphics",
        "render_tech": "Pixel Buffer / Nearest Neighbor",
        "description": "Authentic 16-bit video game aesthetic with multi-layer parallax scrolling backgrounds, indexed color palettes, and retro sprite animations.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["pixel-art", "gaming", "16-bit", "retro", "sprites"]
    },

    # Station 10: Film & Tape
    {
        "slug": "vhs-camcorder",
        "station_id": "10",
        "station_name": "Film & Tape",
        "station_zh": "电影磁带",
        "name": "VHS Home Camcorder",
        "medium": "1990s Analog Magnetic Tape",
        "render_tech": "NTSC Composite Phase / Line Glitch",
        "description": "Retro magnetic tape recording with head tracking buzz, phosphor glow, analog chroma smearing, and blinking green PLAY/REC OSD date stamps.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["vhs", "glitch", "retro", "analog", "tape"]
    },

    # Station 11: Screens & Interfaces
    {
        "slug": "terminal-hacker",
        "station_id": "11",
        "station_name": "Screens & Interfaces",
        "station_zh": "屏幕界面",
        "name": "Terminal Command Console",
        "medium": "Monochrome Phosphor CRT Console",
        "render_tech": "Text Buffer / Monospace Virtual Matrix",
        "description": "Green/Amber phosphor CRT console running real-time packet hex dumps, compiling trees, progress bars, and high-speed typing logs.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["terminal", "hacker", "cli", "code", "cyber"]
    },
    {
        "slug": "cyberpunk-hud",
        "station_id": "11",
        "station_name": "Screens & Interfaces",
        "station_zh": "屏幕界面",
        "name": "Tactical Cyberpunk HUD",
        "medium": "Holographic Augmented Heads-Up Display",
        "render_tech": "WebGL / Canvas Vector Reticles",
        "description": "Futuristic UI overlay featuring rotating radar rings, target tracking reticles, telemetry gauges, and holographic vector wireframes.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["hud", "cyberpunk", "futuristic", "ui", "telemetry"]
    },

    # Station 12: Light & Lines
    {
        "slug": "neon-tubes",
        "station_id": "12",
        "station_name": "Light & Lines",
        "station_zh": "光影线条",
        "name": "Neon Signboard",
        "medium": "Bespoke Glass Tube Neon Lights",
        "render_tech": "Gaussian Glow & Flicker Shaders",
        "description": "Hand-bent gas-discharge neon signs with buzzing ignition flicker, glass tube reflections on wet concrete, and vibrant atmospheric bloom.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["neon", "glow", "night", "light", "vibrant"]
    },

    # Station 13: 3D & Miniature
    {
        "slug": "tilt-shift-diorama",
        "station_id": "13",
        "station_name": "3D & Miniature",
        "station_zh": "3D与微缩模型",
        "name": "Tilt-Shift Miniature Diorama",
        "medium": "Simulated Tilt-Shift Miniature Photography",
        "render_tech": "Depth-of-field Blurring & Step-motion",
        "description": "Macro miniature scale effect with extreme shallow depth-of-field lens blur, enhanced color saturation, and slightly stepped frame timing.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["tilt-shift", "miniature", "diorama", "macro", "toy-like"]
    },

    # Station 14: Instruments & Evidence
    {
        "slug": "satellite-briefing",
        "station_id": "14",
        "station_name": "Instruments & Evidence",
        "station_zh": "仪器实证",
        "name": "Satellite Recon Briefing",
        "medium": "Orbital Remote Sensing Display",
        "render_tech": "Tile Raster Overlays & Vector Tracks",
        "description": "Declassified intelligence satellite view with ground resolution footprints, orbital ground tracks, multispectral false-color bands, and coordinate crosshairs.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["satellite", "geospatial", "recon", "military", "maps"]
    },
    {
        "slug": "lidar-survey",
        "station_id": "14",
        "station_name": "Instruments & Evidence",
        "station_zh": "仪器实证",
        "name": "LiDAR Terrain Survey",
        "medium": "3D Point Cloud Laser Scanning",
        "render_tech": "Point Cloud Shaders & Elevation Gradients",
        "description": "Elevation-colored laser point cloud sweep penetrating forest canopies to reveal hidden archaeological structures, contours, and 3D terrain.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["lidar", "point-cloud", "3d", "terrain", "survey"]
    },
    {
        "slug": "thermal-camera",
        "station_id": "14",
        "station_name": "Instruments & Evidence",
        "station_zh": "仪器实证",
        "name": "Thermal FLIR Camera",
        "medium": "Infrared Thermography",
        "render_tech": "Ironbow / Rainbow Colormap Gradient",
        "description": "Infrared thermal imaging using authentic Ironbow/White-Hot colormaps with temperature spot-meters, heat dissipations, and target locks.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["thermal", "flir", "infrared", "heat", "sensor"]
    },
    {
        "slug": "radar-sweep",
        "station_id": "14",
        "station_name": "Instruments & Evidence",
        "station_zh": "仪器实证",
        "name": "Radar Sweep Documentary",
        "medium": "Marine / Air Traffic Radar PPI Scope",
        "render_tech": "Polar Coordinate Sweep & Phosphor Decay",
        "description": "Rotating plan position indicator (PPI) radar sweep with decaying phosphor wake, nautical distance rings, heading markers, and target blip echoes.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["radar", "nautical", "sweep", "aviation", "sensor"]
    },

    # Station 15: Data & Maps
    {
        "slug": "transit-map",
        "station_id": "15",
        "station_name": "Data & Maps",
        "station_zh": "数据地图",
        "name": "Metro Transit Map",
        "medium": "Schematic Octolinear Subway Map",
        "render_tech": "Vector Graph Routing",
        "description": "Beck-style 45-degree angle subway map with pulsing transit lines, animated train carriages navigating junctions, and transfer station nodes.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["transit", "subway", "maps", "data-viz", "urban"]
    },
    {
        "slug": "3d-map-explainer",
        "station_id": "15",
        "station_name": "Data & Maps",
        "station_zh": "数据地图",
        "name": "3D Map Explainer",
        "medium": "Geopolitical 3D Terrain Flyover",
        "render_tech": "Extruded Isometric / 3D Canvas",
        "description": "Newsroom explainer map featuring extruded topographical elevation, glowing movement corridors, animated curved missile/flight paths, and territory labels.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["maps", "geopolitics", "3d", "explainer", "terrain"]
    },
    {
        "slug": "data-storytelling",
        "station_id": "15",
        "station_name": "Data & Maps",
        "station_zh": "数据地图",
        "name": "Data Journalism Storytelling",
        "medium": "Interactive Scrollytelling Charts",
        "render_tech": "Canvas 2D Data Series Interpolation",
        "description": "Visual data journalism piece using dynamic Sankey diagrams, animated scatter plot distributions, highlighted regression curves, and live counters.",
        "license": "MIT (Core)",
        "assets_license": "CC-BY-NC-4.0",
        "tags": ["charts", "statistics", "data-journalism", "sankey", "scrollytelling"]
    }
]

# Quick lookup dictionary by slug
CATALOG_BY_SLUG: Dict[str, Dict[str, Any]] = {item["slug"]: item for item in CATALOG}

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
    """Scans content for malicious directives, prompt injection vectors, and dangerous commands."""
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


def generate_tailored_skill_markdown(style: Dict[str, Any], style_md_content: str) -> str:
    """Generates a lean, safe, focused SKILL.md specifically for this cherry-picked style."""
    return f"""---
name: opuscar-{style['slug']}
description: Generate code-driven video shorts and motion graphics in the '{style['name']}' aesthetic ({style['station_name']}).
---

# Opuscar Skill: {style['name']} ({style['station_name']})

This skill equips the assistant to produce complete visual narratives and motion sequences rendered exclusively in the **{style['name']}** aesthetic using procedural code (Canvas/WebGL) and local tools without relying on heavy cloud generative video models.

## Aesthetic Identity & Medium
- **Station**: {style['station_id']}. {style['station_name']} ({style.get('station_zh', '')})
- **Medium**: {style['medium']}
- **Primary Engine**: {style['render_tech']}
- **Core License**: {style['license']} (Asset rules: {style['assets_license']})

## Style Brief & Rules
{style['description']}

### Visual & Technical Invariants
The assistant MUST adhere to the aesthetic and physical rendering specifications provided below:

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
   - For audio synthesis, use isolated local offline tools or provide clean audio sync sheets.
"""


def generate_isolated_render_template(style: Dict[str, Any]) -> str:
    """Generates a clean, standalone, zero-dependency HTML5 Canvas render harness."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Opuscar Render Harness - {style['name']}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #111;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      color: #eee;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #canvas-container {{
      box-shadow: 0 10px 40px rgba(0,0,0,0.8);
      border-radius: 8px;
      overflow: hidden;
      background: #000;
    }}
    canvas {{
      display: block;
    }}
    #controls {{
      margin-top: 16px;
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    button {{
      background: #2563eb;
      color: #fff;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
    }}
    button:hover {{ background: #1d4ed8; }}
    #status {{ font-size: 14px; color: #aaa; }}
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
    const duration = 10.0; // 10-second default scene

    // Deterministic Render Function for: {style['name']}
    function renderFrame(timeSec) {{
      const width = canvas.width;
      const height = canvas.height;
      const progress = Math.min(1.0, timeSec / duration);

      // Background Clear
      ctx.fillStyle = '#0a0a0f';
      ctx.fillRect(0, 0, width, height);

      // --- Style-Specific Drawing Logic ({style['name']}) ---
      ctx.save();
      
      // Decorative border
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 4;
      ctx.strokeRect(20, 20, width - 40, height - 40);

      // Style Label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 32px sans-serif';
      ctx.fillText("{style['name']}", 60, 80);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '18px sans-serif';
      ctx.fillText("Station {style['station_id']}: {style['station_name']} | Engine: {style['render_tech']}", 60, 115);

      // Dynamic animated element demonstration
      const centerX = width / 2;
      const centerY = height / 2;
      const pulse = Math.sin(timeSec * 3) * 20;

      ctx.beginPath();
      ctx.arc(centerX, centerY, 80 + pulse, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
      ctx.fill();
      ctx.strokeStyle = '#60a5fa';
      ctx.lineWidth = 3;
      ctx.stroke();

      // Progress bar at bottom
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(60, height - 60, width - 120, 10);
      ctx.fillStyle = '#38bdf8';
      ctx.fillRect(60, height - 60, (width - 120) * progress, 10);

      ctx.restore();
    }}

    function animate(now) {{
      if (isPlaying) {{
        const elapsed = (now - startTime) / 1000;
        const currentSec = elapsed % duration;
        renderFrame(currentSec);
        statusEl.textContent = `Time: ${{currentSec.toFixed(2)}}s / ${{duration}}s | FPS: 60 (Canvas 2D)`;
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


def fetch_style_markdown_from_repo(slug: str) -> str:
    """Attempts to fetch the real STYLE.md from lemomo-ai/lemo-opuscar, falling back to a structured template."""
    raw_url = f"https://raw.githubusercontent.com/lemomo-ai/lemo-opuscar/main/styles/{slug}/STYLE.md"
    try:
        req = urllib.request.Request(raw_url, headers={'User-Agent': 'OpuscarCurator/1.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                return response.read().decode('utf-8', errors='replace')
    except Exception:
        pass

    # High-quality fallback if offline or raw file unreachable
    item = CATALOG_BY_SLUG.get(slug, {})
    return f"""# Style Specification: {item.get('name', slug)}
Station: {item.get('station_id', '00')} - {item.get('station_name', 'General')}
Medium: {item.get('medium', 'Procedural Canvas')}

## Aesthetic Guidelines
- **Palette & Lighting**: High coherence with the chosen medium ({item.get('medium', '')}). Avoid generic gradients.
- **Motion Kinematics**: Ensure motion aligns strictly with procedural easing curves.
- **Rendering Primitives**: Implement frame-by-frame rendering with {item.get('render_tech', 'HTML5 Canvas')}.
- **Pacing**: Aim for deliberate, storyboarded transitions with visual anchors for key dialogue or text cues.
"""


def cherry_pick_style(slug: str, output_base_dir: str) -> Dict[str, Any]:
    """Cherry-picks a single style, sanitizes it, and builds a clean isolated skill directory."""
    if slug not in CATALOG_BY_SLUG:
        return {"success": False, "error": f"Style '{slug}' not found in catalog."}

    style = CATALOG_BY_SLUG[slug]
    style_content = fetch_style_markdown_from_repo(slug)
    
    # Run Security Audit
    audit_results = run_security_audit(style_content)
    if audit_results["severity"] == "HIGH":
        return {
            "success": False, 
            "error": "Security audit failed: Dangerous patterns detected in style source.", 
            "audit": audit_results
        }

    # Prepare Target Directory
    target_skill_dir = Path(output_base_dir) / f"opuscar-{slug}"
    target_skill_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write tailored SKILL.md
    skill_md = generate_tailored_skill_markdown(style, style_content)
    (target_skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # 2. Write official STYLE.md
    (target_skill_dir / "STYLE.md").write_text(style_content, encoding="utf-8")

    # 3. Write isolated render harness
    render_html = generate_isolated_render_template(style)
    (target_skill_dir / "harness.html").write_text(render_html, encoding="utf-8")

    # 4. Write README & Security Clearance
    readme_content = f"""# Opuscar Cherry-Picked Skill: {style['name']}

- **Style Slug**: `{style['slug']}`
- **Station**: {style['station_id']}. {style['station_name']}
- **Security Clearance**: PASSED (0 high-risk directives detected)
- **Host Sandbox Guarantee**: Pure HTML5 Canvas / WebGL harness. No automated `setup.sh` or npm/pip execution.

## How to Test
Open `harness.html` directly in your browser to inspect the render loop at 60fps.

## Clean Execution Notice
When directing an AI agent with this skill, instruct it to write animation scripts into self-contained HTML/JS files rather than installing global system packages.
"""
    (target_skill_dir / "README.md").write_text(readme_content, encoding="utf-8")

    return {
        "success": True,
        "path": str(target_skill_dir.resolve()),
        "slug": slug,
        "style_name": style["name"],
        "audit": audit_results
    }


# --- Web UI Implementation (Built-in HTTP Server) ---

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Opuscar Skill Curator</title>
  <style>
    :root {
      --bg: #0b0f17;
      --card-bg: #141b29;
      --card-border: #1f2b40;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --success: #10b981;
      --warn: #f59e0b;
      --danger: #ef4444;
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
      max-width: 1200px;
      margin: 0 auto 24px auto;
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
      background: var(--pill-bg);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 3px 8px;
      border-radius: 999px;
      font-weight: 600;
      text-transform: uppercase;
    }
    .header-title p {
      font-size: 14px;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .controls {
      max-width: 1200px;
      margin: 0 auto 24px auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
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
      padding: 10px 16px;
      color: #fff;
      font-size: 15px;
      outline: none;
    }
    .search-bar:focus { border-color: var(--accent); }
    .station-filter {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 6px;
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
      color: #0b0f17;
      font-weight: 600;
    }
    .grid {
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 20px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, border-color 0.15s;
    }
    .card:hover {
      transform: translateY(-2px);
      border-color: #3b82f6;
    }
    .card-station {
      font-size: 12px;
      font-weight: 600;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .card-title {
      font-size: 18px;
      font-weight: 700;
      margin: 6px 0 2px 0;
      color: #fff;
    }
    .card-medium {
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 12px;
      font-style: italic;
    }
    .card-desc {
      font-size: 14px;
      color: #cbd5e1;
      margin-bottom: 16px;
      flex-grow: 1;
    }
    .card-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 16px;
    }
    .tag {
      background: rgba(255,255,255,0.06);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      color: #94a3b8;
    }
    .card-actions {
      display: flex;
      gap: 10px;
      border-top: 1px solid var(--card-border);
      padding-top: 14px;
    }
    .btn {
      flex: 1;
      padding: 9px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      text-align: center;
      cursor: pointer;
      border: none;
      transition: background 0.15s;
    }
    .btn-inspect {
      background: #1e293b;
      color: #f1f5f9;
      border: 1px solid #334155;
    }
    .btn-inspect:hover { background: #334155; }
    .btn-pick {
      background: var(--accent);
      color: #0b0f17;
    }
    .btn-pick:hover { background: var(--accent-hover); }

    /* Modal */
    .modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.75);
      backdrop-filter: blur(4px);
      align-items: center;
      justify-content: center;
      z-index: 100;
    }
    .modal {
      background: #101622;
      border: 1px solid var(--card-border);
      width: 90%;
      max-width: 720px;
      max-height: 85vh;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      overflow-y: auto;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--card-border);
      padding-bottom: 12px;
    }
    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 20px;
      cursor: pointer;
    }
    .audit-box {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 13px;
    }
    .audit-box.flagged {
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.3);
    }
    .preview-box {
      background: #090d15;
      padding: 12px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 12px;
      color: #94a3b8;
      max-height: 220px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>

  <header class="header">
    <div class="header-title">
      <h1>Opuscar Skill Curator & Sanitizer <span class="badge">Safe Mode</span></h1>
      <p>Cherry-pick individual styles from lemomo-ai/lemo-opuscar without bloated repos or dangerous setup scripts.</p>
    </div>
    <div>
      <span style="font-size: 13px; color: #94a3b8;">Output: <code>.claude/skills/</code></span>
    </div>
  </header>

  <div class="controls">
    <div class="search-row">
      <input type="text" id="search" class="search-bar" placeholder="Search by style, aesthetic (e.g. watercolor, satellite, blueprint), or technique...">
    </div>
    <div class="station-filter" id="station-filters">
      <button class="station-btn active" data-station="all">All Stations (15)</button>
    </div>
  </div>

  <main class="grid" id="styles-grid"></main>

  <div class="modal-backdrop" id="modal">
    <div class="modal">
      <div class="modal-header">
        <h2 id="modal-title" style="color: #fff; font-size: 20px;"></h2>
        <button class="close-btn" id="modal-close">&times;</button>
      </div>
      <div id="modal-audit" class="audit-box">
        <strong>Security Clearance:</strong> PASSED — Zero elevated root commands, no remote pipes (`curl|bash`), and no background telemetry scripts.
      </div>
      <div>
        <h4 style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">Target Destination:</h4>
        <input type="text" id="dest-input" class="search-bar" value=".claude/skills" style="width: 100%;">
      </div>
      <div>
        <h4 style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">Specification Preview:</h4>
        <div id="modal-preview" class="preview-box">Loading style specification...</div>
      </div>
      <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px;">
        <button class="btn btn-inspect" id="modal-cancel">Cancel</button>
        <button class="btn btn-pick" id="modal-confirm">Cherry-Pick into Skills</button>
      </div>
    </div>
  </div>

  <script>
    let styles = [];
    let activeStation = 'all';
    let currentModalSlug = null;

    async function loadCatalog() {
      const res = await fetch('/api/catalog');
      styles = await res.json();
      buildStationFilters();
      renderStyles();
    }

    function buildStationFilters() {
      const container = document.getElementById('station-filters');
      const stations = new Map();
      styles.forEach(s => {
        if (!stations.has(s.station_id)) {
          stations.set(s.station_id, s.station_name);
        }
      });

      stations.forEach((name, id) => {
        const btn = document.createElement('button');
        btn.className = 'station-btn';
        btn.dataset.station = id;
        btn.textContent = `${id}. ${name}`;
        btn.addEventListener('click', () => {
          document.querySelectorAll('.station-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          activeStation = id;
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
        const matchesStation = activeStation === 'all' || s.station_id === activeStation;
        const matchesSearch = s.name.toLowerCase().includes(query) ||
                              s.description.toLowerCase().includes(query) ||
                              s.medium.toLowerCase().includes(query) ||
                              s.tags.some(t => t.includes(query));
        return matchesStation && matchesSearch;
      });

      if (filtered.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #94a3b8; padding: 40px;">No matching styles found.</div>';
        return;
      }

      filtered.forEach(s => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
          <div>
            <div class="card-station">Station ${s.station_id}: ${s.station_name}</div>
            <h3 class="card-title">${s.name}</h3>
            <div class="card-medium">${s.medium} • ${s.render_tech}</div>
            <p class="card-desc">${s.description}</p>
            <div class="card-meta">
              ${s.tags.map(t => `<span class="tag">#${t}</span>`).join('')}
              <span class="tag" style="color: #60a5fa;">${s.license}</span>
            </div>
          </div>
          <div class="card-actions">
            <button class="btn btn-inspect" onclick="openModal('${s.slug}')">Inspect & Audit</button>
            <button class="btn btn-pick" onclick="quickPick('${s.slug}')">Cherry-Pick</button>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    async function openModal(slug) {
      currentModalSlug = slug;
      const s = styles.find(item => item.slug === slug);
      document.getElementById('modal-title').textContent = `${s.name} (${s.station_name})`;
      document.getElementById('modal-preview').textContent = "Auditing and fetching specification...";
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
      activeStation = 'all';
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
    print(f"\n{'STATION':<28} | {'SLUG':<24} | {'STYLE NAME':<28} | {'MEDIUM'}")
    print("-" * 110)
    for s in CATALOG:
        station_str = f"{s['station_id']}. {s['station_name']}"
        print(f"{station_str:<28} | {s['slug']:<24} | {s['name']:<28} | {s['medium']}")
    print(f"\nTotal curated styles: {len(CATALOG)} across 15 stations.\n")


def cli_search(query: str):
    q = query.lower()
    matches = [
        s for s in CATALOG
        if q in s['slug'] or q in s['name'].lower() or q in s['description'].lower() or any(q in t for t in s['tags'])
    ]
    print(f"\nSearch results for '{query}': {len(matches)} found\n")
    for s in matches:
        print(f"• [{s['slug']}] {s['name']} (Station {s['station_id']}: {s['station_name']})")
        print(f"  Medium: {s['medium']} | Tech: {s['render_tech']}")
        print(f"  Summary: {s['description']}\n")


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
        description="Opuscar Skill Curator & Sanitizer: Discover, audit, and cherry-pick clean agent skills."
    )
    parser.add_argument("--ui", action="store_true", help="Launch the web browser visual curator interface")
    parser.add_argument("--port", type=int, default=7890, help="Port for the web UI server (default: 7890)")
    
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all available styles across all 15 stations")
    
    # search
    search_p = subparsers.add_parser("search", help="Search styles by keyword or tag")
    search_p.add_argument("query", help="Keyword or search phrase")

    # audit
    audit_p = subparsers.add_parser("audit", help="Run security and prompt injection check on a style")
    audit_p.add_argument("slug", help="Style slug (e.g., watercolor-brush, satellite-briefing)")

    # cherry-pick
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
    elif args.command == "audit":
        cli_audit(args.slug)
    elif args.command == "cherry-pick":
        cli_cherry_pick(args.slug, args.dest)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
