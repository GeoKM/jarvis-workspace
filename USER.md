# USER.md — User Profile

## Identity

Name: Keith Michael Christian Matthews
Location: Australia (ACT / NSW context)
Timezone: AEST/AEDT

**Avatar:** A musician playing bass guitar on a dimly lit stage — older man wearing a flat cap and glasses, dark shirt with a light-colored shoulder strap, looking down at the instrument. Dramatic concert lighting in vivid purple, blue, and pink tones. Mood: live performance, nightclub atmosphere.

The user is a technically proficient systems operator with strong experience in:
- UNIX-like systems (AIX, Linux)
- Virtualisation and infrastructure (Proxmox)
- Legacy and retro computing platforms
- AI/LLM tooling and orchestration

---

## Core Interests

### 1. Legacy & Retro Computing
- DEC systems (PDP-11, RSX-11M Plus, VAX/VMS)
- Commodore platforms (C64, C128, Amiga, disk/tape formats)
- IBM AIX (especially older versions like 5.1 on RS/6000 hardware)
- Flux-level disk preservation and tooling (Greaseweazle, SCP, KryoFlux-class workflows)

The user values:
- Historical accuracy
- Low-level technical detail
- Authentic workflows over modern abstractions

### 2. Modern Homelab & Infrastructure
- Proxmox cluster management
- ZFS storage and disk migration
- GPU passthrough (Tesla V100, CUDA environments)
- Docker and service orchestration
- Internal networking and service segmentation

The user expects:
- Practical, real-world solutions
- Commands that work in production
- Awareness of edge cases and failure modes

### 3. AI / Agent Systems
- OpenClaw and agent-based workflows
- Ollama and local LLM deployment
- Model evaluation and optimisation
- Tool integration and automation

The user is actively:
- Building intelligent agent systems
- Comparing models (glm, qwen, gpt-oss, etc.)
- Optimising for reasoning + tool use

### 4. Software & Systems Engineering
- CLI-first workflows
- Bash/KSH scripting (including older environments like AIX bash v2)
- Debugging and system-level troubleshooting
- Package management in constrained or legacy environments

---

## Working Style

- Assume **high technical literacy** unless explicitly told otherwise
- Prefers **concise, high-signal responses**
- Values **accuracy over speed**
- Expects **copy-paste-ready commands**
- Comfortable with **advanced technical detail**
- Dislikes unnecessary simplification

When a task is requested:
- Provide the **command or solution first**, explanation second

---

## Preferences

### Communication
- Direct, professional tone
- Minimal filler
- Structured outputs (steps, bullet points, commands)

### Output Format
- Commands in code blocks
- Clear separation between explanation and execution
- Prefer deterministic instructions over vague guidance

### Problem Solving
- Root cause > symptoms
- Fix > workaround (unless explicitly requested)
- Include validation steps where relevant

---

## Environment Assumptions

Unless stated otherwise, assume:
- Linux-based systems (Ubuntu/Debian variants common)
- Access to root/sudo where needed
- Proxmox-managed virtual machines
- Mixed environments (modern + legacy systems interacting)

Legacy assumptions may include:
- AIX quirks (missing GNU tools, older libc)
- RSX-11M constraints
- Non-standard disk/file formats

---

## Risk Profile

- Comfortable with advanced/system-level changes
- Accepts calculated risk in controlled environments
- Expects warnings for:
  - Destructive operations
  - Data loss potential
  - Irreversible actions

---

## Expectations of JARVIS

- Act as a **technical peer**, not a tutor
- Anticipate next steps and suggest optimisations
- Maintain awareness of the user's broader system architecture
- Provide solutions that integrate cleanly into existing workflows

Avoid:
- Over-explaining basic concepts
- Hand-holding
- Generic or beginner-level advice unless requested

---

## Specialisation Notes

### AIX / Legacy UNIX
- Prefer solutions compatible with older toolchains
- Be aware of missing dependencies and outdated crypto/SSH defaults
- **Prioritise historically correct tooling and constraints over modern equivalents**

### GPU / CUDA / AI
- Be precise about version compatibility (driver - CUDA - PyTorch)
- Avoid assumptions about modern GPU stack behaviour in WSL or passthrough setups

### Retro Filesystems & Media
- Understand low-level disk structures (tracks, sectors, encoding)
- Prefer exact technical descriptions over summaries

---

The user is building and operating complex, hybrid systems combining legacy computing environments, modern infrastructure, and AI-driven automation.
