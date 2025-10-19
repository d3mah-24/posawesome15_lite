#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Auto Commit Script
Automates: git status, git add ., git commit, git push
"""

import subprocess
import sys
import os
from datetime import datetime


def run_command(command, cwd=None, capture_output=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def get_changed_files(repo_path):
    """Get list of changed files"""
    code, stdout, stderr = run_command("git status --short", cwd=repo_path)
    if code != 0:
        return []
    
    files = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            # Extract filename from git status output
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                files.append(parts[1])
    return files


def git_auto_commit(repo_path=None, commit_message=None, branch="main"):
    """
    Automate git operations
    
    Args:
        repo_path: Path to git repository (default: current directory)
        commit_message: Custom commit message (default: auto-generated from files)
        branch: Git branch to push to (default: main)
    """
    
    # Set repository path
    if repo_path is None:
        repo_path = os.getcwd()
    
    print("=" * 60)
    print("🚀 Git Auto Commit Script")
    print("=" * 60)
    print(f"📁 Repository: {repo_path}")
    print(f"🌿 Branch: {branch}")
    print()
    
    # Step 1: Git Status
    print("📊 Step 1: Checking git status...")
    code, stdout, stderr = run_command("git status", cwd=repo_path, capture_output=True)
    
    if code != 0:
        print(f"❌ Error: {stderr}")
        return False
    
    print(stdout)
    
    # Check if there are changes
    if "nothing to commit" in stdout:
        print("✅ No changes to commit!")
        return True
    
    # Get changed files
    changed_files = get_changed_files(repo_path)
    print(f"📝 Changed files: {len(changed_files)}")
    for f in changed_files[:10]:  # Show first 10
        print(f"   - {f}")
    if len(changed_files) > 10:
        print(f"   ... and {len(changed_files) - 10} more files")
    print()
    
    # Step 2: Git Add
    print("➕ Step 2: Adding files (git add .)...")
    code, stdout, stderr = run_command("git add .", cwd=repo_path)
    
    if code != 0:
        print(f"❌ Error adding files: {stderr}")
        return False
    
    print("✅ Files added successfully!")
    print()
    
    # Step 3: Generate commit message
    if commit_message is None:
        # Auto-generate commit message based on changed files
        if len(changed_files) == 1:
            commit_message = f"Update {changed_files[0]}"
        elif len(changed_files) <= 5:
            commit_message = f"Update {', '.join(changed_files)}"
        else:
            # Get file extensions
            extensions = set()
            for f in changed_files:
                ext = os.path.splitext(f)[1]
                if ext:
                    extensions.add(ext)
            
            if extensions:
                commit_message = f"Update {len(changed_files)} files ({', '.join(sorted(extensions))})"
            else:
                commit_message = f"Update {len(changed_files)} files"
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_message = f"{commit_message} - {timestamp}"
    
    print(f"💬 Commit message: {commit_message}")
    print()
    
    # Step 4: Git Commit
    print("💾 Step 3: Committing changes...")
    code, stdout, stderr = run_command(
        f'git commit -m "{commit_message}"',
        cwd=repo_path
    )
    
    if code != 0:
        print(f"❌ Error committing: {stderr}")
        return False
    
    print("✅ Commit successful!")
    print(stdout)
    print()
    
    # Step 5: Git Push
    print(f"🚀 Step 4: Pushing to origin {branch}...")
    code, stdout, stderr = run_command(
        f"git push origin {branch}",
        cwd=repo_path
    )
    
    if code != 0:
        print(f"❌ Error pushing: {stderr}")
        # Check if it's authentication issue
        if "authentication" in stderr.lower() or "permission" in stderr.lower():
            print("\n💡 Tip: Make sure your Git credentials are configured:")
            print("   git config --global user.name 'Your Name'")
            print("   git config --global user.email 'your@email.com'")
        return False
    
    print("✅ Push successful!")
    print(stdout)
    print()
    
    print("=" * 60)
    print("✅ All operations completed successfully!")
    print("=" * 60)
    
    return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Automate git add, commit, and push operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-commit with auto-generated message
  python git_auto_commit.py
  
  # Custom commit message
  python git_auto_commit.py -m "Fix: Update API mapper"
  
  # Specify repository path
  python git_auto_commit.py -p /path/to/repo
  
  # Different branch
  python git_auto_commit.py -b development
        """
    )
    
    parser.add_argument(
        '-p', '--path',
        help='Path to git repository (default: current directory)',
        default=None
    )
    
    parser.add_argument(
        '-m', '--message',
        help='Commit message (default: auto-generated from files)',
        default=None
    )
    
    parser.add_argument(
        '-b', '--branch',
        help='Git branch to push to (default: main)',
        default='main'
    )
    
    args = parser.parse_args()
    
    # Run git operations
    success = git_auto_commit(
        repo_path=args.path,
        commit_message=args.message,
        branch=args.branch
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
