const DEFAULT_APP_URL = "http://localhost:8501";
const input = document.querySelector("#app-url");
const status = document.querySelector("#status");

function isAllowedAppUrl(value) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:") return true;
    if (url.protocol === "http:") {
      const h = url.hostname;
      if (["localhost", "127.0.0.1", "[::1]"].includes(h)) return true;
      if (/^192\.168\.\d{1,3}\.\d{1,3}$/.test(h)) return true;
      if (/^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(h)) return true;
      if (/^172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}$/.test(h)) return true;
    }
    return false;
  } catch {
    return false;
  }
}

chrome.storage.sync.get({ appUrl: DEFAULT_APP_URL }).then(({ appUrl }) => {
  input.value = isAllowedAppUrl(appUrl) ? appUrl : DEFAULT_APP_URL;
});

document.querySelector("#settings-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!isAllowedAppUrl(input.value.trim())) {
    status.textContent = "Use an HTTPS URL, or HTTP on localhost for local development.";
    return;
  }
  chrome.storage.sync.set({ appUrl: input.value.trim() }).then(() => {
    status.textContent = "Settings saved.";
  });
});
