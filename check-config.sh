#!/bin/bash

# Git Configuration Script - Complete Logic
REPO=https://github.com/abdopcnet/posawesome15_lite.git
USER=abdopcnet
EMAIL=abdopcnet@gmail.com
BRANCH=main

# Check user first
CURRENT_USER=$(git config user.name)
if [ "$CURRENT_USER" != "$USER" ]; then
    echo "❌ Access Denied: Only $USER allowed"
    exit 1
fi

# Check branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "❌ Access Denied: Only $BRANCH branch allowed"
    exit 1
fi

# Setup git configuration
git config user.name "$USER" 2>&1
git config user.email "$EMAIL" 2>&1
git branch -M "$BRANCH" 2>&1
git remote set-url origin "$REPO" 2>&1 || git remote add origin "$REPO" 2>&1
git remote set-url upstream "$REPO" 2>&1 || git remote add upstream "$REPO" 2>&1
git config branch.main.remote origin 2>&1
git config branch.main.merge refs/heads/main 2>&1

# Update version automatically
VERSION=$(date +%-d.%-m.%Y)
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" posawesome/__init__.py
git add posawesome/__init__.py

echo "✅ $USER | $BRANCH | posawesome15_lite"
echo "📅 Version updated to: $VERSION"
