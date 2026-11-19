# Review a failed test

Use this before editing the agent or the test. A protected test is any case, control, or suite required by acceptance, CI, promotion, or release rules. If its status is unclear, treat it as protected until the owner confirms it.

## Establish what the failure shows

1. Preserve the original case revision, expected outcome, inputs, simulator instructions, fixtures, judge criteria, run IDs, transcripts, and judge rationale. Identify the exact baseline and candidate. Record any missing evidence.
2. Read the turns and trace in order. Find the first meaningful divergence from the intended scenario and check which agent path ran. Compare with a matched run on the other arm. Decide whether each simulator reply followed the question it actually received. A later simulator error does not erase an earlier agent error. A run that misses the target cannot prove the target behavior, but it may expose a routing or downstream defect.
3. Check what the judge could see and whether its reason follows from that evidence. Record all supported findings: agent behavior, simulator or fixture problem, grader or criterion problem, or OPEN. A score change or a single rerun does not establish cause. Keep the failed verdict and any unresolved findings visible.

## Review a proposed test repair

1. Prepare an exact diff in a separate draft. State the evidence for each edit and the original customer outcome it preserves. Include changes to the simulator, stop rules, fixtures, judge inputs, criteria, thresholds, suite membership, and exclusions when they affect what is exercised or scored. A change to the expected outcome needs an explicit acceptance decision from its owner.
2. Compare the old and proposed revisions on the same baseline and candidate configurations. Reuse matching recorded runs when their inputs and setup are verified. Run any remaining comparisons on an isolated draft case with the applicable run authorization, simulation safety checks, and budget. Show which path each revision exercised. Where available, show that known-good behavior still passes and known-bad behavior still fails. Record missing controls or comparisons as OPEN.
3. Get the test owner's approval of the specific diff before applying it to a protected case or its gate. A request to finish the work, permission to run a comparison, or approval to promote does not approve a test diff. Unattended work can prepare evidence and request review. It cannot approve its own change or remove a failed run from the gate.
4. Read back the approved revision and rerun the protected suite on the intended candidate under the existing gate. Keep the original failure and comparison with the decision record. The release remains blocked until the required gate passes. A focused comparison or a green run on an isolated draft cannot clear it.
