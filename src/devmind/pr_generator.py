"""Generate structured GitHub Pull Request drafts from DevMind run reports."""

from __future__ import annotations

from typing import Any


def generate_pr_draft(report: dict[str, Any]) -> str:
    """Format an evidence-backed GitHub Pull Request description from a run report.
    
    Includes issue summary, localized evidence references, candidate diff,
    test verification results from Docker, and reviewer approval status.
    """
    issue = report.get("issue", "No issue description provided.")
    status = report.get("status", "unknown")
    patch = report.get("candidate_patch", "")
    test_result = report.get("test_result") or {}
    review = report.get("review") or {}
    analysis = report.get("analysis") or {}
    evidence = report.get("evidence") or []
    investigation = report.get("investigation") or {}

    # Extract primary symbol and path for title
    primary_file = "repository"
    primary_symbol = ""
    if evidence and isinstance(evidence[0], dict):
        primary_file = evidence[0].get("path", "source")
        primary_symbol = evidence[0].get("name", "")

    title_symbol = f" in `{primary_symbol}`" if primary_symbol else ""
    title = f"fix({primary_file}): resolve bug{title_symbol}"

    # Build evidence references
    evidence_lines: list[str] = []
    for idx, item in enumerate(evidence[:5], start=1):
        path = item.get("path", "unknown")
        start = item.get("start_line", "?")
        end = item.get("end_line", "?")
        name = item.get("name", "anonymous")
        score = item.get("score", 0.0)
        evidence_lines.append(f"- **[E{idx}]** `{path}:{start}-{end}` (`{name}`) — Cosine Similarity: `{score:.4f}`")
    evidence_text = "\n".join(evidence_lines) if evidence_lines else "- No specific evidence chunks linked."

    # Test execution summary
    test_passed = test_result.get("passed", False)
    test_executed = test_result.get("executed", False)
    test_runner = test_result.get("runner", "isolated container")
    if test_executed:
        test_badge = "✅ **TESTS PASSED (ISOLATED DOCKER SANDBOX)**" if test_passed else "❌ **TESTS FAILED**"
        exit_code = test_result.get("exit_code", 0)
        test_summary = f"{test_badge}\n- Runner: `{test_runner}`\n- Container Exit Code: `{exit_code}`\n- Isolation: `--network=none`, `--memory=1g`, `--read-only`"
    else:
        reason = test_result.get("reason", "Docker test runner was not executed.")
        test_summary = f"⚠️ **TESTS NOT EXECUTED**\n- Reason: {reason}"

    # Review verdict
    verdict = review.get("verdict", status)
    reason = review.get("reason", "A candidate patch is a proposal requiring human review.")

    pr_body = f"""# {title}

## 📋 Problem Description
{issue.strip()}

- **Issue Type:** `{analysis.get('issue_type', 'general')}`
- **Identified Keywords:** {', '.join(f'`{k}`' for k in analysis.get('keywords', [])[:6]) or 'N/A'}

---

## 🔍 Root Cause & Traceable Evidence (RAG Localization)
DevMind statically indexed the repository and localized the fault to the following source spans:

{evidence_text}

### Investigation Hypotheses:
"""
    for hyp in investigation.get("hypotheses", [])[:3]:
        pr_body += f"- {hyp}\n"
    if not investigation.get("hypotheses"):
        pr_body += "- Code evidence overlaps reported symptoms.\n"

    pr_body += f"""
---

## 🧪 Isolated Verification Results
{test_summary}

---

## 🛡️ Reviewer Gate Status
- **Verdict:** `{verdict}`
- **Reviewer Note:** {reason}

---

## 💻 Proposed Candidate Patch
```diff
{patch.strip() if patch else "# No candidate diff generated"}
```

### How to Apply Locally:
```bash
git apply devmind-candidate.patch
```
*Generated autonomously by DevMind Agentic RAG Framework.*
"""
    return pr_body.strip()
