#!/bin/bash
# Repository Configuration Checker

echo "🔍 Checking Repository Configuration..."
echo "========================================"

# Check current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Current Branch: $current_branch"

# Check remotes
echo ""
echo "🌐 Remote Configuration:"
git remote -v

# Check if both origin and upstream point to correct URL
origin_url=$(git remote get-url origin)
upstream_url=$(git remote get-url upstream)
expected_url="https://github.com/abdopcnet/posawesome15_lite.git"

echo ""
echo "✅ Configuration Status:"
if [ "$origin_url" = "$expected_url" ]; then
    echo "   ✅ Origin: CORRECT"
else
    echo "   ❌ Origin: INCORRECT ($origin_url)"
fi

if [ "$upstream_url" = "$expected_url" ]; then
    echo "   ✅ Upstream: CORRECT"
else
    echo "   ❌ Upstream: INCORRECT ($upstream_url)"
fi

if [ "$current_branch" = "main" ]; then
    echo "   ✅ Branch: CORRECT (main)"
else
    echo "   ⚠️  Branch: $current_branch (not main)"
fi

echo ""
echo "🛡️  Repository Protection: ACTIVE"
echo "📋 To maintain this configuration:"
echo "   1. Always pull from upstream before changes"
echo "   2. Never change remote URLs"
echo "   3. Keep main branch as primary"
