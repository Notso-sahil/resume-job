# System Evolution, Diff & Implementation Summary: `resume-job`

> **Document Scope**: Complete audit of all architectural changes, retained production bug fixes, purged constraints, experience pipeline overhauls, and atomic Git commits across Iterations 1 and 2 in `resume-job`.  
> **Timestamp**: September 30, 2026  
> **Status**: Verified & Tested (29/29 Pytest passing, 0 regressions)  
> **Protocol**: Strict 1-File-Per-Commit, Zero Remote Push  

---

## 1. Architectural Boundary Overview

The refactor establishes the strict boundary between the **nine retained production bug fixes** from `resume-job-new`, the **purged "Honest Engineering" / metric suppression constraints**, and the **permanent RE-jadx experience pipeline migration**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE REFACTOR BOUNDARY                          │
├───────────────────────────────────┬────────────────────────────────────┤
│     RETAINED BUG FIXES            │    ROLLED BACK / PURGED CONSTRAINTS │
├───────────────────────────────────┼────────────────────────────────────┤
│ 1. PDF Unicode & Ligature Normal- │ 1. Metric Suppression & [TODO]     │
│    ization (`profile_extractor`)  │    Placeholders (`synthesis_prompts│
│ 2. MCP 2024-11-05 Session Hand-   │ 2. Mandatory Real-Only Scraping    │
│    shake & Re-auth (`browser_cli`)│    from Candidate PDF (`models.py`)│
│ 3. React/Vue Synthetic Descriptor │ 3. "Amplify, Don't Fabricate" Rest-│
│    Bypass (`form_filler.py`)      │    rictions & Prompts (`nodes.py`) │
│ 4. Dynamic Phone Digit Matcher    │ 4. Resume Change Log & Provenance  │
│ 5. Windows CP1252 UTF-8 Bootstraps│    Diff Tables (`interview_dossier│
│ 6. CLI Bridge Manifest Automation │ 5. Original Bullet Snapshotting for│
│ 7. MV3 Service Worker Keepalive   │    Audit Trailing (`experience_p`) │
│ 8. State Machine Integrity Gates  │                                    │
│ 9. Academic Standing Normalizer   │                                    │
├───────────────────────────────────┴────────────────────────────────────┤
│                    EXPERIENCE VS. PROJECT ROUTING                      │
├───────────────────────────────────┬────────────────────────────────────┤
│         PROJECTS POOL             │         EXPERIENCE PIPELINE        │
│         (`projects.md`)           │    (`CandidateProfile.experience`) │
├───────────────────────────────────┼────────────────────────────────────┤
│ • 9 Eligible Real Projects        │ • Permanent Ingestion:             │
│ • Slot 1: Verified Domain Anchor  │   Organization: IFSO, Delhi Police │
│ • Slots 2 & 3: Role Synthesized   │   Role: AI Engineering Intern      │
│ [X] RE-jadx BLACKLISTED & PURGED  │   Tech: Java, Python, MCP, JADX    │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 2. Recent Iteration Breakdown (Priority 0 & Phase 1 / Section 2)

This iteration completed the Section 1 evaluator expansion and the complete Section 2 experience pipeline overhaul under the strict **1-file-per-commit atomic protocol**:

### 2.1 Priority 0 — Section 1.4–1.6 Evaluator Upgrade

#### 1. `src/evaluators/sanity_checker.py`
* **Commits**:
  - [`669a7f2`](file:///c:/Users/elite/Desktop/resume-job/src/evaluators/sanity_checker.py) — `feat(evaluator): implement PortfolioSanityChecker with forbidden marker and metric enforcement`
  - [`beab8ed`](file:///c:/Users/elite/Desktop/resume-job/src/evaluators/sanity_checker.py) — `fix(evaluator): support hyphenated time units in PortfolioSanityChecker METRIC_PATTERN`
* **Changes**:
  - Implemented the `PortfolioSanityChecker` class to enforce ATS scoring, quantified impact, and three-slot structure without breaking existing LangGraph functions (`check_metric_plausibility`, `check_stack_cohesion`, `audit_portfolio`).
  - Added `FORBIDDEN_MARKERS = ["[TODO", "TODO:", "add your real", "measured metric", "placeholder", "XXXX", "<insert"]`.
  - Added robust `METRIC_PATTERN` matching percentages, dollar amounts, multipliers (`\d+x`), units (`ms`, `s`, `sec`, `seconds`, `QPS`, `tokens/sec`, `GB`, `MB`, `VRAM`), and hyphenated time windows (e.g. `5-second window`).
  - Implemented `audit_bullet()`: rejects incomplete placeholders, requires numeric metrics, and mandates depth ($\ge 12$ words).
  - Implemented `audit_portfolio()`: asserts exactly 3 projects, Slot 1 anchor requirement (`is_anchor=True`), 3–5 bullets per project, and evaluates every bullet via `audit_bullet()`. Polymorphic across dicts and `ProjectSpec` instances.

---

#### 2. `src/evaluator/__init__.py`
* **Commit**: [`a7c0321`](file:///c:/Users/elite/Desktop/resume-job/src/evaluator/__init__.py) — `refactor(evaluator): add backward-compatible src.evaluator package proxy`
* **Changes**:
  - Created a backward-compatible proxy package registering `sys.modules["src.evaluator.sanity_checker"] = sanity_checker`.
  - Re-exports `PortfolioSanityChecker`, `check_metric_plausibility`, `check_stack_cohesion`, and `audit_portfolio`.
  - Allows seamless imports via both `from src.evaluators.sanity_checker import ...` and `from src.evaluator.sanity_checker import ...`.

---

#### 3. `tests/test_evaluator.py`
* **Commit**: [`ff37175`](file:///c:/Users/elite/Desktop/resume-job/tests/test_evaluator.py) — `test(evaluator): add PortfolioSanityChecker unit tests for markers, metrics, and slot structure`
* **Changes**:
  - Appended 4 dedicated unit tests (bringing the evaluator suite from 6 to 10 passed tests):
    1. `test_sanity_checker_rejects_todo_placeholders()`: asserts `valid == False` on `[TODO` markers.
    2. `test_sanity_checker_requires_explicit_metrics()`: asserts `valid == False` on unquantified text.
    3. `test_sanity_checker_accepts_valid_xyz_bullet()`: asserts `valid == True` for compliant Google XYZ bullets.
    4. `test_sanity_checker_validates_three_slot_structure()`: asserts `passed == True` on compliant 3-project portfolios.

---

### 2.2 Phase 1 — Section 2 Experience Pipeline Overhaul

#### 4. `src/extractors/project_loader.py`
* **Commit**: [`c1a82b4`](file:///c:/Users/elite/Desktop/resume-job/src/extractors/project_loader.py) — `feat(extractors): create project_loader with RE-jadx blacklist heuristics`
* **Changes**:
  - Implemented `RE_JADX_PATTERNS = [r"\bre-?jadx\b", r"\bjadx\b", r"\breverse[- ]engineering agent\b"]`.
  - Implemented `is_re_jadx_project(title, overview)` for case-insensitive heuristic detection.
  - Implemented `load_eligible_projects_from_markdown(file_path)` which parses `projects.md`, extracts metadata/bullets, and drops Project 5 (RE-jadx), returning exactly 9 verified non-internship candidate projects.

---

#### 5. `src/schemas/models.py`
* **Commit**: [`a409ff1`](file:///c:/Users/elite/Desktop/resume-job/src/schemas/models.py) — `refactor(schemas): update ExperienceEntry with structured internship fields and alias compatibility`
* **Changes**:
  - Upgraded `ExperienceEntry` with structured fields: `company`, `role`, `location` (defaulting to `"New Delhi, India"`), `start_date`, `end_date`, `period`, `technologies`, `bullets`, and `is_internship` (default `True`).
  - Added bidirectional `@model_validator(mode="before")` on `ExperienceEntry`:
    - Synchronizes `company <-> organization`
    - Synchronizes `(start_date, end_date) <-> period` (parses `"Month YYYY – Month YYYY"` or creates formatted period strings)
    - Guarantees 100% backward compatibility with `docx_renderer.py`, `latex_renderer.py`, and `jakes_resume.tex.jinja2`.
  - Extended `ProjectSpec` with polymorphic alias support for `title <-> project_title`, `technologies <-> tech_stack`, `bullets <-> xyz_bullets`, and `overview`.
  - Extended `CandidateProfile` with `projects: List[ProjectSpec]` and `name <-> full_name` synchronization.

---

#### 6. `src/prompts/experience_prompts.py`
* **Commit**: [`59647ed`](file:///c:/Users/elite/Desktop/resume-job/src/prompts/experience_prompts.py) — `feat(prompts): add canonical RE-jadx experience definition and dynamic tailoring prompt`
* **Changes**:
  - Added `CANONICAL_RE_JADX_EXPERIENCE` anchoring the Special Cell, Delhi Police (IFSO Unit) AI Engineering & Security Research Intern role (May 2026 – August 2026) with verified tech stack (Java, Python 3.10+, MCP, Vertex AI, JADX, Frida, Bash) and 4 verified base Google XYZ bullets.
  - Implemented `build_experience_tailoring_prompt()` to dynamically tailor internship bullets toward target JD keywords while preserving factual truth and prohibiting placeholder leaks.

---

#### 7. `src/extractors/profile_extractor.py`
* **Commit**: [`7320a36`](file:///c:/Users/elite/Desktop/resume-job/src/extractors/profile_extractor.py) — `fix(extractors): integrate ensure_re_jadx_in_experience into profile extraction pipeline`
* **Changes**:
  - Implemented `ensure_re_jadx_in_experience(profile)`:
    1. Purges any accidental RE-jadx occurrences from `profile.projects` and `profile.real_projects`.
    2. Inspects `profile.experience` for IFSO / Delhi Police / JADX markers and prepends canonical RE-jadx `ExperienceEntry` if absent.
  - Added `parse_candidate_profile(text)` wrapper.
  - Hooked `ensure_re_jadx_in_experience` into `load_or_extract_profile` and `extract_profile_from_pdf` to guarantee candidate profile invariants while preserving clean parsing for third-party resumes (e.g. Alex Rivera).

---

#### 8. `tests/test_experience_pipeline.py`
* **Commit**: [`55dc314`](file:///c:/Users/elite/Desktop/resume-job/tests/test_experience_pipeline.py) — `test(experience): add dedicated test suite for RE-jadx isolation and experience pipeline`
* **Changes**:
  - Created a dedicated 3-test test suite:
    1. `test_re_jadx_detection_heuristics()`: validates regex heuristics across positive and negative cases.
    2. `test_load_eligible_projects_excludes_re_jadx()`: parses synthetic markdown and verifies RE-jadx exclusion.
    3. `test_re_jadx_migrated_to_experience_and_purged_from_projects()`: tests end-to-end sanitization, confirming RE-jadx is purged from projects and injected into experience with full details.

---

## 3. Prior Iteration Summary (Iteration 1: Retained Bug Fixes & System Diff)

For complete provenance, the previous 10 atomic commits from Iteration 1 are documented below:

1. **`finder/browser_client.py`** ([`4b68099`](file:///c:/Users/elite/Desktop/resume-job/finder/browser_client.py)): MCP 2024-11-05 session handshake, session ID tracking, auto re-authentication on 400 Bad Request.
2. **`finder/form_filler.py`** ([`77496d4`](file:///c:/Users/elite/Desktop/resume-job/finder/form_filler.py)): React/Vue `setNativeValue` synthetic descriptor setter and dynamic phone number sanitization (`phone_raw`, `phone_display`).
3. **`finder/finder_cli.py`** ([`8c263f4`](file:///c:/Users/elite/Desktop/resume-job/finder/finder_cli.py)): Windows CP1252 UTF-8 stream bootstrapping (`sys.stdout.reconfigure(encoding="utf-8")`).
4. **`finder/state_tracker.py`** ([`0193a6c`](file:///c:/Users/elite/Desktop/resume-job/finder/state_tracker.py)): Added `fill_preview` JSON column migration and `PENDING_CONFIRM` state transition.
5. **`BrowseAI/packages/bridge/src/`** ([`3427785`](file:///c:/Users/elite/Desktop/resume-job/BrowseAI/packages/bridge/src/cli.ts)): Automated bridge registration CLI (`nexus-bridge register`, `patch-mcp`, `set-id`) and Chrome Native Messaging Host configuration.
6. **`src/schemas/models.py`** ([`bc1e414`](file:///c:/Users/elite/Desktop/resume-job/src/schemas/models.py)): Added `is_anchor: bool = False` and `is_synthesized: bool = True` to `ProjectSpec`.
7. **`src/prompts/synthesis_prompts.py`** ([`02a65fb`](file:///c:/Users/elite/Desktop/resume-job/src/prompts/synthesis_prompts.py)): Purged `_bullet_has_metric` and `[TODO]` appending; added polymorphic `build_synthesis_prompt` and `generate_xyz_bullet`.
8. **`src/agents/nodes.py`** ([`e4cb1c2`](file:///c:/Users/elite/Desktop/resume-job/src/agents/nodes.py)): Safe structured output unpacking with fallback to `build_fallback_projects` in `synthesize_projects_node`.
9. **`PROJECT_CONTEXT.md`** ([`0f21f41`](file:///c:/Users/elite/Desktop/resume-job/PROJECT_CONTEXT.md)): Grounded candidate profile (Sahil Yadav, 3rd Year B.Tech AIML at VIPS New Delhi) and 3-Project Portfolio Rule.
10. **`CHANGELOG_AND_SYSTEM_EVOLUTION.md`** ([`ea1f1ae`](file:///c:/Users/elite/Desktop/resume-job/CHANGELOG_AND_SYSTEM_EVOLUTION.md)): Complete historical evolution and diff documentation.

---

## 4. Complete Test Suite & Regression Results

All 29 tests run locally via `pytest` passed with zero errors:

```
tests/test_evaluator.py::test_ats_scorer_full_match PASSED               [  3%]
tests/test_evaluator.py::test_ats_scorer_partial_match PASSED            [  6%]
tests/test_evaluator.py::test_sanity_checker_valid_portfolio PASSED      [ 10%]
tests/test_evaluator.py::test_sanity_checker_invalid_power_verb PASSED   [ 13%]
tests/test_evaluator.py::test_sanity_checker_forbidden_phrase PASSED     [ 17%]
tests/test_evaluator.py::test_audit_portfolio_end_to_end PASSED          [ 20%]
tests/test_evaluator.py::test_sanity_checker_rejects_todo_placeholders PASSED [ 24%]
tests/test_evaluator.py::test_sanity_checker_requires_explicit_metrics PASSED [ 27%]
tests/test_evaluator.py::test_sanity_checker_accepts_valid_xyz_bullet PASSED [ 31%]
tests/test_evaluator.py::test_sanity_checker_validates_three_slot_structure PASSED [ 34%]
tests/test_experience_pipeline.py::test_re_jadx_detection_heuristics PASSED [ 37%]
tests/test_experience_pipeline.py::test_load_eligible_projects_excludes_re_jadx PASSED [ 41%]
tests/test_experience_pipeline.py::test_re_jadx_migrated_to_experience_and_purged_from_projects PASSED [ 44%]
tests/test_pipeline.py::test_output_format_validation PASSED             [ 48%]
tests/test_pipeline.py::test_pipeline_integration_docx PASSED            [ 51%]
tests/test_pipeline.py::test_slugify_company PASSED                      [ 55%]
tests/test_pipeline.py::test_archival_on_subsequent_run PASSED           [ 58%]
tests/test_pipeline.py::test_job_config_loading_and_execution PASSED     [ 62%]
tests/test_profile_extractor.py::test_parse_profile_deterministic_no_hardcoded_leak PASSED [ 65%]
tests/test_profile_extractor.py::test_find_candidate_resumes PASSED      [ 68%]
tests/test_profile_extractor.py::test_extract_profile_from_resume_pdf PASSED [ 72%]
tests/test_profile_extractor.py::test_parse_profile_with_uppercase_org_and_bullets PASSED [ 75%]
tests/test_profile_extractor.py::test_experience_tailoring_preserves_facts_and_enriches_jd PASSED [ 79%]
tests/test_profile_extractor.py::test_fallback_synthesize_candidate_profile PASSED [ 82%]
tests/test_profile_extractor.py::test_profile_normalizes_2nd_year_to_3rd_year PASSED [ 86%]
tests/test_renderers.py::test_render_docx PASSED                         [ 89%]
tests/test_renderers.py::test_render_latex PASSED                        [ 93%]
tests/test_renderers.py::test_render_dossier PASSED                      [ 96%]
tests/test_renderers.py::test_renderers_fallback_with_no_candidate_profile PASSED [100%]

============================= 29 passed in 0.98s ==============================
```

---

## 5. Complete Atomic Commit History

| Commit | Scope | Target File | Description |
| :---: | :---: | :--- | :--- |
| `4b68099` | Finder | `finder/browser_client.py` | Implement MCP 2024-11-05 protocol handshake and auto re-auth |
| `77496d4` | Finder | `finder/form_filler.py` | Add React/Vue setNativeValue descriptor setter and phone sanitization |
| `8c263f4` | Finder | `finder/finder_cli.py` | Configure UTF-8 console output bootstrapping for Windows CLI |
| `0193a6c` | Finder | `finder/state_tracker.py` | Add fill_preview JSON column migration and PENDING_CONFIRM state |
| `3427785` | Bridge | `BrowseAI/packages/bridge/src/*` | Implement automated bridge registration CLI and configuration persistence |
| `bc1e414` | Schemas | `src/schemas/models.py` | Add is_anchor and is_synthesized flags to ProjectSpec |
| `02a65fb` | Prompts | `src/prompts/synthesis_prompts.py` | Add generate_xyz_bullet and polymorphic build_synthesis_prompt |
| `e4cb1c2` | Agents | `src/agents/nodes.py` | Add robust structured output handling and fallback to synthesize_projects_node |
| `0f21f41` | Docs | `PROJECT_CONTEXT.md` | Update PROJECT_CONTEXT with system architecture and recovery playbook |
| `ea1f1ae` | Docs | `CHANGELOG_AND_SYSTEM_EVOLUTION.md` | Add CHANGELOG_AND_SYSTEM_EVOLUTION detailing diff and architecture audit |
| `669a7f2` | Evaluator | `src/evaluators/sanity_checker.py` | Implement PortfolioSanityChecker with forbidden marker and metric enforcement |
| `a7c0321` | Evaluator | `src/evaluator/__init__.py` | Add backward-compatible src.evaluator package proxy |
| `beab8ed` | Evaluator | `src/evaluators/sanity_checker.py` | Support hyphenated time units in PortfolioSanityChecker METRIC_PATTERN |
| `ff37175` | Tests | `tests/test_evaluator.py` | Add PortfolioSanityChecker unit tests for markers, metrics, and slot structure |
| `c1a82b4` | Extractors | `src/extractors/project_loader.py` | Create project_loader with RE-jadx blacklist heuristics |
| `a409ff1` | Schemas | `src/schemas/models.py` | Update ExperienceEntry with structured internship fields and alias compatibility |
| `59647ed` | Prompts | `src/prompts/experience_prompts.py` | Add canonical RE-jadx experience definition and dynamic tailoring prompt |
| `7320a36` | Extractors | `src/extractors/profile_extractor.py` | Integrate ensure_re_jadx_in_experience into profile extraction pipeline |
| `55dc314` | Tests | `tests/test_experience_pipeline.py` | Add dedicated test suite for RE-jadx isolation and experience pipeline |

---

## 6. Inviolable Operational Protocols Enforced

1. **Strict 1-File-Per-Commit Protocol**: Every file change is committed independently with an atomic, descriptive commit message.
2. **Zero Remote Push**: Commits are retained strictly on local Git branches; `git push` is prohibited.
3. **Candidate Invariants**: Sahil Yadav, 3rd Year B.Tech AIML at VIPS, New Delhi; RE-jadx permanently confined to Work Experience; Slots 2 & 3 tailored to target tech stack with Google XYZ metrics.
4. **Zero Pollution**: No one-off, audit, scratch, or migration scripts left in workspace.
