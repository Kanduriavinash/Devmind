# Presentation accuracy review

**Deck reviewed:** `DevMind_Presentation.pptx` (15 slides), inspected from the current project workspace on 17 November 2026. This review identifies claim corrections needed before presentation. It does not modify the deck.

## Required claim corrections

| Slide | Current claim or framing | Evidence-based correction |
|---|---|---|
| 1 | “Agentic RAG Framework” and “Autonomous … Repair & Verification” | Describe DevMind as a local bug-analysis prototype with optional model-generated patch proposals and disposable Docker tests. It is not an autonomous repair system. |
| 3 | A unified pipeline that localizes, patches, verifies, and outputs a PR draft | State that DevMind accepts a local repository or public GitHub URL, retrieves traceable evidence, can request a candidate diff, and can test it in Docker. A passing selected test requires human review. DevMind does not create or submit PRs. |
| 4–5 | Broad claims that existing systems lack repository context or end-to-end verification | Cite specific prior work and compare scope carefully. SWE-agent, AutoCodeRover, Agentless, and RepairAgent already study repository navigation, localization, tool use, and/or testing; do not claim novelty for these general capabilities. |
| 6 | Objectives shown as completed features | Keep these as objectives and add current status. The project has a deterministic analyzer, TF-IDF retrieval, optional local embeddings, optional model patching, and Docker candidate tests; trained classification and verified real-repository repairs are not established. |
| 7 | Broad GitHub repository and SWE-bench-style experiment setup | Report the actual retrieval study: five SWE-bench Lite development issues from five repositories, four query variants, five methods, and one unreviewed changed-file proxy per issue. No repair benchmark was graded. |
| 8–9 | Independent “agents” and an end-to-end PR-draft workflow | Call this a staged workflow, not a set of autonomous agents. The Task Analyzer and Planner are deterministic; model investigation/patching is optional. Output is a run report and candidate diff, not a PR draft. |
| 10 | Embeddings/vector database are the main retrieval pipeline | TF-IDF is the default. Dense Sentence Transformers retrieval is optional and local. In the five-case proxy pilot, dense cosine scored lower than TF-IDF on P@5, Recall@5, MRR, and nDCG@5 and took 594.737 seconds to build indexes. |
| 11–12 | Separate agents, GitHub cloning, deployment, and broad evaluation framework presented as established | Distinguish implemented modules from planned evaluation. Public GitHub repositories are imported as bounded ZIP snapshots; no repository code is run on the host. The optional API is loopback-only, and the extension only launches the local app with a public repository URL. |
| 13 | Scope limited to Python, while listing PR output and broad autonomous workflow | State that Python and JavaScript/TypeScript have the most complete examples; the extension is an unpacked local launcher. Private-repository auth, PR creation, auto-merge, hosted deployment, official SWE-bench grading, and verified real-issue repair are not established. |
| 14 | References | Keep primary, verified citations and ensure every literature claim is supported. The manuscript bibliography was separately checked and corrected for BRaIN, BotSE 2026, and SpIDER. |

## Measured retrieval result for slide 10

For the five unreviewed file-change proxies, mean raw-query metrics were:

- TF-IDF: P@1 0.400, P@5 0.160, Recall@5 0.800, MRR 0.550, nDCG@5 0.612321.
- Dense cosine: P@1 0.400, P@5 0.080, Recall@5 0.400, MRR 0.400, nDCG@5 0.400.

These figures are descriptive agreement with weak proxy labels, not fault-location ground truth or repair accuracy. The derived results and raw evidence are in `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json` and `evaluation/raw_runs/`.

## Current release limits

The model-generated Qwen candidate for the synthetic cart fixture failed to apply, and a follow-up request timed out. A deterministic fixture provider passed a known patch after one intentionally bad attempt; that is not model repair evidence. No public QuickCart or cricket-scorer repository was modified or validated by this run.

The current slide authoring runtime lacks `@oai/artifact-tool`. The deck therefore remains unchanged pending a managed presentation-authoring runtime; use the corrections above when editing, then render and inspect all slides.
