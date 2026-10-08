# 🤝 Contributing to Megan

Welcome to the **Megan** project! First off, thank you for taking the time to contribute. Because Megan is being developed collaboratively by multiple team members across different domains (AI/LLM, Voice, PC Automation, Activation Steering, Frontend React, and Backend FastAPI), following clear, consistent standards will keep everyone productive and prevent conflicts.

Please take a few minutes to read this guide before starting on any feature or bug fix.

---

## 📋 Table of Contents
1. [Team Working Agreements & Roles](#-team-working-agreements--roles)
2. [Prerequisites & Development Environment](#-prerequisites--development-environment)
3. [Git Workflow & Branching Strategy](#-git-workflow--branching-strategy)
4. [Step-by-Step: Making Your First Contribution](#-step-by-step-making-your-first-contribution)
5. [Pull Request (PR) Process & Checklist](#-pull-request-pr-process--checklist)
6. [Code Style & Quality Guidelines](#-code-style--quality-guidelines)
7. [Testing Requirements](#-testing-requirements)
8. [Module Ownership & Coordination](#-module-ownership--coordination)
9. [Troubleshooting & Help](#-troubleshooting--help)

---

## 👥 Team Working Agreements & Roles

With 3+ engineers actively contributing to the repository, keep these core rules in mind:
- **Never push directly to `main`**: All changes must go through a Pull Request with at least **one approving review** from another teammate.
- **Communicate before starting**: Check issues or notify team members on chat before starting work on a major component to avoid duplicate effort.
- **Keep PRs focused**: Small, atomic PRs (under 400 lines of code changed) are much easier and faster to review. Avoid bundling multiple unrelated features into one PR.
- **Keep `main` green and deployable**: `main` should always pass linting, type checks, and tests.

---

## 🛠️ Prerequisites & Development Environment

### 1. Required Tools
- **Git** (latest version)
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** & **npm** (for the React + Vite frontend)
- **VS Code** (recommended editor)

### 2. Fork and Clone
If using a shared organization/team repository:
```bash
git clone https://github.com/your-org/megan.git
cd megan
```
If using a fork-based workflow:
```bash
git clone https://github.com/<your-username>/megan.git
cd megan
git remote add upstream https://github.com/your-org/megan.git
```

### 3. Backend Setup (Python)
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate # macOS/Linux

# Upgrade pip & install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
```

### 4. Frontend Setup (React + Tailwind + Vite)
```bash
cd frontend
npm install
cd ..
```

### 5. Verify Setup
Run dev tests to confirm everything is linked:
```bash
pytest tests/
```

---

## 🌿 Git Workflow & Branching Strategy

We follow a structured **Feature Branch Workflow**:

### Branch Naming Conventions
Use descriptive prefixes followed by a short hyphenated name:
- `feature/<name>` — New feature (e.g., `feature/voice-vad-listener`, `feature/steering-dashboard-charts`)
- `fix/<name>` or `bugfix/<name>` — Bug fixes (e.g., `fix/intent-classifier-crash`, `fix/tray-minimize`)
- `docs/<name>` — Documentation changes (e.g., `docs/update-architecture`)
- `refactor/<name>` — Code restructuring without altering behavior
- `test/<name>` — Adding or updating test suites

### Branch Creation Example
```bash
# 1. Fetch latest changes from main
git checkout main
git pull origin main

# 2. Create your feature branch
git checkout -b feature/automation-safeguard
```

---

## 🚀 Step-by-Step: Making Your First Contribution

### Step 1: Sync with `main` frequently
Before starting and before pushing, rebase or merge with `main`:
```bash
git checkout main
git pull origin main
git checkout feature/your-feature-name
git merge main
```

### Step 2: Implement Your Changes
- Write clean, modular code with type hints and docstrings.
- If you add new actions or endpoints, update the corresponding config files (`configs/`) and TypeScript definitions (`frontend/src/types/`).
- Do not commit large model weights, audio recordings, or credentials. Check `.gitignore`!

### Step 3: Run Formatters & Linters
Always clean up code before committing:
```bash
# Backend formatting & linting
black .
ruff check . --fix
mypy core/ api/ chatbot/

# Frontend formatting & linting
cd frontend
npm run lint
cd ..
```

### Step 4: Run Tests
Ensure existing and new unit tests pass:
```bash
pytest
```

### Step 5: Commit with Clear Messages
Follow Conventional Commits format:
```bash
git add .
git commit -m "feat(automation): add confirmation prompt for folder deletion"
```
Prefixes: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`

### Step 6: Push to GitHub
```bash
git push -u origin feature/your-feature-name
```

---

## 🔍 Pull Request (PR) Process & Checklist

1. **Open a PR on GitHub**:
   - Go to your repository on GitHub.
   - Click **Compare & pull request**.
   - Base branch: `main` ⬅️ Compare branch: `feature/your-branch`.

2. **Fill Out the PR Description**:
   Include:
   - What changed and why.
   - Which modules are affected.
   - How you tested the changes (automated tests, manual UI checks).
   - Any configuration or `.env` updates needed.

3. **Code Review & Feedback**:
   - At least **1 peer review approval** is required before merging.
   - Address feedback promptly. Push new commits directly to your feature branch; GitHub updates the PR automatically.
   - Be respectful, constructive, and supportive in code reviews.

4. **Merging**:
   - Use **Squash and Merge** or **Rebase and Merge** to keep the history clean.
   - Delete your branch after successful merge.

---

## 🎨 Code Style & Quality Guidelines

### Python (Backend)
- **Formatting**: Format with `black` (line length 100).
- **Type Hints**: Use type hints on all public functions (`def execute_action(name: str, params: dict[str, Any]) -> bool:`).
- **Docstrings**: Include clear Google-style docstrings on classes and functions.
- **Error Handling**: Catch specific exceptions and log with `core.logger`. Never silence errors with bare `except: pass`.
- **Safety**: Any OS automation handler interacting with files or system processes must pass through `automation.sandbox` and `automation.confirmation`.

### TypeScript / React (Frontend)
- **Components**: Functional components with hooks and TypeScript interfaces.
- **Styling**: Utility classes with Tailwind CSS following the `megan-*` purple theme palette.
- **State Management**: Zustand stores (`frontend/src/store/`) for shared state.
- **API calls**: Centralize API calls and WebSocket connections in custom hooks (`useChat`, `useSteering`, `useWebSocket`).

---

## 🧪 Testing Requirements

Every new feature or bug fix must include corresponding tests:
- `tests/test_chatbot/` — Chat logic, intent classifier, conversation history.
- `tests/test_automation/` — Whitelist validation, confirmation gate, file/app handlers.
- `tests/test_voice/` — Audio capture helpers, wake word handlers, language detection.
- `tests/test_steering/` — Hook registration, vector additions, preset configurations.

Run the full test suite with coverage:
```bash
pytest --cov=. --cov-report=term-missing
```

---

## 🗺️ Module Ownership & Coordination

To streamline work among multiple developers, here is the suggested area division:
- **Core & API Lead**: `core/`, `api/`, `configs/`, cross-system stability.
- **AI & Steering Engineer**: `llm/`, `steering/`, TransformerLens hooks & vectors.
- **PC Automation & Safety Engineer**: `automation/`, whitelist, sandbox guards.
- **Voice Pipeline Engineer**: `voice/`, openWakeWord, Whisper STT.
- **Frontend / UI Engineer**: `frontend/` (React, Tailwind, Zustand, Recharts).

Coordinate breaking interface changes ahead of time in team discussions.

---

## 🆘 Troubleshooting & Help

- **Merge conflicts?** Run `git checkout main && git pull`, then `git checkout your-branch && git merge main`. Resolve conflicts in your editor and commit.
- **Model weights issue?** Run `python scripts/download_models.py` or verify your Hugging Face token in `.env`.
- **Frontend proxy issues?** Make sure the FastAPI backend is running on port 8000 while Vite runs on port 5173.

Thank you for contributing to Megan! 🚀
