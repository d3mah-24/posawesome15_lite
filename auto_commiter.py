#!/usr/bin/env python3
"""
Smart Git Commit Script
Automatically detects changed files and commits them one by one with intelligent commit messages

This replaces the old commit_files.sh script with a more intelligent and flexible approach:
- Auto-detects all changed files (staged, unstaged, untracked)
- Interactive mode for selective commits
- Smart commit messages based on file type and path
- No manual maintenance required
- Cron-friendly with silent mode
"""

import os
import subprocess
import sys
import datetime
from pathlib import Path

# Configuration for cron mode
REPO_PATH = "/home/frappe/frappe-bench-15/apps/posawesome"
LOG_FILE = "/home/frappe/frappe-bench-15/apps/posawesome/auto_commiter.log"

def log_message(message, silent_mode=False):
    """Log message with timestamp for cron mode"""
    if silent_mode:
        # Write to log file for cron
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass  # Ignore log errors in cron mode
    else:
        # Print for interactive mode
        print(message)

def run_git_command(command):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=REPO_PATH)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_changed_files(silent_mode=False):
    """Get list of changed files from git"""
    log_message("🔍 Detecting changed files...", silent_mode)
    
    # Get staged files
    success, staged_files, error = run_git_command("git diff --cached --name-only")
    staged = staged_files.split('\n') if staged_files else []
    
    # Get unstaged files  
    success, unstaged_files, error = run_git_command("git diff --name-only")
    unstaged = unstaged_files.split('\n') if unstaged_files else []
    
    # Get untracked files
    success, untracked_files, error = run_git_command("git ls-files --others --exclude-standard")
    untracked = untracked_files.split('\n') if untracked_files else []
    
    # Combine all changed files (remove empty strings)
    all_files = list(filter(None, staged + unstaged + untracked))
    
    log_message(f"📊 Found {len(all_files)} changed files:", silent_mode)
    for i, file in enumerate(all_files, 1):
        status = "📝" if file in staged else "🔄" if file in unstaged else "🆕"
        log_message(f"  {i:2d}. {status} {file}", silent_mode)
    
    return all_files

def generate_commit_message(filepath):
    """Generate intelligent commit message based on file path and content"""
    file_path = Path(filepath)
    filename = file_path.stem
    
    # Frontend improvement policies
    if "frontend" in filepath and "policy" in filepath:
        return "📋 Add frontend improvement policy with batch queue system"
    
    # Backend improvement policies  
    if "backend" in filepath and ("improvement" in filepath or "policy" in filepath):
        return "🏗️ Add backend improvement policy with ORM optimization"
    
    # Legacy API backups
    if "_old_backup" in filepath and filepath.endswith(".py"):
        return f"📦 Backup legacy customer API: {filename}"
    
    # Modern customer APIs
    if "/customer/" in filepath and filepath.endswith(".py"):
        if filename.startswith("get_"):
            return f"🔍 Implement customer retrieval API: {filename}"
        elif filename.startswith("post_"):
            return f"✨ Implement customer creation API: {filename}" 
        elif filename.startswith("update_"):
            return f"🔄 Implement customer update API: {filename}"
        elif filename.startswith("delete_"):
            return f"🗑️ Implement customer deletion API: {filename}"
        else:
            return f"✨ Implement modern customer API: {filename}"
    
    # Sales invoice APIs
    if "/sales_invoice/" in filepath and filepath.endswith(".py"):
        return f"💰 Implement sales invoice utility: {filename}"
    
    # Item APIs
    if "/item/" in filepath and filepath.endswith(".py"):
        return f"📦 Implement item API: {filename}"
    
    # Payment APIs
    if "/payment/" in filepath and filepath.endswith(".py"):
        return f"💳 Implement payment API: {filename}"
    
    # Configuration files
    if filename in ["__init__", "hooks"]:
        return f"⚙️ Update module configuration: {filename}"
    
    # Documentation files
    if filepath.endswith(".md"):
        if "analysis" in filepath:
            return f"📊 Add technical analysis: {filename}"
        elif "README" in filepath:
            return f"📚 Update documentation: {filename}"
        else:
            return f"📄 Add documentation: {filename}"
    
    # JavaScript/Vue files
    if filepath.endswith((".js", ".vue", ".ts")):
        return f"🎨 Update frontend component: {filename}"
    
    # CSS files
    if filepath.endswith((".css", ".scss", ".sass")):
        return f"💄 Update styles: {filename}"
    
    # Python files (general)
    if filepath.endswith(".py"):
        return f"🐍 Update Python module: {filename}"
    
    # JSON configuration files
    if filepath.endswith(".json"):
        return f"⚙️ Update configuration: {filename}"
    
    # Default message
    return f"📄 Update file: {filename}"

def commit_file(filepath, silent_mode=False):
    """Add and commit a single file"""
    log_message(f"\n📝 Processing: {filepath}", silent_mode)
    
    # Check if file exists
    if not os.path.exists(os.path.join(REPO_PATH, filepath)):
        log_message(f"⚠️  File not found: {filepath}", silent_mode)
        return False
    
    # Generate commit message
    commit_msg = generate_commit_message(filepath)
    log_message(f"💬 Commit message: {commit_msg}", silent_mode)
    
    # Add file to staging
    success, output, error = run_git_command(f'git add "{filepath}"')
    if not success:
        log_message(f"❌ Failed to stage file: {error}", silent_mode)
        return False
    
    log_message("✅ File staged successfully", silent_mode)
    
    # Commit the file
    success, output, error = run_git_command(f'git commit -m "{commit_msg}"')
    if not success:
        if "nothing to commit" in error:
            log_message("ℹ️  No changes to commit", silent_mode)
            return True
        else:
            log_message(f"❌ Failed to commit: {error}", silent_mode)
            return False
    
    log_message("✅ File committed successfully", silent_mode)
    return True

def interactive_commit():
    """Interactive mode - ask user for each file"""
    changed_files = get_changed_files()
    
    if not changed_files:
        print("✨ No changed files detected!")
        return
    
    print(f"\n🚀 Ready to commit {len(changed_files)} files")
    print("Choose an option:")
    print("  1. Commit all files automatically")
    print("  2. Review and commit each file interactively") 
    print("  3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return
    
    if choice == "1":
        # Commit all files automatically
        print("\n🤖 Committing all files automatically...")
        committed = 0
        for filepath in changed_files:
            if commit_file(filepath):
                committed += 1
        print(f"\n🎉 Successfully committed {committed}/{len(changed_files)} files!")
        
    elif choice == "2":
        # Interactive mode
        print("\n🎯 Interactive commit mode")
        committed = 0
        for i, filepath in enumerate(changed_files, 1):
            print(f"\n--- File {i}/{len(changed_files)} ---")
            print(f"📁 {filepath}")
            
            # Generate and show commit message
            commit_msg = generate_commit_message(filepath)
            print(f"💬 Suggested message: {commit_msg}")
            
            try:
                action = input("Action? (y)es / (n)o / (e)dit message / (q)uit: ").lower().strip()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
                
            if action in ['q', 'quit']:
                break
            elif action in ['n', 'no']:
                print("⏭️  Skipped")
                continue
            elif action in ['e', 'edit']:
                try:
                    custom_msg = input("Enter custom commit message: ").strip()
                    if custom_msg:
                        # Commit with custom message
                        success, output, error = run_git_command(f'git add "{filepath}"')
                        if success:
                            success, output, error = run_git_command(f'git commit -m "{custom_msg}"')
                            if success:
                                print("✅ Committed with custom message")
                                committed += 1
                            else:
                                print(f"❌ Failed to commit: {error}")
                        else:
                            print(f"❌ Failed to stage: {error}")
                    else:
                        print("⏭️  Skipped (empty message)")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
            else:
                # Default: commit with suggested message
                if commit_file(filepath):
                    committed += 1
        
        print(f"\n🎉 Successfully committed {committed} files!")
        
    else:
        print("👋 Goodbye!")

def auto_commit_all(silent_mode=False):
    """Automatically commit all changed files and push"""
    changed_files = get_changed_files(silent_mode)
    
    if not changed_files:
        log_message("✨ No changed files detected!", silent_mode)
        return False
    
    log_message(f"\n🤖 Auto-committing {len(changed_files)} files...", silent_mode)
    committed = 0
    
    for filepath in changed_files:
        if commit_file(filepath, silent_mode):
            committed += 1
    
    log_message(f"\n🎉 Successfully committed {committed}/{len(changed_files)} files!", silent_mode)
    
    if committed > 0:
        # Auto push to remote
        log_message("\n🚀 Pushing to remote repository...", silent_mode)
        success, output, error = run_git_command("git push origin main")
        if success:
            log_message("✅ Successfully pushed to remote!", silent_mode)
            return True
        else:
            log_message(f"❌ Failed to push: {error}", silent_mode)
            return False
    
    return committed > 0

def main():
    """Main function"""
    # Check for silent mode (for cron)
    silent_mode = "--silent" in sys.argv or "--cron" in sys.argv
    
    if not silent_mode:
        print("🚀 Smart Git Auto-Commit & Push Tool")
        print("=" * 45)
    
    # Change to repository directory
    os.chdir(REPO_PATH)
    
    # Check if we're in a git repository
    success, output, error = run_git_command("git status")
    if not success:
        log_message("❌ Not a git repository or git not found!", silent_mode)
        sys.exit(1)
    
    # Auto commit and push all changes
    success = auto_commit_all(silent_mode)
    
    # Show final status
    if not silent_mode:
        print("\n📈 Current status:")
        success, output, error = run_git_command("git log --oneline -5")
        if success and output:
            print("Recent commits:")
            for line in output.split('\n'):
                print(f"  🔹 {line}")
        
        if success:
            print("\n✅ All changes committed and pushed successfully!")
        else:
            print("\n⚠️  No changes were committed or push failed")
    else:
        # Log final status for cron
        log_message("=== Auto-commit cron job completed ===", silent_mode)

if __name__ == "__main__":
    main()