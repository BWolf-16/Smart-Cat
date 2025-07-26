# 🎯 KiCad Plugin Manager - Correct Setup Guide

KiCad Plugin Manager requires a specific URL format and repository structure. Here's the **correct way** to set it up:

## ✅ **Correct URLs for KiCad Plugin Manager**

### Method 1: Direct Metadata URL (Recommended)
```
https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/metadata.json
```

### Method 2: Repository-based URL
```
https://github.com/BWolf-16/Smart-Cat/raw/main/metadata.json
```

## 🔧 **Setup Steps**

### 1. In KiCad Plugin Manager:
1. Open **KiCad**
2. Go to **Tools** → **Plugin and Content Manager**  
3. Click **Settings** (gear icon)
4. Click **Add** to add a new repository
5. **Repository Name**: `Smart Cat AI`
6. **Repository URL**: Use one of the URLs above
7. Click **OK**

### 2. Alternative: Manual Repository Entry
If the automatic detection doesn't work:

1. **Repository Type**: `Package Repository`
2. **URL**: `https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/metadata.json`
3. **Name**: `Smart Cat AI Assistant`

## 🚨 **Important: Create GitHub Release First**

Before the URLs will work, you need to:

1. **Go to**: https://github.com/BWolf-16/Smart-Cat
2. **Create Release**: Tag `v1.0.0`
3. **Upload**: `smart_cat_plugin.zip` (the minimal package)
4. **Publish** the release

## 🎯 **Why the Original URL Failed**

❌ **Wrong**: `https://github.com/BWolf-16/Smart-Cat`
- KiCad can't auto-detect the metadata location
- Repository structure unclear

✅ **Correct**: `https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/metadata.json`
- Direct path to metadata file
- KiCad knows exactly where to look

## 📋 **Verify Your Setup**

After adding the repository, you should see:
- **Plugin Name**: Smart Cat AI Assistant
- **Version**: 1.0.0
- **Size**: ~45 KB
- **Install** button available

## 🔄 **Alternative Installation Methods**

If Plugin Manager still doesn't work:

### Quick Install via Script:
```powershell
curl -o setup.py https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/setup.py
python setup.py install-repo
```

### Manual Installation:
1. Download `smart_cat_plugin.zip` from releases
2. Extract to KiCad plugins directory
3. Restart KiCad

---

**Use the direct metadata URL for guaranteed success! 🐱👓✨**
