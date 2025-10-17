#!/usr/bin/env python3
"""
Simple Git Auto Commit - One file only
git status > git add > git commit > git push
"""

import os
import subprocess
import datetime

# Configuration
REPO_PATH = "/home/frappe/frappe-bench-15/apps/posawesome"

def run_git(command):
    """Run git command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_first_changed_file():
    """Get first changed file from git status"""
    success, status, error = run_git("git status --porcelain")
    if not success or not status.strip():
        return None
    
    # First line = first file
    first_line = status.split('\n')[0].strip()
    if first_line:
        filename = first_line[2:].strip()  # Remove status codes (XY format)
        return filename
    return None

def commit_one_file():
    """Commit one file only"""
    os.chdir(REPO_PATH)
    
    # git status
    filename = get_first_changed_file()
    if not filename:
        return False
    
    # git add
    success, output, error = run_git(f'git add "{filename}"')
    if not success:
        return False
    
    # git commit
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit: {filename} at {timestamp}"
    success, output, error = run_git(f'git commit -m "{commit_msg}"')
    if not success:
        return False
    
    # git push
    success, output, error = run_git("git push origin main")
    return success

def main():
    """One file only"""
    commit_one_file()

if __name__ == "__main__":
    main()