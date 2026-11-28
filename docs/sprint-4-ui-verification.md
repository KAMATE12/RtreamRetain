# S4-04 — Interface readability verification

Issue: #26
Sprint: Sprint 4 — November 16–29, 2026

Status: implemented, locally verified and published; GitHub Actions passed.
Final acceptance review remains pending.

## Scope

Improve the existing Angular interface without introducing a UI framework.

Changes include:

- Wider application layout and a compact Sprint 4 header.
- Prominent synthetic-data notice.
- Summary indicators displayed as responsive cards.
- Consistent styling for comparisons, suggestions and action forms.
- Text-labelled status badges for saved actions.
- Secondary, expandable technical connection checks.
- Visible keyboard focus and narrow-screen adaptation.

No backend code, indicator formulas or suggestion rules changed.

## Automated local verification

The project author supplied the following successful execution results:

| Check | Result |
|---|---|
| Frontend test files | 4 passed |
| Frontend tests | 79 passed |
| Production build | Passed |
| Initial bundle raw size | 307.18 kB |
| Estimated transfer size | 81.00 kB |
| Build style-budget warnings | None shown |
| git diff --check | No whitespace errors reported |

The tests cover indicator requests and panels, action requests,
creation and listing, and status-update behaviour.

These local results are separate from the CI evidence recorded below.

## Browser observations

Browser: Microsoft Edge on Windows.
Application: http://127.0.0.1:4200

Before-and-after screenshots were supplied in the project conversation.
They show the previous narrow layout, the updated application header,
indicator cards, saved actions and narrow-screen rendering.
The image files are not yet included in this repository.

### Desktop

The supplied screenshots show:

- Wider use of the available page space.
- Four summary indicator cards in one row.
- Clearly labelled month and plan controls.
- Consistent saved-action cards.
- Dismissed and Completed statuses identified by text.
- Retained rule identifiers, versions, context and creation dates.
- Synthetic-data and interpretation notices.

The exact desktop viewport dimensions were not recorded.

### Narrow-screen measurements

Console measurements supplied by the project author:

| Viewport width | Viewport height | Page width | Horizontal overflow |
|---|---|---|---|
| 966 CSS px | 844 CSS px | 966 CSS px | false |
| 390 CSS px | 509 CSS px | 390 CSS px | false |

For the second measurement, the device toolbar displayed 390 × 844,
but window.innerHeight returned 509. This record uses the measured
viewport height rather than assuming the toolbar height was effective.

Screenshots show the four indicator cards stacked vertically.
The project author additionally confirmed:

- Comparison columns are accessible by scrolling inside the table.
- The review form fields and buttons remain usable at narrow width.

### Zoom, keyboard and secondary controls

The project author confirmed completion of the instructed checks:

- Important information and controls remain usable at 200% browser zoom.
- Keyboard navigation with Tab and Shift+Tab works.
- Keyboard focus remains visible.
- Technical connection checks remain accessible in their secondary section.

The instructions included returning browser zoom to 100%.
Exact viewport dimensions at 100% and 200% zoom were not recorded.
No separate 200% screenshot was supplied.

These are project-author observations, not an independent usability study.

## Data and interpretation

The supplied September 2026 all-plan screenshots display:

- Beginning-of-month cohort: 100 customers.
- Cancellation requests: 19.
- Cancellation-request rate: 19%.
- Average viewing time: 57.14 hours per cohort customer.

Plan comparisons retain cohort sizes, cancellation counts and rates.
Suggestions retain their rule and rationale.
Actions remain proposals based on synthetic observations.
Completed does not establish improved customer retention.

## Verification limits

The production build verifies compilation, not visual usability.

Existing automated tests provide regression evidence for application
behaviour. This record does not claim that every loading, empty-data,
API-error or recovery state was manually rechecked after the styling edits.

No complete accessibility audit, screen-reader assessment or formal
contrast measurement is claimed.

The screenshots and manual checks do not establish usefulness for real
retention managers or proven retention effectiveness.

## Publication and remaining work

- Publish this documentation update containing the CI evidence.
- Add repository screenshot evidence and links where available.
- Complete any outstanding acceptance evidence, including contrast checks
  and precise desktop/zoom viewport records.
- Review issue #26 acceptance criteria before closing it.

## References

- [S4-04 issue](https://github.com/KAMATE12/RtreamRetain/issues/26)
- [Monthly indicators](monthly-indicators-dashboard.md)
- [Retention actions](retention-actions.md)
- [Sprint 4 plan](sprint-4-plan.md)
## Publication and CI evidence

Implementation commit: 4315ac3 —
feat: improve dashboard and retention action readability.

- [Implementation commit](https://github.com/KAMATE12/RtreamRetain/commit/4315ac3)
- [Successful workflow](https://github.com/KAMATE12/RtreamRetain/actions/runs/46084542109)

The supplied GitHub Actions screenshot shows:

| Check | Observed result |
|---|---|
| Workflow | Starter checks #58 |
| Commit | 4315ac3 |
| Branch | main |
| Overall result | Success |
| Backend job | Success, 12 seconds |
| Frontend job | Success, 20 seconds |
| Frontend test files | 4 passed |
| Frontend tests | 79 passed |
| Total duration | 23 seconds |

The screenshot does not establish backend test counts or execution
of PostgreSQL integration tests in CI.

Final acceptance review remains pending, including the outstanding
verification evidence listed above.

## Additional viewport and contrast verification

This section updates the earlier limitations concerning zoom viewport
measurements and the absence of numerical colour-contrast checks.

### Browser zoom measurements

The project author supplied these console results after following the
100%, then 200% browser-zoom sequence, with device emulation disabled:

| Browser zoom | Viewport width | Viewport height | Page horizontal overflow |
|---|---|---|---|
| 100% | 450 CSS px | 596 CSS px | false |
| 200% | 225 CSS px | 298 CSS px | false |

Developer tools were docked beside the application, reducing its
available width. These are not full-window desktop dimensions.
The author previously confirmed that important information and
controls remained usable at 200% zoom.

Earlier wide-screen screenshots provide qualitative layout evidence;
their exact viewport dimensions remain unrecorded.

### Calculated colour contrast

Ratios were calculated from the supplied CSS hexadecimal colours,
using sRGB relative luminance and the formula
(Llighter + 0.05) / (Ldarker + 0.05).

| Element | Text | Background | Contrast ratio |
|---|---|---|---|
| Main text | #172940 | #f3f6fa | 13.57:1 |
| Paragraph | #40516a | #ffffff | 8.07:1 |
| Secondary text on light panel | #536175 | #f8faff | 6.03:1 |
| Primary button | #ffffff | #244887 | 8.93:1 |
| Primary button hover | #ffffff | #193765 | 11.83:1 |
| Proposed status | #244887 | #edf3fc | 8.01:1 |
| In Progress status | #704900 | #fff5de | 7.33:1 |
| Completed status | #245a3d | #edf6f0 | 7.31:1 |
| Dismissed status | #465267 | #f0f2f5 | 7.03:1 |
| Synthetic-data notice | #28564c | #edf6f3 | 7.55:1 |
| Error message | #8a2424 | #fff1f0 | 8.10:1 |

These calculations cover the listed opaque text/background pairs.
They do not measure rendered pixels, disabled-control opacity,
all borders, focus indicators or every possible interface state.
They are a practical colour check, not an accessibility certification.

### Acceptance evidence still to link

Before-and-after screenshots were supplied in the project conversation.
Their publication in issue #26 or the repository has not been confirmed.

The implementation and CI evidence are already published.
Final issue acceptance should reference this verification record and
the screenshots, while retaining the limitations documented here.
