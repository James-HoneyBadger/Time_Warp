# 🔗 VS Code GitHub Integration Guide

## Automatic GitHub Integration Setup

### 1. Install Required VS Code Extensions
```bash
# Open VS Code and install these extensions:
# - GitHub Pull Requests and Issues
# - GitLens — Git supercharged
# - GitHub Copilot (optional)
# - Python extension pack
```

### 2. Configure Git in VS Code
1. Open VS Code in the Time_Warp project folder
2. Press `Ctrl+Shift+P` and type "Git: Clone"
3. Or open the integrated terminal (`Ctrl+``) and run:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. VS Code Settings for Auto-Sync
The `.vscode/settings.json` is configured for:
- ✅ Auto-fetch from GitHub
- ✅ Smart commits
- ✅ Auto-sync without confirmation
- ✅ Python path configuration
- ✅ File associations for Time_Warp languages

### 4. GitHub Actions Integration
- ✅ Automatic testing on push/PR
- ✅ Code quality checks
- ✅ Multi-Python version testing
- ✅ Linting and formatting

## Daily Workflow with Auto-Sync

### Making Changes:
1. Edit files in VS Code
2. VS Code will show changes in Source Control panel
3. Stage changes with `+` button or `Ctrl+Enter`
4. Commit with message
5. VS Code will auto-push to GitHub (configured in settings)

### Pulling Changes:
- VS Code auto-fetches every few minutes
- Click "Sync Changes" button when available
- Or use `Ctrl+Shift+P` → "Git: Sync"

### Branch Management:
- Create branches: Click branch name in status bar
- Switch branches: Status bar or Command Palette
- Merge via GitHub Pull Requests extension

## VS Code Workspace Features

### Custom File Types:

- `.pilot` files → Custom PILOT language
- `.bas` files → BASIC language
- `.logo` files → Logo/Lisp syntax


### Debug Configuration:
- F5 to launch Time_Warp IDE with debugger
- Configured for Python debugging with breakpoints
- Integrated terminal for testing

### Task Runner:
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Run tests, start Time_Warp, install dependencies

## GitHub Repository Auto-Maintenance

### Enabled Features:
1. **Dependabot** - Auto dependency updates
2. **GitHub Actions** - CI/CD pipeline
3. **Branch Protection** - Require PR reviews
4. **Issue Templates** - Structured bug reports
5. **Auto-merge** - For approved PRs

### Repository Settings to Enable:
1. Go to your GitHub repo → Settings
2. Enable "Auto-merge pull requests"
3. Set up branch protection rules for `main`
4. Enable Dependabot alerts
5. Configure GitHub Actions permissions

## Troubleshooting

### If Auto-Sync Doesn't Work:
1. Check VS Code Git settings
2. Verify GitHub authentication
3. Use Command Palette → "GitHub: Sign In"

### For Merge Conflicts:
1. VS Code will show conflict markers
2. Use built-in merge editor
3. Or use GitLens for visual merging

### Performance Issues:
1. Exclude large files in .gitignore
2. Use Git LFS for binary assets
3. Regular cleanup: `git gc --aggressive`