# DevMind browser extension

This Manifest V3 extension opens the DevMind web UI when its toolbar icon is clicked. On a `github.com/owner/repository` page, it passes the repository URL to DevMind so the public-repository field is prefilled. The extension reads only the active tab URL after the user clicks it.

## Local setup

1. Install the Python extras and start DevMind with `streamlit run streamlit_app.py` from the project directory. The default URL is `http://localhost:8501`.
2. In Brave or Chrome, open the extensions page, enable developer mode, and choose **Load unpacked**.
3. Select this `browser-extension` directory.
4. Pin the extension. Open its options if your DevMind page uses a different URL.
5. Click the extension. On a GitHub repository page, DevMind opens with that repository URL filled in.

Only HTTPS app URLs and HTTP loopback URLs are accepted. The extension does not authenticate to GitHub, read repository files, or write to GitHub. Private repositories are not supported. The web UI downloads public repository snapshots locally and runs analysis through DevMind's existing local pipeline.

This is a local unpacked extension prototype. A hosted DevMind service, Chrome Web Store listing, and Brave Web Store listing require separate deployment and release work.
