#!/usr/bin/env python3
import subprocess

# Emojis by extension
EMOJI = {'.js': '🔄', '.vue': '💄', '.py': '🐍', '.md': '📝', '.json': '📋', '.css': '🎨', '.html': '🌐'}

# Get changed files (skip untracked files)
files = [f.split()[1] for f in subprocess.getoutput("git status --porcelain").strip().split('\n') if f and f.split()[0] in ['M', 'A', '??'] and 'auto_commit.py' not in f]

if not files:
    print("✅ No changes")
    exit()

# Commit each file
for f in files:
    ext = f[f.rfind('.'):] if '.' in f else ''
    emoji = EMOJI.get(ext, '📄')
    subprocess.run(f"git add {f}", shell=True)
    subprocess.run(f'git commit -m "{emoji} {f}"', shell=True)

# Check if no more changes, then push
if not subprocess.getoutput("git status --porcelain"):
    subprocess.run("git push origin main", shell=True)
    print("✅ Done")
