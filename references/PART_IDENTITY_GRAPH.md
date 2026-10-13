# PART_IDENTITY_GRAPH — V4.33

**Status:** USER APPROVED / PUSH 2026-10-07.

## 1. Scope

Use when one drawing/detail/DATA cluster contains multiple barcodes/codes, constituent marks such as ①/②, weld/assembly relationships, or multiple candidate manufacturing parts.

The purpose is to prevent assigning one whole view/DATA bundle to multiple part codes without evidence.

## 2. Required graph

Persist an evidence-equivalent mapping:

```text
BARCODE/CODE
<-> PART_ID / CONSTITUENT_ID
<-> SOURCE_VIEW(S)
<-> DATA_CLUSTER(S)
<-> MATERIAL / THICKNESS
<-> ASSEMBLY / WELD RELATION
```

Each edge requires source provenance.

A drawing can show an assembly and its child parts together; paper proximity does not merge them into one manufacturing part.

## 3. Collision gate

### Welded parent/child contact ownership

For an assembly or A/B detail, identify which code owns the main
manufacturing sheet, which constituent is mounted/welded to it, and
which actual physical face hosts each proved contact. Preserve the
assembly-view ID and contact-site provenance in the independent
WELD_SITE_KEGAKI_CLOSURE ledger. A side-positioning view beside a
part is not ignorable merely because its curves are not CUT.
The KH851 customer exception requires marking proved weld sites even
if a KEGAKI callout is absent. Do not transfer the site to an
adjacent barcode solely by paper proximity.


Raise `PART_IDENTITY_COLLISION` when:

- two independent codes receive the same complete DATA/source-view bundle;
- a constituent marker is present but unowned;
- a view is assigned to a code only because it is nearest that barcode;
- material/thickness or explicit part identity conflicts with the proposed ownership;
- a welded child is dropped because its geometry appears inside an assembly drawing.

Shared assembly views are allowed only with an explicit shared-view role; manufacturing child geometry must still be separated by proved ownership.

## 4. Output behavior

If identity is unresolved but source views are identifiable, preserve the views under REVIEW ONLY and FLAG the ownership question. Do not duplicate the same manufacturing geometry under multiple codes as if each were independently solved.

If only one local ownership is unresolved, keep other proved parts/members executable.

## 5. Non-generalization

Constituent symbols, numbering style and weld notation identify candidate ownership structure only within the actual drawing. Do not hardcode a universal meaning for a particular circled number, page position or barcode order without source evidence.
