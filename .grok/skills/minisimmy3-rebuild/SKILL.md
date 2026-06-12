# MiniSimmy3 Rebuild Skill

## Purpose
Helps develop and refine MiniSimmy3 — a modular creature evolution simulation built in p5.js + Tailwind. Focuses on code quality, long-term maintainability, and reaching high parity with the original monolithic version.

## Key Principles (from recent work)

- **Small, incremental changes preferred**: The user likes working in small "next" style chunks rather than large refactors.
- **Heavy emphasis on code legibility and documentation**: Almost every recent chunk has focused on adding clear comments, section headers, and explanations.
- **Auditing and defensive coding**: Multiple passes have been done to add guards, null checks, and error resilience.
- **Saving system is critical**: Auto-save after important actions, manual save option, and persistence of eggs + Gene Vault + economy across Prestige and page reloads.
- **Game Guide importance**: A detailed standalone Game Guide has been created and expanded. It should explain all major systems clearly.

## Current State (as of late June 2026)

- Codebase has undergone extensive polishing, documentation, and auditing.
- Saving system is robust and well-integrated.
- Main landing page has social links, media section, and links to both MiniSimmy3 and the legacy MiniSimmy2.
- A comprehensive standalone Game Guide exists.
- Historical roadmap has been maintained.
- Project is in a "highly polished, ready for testing" state (confidence ~97/100).

## Recommended Workflow

1. Make small, focused changes.
2. Document what was done clearly (in code comments and commit messages).
3. Run audit-style checks for missing functions, null references, and consistency.
4. Update the Game Guide when adding or changing major systems.
5. Keep the roadmap reasonably up to date with major phases.

## Things to Prioritize

- Code readability and comments
- Saving system reliability
- Consistency in UI patterns (especially modals)
- Clear explanations in the Game Guide
- Defensive coding to prevent runtime errors

## Avoid

- Large risky refactors without breaking them into small chunks
- Adding major new features before the current version is stable and tested
- Leaving functions or systems undocumented