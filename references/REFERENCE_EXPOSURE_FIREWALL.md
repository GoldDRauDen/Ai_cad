# REFERENCE_EXPOSURE_FIREWALL — V4.33

**Status:** USER APPROVED / PUSH 2026-10-07.

## 1. Purpose

Prevent hindsight/reverse-fit after a sample/reference DXF becomes visible.

The failure this gate prevents is:

`source unresolved -> inspect sample -> learn the answer -> rewrite history as "source was already clear"`.

A reference can diagnose, verify or teach a general lesson. It cannot retroactively change what the source-only solver had actually established.

## 2. Source-only freeze

Before a reference/sample is opened for calibration or comparison, persist an immutable `SOURCE_ONLY_SNAPSHOT` containing, at minimum:

- source file identities/hashes when available;
- code/part identity state;
- preliminary/final feature census;
- source groups and source members;
- part-identity graph when applicable;
- FACE_GRAPH / candidate topology state;
- dimension/witness ownership;
- current canonical/provisional output status;
- unresolved objects and blocker classes;
- claims with evidence provenance.

The snapshot must exist before `REFERENCE_EXPOSED=true`.

## 3. Post-reference statuses

Use these explicit states:

- `SOURCE_ONLY_SOLVED`
- `SOURCE_ONLY_UNRESOLVED`
- `REFERENCE_ASSISTED_UNDERSTANDING`
- `REFERENCE_CONFLICT`
- `CUSTOMER_CONFIRMATION_PENDING`

A claim that was unresolved before reference exposure does not become source-proved merely because the reference reveals a plausible answer.

## 4. Provenance immutability

After reference exposure:

- reference/sample evidence remains `APPROVED_REFERENCE` or `REFERENCE`, never silently rewritten as PRINTED/CUSTOMER_DATA;
- an unresolved pre-reference claim may be upgraded to source-proved only when new non-reference evidence is identified and recorded;
- job-specific reference coordinates must not be copied into a new source interpretation;
- a general lesson may be promoted only through the normal FACT -> ROOT_CAUSE -> PROPOSED_LESSON -> REGRESSION_CASE -> APPROVAL process.

If a session has already seen the sample, that same session cannot prove a truly blind source-only solve by re-reading the source.

## 5. Sample FLAG boundary

When the operator declares sample FLAG/Magenta geometry to be pending customer confirmation:

`SAMPLE_FLAGGED_GEOMETRY -> CUSTOMER_CONFIRMATION_PENDING`.

Such geometry is not approved-reference authority. It must not:

- fill a missing source dimension;
- resolve a source topology;
- become production geometry merely because it is present in the sample;
- be promoted into a universal rule.

It may be compared and reported as pending. Only independent source evidence or explicit user/customer confirmation may close it.

## 6. Blind regression requirement

For calibration cases intended to prove future source-only capability:

1. withhold the sample/reference from the solver;
2. run the full source-only pipeline;
3. persist/freeze the source-only result;
4. only then expose the sample to the comparator;
5. classify mismatches without changing the frozen provenance.

A regression that lets the solver see the expected sample before source-only freeze is not evidence that the AI can solve the drawing independently.

## 7. Audit rule

When a pre-reference field changes from unresolved/FLAGGED to PROVED after sample exposure, require one of:

- new PRINTED/HANDWRITTEN-REVISION/CUSTOMER_DATA/USER_CONFIRMED evidence not available in the frozen snapshot; or
- keep the result as `REFERENCE_ASSISTED_UNDERSTANDING`.

Otherwise fail `POST_REFERENCE_SOURCE_REWRITE`.

## 8. Non-generalization

This firewall does not make a sample untrustworthy. Approved reference geometry remains valuable audit evidence. The rule only preserves chronology and provenance so the AI cannot claim prior understanding that did not actually exist.
