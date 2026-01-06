## Format
### [Category] - Brief Title
**Date:** YYYY-MM-DD
**Context:** What you encountered
**Solution/Learning:** What you learned
**Files Affected:** List of files

### [Environment] - Dependency Management
**Date:** 2026-01-06
**Context:** Several dependencies were missing from the environment (aiohttp, bs4, colorlog) causing import errors.
**Solution/Learning:** Always check imports and verify installed packages. `requirements.txt` might be incomplete.
**Files Affected:** `requirements.txt` (needs update), `src/dashboard/app.py`

### [Streamlit] - Page Config Placement
**Date:** 2026-01-06
**Context:** `st.set_page_config` must be the very first Streamlit command.
**Solution/Learning:** Moved it to the top of `app.py`.
**Files Affected:** `src/dashboard/app.py`
