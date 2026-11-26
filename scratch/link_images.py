import re
import shutil
from pathlib import Path

root = Path("quickcart")
html_files = list(root.glob("*.html"))

print(f"Scanning {len(html_files)} HTML files in {root}...")

all_refs = set()
for hf in html_files:
    try:
        content = hf.read_text(encoding="utf-8")
        matches = re.findall(r'src=["\']([^"\']+)["\']', content)
        for m in matches:
            if "/" in m and not m.startswith("http") and not m.startswith("$") and not m.startswith("data:"):
                all_refs.add(m)
    except Exception as e:
        print(f"Error reading {hf}: {e}")

print(f"Found {len(all_refs)} unique local image references.")

copied = 0
missing = 0
for ref in sorted(all_refs):
    parts = ref.split("/")
    folder_name = parts[0]
    filename = parts[-1]
    
    target_dir = root / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = root / ref
    
    # Check if file already exists at target
    if target_file.is_file():
        continue
    
    # Check if filename exists at root
    source_file = root / filename
    if source_file.is_file():
        shutil.copy2(source_file, target_file)
        copied += 1
    else:
        # Check case-insensitive
        found = False
        for cand in root.glob("*"):
            if cand.is_file() and cand.name.lower() == filename.lower():
                shutil.copy2(cand, target_file)
                copied += 1
                found = True
                break
        if not found:
            missing += 1
            print(f"Missing source for: {ref}")

print(f"Done! Copied {copied} images into their referenced subfolders. Missing: {missing}")
