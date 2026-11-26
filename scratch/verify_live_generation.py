"""Live code-generation test script for DevMind on Cricket Scorer repository.

Tests Stages 1 through 7 independently:
1. Bug description is submitted.
2. Repository analysis completes.
3. Relevant source code is retrieved.
4. An actual request is sent to the configured LLM.
5. The LLM returns a newly generated code patch.
6. The generated patch is parsed into a unified diff.
7. The proposed changes are recorded/displayed.

Then separately tests if the patch applies and passes tests in Docker.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# DevMind imports
from devmind.analyzer import analyze_issue
from devmind.planner import create_plan
from devmind.indexer import index_repository
from devmind.retrieval import retrieve
from devmind.code_agent import generate_candidate_patch, validate_unified_diff
from devmind.providers import OpenAICompatibleProvider
from devmind import sandbox

issue = "In script.js addRun, change matchState.balls += 2; to matchState.balls += 1; so that each legal delivery adds one ball."
repo_path = Path("examples/cricket-scorer-pro-buggy").resolve()

print("=" * 70)
print("DEVMIND LIVE LLM CODE-GENERATION VERIFICATION AUDIT")
print("=" * 70)

# Stage 1: Bug description is submitted
t0 = datetime.now()
print("\n--- STAGE 1: Bug Description Submission ---")
print(f"Timestamp: {t0.isoformat()}")
print(f"Target Repository: {repo_path}")
print(f"Submitted Issue:\n  {issue}")
stage1_success = True

# Stage 2: Repository analysis completes
t1 = datetime.now()
print("\n--- STAGE 2: Repository Analysis ---")
print(f"Timestamp: {t1.isoformat()}")
analysis = analyze_issue(issue)
plan = create_plan(analysis)
chunks = index_repository(repo_path)
print(f"Analysis Summary: {analysis.summary}")
print(f"Extracted Keywords: {analysis.keywords}")
print(f"Component Hints: {analysis.component_hints}")
print(f"Issue Type: {analysis.issue_type}")
print(f"Total Source Chunks Indexed: {len(chunks)}")
print(f"Generated Plan Steps: {len(plan)}")
stage2_success = len(chunks) > 0 and len(analysis.keywords) > 0

# Stage 3: Relevant source code is retrieved
t2 = datetime.now()
print("\n--- STAGE 3: Relevant Source Code Retrieval (RAG) ---")
print(f"Timestamp: {t2.isoformat()}")
query = " ".join([issue, *analysis.keywords, *analysis.component_hints])
ev = retrieve(query, chunks, limit=1)
evidence_records = [
    {
        "path": e.chunk.path,
        "name": e.chunk.name,
        "kind": e.chunk.kind,
        "start_line": e.chunk.start_line,
        "end_line": e.chunk.end_line,
        "score": e.score,
        "content": e.chunk.content,
    }
    for e in ev
]
for idx, e in enumerate(evidence_records, 1):
    print(f"  [{idx}] {e['path']}:{e['start_line']}-{e['end_line']} `{e['name']}` (Score: {e['score']:.4f})")
stage3_success = len(evidence_records) > 0 and evidence_records[0]["name"] == "addRun"
print(f"Stage 3 Success: {stage3_success} (Retrieved target function `addRun`)")

# Stage 4: An actual request is sent to the configured LLM
t3 = datetime.now()
print("\n--- STAGE 4: Actual Request Sent to Configured LLM ---")
os.environ["DEVMIND_LLM_DISABLE_THINKING"] = "true"
base_url = "http://localhost:11434/v1"
model_id = "qwen3:1.7b"
provider = OpenAICompatibleProvider(
    base_url=base_url,
    model=model_id,
    timeout=240,
    max_retries=0,
)
print(f"Timestamp Request Sent: {t3.isoformat()}")
print(f"Provider Class: {type(provider).__name__}")
print(f"Configured Base URL: {provider.base_url}")
print(f"Configured Model Identifier: {provider.model}")
print(f"Timeout Setting: {provider.timeout}s")
print("Sending request to Ollama HTTP API...")

trace: dict[str, object] = {}
patch = generate_candidate_patch(
    issue,
    evidence_records,
    provider,
    investigation=[f"[E1] {evidence_records[0]['name']} may be relevant because its name or source overlaps the issue"],
    repository_metadata={"root_name": repo_path.name, "language": "JavaScript"},
    generation_trace=trace,
)

t4 = datetime.now()
duration = (t4 - t3).total_seconds()
stage4_success = "raw_model_response" in trace

# Stage 5: The LLM returns a newly generated code patch
print("\n--- STAGE 5: LLM Response Received ---")
print(f"Timestamp Response Received: {t4.isoformat()}")
print(f"Total Model Latency: {duration:.2f} seconds")
raw_response = str(trace.get("raw_model_response", ""))
print(f"Raw Model Response Length: {len(raw_response)} characters")
print("-" * 50)
print("EXACT RAW MODEL RESPONSE START:")
print(raw_response)
print("EXACT RAW MODEL RESPONSE END:")
print("-" * 50)
stage5_success = len(raw_response.strip()) > 0

# Stage 6: The generated patch is parsed into a unified diff
print("\n--- STAGE 6: Generated Patch Parsed into Unified Diff ---")
is_valid_diff = False
validation_error = None
changed_files = []
if patch:
    print(f"Parsed & Normalized Candidate Patch:\n{patch}")
    try:
        changed_files = validate_unified_diff(patch, allowed_paths={e["path"] for e in evidence_records})
        is_valid_diff = True
        print(f"Validation Result: VALID (Changed files: {changed_files})")
    except Exception as exc:
        validation_error = str(exc)
        print(f"Validation Result: INVALID ({exc})")
else:
    print("CodeAgent returned None: Model output could not be parsed into a valid unified diff.")
    if "validation" in trace:
        validation_error = str(trace["validation"])
        print(f"CodeAgent validation info: {trace['validation']}")
stage6_success = is_valid_diff and patch is not None

# Stage 7: The proposed changes are displayed in DevMind / recorded
t5 = datetime.now()
print("\n--- STAGE 7: Proposed Changes Recorded / Displayed ---")
print(f"Timestamp: {t5.isoformat()}")
audit_record = {
    "audit_test_name": "live_llm_code_generation_cricket_scorer",
    "timestamp_start": t0.isoformat(),
    "timestamp_request_sent": t3.isoformat(),
    "timestamp_response_received": t4.isoformat(),
    "latency_seconds": duration,
    "model_identifier": model_id,
    "model_base_url": base_url,
    "issue_submitted": issue,
    "target_repository": str(repo_path),
    "analysis_summary": analysis.summary,
    "keywords": analysis.keywords,
    "retrieved_evidence": evidence_records,
    "exact_raw_model_response": raw_response,
    "parsed_candidate_patch": patch,
    "is_valid_unified_diff": is_valid_diff,
    "validation_error": validation_error,
    "changed_files": changed_files,
    "stages": {
        "stage_1_bug_description_submitted": stage1_success,
        "stage_2_repository_analysis_completed": stage2_success,
        "stage_3_relevant_source_code_retrieved": stage3_success,
        "stage_4_actual_request_sent_to_llm": stage4_success,
        "stage_5_llm_returned_generated_code": stage5_success,
        "stage_6_parsed_into_unified_diff": stage6_success,
        "stage_7_proposed_changes_displayed": True,
    },
}

audit_path = Path("reports/live_model_generation_audit.json")
audit_path.parent.mkdir(parents=True, exist_ok=True)
audit_path.write_text(json.dumps(audit_record, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Audit record successfully saved to: {audit_path.resolve()}")

# SEPARATE STEP: Check whether the patch applies and passes tests in Docker
print("\n" + "=" * 70)
print("SEPARATE VERIFICATION: DOCKER SANDBOX TEST EXECUTION")
print("=" * 70)
if patch and is_valid_diff:
    print("Testing candidate patch inside isolated Docker container (`devmind-sandbox:node22`)...")
    try:
        docker_result = sandbox.run_tests(
            repo_path,
            candidate_patch=patch,
            image="devmind-sandbox:node22",
            test_runner="node",
            timeout=120,
        )
        print(f"Docker Executed: {docker_result.get('executed')}")
        print(f"Docker Passed: {docker_result.get('passed')}")
        print(f"Exit Code: {docker_result.get('exit_code')}")
        print(f"Runner: {docker_result.get('runner')}")
        print(f"Command: {docker_result.get('test_command')}")
        print(f"Stdout:\n{docker_result.get('stdout')}")
        if docker_result.get("stderr"):
            print(f"Stderr:\n{docker_result.get('stderr')}")
        audit_record["docker_test_result"] = docker_result
        audit_path.write_text(json.dumps(audit_record, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        print(f"Docker test execution encountered an error: {exc}")
        audit_record["docker_test_result"] = {"executed": False, "error": str(exc)}
        audit_path.write_text(json.dumps(audit_record, indent=2, ensure_ascii=False), encoding="utf-8")
else:
    print("Skipping Docker test execution because no valid patch was produced by the LLM.")

print("\n" + "=" * 70)
print("AUDIT EXECUTION COMPLETE")
print("=" * 70)
