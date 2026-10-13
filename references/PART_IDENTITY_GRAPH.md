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

## 2A. Assembly datum ownership and indirect feature positions

When an assembly/installation view provides the only route to a child part's hole, slot or KEGAKI position, keep its shared **assembly-frame dimension witnesses** distinct from the child's physical manufacturing geometry. Before flagging that child feature as undimensioned:

- prove each participating barcode/part code, target feature, host face and related parent/child part;
- resolve physical assembly contact/attachment and witness identities, not proximity of views or nominal symmetry;
- hand the proved, signed relation graph to `skills/lispcad/core/DATUM_DIMENSION.md` §4.2.2b, then apply any required face-to-flat transform;
- audit each derived feature from the child's own datum with the source evidence and assembly-fit closure;
- retain unresolved physical relationships as local FLAG. Do not copy reference/sample coordinates or silently duplicate child contours under the parent code.

The graph solves *positions*, not part ownership; it cannot replace PART_IDENTITY_GRAPH or create a manufacturing feature not actually called out in the source.

## 3. Collision gate

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
