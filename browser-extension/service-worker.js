const DEFAULT_APP_URL = "http://localhost:8501";

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

function repositoryFromTab(tabUrl) {
  try {
    const url = new URL(tabUrl);
    if (url.protocol !== "https:" || url.hostname !== "github.com") return null;
    const [owner, rawRepository] = url.pathname.split("/").filter(Boolean);
    if (!owner || !rawRepository) return null;
    const repository = rawRepository.replace(/\.git$/i, "");
    if (!/^[A-Za-z0-9_.-]{1,100}$/.test(owner) || !/^[A-Za-z0-9_.-]{1,100}$/.test(repository)) return null;
    return `https://github.com/${owner}/${repository}`;
  } catch {
    return null;
  }
}

chrome.action.onClicked.addListener((tab) => {
  chrome.storage.sync.get({ appUrl: DEFAULT_APP_URL }, ({ appUrl }) => {
    const destination = isAllowedAppUrl(appUrl) ? new URL(appUrl) : new URL(DEFAULT_APP_URL);
    const repository = repositoryFromTab(tab.url || "");
    if (repository) destination.searchParams.set("repo", repository);
    chrome.tabs.create({ url: destination.toString() });
  });
});
