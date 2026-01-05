## Format
### [Tooling] - Repository Mismatch
**Date:** 2026-01-05
**Context:** The agent instructions were for "Splitwiser", but the repository is "NewsAI".
**Solution/Learning:** Adapted to the current repository context. Prioritized improving the existing Streamlit app.
**Files Affected:** N/A

### [Dependencies] - Missing Dependencies
**Date:** 2026-01-05
**Context:** `streamlit run` failed multiple times due to missing dependencies (`matplotlib`, `plotly`, `aiohttp`, `keybert`, etc.).
**Solution/Learning:** Iteratively installed missing packages. Should check `requirements.txt` or `pyproject.toml` more thoroughly next time, or assume the environment needs setup.
**Files Affected:** N/A
