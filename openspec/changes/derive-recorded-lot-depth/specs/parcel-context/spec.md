## ADDED Requirements

### Requirement: Recorded boundary lot-depth derivation
The system SHALL derive approximate Chapter 1 LA lot depth from cited recorded boundary measurements for supported straight interior quadrilaterals with effectively parallel side lines and an established opposite rear boundary. It SHALL validate identity, bearings, closure and GIS agreement, retain operands and regulatory references, and label the result machine-corroborated rather than legally verified.

#### Scenario: Stagg unequal side lengths
- **WHEN** the recorded map establishes side lengths 171.10 and 188 feet, effectively parallel bearings, Stagg frontage and the opposite rear boundary
- **THEN** deterministic midpoint depth is approximately 179.55 feet with source-page evidence, assumptions and any GIS boundary discrepancies visible

#### Scenario: Unsupported or conflicting boundary interpretation
- **WHEN** identity, frontage, rear-line treatment, bearings or boundary shape is ambiguous, the lot is curved, corner, through or gore-shaped, or depth conflicts with GIS
- **THEN** no derived depth is accepted and a specific reason is retained without discarding independently valid area observations

#### Scenario: Reuse without clearing legal checks
- **WHEN** a derived depth is accepted
- **THEN** assessments can reuse it without transcription while retaining provenance, professional applicability checks and irregular setback-envelope withholding

#### Scenario: Generalization and cache versioning
- **WHEN** another qualifying parcel is searched or extraction logic changes
- **THEN** the same derivation applies without address-specific logic and old extraction cache results do not suppress the new method
