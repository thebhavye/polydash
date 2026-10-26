# Accessibility and responsive-layout analysis spike

Informative research for #13, reviewed 2026-10-26. The study originally proposed
all three checks below. PR #21 implements PD2001/PD2002 as warning-only rules;
PD2101 remains deferred and unregistered. No layout schema extension is introduced.

## What the current description can tell us

Dashboard and component titles, filter options, nesting, table columns and
layout direction are available in the v1 IR. We can detect omitted/blank textual
labels or titles and report their authoring location. We cannot establish that
a title is descriptive, that generated HTML associates it with an input, or
that a chart has an adequate equivalent description of its data.

The W3C [labels/instructions guidance](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html)
distinguishes visible instructions from programmatically associated names.
A title check is a useful authoring warning, not a WCAG conformance guarantee.
`title` does not imply `alt` text. For charts, the generator would need a separate
reviewed contract for summaries/data tables or other meaningful alternatives.

The current schema has no heading levels, landmarks, focus order, keyboard
handlers or per-component accessibility roles. Those are generator contracts;
checking them in IR today would invent semantics. Theme is only light/dark, so
there are no declared foreground/background values from which to compute even
a static contrast ratio. If explicit resolved color tokens are added later,
a token-pair contrast check could be considered, with a limited stated scope.

## Responsive findings

A row/column direction alone cannot prove overflow. The IR has no fixed widths,
minimum widths, viewport assumptions, gaps or wrap policy. Long table columns
or many children can be hints, not sound errors. Do not flag all rows or wide
tables as inaccessible: the W3C [reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
recognizes exceptions for content requiring two-dimensional layout, including
data tables. Actual reflow needs generated CSS and browser/zoom verification.

If a future schema exposes a fixed minimum width and an explicit no-wrap layout,
the compiler could warn when declared child minima plus gaps exceed a declared
container width. This is arithmetic over declarations, not a prediction of text
measurement, runtime data or every browser's layout.

## Rule proposals and first fixture pairs

The title rules receive Dashboard + schema context, collect Diagnostic findings,
and use `Dashboard.location(path)`. Their severity is warning so existing
valid configs do not suddenly fail. Missing titles anchor the component object
while retaining the absent `/title` path; blank titles anchor the title value.
Only inspect nodes with a known type and a well-typed title (when present).
Schema/type errors remain the existing rules' responsibility.

### PD2001: Filter title is missing or blank (implemented in #21)

Warning, category accessibility (implemented by the separate title-rule change). A filter accepts input and should have
an author-supplied visible label. Test `title.strip()` only for blankness; do not
normalize the stored text. No title fallback from an internal ID is assumed.

Invalid mini-component:

```json
{"id":"region","type":"filter","options":["North","South"],"title":"  "}
```

Conforming mini-component:

```json
{"id":"region","type":"filter","options":["North","South"],"title":"Region"}
```

Embed each in `{"title":"Sales","layout":{"direction":"column"},"components":[COMPONENT]}`.
Expected finding: PD2001, warning, `/components/0/title` for the first;
none for the second. Add a missing-title case with a component-object location.
Both examples are valid under the current schema; the first now emits a warning
without removing IR or changing success status. Original estimate: about one day
for the rule, JSON/YAML fixtures and diagnostics documentation.

### PD2002: Chart title is missing or blank (implemented in #21)

Warning, category accessibility (implemented by the separate title-rule change). A chart should have a human-readable
title for context. This does not establish an adequate chart text alternative.

Invalid mini-component:

```json
{"id":"trend","type":"chart","data":{"source":"sales.csv"},"series":["revenue"]}
```

Conforming mini-component:

```json
{"id":"trend","type":"chart","title":"Revenue by month","data":{"source":"sales.csv"},"series":["revenue"]}
```

Use the same Dashboard wrapper. Expected finding: PD2002 warning at
`/components/0/title`, anchored to the chart object for the first; none for the
second. Both remain accepted by the validator; only the first warns. Original estimate:
about one day, sharing blank-title handling and format-equivalence tests with PD2001.

### PD2101: Declared fixed-width row exceeds container (defer)

Proposed warning, category responsive. **Requires a new schema and generator
contract** for `width`, `gap`, `wrap`, and child `minWidth`; these keys are
currently unsupported. Do not ship a rule or use these as v1 valid fixtures.

Under that hypothetical extension, invalid mini-layout:

```json
{"width":320,"gap":16,"wrap":false,"children":[{"minWidth":200},{"minWidth":200}]}
```

Conforming mini-layout:

```json
{"width":320,"gap":16,"wrap":true,"children":[{"minWidth":200},{"minWidth":200}]}
```

For no-wrap rows only, compare sum(child minima) + gap*(count-1) to width.
Expected future warning anchors the layout's wrap setting; the second explicitly
permits wrapping. These are layout proposals rather than complete v1 components.
Effort: at least two to three days after width units/layout behavior are agreed,
plus rendered viewport tests. Defer until that contract exists.

## Prior art and what to reuse

| Tool / official basis | Relevant capability | Verdict |
| --- | --- | --- |
| [axe-core](https://github.com/dequelabs/axe-core) | Tests a rendered DOM for many accessibility rules; incomplete/manual checks remain | Complement with IR authoring warnings, defer rendered-name/contrast checks to this tooling and manual tests |
| [HTML-validate](https://html-validate.org/usage/) | Offline HTML5 validation, including configurable rules | Reuse against generated HTML when generation exists; do not reimplement HTML parsing/rules in the dashboard analyzer |
| [Stylelint](https://stylelint.io/user-guide/rules/) | CSS and media-query validity/convention checks | Reuse for generated CSS validity; it does not prove viewport reflow or usability |
| W3C labels/reflow guidance linked above | Defines the scope and limitations of the accessibility questions | Use as rule rationale and rendered-test guidance; do not equate a passing compiler warning check with conformance |

No tools are installed as part of this documentation spike. Adding a testing
library later follows normal dependency approval.

## Not feasible from the current static input

- Rendered contrast with runtime styles, transparency, images and dynamic data.
- Keyboard operability, focus trapping/order after DOM mutation, or screen-reader behavior.
- Semantic landmark/heading correctness of HTML that has not been generated.
- Exact text/table overflow, zoom behavior or responsive reflow across browsers.
- Whether a chart's title adequately conveys all relevant data relationships.
- Complete accessibility or WCAG certification.

## Next actions for maintainer triage

Proposal issues [#17](https://github.com/thebhavye/polydash/issues/17) (PD2001) and
[#18](https://github.com/thebhavye/polydash/issues/18) (PD2002) carry the example pairs above;
PR #21 implements them as warnings. Generator label/title mapping still needs
review when generation is implemented.
Recommend accepting those bounded authoring checks. Keep PD2101 deferred until
the layout schema has width/wrap semantics. Drop blanket row/column-count and
"all charts have alt text" rules: the current IR cannot support those claims.
When a generator exists, plan HTML validation, axe checks and manual keyboard/
zoom review rather than replacing them with IR heuristics.
