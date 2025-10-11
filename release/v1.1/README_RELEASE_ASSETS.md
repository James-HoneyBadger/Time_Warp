# Release Assets - Important Note

## 📦 **Release Archive Management**

### ⚠️ **GitHub File Size Limitation**

The release archive `Time_Warp-IDE-v1.1.tar.gz` is **not included in git** because it exceeds GitHub's 100MB file size limit (actual size: ~229MB).

### 🎯 **For GitHub Releases:**

1. **Generate the archive locally:**
   ```bash
   ./scripts/prepare_release.sh
   ```

2. **Upload manually to GitHub Release:**
   - Go to GitHub Releases page
   - Edit or create the v1.1 release
   - Upload the `Time_Warp-IDE-v1.1.tar.gz` file directly as a release asset
   - Include other release files: `VERSION_INFO.txt`, `install.sh`, `SHA256SUMS.txt`

### 📋 **What's Included in Git:**

- ✅ `VERSION_INFO.txt` - Release information and verification results
- ✅ `install.sh` - Installation script
- ✅ `SHA256SUMS.txt` - File checksums (updated after archive creation)
- ❌ `Time_Warp-IDE-v1.1.tar.gz` - Too large for git (upload to GitHub manually)

### 🔧 **Archive Contents:**

The release archive contains the complete Time_Warp IDE including:
- Core framework and all language executors
- GUI components and theme system
- Games engine and plugin architecture
- Complete documentation and examples
- Test suites and build scripts

**Size**: ~229MB (includes all dependencies and frameworks)

### 💡 **Alternative Distribution:**

For automated distribution, consider:
- GitHub Releases (manual upload)
- Package managers (PyPI, etc.)
- Container images
- Git LFS for large files

---
*Note: This approach keeps the git repository clean while still providing complete release assets for users.*