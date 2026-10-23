## Context
The context API and assessment already precede asynchronous EvidenceJob completion. The missing behavior is an explicit view of usable facts, pending dimensions and actions. Keep the existing generation guards and validated completion path.
## Goals / Non-Goals
Make the existing progressive data arrival useful and understandable. Do not stream unchecked model tokens, guess dimensions, or change legal evaluation.
## Decisions
Extend EvidenceJob with initial assessment counts and navigation callbacks. Use a small stage-label map, a persistent availability panel and accepted-measurement summary. Distinguish zero-reading completion, errors and cancellation. Source failure remains unknown rather than an empty positive finding. Preserve draft state through context updates.
## Risks / Trade-offs
Preliminary evaluated counts do not establish full buildability; explicitly limit them to available evidence. Map extraction can finish with no measurements or fail; early findings stay available. Test delayed polling and input changes before validated completion.
