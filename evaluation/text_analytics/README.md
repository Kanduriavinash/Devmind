# Text Analytics evaluation status

DevMind's existing Task Analyzer is deterministic and rule-based. It has no independently annotated issue-classification corpus, so precision, recall, F1, and accuracy are unavailable.

The new query-variant trace supports a retrieval ablation; it does not change or validate issue-category classification. If supervised category classification is later attempted, prepare independent labels with repository-aware splits, preserve class imbalance in evaluation, compare the rule baseline with TF-IDF + Logistic Regression and Linear SVM, and report per-class precision/recall/F1 plus macro and weighted F1 and a confusion matrix. Do not split near-duplicate reports from one repository across train and test. No classifier result is present now.

