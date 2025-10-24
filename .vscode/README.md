# VSCode Workspace Configuration

## Static Extensions List

This workspace has a **locked** set of VSCode extensions. No additional extensions should be installed.

### Required Extensions

1. **dbaeumer.vscode-eslint** - ESLint for JavaScript/Vue
2. **github.copilot** - GitHub Copilot AI assistant
3. **github.copilot-chat** - GitHub Copilot Chat
4. **ms-python.python** - Python language support
5. **natqe.reload** - Reload VSCode window
6. **vue.volar** - Vue 3 language support

### Installation

When connecting via SSH, VSCode will automatically prompt to install the recommended extensions.

If you need to manually install all extensions:

```bash
code --install-extension dbaeumer.vscode-eslint
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension ms-python.python
code --install-extension natqe.reload
code --install-extension vue.volar
```

### Configuration Policy

- ⚠️ **DO NOT** install additional extensions
- ⚠️ **DO NOT** modify `.vscode/extensions.json`
- ⚠️ **DO NOT** modify workspace settings in `.vscode/settings.json`
- ✅ Extension auto-updates are **disabled**
- ✅ Extension recommendations from other sources are **ignored**

### Settings Overview

- **Auto-format on save**: Enabled
- **Tab size**: 2 spaces
- **EOL**: LF (Unix)
- **Trim trailing whitespace**: Enabled
- **Insert final newline**: Enabled

### Troubleshooting

If extensions are not loading:

1. Reload VSCode: `Ctrl+Shift+P` → "Reload Window"
2. Check SSH connection: Extensions must be installed on the SSH host
3. Verify extensions: `code --list-extensions`
4. Run checker script: `.vscode/check-extensions.sh`

### Checking Extensions

To verify only approved extensions are installed:

```bash
.vscode/check-extensions.sh
```

This script will:
- ✅ Check all required extensions are installed
- ⚠️ Detect any unauthorized extensions
- 💡 Provide commands to remove unauthorized extensions

### Maintenance

These files are version-controlled and should not be modified:

- `.vscode/extensions.json` - Required extensions list
- `.vscode/settings.json` - Workspace settings
- `.vscode/README.md` - This documentation
