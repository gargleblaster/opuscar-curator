# Opuscar Skill Curator & Sanitizer

> 🌐 **Live Web Workbench:** [**https://gargleblaster.github.io/opuscar-curator/**](https://gargleblaster.github.io/opuscar-curator/)

A lightweight, zero-dependency utility that allows developers and AI coding agents to safely discover, inspect, sanitize, and **cherry-pick individual code-driven film styles** from `lemomo-ai/lemo-opuscar` into clean, isolated agent skills without polluting your host environment.

---

## Key Benefits

1. **Zero Supply-Chain & RCE Risk**: Completely avoids running `setup.sh` or pulling unvetted npm/pip dependencies into your global environment.
2. **Context Window Protection**: The full `lemo-opuscar` repo includes 99 styles and dozens of markdown guides that bloat your agent's context window. This tool extracts **only** the single style you need into a lean ~35-line `SKILL.md`.
3. **Security & Prompt-Injection Scanner**: Scans every style definition and code harness before export, ensuring no unauthorized remote pipes (`curl | bash`), root commands, or prompt overrides enter your workspace.
4. **Environment Isolation**: Bundles a standalone Canvas/WebGL test harness (`harness.html`) so you can preview and verify animations locally in the browser with zero build steps or package installations.

---

## Global CLI Usage

Run directly from any terminal window:

```bash
# Launch the visual browser interface (http://127.0.0.1:7890)
opuscar-curator --ui

# List all curated styles across all 15 stations
opuscar-curator list

# Search by keyword or aesthetic
opuscar-curator search satellite
opuscar-curator search blueprint
opuscar-curator search watercolor

# Audit a style before using
opuscar-curator audit satellite-briefing

# Sync catalog with upstream repository to pull any newly added styles
opuscar-curator sync

# Cherry-pick a clean skill directly into your active project skills
opuscar-curator cherry-pick satellite-briefing --dest .claude/skills
```

---

## Repository Structure

```text
opuscar-curator/
├── opuscar_curator.py   # Self-contained executable & local web UI server
├── README.md            # Documentation & usage guide
├── LICENSE              # MIT License
└── .gitignore
```

## License

MIT License.
