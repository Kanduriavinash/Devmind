# DevMind term report draft

This is an evidence-based manuscript draft in the faculty-provided Procedia
Computer Science LaTeX format. The current review build is
`build/review_2026-11-17/DevMind_Term_Report.pdf`; it includes the dense retrieval
results, corrected references, and current Docker evidence. It was compiled with
Tectonic/XeTeX and visually inspected across all eight pages. The faculty
PDFLaTeX build remains unverified.

## Files

- `DevMind_Term_Report.tex` — report source.
- `DevMind_Term_Report_Tectonic_Preview.pdf` — current 8-page review preview compiled
  with Tectonic 0.17.0; it is not the final faculty-environment build.
- `figures/devmind-architecture.pdf` — original system diagram.
- `figures/devmind-repair-workflow.pdf` — original bounded-repair diagram.
- `generate_figures.py` — regenerates the two diagrams.
- Both vector figures are embedded from this folder by `DevMind_Term_Report.tex`.
- `elsarticle.cls`, `ecrc.sty`, `procslogo.pdf` — supporting files copied from
  the faculty-provided package so the draft can be compiled from this folder.

## Compile

For the faculty workflow, install a LaTeX distribution with PDFLaTeX and the
standard graphics packages. From this folder, run:

```text
pdflatex DevMind_Term_Report.tex
pdflatex DevMind_Term_Report.tex
```

The current review PDF was compiled with the pinned Tectonic 0.17.0 binary
(SHA-256 `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`) using
`tectonic -X compile --reruns 2 --keep-intermediates --keep-logs --untrusted
--outdir build/review_2026-11-17 DevMind_Term_Report.tex` and visually reviewed
across all eight pages. The build has a publisher-template header overflow and
some underfull spacing warnings; the former remains a layout defect to resolve
if the faculty permits changing the supplied class/template. This XeTeX preview does not certify
the PDFLaTeX build or its appearance in the faculty's final environment. The
supplied template also still displays placeholder publication metadata (year
2025 and volume 00), which must be confirmed or replaced by the faculty.

## Before submission

1. Confirm the three author names and order against the team roster; replace the remaining institution, city, and faculty placeholders.
2. Confirm the final author order, corresponding author, and acknowledgements.
3. Recheck the recorded test counts and run reports at the final project freeze;
   the latest full suite was 179 passed and 3 Windows symlink skips in 5.73s
   (17 November 2026).
4. Build with the faculty's intended PDFLaTeX environment and inspect every
   page at normal reading size; verify fonts, overflow, floats, references, and
   the template's publication metadata before submission.
5. Keep the distinction between implemented functionality, recorded tests,
   planned evaluation, and unmeasured quality claims intact.

The two friends' reports were used only to identify useful report structures
and transparency practices. Their text, tables, diagrams, and results were not
copied into this draft.


## Reference verification

BRaIn is cited as an arXiv preprint, not as conference proceedings. Reformulate, Retrieve, Localize is cited under its verified BotSE 2026 workshop name. SpIDER uses the ACL Anthology record and page range instead of an unverified DOI. Primary records: https://arxiv.org/abs/2501.10542, https://conf.researchr.org/details/icse-2026/botse-2026-papers/5/Reformulate-Retrieve-Localize-Agents-for-Repository-Level-Bug-Localization, and https://aclanthology.org/2026.emnlp-main.1938/.
