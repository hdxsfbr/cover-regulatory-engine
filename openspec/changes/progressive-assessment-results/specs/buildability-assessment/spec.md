## ADDED Requirements
### Requirement: Progressive assessment availability
While map extraction runs, the interface SHALL show available parcel identity, zoning status, map availability and preliminary constraint counts, with direct actions to inspect results and edit design inputs. Pending measurements SHALL not be represented as established facts. Completion SHALL update results from validated evidence without erasing user inputs.
#### Scenario: Slow map extraction
- **WHEN** parcel context and an initial assessment arrive before extraction completes
- **THEN** users see available facts and preliminary result counts and can inspect or edit their design while extraction continues
#### Scenario: Validated completion
- **WHEN** extraction completes
- **THEN** accepted measurements appear, dependent results update and remaining applicability checks stay explicit
#### Scenario: Empty or failed reading
- **WHEN** extraction yields no measurements, fails or is cancelled
- **THEN** previously available facts remain usable and the interface explains the outcome and offers applicable recovery
### Requirement: Understandable extraction stages
Extraction progress SHALL use plain-language stages and distinguish map reading from legal verification without invented progress percentages or time estimates.
#### Scenario: Stage advances
- **WHEN** a job advances from document discovery to reading and validation
- **THEN** the displayed stage and explanation change while available facts remain visible
