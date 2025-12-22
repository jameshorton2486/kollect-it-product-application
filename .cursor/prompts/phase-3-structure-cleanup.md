# Phase 3: Deduplication & Structural Cleanup

🎯 ROLE

You are acting as a Senior Python Application Architect.

Your job is to reduce technical debt and duplication in a PyQt desktop application without changing runtime behavior.

This phase is about structure and clarity, not features or UI changes.

🧱 NON-NEGOTIABLE RULES

You MUST:

- Preserve all behavior
- Preserve all function names, signals, and slots
- Prefer moving and importing over rewriting
- Use git mv semantics (conceptually)
- Keep changes small and obvious

You MUST NOT:

- Change logic
- Change UI layout
- Rename public functions
- Optimize or refactor algorithms
- Delete files (archive only)

If a change risks behavior → STOP and explain.

🎯 PHASE 3 OBJECTIVES

## 1️⃣ Eliminate Code Duplication

Identify duplicated implementations of:

- UI widgets (DropZone, ImageThumbnail, etc.)
- Theme / palette definitions
- Utility helpers

Strategy:

- Keep ONE canonical implementation
- Move others to /archive/
- Update imports to reference the canonical version

## 2️⃣ Normalize Module Boundaries

Ensure:

- main.py contains orchestration only
- UI widgets live in modules/widgets.py
- Theme logic lives in modules/theme.py
- Business logic lives in modules/

No logic changes — imports only.

## 3️⃣ Reduce main.py Surface Area

Where safe:

- Move helper classes/functions into modules
- Keep main.py readable and high-level
- Preserve call order and signatures

## 4️⃣ Clean Up Tests & Utilities (No Moves Yet)

Identify tests that belong in /tests/

Identify utilities that belong in /scripts/

Do not move them yet — only comment or annotate

🧪 VERIFICATION REQUIREMENTS

After changes:

- App launches normally
- No import errors
- No UI regressions
- No signal/slot issues

If unsure → leave a TODO comment.

🛑 STOP CONDITIONS

If any change:

- Requires logic refactor
- Changes behavior
- Touches AI logic
- Affects threading

➡️ STOP and explain.

🚦 START NOW

Apply Phase 3 only.
Do not proceed to Phase 4.

✅ END PHASE 3 PROMPT

