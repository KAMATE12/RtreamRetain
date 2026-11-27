# S4-04 — Interface readability verification

Issue: #26
Sprint: Sprint 4 — November 16–29, 2026

Status: implemented and locally verified.
Publication and CI evidence remain to be recorded.
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

These are local results. No CI result for S4-04 is claimed yet.

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

- Record the implementation commit and its GitHub Actions result.
- Add repository screenshot evidence and links where available.
- Complete any outstanding acceptance evidence, including contrast checks
  and precise desktop/zoom viewport records.
- Review issue #26 acceptance criteria before closing it.

## References

- [S4-04 issue](https://github.com/KAMATE12/RtreamRetain/issues/26)
- [Monthly indicators](monthly-indicators-dashboard.md)
- [Retention actions](retention-actions.md)
- [Sprint 4 plan](sprint-4-plan.md)
