## Format
### [Category] - Brief Title
**Date:** YYYY-MM-DD
**Context:** What you encountered
**Solution/Learning:** What you learned
**Files Affected:** List of files

### [Tooling] - CSS File Location
**Date:** 2024-10-12
**Context:** `app.py` is executed from `src/dashboard/`, but `styles.css` was located in `src/`. `load_css` uses a relative path.
**Solution/Learning:** Moved `styles.css` to `src/dashboard/` to simplify loading and keep dashboard assets together.
**Files Affected:** `src/styles.css` (deleted), `src/dashboard/styles.css` (created)
