# Feature — Revision and Cancellation Scope

## Authority and trigger

This is the current production feature rule selected by `REVISION_CANCELLATION`
in `skills/lispcad/router/ROUTER.yaml`. It applies to revisions,
strike-throughs, handwritten/red corrections, clouds and cancellation notes
actually present in the current customer's source.

## Required evidence

1. Identify the affected code, view, note or leader, physical feature family,
   affected member/group IDs, quantity and datum from the source. Apply the
   precedence specified in `skills/lispcad/core/DATUM_DIMENSION.md`.
2. Distinguish cancellation of a whole feature from cancellation of only a
   tolerance, finish or process operation. A struck-through tolerance does not
   automatically delete the underlying CUT geometry.
3. Record both original and effective family counts and preserve canceled
   source members as `CANCELED` in the source ledger. Do not manufacture the
   canceled operation.
4. Do not extend a cancellation to adjacent holes, slots, leaders, codes,
   mirrored parts or DATA clusters without source-proved scope.
5. If identity, scope or affected geometry cannot be proved, route the family
   `UNKNOWN`, isolate the unresolved feature as REVIEW/FLAG, and preserve
   independent proved members. Do not downgrade a complete proved part solely
   because of a local ambiguity.
6. Before PASS, close source manufacturing notes, feature census, canonical
   member mapping, active and canceled quantities, and saved-DXF read-back.

## Evidence boundary

`regression/datum/520709-07_APPROVED.md` contains an approved example where
two whole Ø8H7 holes were canceled. Its code IDs, coordinates and quantities
are case-specific regression evidence, **not universal manufacturing rules**.
Load that regression only for relevant QA or explicit audit; never use it
as the ordinary feature rule or as a source of missing dimensions.
