# Phase 5: Logging, Crash Handling & Recovery (PRODUCTION SAFETY)

🎯 ROLE

You are acting as a Senior Reliability Engineer responsible for making a desktop application production-safe.

Your goal is to add observability, crash resilience, and recovery mechanisms without changing application behavior.

This phase is about diagnostics and safety, not features.

🧱 NON-NEGOTIABLE RULES

You MUST:

- Preserve all existing logic and workflows
- Add logging and handlers around existing code
- Use standard Python logging facilities
- Fail gracefully instead of crashing
- Keep everything configurable

You MUST NOT:

- Change business logic
- Change UI workflows
- Add external SaaS dependencies unless optional
- Introduce blocking operations in the UI thread

If any requirement conflicts → STOP and explain.

🎯 PHASE 5 OBJECTIVES

## 1️⃣ Centralized Logging (File-Based)

Implement:

- A single logging configuration module
- Rotating file logs (size-limited)
- Log directory creation if missing

Requirements:

- Console logging remains
- File logs stored outside repo (e.g. logs/)
- No secrets logged

## 2️⃣ Global Exception Handling

Add:

- A top-level exception handler
- User-friendly crash dialog
- Full traceback written to log file

Rules:

- Do not swallow exceptions silently
- UI must remain responsive where possible

## 3️⃣ Thread & Async Error Visibility

Ensure:

- Exceptions in background threads are logged
- UI shows failure states instead of freezing
- Threads are cleaned up safely

## 4️⃣ Temporary File & Session Cleanup

Add:

- Safe cleanup hooks on exit
- Guard against orphaned temp directories
- Cleanup failures logged, not fatal

## 5️⃣ Optional Recovery Hooks

Where safe:

- Detect incomplete prior sessions
- Offer user a recovery message (non-blocking)
- No automatic destructive actions

🧩 IMPLEMENTATION GUIDELINES

- Add new helpers in modules/logging_setup.py or similar
- Keep main.py changes minimal
- Use context managers where possible
- Default behavior should be safe + quiet

🧪 VERIFICATION REQUIREMENTS

After Phase 5:

- App launches normally
- Logs are written to disk
- Crashes produce readable logs
- No performance regression
- No UI changes unless error occurs

🛑 STOP CONDITIONS

If any change:

- Alters workflows
- Touches AI logic
- Changes threading models

➡️ STOP and explain.

🚦 START NOW

Apply Phase 5 only.

✅ END PHASE 5 PROMPT

