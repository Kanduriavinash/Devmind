# QuickCart cart reload regression demo

This is an isolated, minimal reproduction for DevMind demos. It models the
inline JavaScript cart persistence pattern in `Kanduriavinash/QuickCart` and
intentionally omits the storage read from the page-load handler. It is **not**
a copy of the current public QuickCart repository and does not claim that the
public repository currently has this defect. The current public `index3.html`
contains both a storage write and a page-load read; reproduce the reported
live-site behavior separately before describing it as an upstream bug.

Expected behavior: add an item, reload the page, and retain the item and count.
Run the baseline regression check inside DevMind's Node Docker sandbox; it
should fail before a candidate repair and pass only after the candidate adds
the missing restoration call. The source project must remain untouched.
