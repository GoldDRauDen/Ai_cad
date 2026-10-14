# WELD_SITE_KEGAKI_CLOSURE — source-first hard gate

**Scope:** source-proved or source-suspected weld/assembly contact, with
**KH 851** as the customer-scoped mandatory marking exception. This is a
completeness check, not a geometric formula.

## Source authority before CAD output

1. Read numeric customer code from JOB STATISTICS, never a barcode suffix
   or Japanese name. KH 851 requires KEGAKI at every proved weld site
   even if no marking callout appears in the drawing (catalog J418).
2. Independently harvest all source assembly views, A/B or parent/child
   identities, physical weld/contact sites and installation witnesses
   BEFORE drawing marking coordinates.
3. Identify main/parent as the sheet being marked and child as the mounted
   part, including the actual physical host face. Never merge an assembly
   view into CUT, or copy the entire child outline as locating marks.
4. Solve each contact/mark with source dimensions, projection and
   physical face/attachment transforms; folded geometry must fold back
   to the same weld site.
5. If a required KEGAKI location remains unresolved, preserve a local
   source/canonical FLAG and mark the part REVIEW. No fabricated RED line.

V4.27 remains active for other customers: source-scoped weld cue plus a
non-self-locating child requires KEGAKI. A generic RIB/support does not
alone prove welding; self-locating pieces without a source/customer rule
do not acquire automatic marks. KH851 overrides only the need for a
printed marking callout once a physical weld site is proved.

## Independent source-census ledger

Persist per code before feature routing:

- part_code: the part's exact barcode/identity (e.g. 059685)
- customer_code: numeric ID from job statistics (e.g. 851)
- source_assembly_view_ids: all relevant views, including side A/B views
- source_weld_site_ids: independent welded-contact/site inventory
- weld_site_census: source_evidence, inspected_assembly_view_ids,
  sites, and no_weld_evidence if sites is empty

Each site retains weld_site_id, status (PROVED/FLAGGED), parent_code,
child_part_id, assembly_view_id, source_evidence, host_face for proved
sites, mark_status (PROVED/FLAGGED) for required marks, mark_member_ids
and source-backed datum_evidence for proved marks. Unresolved fields
are written to unresolved_fields. Other customers may require marks
from mark_required_by_source or a proved weld_required_cue with
self_locating=false. Non-required cases need not_required_evidence.

The two independent source inventories MUST agree with the weld-site
census. No-weld disposition requires an explicit source-grounded reason;
an empty list is not enough. A closed ledger does not prove that the
Reader actually inspected the PDF: independent source/holistic QA must
still check all views, dimensions and weld/contact evidence.

### Manufacturing mark provenance

A proved marking must have a host-face datum/witness expression and real
KEGAKI source-backed canonical members. Manufacturing mark entities
are RED (DXF color 1), role kegaki, LINE or source-proved LWPOLYLINE.
Unconfirmed marks remain FLAGGED_NO_GEOMETRY or an explicit Magenta
preview/source-view (never RED or CUT). Any missing required mark is FAIL.

Do not borrow missing dimensions or coordinates from a sample/reference:
the source-only reference firewall remains mandatory.

## Executable gates

- Router: tools/resolve_rules.py checks a complete independent source
  weld inventory for KH 851 and refuses KEGAKI=NO on required sites.
- Canonical: tools/canonical_contract.py calls the new
  tools/weld_kegaki_guard.py before exporting, ensuring every required
  weld site has a real KEGAKI source+canonical member and proved RED
  geometry, or a local REVIEW/FLAG. Canonical entity IDs/read-back remain.
- Holistic QA: compare actual source assembly views and part identities
  with the inventory. Ledger self-equality is never sufficient when
  the real source contains an unharvested weld feature.

## Regression targets (521013-12)

- 059685: A-B installation/weld to KEGAKI is required under KH851
  without an explicit mark callout; omitted group must FAIL.
- 059676 and 059678: classify separate contacts/mark groups by
  source witness and part identity, not by copying sample U-shapes.
- 059683: user's red 14 mm dimension is CUSTOMER_CONFIRMATION_PENDING,
  not production geometry, even if the DXF sample contains Magenta.
- For other customers, genuinely self-locating contacts with no source
  marking obligation must not automatically receive KEGAKI.

Synthetic regression geometry exercises these gates but is NOT an
independent CAD solution of the user's PDF.

This change does not alter Nobi, R/C, source hierarchy, other customer
rule data, or the TrainAiCad-CANONICAL-V4.31 schema version.
