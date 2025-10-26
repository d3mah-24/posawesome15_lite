#!/usr/bin/env python3
import subprocess

# Emojis by extension
EMOJI = {'.js': '🔄', '.vue': '💄', '.py': '🐍', '.md': '📝', '.json': '📋', '.css': '🎨', '.html': '🌐'}

# Get changed files
files = subprocess.getoutput("git status --short").strip().split('\n')
files = [f.split()[1] for f in files if f.strip()]

if not files:
    print("✅ No changes")
    exit()

# Commit each file
for f in files:
    ext = f[f.rfind('.'):] if '.' in f else ''
    emoji = EMOJI.get(ext, '📄')
    filename = f.split('/')[-1]  # Get only filename without path
    subprocess.run(f"git add {f}", shell=True)
    subprocess.run(f'git commit -m "{emoji} {filename}"', shell=True)

# Check if no more changes, then push
if not subprocess.getoutput("git status --porcelain"):
    subprocess.run("git push origin main", shell=True)
    print("✅ Done")
