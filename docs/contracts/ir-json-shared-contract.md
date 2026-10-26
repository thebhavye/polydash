# Shared JSON / Dashboard IR contract

Status: **Proposed for joint #2/#6 review**, not the completed specifications. Date: 2026-10-26.

## Remove the planning cycle

Old dependencies: #2 -> #6 -> #2. Both should depend on #1's baseline and develop together against this shared contract; neither waits for the other's issue closure. Joint review reconciles their examples before either is agreed. Downstream tasks requiring both still wait for both. This removes the scheduling cycle without pretending the specifications are independent.

## Minimal common surface

- One input describes one Dashboard. Proposed JSON root: object with title, layout and components. Exact requiredness/defaults remain joint decisions.
- Components have id, type discriminant and schema-declared properties. Nested props versus direct properties is an explicit open decision; do not implement a spelling yet.
- Preserve component order. Layout and DataBinding remain explicit target concepts. #2 chooses the smallest useful model; #6 maps it. Do not silently replace bindings with ad-hoc chart fields.
- Shared unvalidated located values support object/array/string/number/boolean/null, key/value spans and duplicate members. Only successful analysis constructs DashboardIR.
- One schema defines allowed kinds, typed properties and required fields. No widget list is finalized here.
- Retain a path-to-start-location side table for values, with missing fields anchored to the containing object. Key-token spans and end offsets are future refinements. See architecture location conventions.
- Future YAML uses the same analyzer/generator. Equivalent meaning yields equivalent semantic IR, with independently correct source locations.

## Proposed syntax / semantic amendment

Adopt PR #15's v1 boundary as the review proposal: malformed JSON such as `{"title": }` is PD0001 syntax; well-formed JSON with a wrong required dashboard shape such as `{"components": {}}` is loader-level PD0002; unknown kinds and missing fields remain semantic. This agrees with #6's original parse-level shape instruction. Reclassification later would need coordinated code, docs and fixture changes.

Propose rejecting duplicate JSON keys rather than silently retaining the last value. #6 owns the category. Duplicate component IDs are separate semantic errors; #2 owns case/whitespace equality.

## Joint handoff checklist

| Shared decision | #2 owns | #6 owns |
| --- | --- | --- |
| Root vocabulary | Typed meaning/defaults/invariants | Spelling, nesting, rejected shapes |
| Components | Initial kinds and typed properties | Matching JSON forms and error categories |
| Layout/bindings | Small model and reference invariants | Exact JSON representation |
| IDs/numbers | Equality and value constraints | Lexical acceptance, duplicate keys, numeric precision |
| Origins | IR/property provenance | Token/key/value/EOF spans |
| Examples | At least three worked IR examples | At least five valid and five malformed fixtures |

Cross-check the same examples, including wrong shapes, unknown kinds, missing fields and duplicate IDs. Approve property placement, component scope, layout, bindings, defaults, numbers and error categories before implementation. This coordination contract neither completes #2/#6 nor permits YAML implementation.
