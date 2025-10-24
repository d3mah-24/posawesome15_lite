#!/bin/bash
# VSCode Extensions Enforcer
# This script ensures only approved extensions are installed

REQUIRED_EXTENSIONS=(
    "dbaeumer.vscode-eslint"
    "github.copilot"
    "github.copilot-chat"
    "ms-python.python"
    "natqe.reload"
    "vue.volar"
)

echo "🔍 Checking VSCode extensions..."

# Get list of installed extensions
INSTALLED=$(code --list-extensions 2>/dev/null | grep -v "^Extensions installed on SSH:")

if [ -z "$INSTALLED" ]; then
    echo "❌ Cannot get extensions list. Is VSCode installed?"
    exit 1
fi

# Check for required extensions
echo "✅ Required extensions:"
for ext in "${REQUIRED_EXTENSIONS[@]}"; do
    if echo "$INSTALLED" | grep -q "^$ext$"; then
        echo "  ✓ $ext"
    else
        echo "  ✗ $ext (MISSING)"
    fi
done

# Check for unauthorized extensions
echo ""
echo "🔍 Checking for unauthorized extensions..."
UNAUTHORIZED=()

while IFS= read -r ext; do
    is_required=false
    for req in "${REQUIRED_EXTENSIONS[@]}"; do
        if [ "$ext" == "$req" ]; then
            is_required=true
            break
        fi
    done

    if [ "$is_required" = false ]; then
        UNAUTHORIZED+=("$ext")
    fi
done <<< "$INSTALLED"

if [ ${#UNAUTHORIZED[@]} -eq 0 ]; then
    echo "✅ No unauthorized extensions found"
else
    echo "⚠️  Found ${#UNAUTHORIZED[@]} unauthorized extension(s):"
    for ext in "${UNAUTHORIZED[@]}"; do
        echo "  - $ext"
    done
    echo ""
    echo "💡 To remove unauthorized extensions, run:"
    for ext in "${UNAUTHORIZED[@]}"; do
        echo "   code --uninstall-extension $ext"
    done
fi

echo ""
echo "📊 Summary:"
echo "  Required: ${#REQUIRED_EXTENSIONS[@]}"
echo "  Installed: $(echo "$INSTALLED" | wc -l)"
echo "  Unauthorized: ${#UNAUTHORIZED[@]}"
