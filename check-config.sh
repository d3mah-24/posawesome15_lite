#!/bin/bash

# Git Configuration Script
source .git-protection

git config user.name "$USER" 2>&1
git config user.email "$EMAIL" 2>&1
git branch -M "$BRANCH" 2>&1
git remote set-url origin "$REPO" 2>&1 || git remote add origin "$REPO" 2>&1
git remote set-url upstream "$REPO" 2>&1 || git remote add upstream "$REPO" 2>&1
git config branch.main.remote origin 2>&1
git config branch.main.merge refs/heads/main 2>&1

echo "✅ $USER | $BRANCH | posawesome15_lite"
