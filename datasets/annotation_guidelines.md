# Issue localization annotation guidelines

## Label types

- `changed_file_proxy`: a file in the linked fix diff, kept as a weak file-level localization label.
- `reviewed_file`: a reviewer independently judged the file relevant to the issue using the issue and base-commit source.
- `reviewed_function`: a reviewer independently identified a relevant function and recorded its exact base-commit span in an extended annotation record.
- `excluded`: an issue or changed file excluded under an explicit reason.

Never relabel a changed file as an exact bug location without independent inspection. A PR may include tests, formatting, refactoring, generated artifacts, or related changes. Keep each PR-changed path and the reviewer decision so filtering is auditable.

## Review procedure

1. Read only the issue report and the base-commit code to judge localization. Do not inspect the fix commit before making any independent `reviewed_*` judgment.
2. Record the fix/PR metadata and changed-file proxy in separate provenance fields after the independent judgment.
3. Mark confidence `high`, `medium`, or `low` and write a reason for every excluded or ambiguous path.
4. If two annotators are available, annotate independently first; reconcile disagreements afterward and retain both original labels plus the adjudicated decision.
5. Report inter-annotator agreement only when there are multiple independent annotations and state the statistic and sample size.
6. Do not infer function-level fault labels by assigning every function in a changed file as relevant.

## Getting the correct base source

`annotation_review_packet.csv` contains workspace-local snapshot paths for use on the evaluation machine. If reviewing elsewhere, use only the repository and `base_commit` recorded in the packet. For example, in PowerShell:

```powershell
git clone --no-checkout https://github.com/<owner>/<repository>.git <local-folder>
git -C <local-folder> checkout --detach <base_commit>
```

Replace the placeholders with the packet values. Confirm `git -C <local-folder> rev-parse HEAD` equals the packet's full `base_commit` before review. Open source files for static reading only; do not install dependencies, run tests, or execute repository code. Do not browse pull requests, fixing commits, or current/default-branch source while forming the independent judgment. If the base commit cannot be fetched, record the case as unavailable instead of substituting another revision.

## Leakage controls

`evaluation_inputs.csv` may contain issue text, repository identity, base commit, language, and a local path to the base snapshot. It must not contain fix URLs, fix commit IDs, commit messages, patches, changed-file lists, test changes, or post-fix source. The retrieval pipeline must index only the base snapshot. The ground-truth CSV is joined after ranking for metric calculation; it must not be used to construct the query, chunk text, or retrieval score.

## Confidence and disagreement

Use confidence as a human judgment field, not a probability. Preserve unresolved disagreement rather than forcing a label. Report metrics both with and without low-confidence proxy labels if enough records exist; if not, state that the sample is too small.

