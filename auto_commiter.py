#!/usr/bin/env python3
"""
Simple Auto Git Commit & Push
Just commits all changes and pushes with basic logging
"""

import os
import subprocess
import datetime

# Configuration
REPO_PATH = "/home/frappe/frappe-bench-15/apps/posawesome"
LOG_FILE = "/home/frappe/frappe-bench-15/apps/posawesome/auto_commiter.log"

def log(message):
    """Log message with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_git(command):
    """Run git command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def commit_and_push():
    """Simple: add all, commit, push, log"""
    os.chdir(REPO_PATH)
    
    # Check if there are any changes
    success, status, error = run_git("git status --porcelain")
    if not success or not status.strip():
        log("No changes to commit")
        return True
    
    # Get list of changed files for logging
    files = []
    for line in status.split('\n'):
        if line.strip():
            files.append(line[3:].strip())
    
    log(f"Found {len(files)} changed files: {', '.join(files)}")
    
    # Add all changes
    success, output, error = run_git("git add .")
    if not success:
        log(f"Failed to add files: {error}")
        return False
    
    # Commit with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-commit: {len(files)} files at {timestamp}"
    
    success, output, error = run_git(f'git commit -m "{commit_msg}"')
    if not success:
        if "nothing to commit" in error:
            log("Nothing to commit")
            return True
        log(f"Failed to commit: {error}")
        return False
    
    # Get commit ID
    success, commit_id, error = run_git("git rev-parse --short HEAD")
    if success:
        log(f"Committed: {commit_id} - {len(files)} files")
    
    # Push
    success, output, error = run_git("git push origin main")
    if success:
        log(f"Pushed commit {commit_id} successfully")
        return True
    else:
        log(f"Failed to push: {error}")
        return False

def main():
    """Main function"""
    log("=== Auto-commit started ===")
    success = commit_and_push()
    if success:
        log("=== Auto-commit completed successfully ===")
    else:
        log("=== Auto-commit failed ===")

if __name__ == "__main__":
    main()