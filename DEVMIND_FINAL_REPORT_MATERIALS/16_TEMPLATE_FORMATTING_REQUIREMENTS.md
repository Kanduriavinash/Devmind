# 16. Template and Formatting Requirements (Procedia Computer Science / ICMLDE)

This document extracts all formal formatting instructions from `Faculty_Provided_PROCS_ICMLDE2024_Template.pdf` and `reports/devmind-report-draft/README.md` to ensure the final report complies with Elsevier Procedia Computer Science specifications:

---

## 1. Document Layout & Page Constraints
- **Document Class:** `\documentclass[3p,times,procedia]{elsarticle}` with `\usepackage{ecrc}`.
- **Page Format:** Single-column format suitable for direct printing on trim size $192 \times 262$ mm.
- **Margins:** Top margin 25mm, bottom margin 25mm, left margin 20mm, right margin 20mm.
- **Line Clearances:** Leave exactly one blank line between paragraphs. Avoid manual line hyphenation at the ends of lines.
- **Page Numbering:** Do not manually number pages on the front; page numbering is injected by the publisher.

---

## 2. Front Matter Specifications
1. **Journal Header:**
   - Procedia Computer Science 00 (2025) 000–000
   - Conference Title: *International Conference on Machine Learning and Data Engineering*
2. **Title:**
   - Capitalize first letter of each major word.
   - Example: `DevMind: An Evidence-Grounded Agentic RAG Framework for Autonomous Multi-Language Bug Localization, Verification, and Sandboxed Program Repair`
3. **Authors & Affiliations:**
   - Format: `First Author a, Second Author a, Third Author a, *`
   - Address block: Department of Computer Science and Engineering, Amrita School of Computing, Amrita Vishwa Vidyapeetham, Amritapuri, India.
   - Explicit corresponding author footnote (`* Corresponding author. Email: ...`).
4. **Abstract:**
   - Single paragraph, self-contained, 150–250 words. Must summarize background, problem, methodology, empirical findings, and limitations.
5. **Keywords:**
   - Exactly 5 to 6 keywords separated by semicolons (`;`).
   - Example: `Software Bug Localization; Retrieval-Augmented Generation (RAG); Reciprocal Rank Fusion; Unified Diff Validation; Non-Root Docker Sandboxing; Text Analytics.`

---

## 3. Structural & Typographical Rules
1. **Nomenclature (Optional Box):**
   - Placed immediately following the Introduction in a dedicated framed table/box matching body font size.
2. **Section Headings:**
   - Main sections: Numbered with Arabic numerals (`1. Introduction`, `2. Related Work`), bold, 10 pt font, capitalized first letter.
   - Subsections: Numbered with decimal format (`1.1. Structure`, `3.2. Vector Representation`), italicized, left-justified.
   - Ensure a minimum of two lines of body text follow any heading before a page break.
3. **Tables:**
   - Captions MUST be placed **ABOVE** the table, left-justified (e.g., `Table 1. Retrieval strategy performance comparison across five evaluation repositories.`).
   - Use standard Elsevier horizontal rules: `\toprule`, `\midrule`, `\bottomrule`. **Vertical table lines are strictly prohibited.**
   - All tables must be embedded in the text near their first reference, not placed at the end.
4. **Figures:**
   - Captions MUST be placed **BELOW** the figure, centered or left-justified (e.g., `Fig. 1. DevMind End-to-End System Architecture.`).
   - Must be minimum 300 DPI high-resolution vector/raster graphics.
5. **Mathematical Notation:**
   - Vectors and matrices indicated in **bold** (`\mathbf{e}_q`).
   - Scalar variables indicated in *italics* ($k, b, N$).
   - Standard SI units for measurements (seconds: `s`, megabytes: `MiB`).
6. **Citations & References:**
   - In-text citation style: Bracketed numbers (`[1]`, `[2,3]`).
   - Placement: References section collated at the very end of the manuscript.
   - Acknowledgements: Collate in a separate unnumbered section immediately before References.
