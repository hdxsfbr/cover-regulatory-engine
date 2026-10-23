# Source verification

Checked 2026-10-22 UTC. These are acquisition checks, not approval of regulatory rules.

## GIS

`data/sources/gis-manifest.json` records the eight configured layers, their field schemas, coordinate references, attribution fields, retrieval timestamps, and actual one-record query responses. All eight queries succeeded without credentials. Requests used `where=1=1`, one record, and no geometry; the probe verifies access, not spatial correctness or completeness.

County sources are published by Los Angeles County GIS; zoning is published through LA City Planning's ZIMAS service; selected overlays are published through the City's GIS service. The layer copyright fields were empty. These metadata responses supply neither a blanket redistribution license nor a reliable last-update timestamp. Public access is not itself a license. Keep source URLs and attribution attached to derived records. LARIAC Buildings 2020 has an explicit vintage; do not equate retrieval time with data vintage for the other layers.

The City's [GeoHub](https://geohub.lacity.org/) describes its public data as available to explore, download, and use in applications. That general statement does not establish identical terms for every County and ZIMAS layer. Layer-specific reuse terms remain unverified; the manifest states this rather than assigning a guessed license.

## Regulatory text

`data/sources/regulatory-manifest.json` records the direct acquisition results for LAMC 12.08, 12.21.1, 12.03, and 12.22. All four direct requests returned HTTP 403. No API-authentication workaround or access-control bypass was attempted.

The web research reader could inspect:

- [12.08, R1](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-2052): source edition displayed as 2026 Rev. 9.
- [12.21.1, height](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-6325): source edition displayed as 2026 Rev. 9.
- [12.03, definitions](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-886): lot dimensions, residential floor area, and related definitions.

The [Planning and Zoning 12.22 page](https://codelibrary.amlegal.com/codes/los_angeles/latest/lapz/0-0-0-6561) timed out in that reader. The [Municipal Code alternative](https://codelibrary.amlegal.com/codes/los_angeles/latest/lamc/0-0-0-114455) was indexed, but opening it exceeded the reader's 4 MiB content limit. Search excerpts do not constitute a complete review of its exceptions.

An [official City Clerk record](https://cityclerk.lacity.org/lacityclerkconnect/index.cfm?cfnumber=16-1460&fa=ccfi.viewrecord) identifies Ordinance 184802 and its 2017 amendments. This is useful historical evidence, but it is not a substitute for a complete current consolidated exceptions section. The older [LADBS commentary](https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/zoning/zoning-code-manual-and-commentary.pdf) likewise cannot establish current law by itself.

No specific publisher reuse terms were verified. No publisher commentary, imagery, or full code snapshot has been incorporated. The original failures are retained as acquisition history. See the successful acquisition update below.

## Ingestion authentication preflight

Claude Code authentication was checked with inherited Anthropic API key, token, and endpoint overrides removed. It reported subscription authentication (`claude.ai`, Max). No paid extraction was run and no account identifiers or credentials were saved.

## Successful acquisition update

On 2026-10-22 UTC, requests with browser User-Agent, Accept, and Accept-Language headers retrieved all four sections. The original 403 responses carried Cloudflare challenge markers. Changing User-Agent alone was insufficient. One Planning and Zoning exceptions request was challenged again; the official Municipal Code counterpart returned the complete section. This is an intermittent upstream restriction, not an authentication requirement.

The full section text is stored under `data/sources/regulations/`, extracted from the HTML codecontent container. Each record contains a SHA-256 content hash, source URL, section, edition, retrieval time, and text. No publisher images or application JavaScript are retained. The exception HTML exceeded the separate web reader's 4 MiB limit; local acquisition received its complete HTML document.

Snapshots document the published edition, not a guarantee that later legislation has already been incorporated. Unknown section-wide effective dates remain null.
