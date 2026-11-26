import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { runInNewContext } from "node:vm";
import test from "node:test";

const workerSource = await readFile(new URL("../service-worker.js", import.meta.url), "utf8");

async function simulateClick({ tabUrl, appUrl = "http://localhost:8501" }) {
  let clickHandler;
  const createdTabs = [];
  const chrome = {
    action: { onClicked: { addListener(handler) { clickHandler = handler; } } },
    storage: { sync: { get: (_defaults, callback) => queueMicrotask(() => callback({ appUrl })) } },
    tabs: { create: (details) => { createdTabs.push(details); return Promise.resolve(); } },
  };
  runInNewContext(workerSource, { chrome, URL });
  return new Promise((resolve) => {
    chrome.tabs.create = (details) => { createdTabs.push(details); resolve(createdTabs); };
    clickHandler({ url: tabUrl });
  });
}

test("clicking on a GitHub issue opens DevMind with the repository prefilled", async () => {
  const tabs = await simulateClick({ tabUrl: "https://github.com/pallets/click/issues/42" });
  const destination = new URL(tabs[0].url);
  assert.equal(destination.origin, "http://localhost:8501");
  assert.equal(destination.searchParams.get("repo"), "https://github.com/pallets/click");
});

test("clicking outside GitHub still opens DevMind without a repository", async () => {
  const tabs = await simulateClick({ tabUrl: "https://example.com/page" });
  const destination = new URL(tabs[0].url);
  assert.equal(destination.origin, "http://localhost:8501");
  assert.equal(destination.searchParams.has("repo"), false);
});

test("an unsafe configured URL falls back to local DevMind", async () => {
  const tabs = await simulateClick({ tabUrl: "https://example.com", appUrl: "javascript:alert(1)" });
  assert.equal(new URL(tabs[0].url).origin, "http://localhost:8501");
});
