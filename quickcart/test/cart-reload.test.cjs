const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const test = require("node:test");

const targetFile = fs.existsSync(path.join(__dirname, "..", "index3.html")) ? "index3.html" : "index.html";
const html = fs.readFileSync(path.join(__dirname, "..", targetFile), "utf8");
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script\s*>/gi)];
const cartScriptMatch = scripts.find(m => m[1].includes("loadCartFromStorage"));
const inlineScript = cartScriptMatch ? cartScriptMatch[1] : (scripts[0]?.[1] ?? "");
assert.ok(inlineScript, "demo page must contain its inline cart script");

function loadPage(storage) {
  const listeners = {};
  const dummyEl = { textContent: "", innerHTML: "", style: {}, offsetWidth: 100, classList: { add() {}, remove() {} }, addEventListener: () => {} };
  const cartCount = { textContent: "0", classList: { add() {}, remove() {} }, addEventListener: () => {} };
  const context = {
    localStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, String(value)),
      removeItem: (key) => storage.delete(key),
    },
    window: {
      addEventListener: (name, callback) => {
        listeners[name] = listeners[name] || [];
        listeners[name].push(callback);
      },
    },
    document: {
      getElementById: (id) => id === "cartCount" ? cartCount : dummyEl,
      querySelector: () => dummyEl,
      querySelectorAll: () => [dummyEl],
      addEventListener: (name, cb) => {},
    },
    getComputedStyle: () => ({ gap: "32px" }),
    setTimeout: (fn) => fn(),
    setInterval: () => {},
    clearInterval: () => {},
    IntersectionObserver: class { observe() {} unobserve() {} disconnect() {} },
    JSON,
    String,
    Date,
  };
  vm.runInNewContext(inlineScript, context, { filename: targetFile + "#inline-script" });
  (listeners.load || []).forEach((fn) => fn());
  return { context, cartCount };
}

test("cart contents and badge survive a page reload", () => {
  const storage = new Map();
  storage.set("quickCartItems", JSON.stringify([{ id: 101, name: "Fossil Chronograph Watch", price: 4999, quantity: 1 }]));
  const reloadedPage = loadPage(storage);
  assert.equal(String(reloadedPage.cartCount.textContent), "1");
});
