# Contributing to signalfeed

## First-time machine setup

These steps only need to be done once per computer you develop on.

### 1. Install Git

**Windows:**
- Download from https://git-scm.com/download/win, run the installer,
  keep defaults (make sure "Git from the command line and also from
  3rd-party software" is selected on the PATH step).

> Note: GitHub Desktop bundles its own internal copy of git that does NOT
> get added to your system PATH. You need the standalone Git for Windows
> install above even if GitHub Desktop is already installed — they don't
> conflict, and both can coexist.

**Linux (Debian/Ubuntu-based):**
```bash
sudo apt update
sudo apt install git
```
Other distros: use your package manager (`dnf install git`, `pacman -S git`, etc.)

**Confirm it worked (both OSes):** open a **new** terminal and run:
git --version 

### 2. Install Python (3.11+)

**Windows:**
- Download from https://python.org (NOT the Microsoft Store version —
  it has extra PATH quirks). During install, check "Add python.exe to PATH."

**Linux:**
Most distros ship Python already. Check first:
```bash
python3 --version
```
If missing or too old:
```bash
sudo apt install python3 python3-pip python3-venv
```

**Confirm it worked:**
- Windows: `python --version`
- Linux: `python3 --version`

> Note: on Linux the command is `python3` and `pip3`, not `python`/`pip`
> (which may not exist or point somewhere unexpected). Substitute
> accordingly in every command below.

### 3. Clone the repo

**Windows:** via GitHub Desktop — File → Clone Repository → select `signalfeed`.

**Linux:** either GitHub Desktop (available as a Flatpak/AppImage on Linux)
or plain git:
```bash
git clone https://github.com/<your-username>/signalfeed.git
cd signalfeed
```

### 4. Install pre-commit

Open a terminal in the cloned repo folder.
- Windows + GitHub Desktop: Repository menu → "Open in Command Prompt" /
  PowerShell / Terminal.
- Linux: `cd` into wherever you cloned it.

**Windows:**
pip install pre-commit
pre-commit install

**Linux:**
```bash
pip3 install --user pre-commit
pre-commit install
```

> If `pre-commit` isn't recognized after installing on Linux, it likely
> installed to `~/.local/bin`, which may not be on PATH. Add this to your
> `~/.bashrc` (or `~/.zshrc` if using zsh):
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Then restart your terminal or run `source ~/.bashrc`.

**Confirm it worked (both OSes):**
pre-commit run --all-files

Should run without errors (may say "no files to check" if there's
nothing to lint yet — that's fine).

### 5. If any command isn't recognized

This almost always means PATH wasn't updated in your current terminal
session. Fix:
1. Fully close and reopen your terminal (or the whole app, e.g. VS Code)
   — PATH changes don't apply to already-open windows.
2. If it still fails: Windows — restart your computer. Linux — log out
   and back in, or `source ~/.bashrc`.

## Making changes

- Just edit code and commit as normal (via GitHub Desktop or `git`).
  `pre-commit` will automatically run `ruff` (formatting/linting) on
  every commit and block it if there's an issue it can't auto-fix.
- Style: Python code follows PEP 8 via `ruff` (config in `pyproject.toml`
  at repo root) — same rules everywhere Python appears in the project
  (`/server` and `/desktop`).
- Commit messages: please use Conventional Commits style, e.g.
  `feat: add feed subscription endpoint`, `fix: correct sync timestamp bug`,
  `chore: update dependencies`.

## Questions
Open a GitHub Issue, or reach out directly — this is a small personal
project, response time may vary.