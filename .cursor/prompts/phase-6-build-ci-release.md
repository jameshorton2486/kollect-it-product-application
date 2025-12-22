# Phase 6: Build, CI & Distribution (RELEASE ENGINEERING)

🎯 ROLE

You are acting as a Senior Release Engineer preparing a Windows desktop application for distribution.

Your responsibility is to make the app buildable, testable, and releasable — not to change functionality.

🧱 NON-NEGOTIABLE RULES

You MUST:

- Keep builds reproducible
- Pin versions explicitly
- Separate build logic from runtime logic
- Preserve source-based execution

You MUST NOT:

- Change app behavior
- Embed secrets
- Add platform-specific hacks without guards
- Assume admin privileges

🎯 PHASE 6 OBJECTIVES

## 1️⃣ Build System (PyInstaller)

Create:

- A PyInstaller .spec file
- Explicit hidden imports
- Clean data file inclusion rules

Requirements:

- Build works on clean Windows machine
- Output clearly versioned
- Build artifacts excluded from Git

## 2️⃣ Versioning

Add:

- A single authoritative version source
- Version injected into:
  - App window
  - Logs
  - Build artifacts

No duplicate version definitions.

## 3️⃣ CI Pipeline (GitHub Actions)

Create:

- .github/workflows/build.yml
- Lint + test step
- Build artifact generation
- No secrets in workflow files

## 4️⃣ Installer Preparation (NO SIGNING YET)

Prepare (but do not finalize):

- Installer script stub (NSIS or Inno Setup)
- Directory layout
- Icon placeholders
- Upgrade-safe install paths

## 5️⃣ Release Hygiene

Add:

- Build output ignored in .gitignore
- Release checklist documentation
- Clear separation between dev vs release artifacts

🧩 IMPLEMENTATION GUIDELINES

- Put build assets in /build/
- Put CI in /.github/workflows/
- Keep documentation explicit
- Favor clarity over automation tricks

🧪 VERIFICATION REQUIREMENTS

After Phase 6:

- pyinstaller build succeeds locally
- CI workflow validates syntax
- No build artifacts tracked by Git
- Repo remains runnable from source

🛑 STOP CONDITIONS

If any change:

- Touches runtime logic
- Changes UI
- Breaks source execution

➡️ STOP and explain.

🚦 START NOW

Apply Phase 6 only.

✅ END PHASE 6 PROMPT

