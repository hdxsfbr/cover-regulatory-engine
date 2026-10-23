# Acceptance — 2026-10-22

Stagg's general live browser extraction returned **179.55 ft** and **10,720 sq ft** from the acquired assessor/tract documents. No parcel-specific runtime observations were added. The browser opened the derived-depth explanation and verified source citations and that the front-yard assessment input uses 179.55 ft with machine-corroborated provenance. The front-yard status remains needs-review for independent applicability checks; irregular setback geometry remains withheld.

- 108 backend tests pass (including 22 targeted derivation tests); four existing dependency deprecation warnings remain.
- 24 browser tests pass, including derived measurement operands, assumptions and citation access.
- TypeScript/production build and strict OpenSpec validation pass.
- Actual browser proof, screenshot, model output, recorded-map crops, document reference and logs are in `data/delivery/stagg-depth/`.
- Evidence/interpretation and support limits are documented in `docs/recorded-lot-depth.md`.

The initial model run correctly read an east bearing printed as NORTH; the first parser accepted only quadrant notation and rejected it. Cardinal bearings were added and tested. That initial rejection is retained. A later full browser run with the revised prompt/validator accepted the depth without manual intervention. An initial browser attempt overlapped API restart and timed out before candidates; the completed fresh attempt passed.

GIS transverse dimensions differ from recorded dimensions and the UI reports this. The result is a source-derived approximate depth under the stated rear-boundary interpretation, not professional survey/legal approval. Other irregular shapes remain outside this bounded method; the rotated different-parcel test verifies it is not an address exception.
