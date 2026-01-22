# 🚀 Quick Setup Guide for pytest in WSL/Linux

## 🆘 Installation Errors in WSL?

### TLS Certificate Error?

If you get: `Could not find a suitable TLS CA certificate bundle`

**Quick Fix (Copy & Paste):**

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates
cd /mnt/d/Code/CRM/horizon-sync-be
rm -rf venv_wsl
python3 -m venv venv_wsl
./venv_wsl/bin/pip install --upgrade pip --no-cache-dir
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir
./venv_wsl/bin/pytest --version
```

The key fixes:
- `sudo apt-get install ca-certificates` - Install system certificates
- `rm -rf venv_wsl` - Remove corrupted venv
- `--no-cache-dir` - Skip cache that might have bad certificates

### "externally-managed-environment" Error?

Use the full path to pip:

```bash
cd /mnt/d/Code/CRM/horizon-sync-be
rm -rf venv_wsl
python3 -m venv venv_wsl
./venv_wsl/bin/pip install --upgrade pip --no-cache-dir
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir
./venv_wsl/bin/pytest --version
```

---

## Issue
`zsh: command not found: pytest` or `externally-managed-environment` error

## Solution

Since you're using WSL/Linux with zsh, follow these steps:

### Step 1: Create a Virtual Environment

```bash
cd /mnt/d/Code/CRM/horizon-sync-be
python3 -m venv venv_wsl
```

### Step 2: Activate the Virtual Environment

```bash
source venv_wsl/bin/activate
```

You should see `(venv_wsl)` at the beginning of your terminal prompt.

**CRITICAL: You MUST see `(venv_wsl)` in your prompt before proceeding!**

Verify activation worked:
```bash
echo $VIRTUAL_ENV
# Should output the full path to venv_wsl
```

### Step 3: Install Dependencies

Use the venv's own pip with `--no-cache-dir` flag (fixes certificate issues in WSL):

```bash
./venv_wsl/bin/pip install --upgrade pip setuptools --no-cache-dir
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir
```

**If you still get certificate errors, install system certificates first:**

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates
```

Then try the install again:
```bash
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir
```

**Or if using source activate**, verify the prompt shows `(venv_wsl)`:
```bash
source venv_wsl/bin/activate
pip install --upgrade pip setuptools --no-cache-dir
pip install -r requirements.txt --no-cache-dir
```

**Alternative: Install just the testing packages:**

```bash
./venv_wsl/bin/pip install pytest pytest-asyncio pytest-cov httpx sqlalchemy --no-cache-dir
```

### Step 4: Verify Installation

```bash
pytest --version
```

You should see output like: `pytest 7.4.4`

## ✅ Now You Can Run Tests

### Run all tests:
```bash
pytest tests/ -v
```

### Run specific service:
```bash
pytest tests/services/test_auth_service.py -v
```

### Run specific test class:
```bash
pytest tests/services/test_auth_service.py::TestAuthLogin -v
```

### Run with coverage:
```bash
pytest tests/ --cov=services --cov-report=html
```

### Run in parallel (faster):
```bash
./venv_wsl/bin/pip install pytest-xdist
pytest tests/ -n auto -v
```

## ⚡ Super Quick Setup (One Command)

If you want to do everything in one shot (handles certificate issues):

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates && \
cd /mnt/d/Code/CRM/horizon-sync-be && \
rm -rf venv_wsl && \
python3 -m venv venv_wsl && \
./venv_wsl/bin/pip install --upgrade pip setuptools --no-cache-dir && \
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir && \
./venv_wsl/bin/pytest --version && \
echo "✅ Setup complete! Run: ./venv_wsl/bin/pytest tests/ -v"
```

This handles:
- ✅ System certificates (fixes TLS errors)
- ✅ Fresh clean venv
- ✅ Latest pip version
- ✅ All dependencies installed
- ✅ pytest verified

## 📌 Important: Activate Before Each Session

Every time you open a new terminal, you need to activate the virtual environment:

```bash
source /mnt/d/Code/CRM/horizon-sync-be/venv_wsl/bin/activate
```

Or add this to your `.zshrc` to make it permanent:

```bash
alias horizontest='source /mnt/d/Code/CRM/horizon-sync-be/venv_wsl/bin/activate && cd /mnt/d/Code/CRM/horizon-sync-be'
```

Then you can just type:
```bash
horizontest
```

## 🔗 Helpful Documentation

Once you have pytest working, read these docs:

- **Quick Start**: `tests/QUICK_REFERENCE.md` (5 min read)
- **Running Tests**: `tests/TEST_EXECUTION_GUIDE.md` (15 min read)
- **Complete Guide**: `tests/README.md` (20 min read)

## 🆘 Troubleshooting

### Getting TLS/Certificate errors?

**The virtual environment's pip lost its certificate bundle.** This is common in WSL.

**Complete Fix:**

```bash
# Step 1: Install system certificates (one-time in WSL)
sudo apt-get update && sudo apt-get install -y ca-certificates

# Step 2: Delete the corrupted venv
cd /mnt/d/Code/CRM/horizon-sync-be
rm -rf venv_wsl

# Step 3: Create fresh venv
python3 -m venv venv_wsl

# Step 4: Install with --no-cache-dir flag (important!)
./venv_wsl/bin/pip install --upgrade pip --no-cache-dir
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir

# Step 5: Verify
./venv_wsl/bin/pytest --version
```

**The key flags that fix the issue:**
- `sudo apt-get install ca-certificates` - Installs system root certificates
- `rm -rf venv_wsl` - Removes any cached bad certificates
- `--no-cache-dir` - Skips using pip's local cache

### Getting "externally-managed-environment" error?

**This means the virtual environment activation didn't work.** Use the full path to pip instead:

```bash
# Option 1: Use full path to pip (recommended, avoids the error)
cd /mnt/d/Code/CRM/horizon-sync-be
./venv_wsl/bin/pip install --upgrade pip --no-cache-dir
./venv_wsl/bin/pip install -r requirements.txt --no-cache-dir
./venv_wsl/bin/pytest --version
```

Or verify activation worked:
```bash
# Check if venv is activated
echo $VIRTUAL_ENV
# Should show: /mnt/d/Code/CRM/horizon-sync-be/venv_wsl
# If it's empty, run: source venv_wsl/bin/activate
```

### Still getting "command not found: pytest"?

Make sure your virtual environment is activated:
```bash
# Check if activated (should show venv_wsl in prompt)
echo $VIRTUAL_ENV

# If empty, activate it:
source /mnt/d/Code/CRM/horizon-sync-be/venv_wsl/bin/activate
```

Or just use the full path:
```bash
/mnt/d/Code/CRM/horizon-sync-be/venv_wsl/bin/pytest tests/ -v
```

### Getting permission errors?

Use the full path to pip:
```bash
/mnt/d/Code/CRM/horizon-sync-be/venv_wsl/bin/pip install pytest pytest-asyncio pytest-cov
```

## ✨ Success Check

Once everything is set up, run:

```bash
cd /mnt/d/Code/CRM/horizon-sync-be
source venv_wsl/bin/activate
pytest tests/services/test_auth_service.py -v --tb=short
```

You should see test output starting with:
```
tests/services/test_auth_service.py::TestAuthRegister::test_register_success PASSED
```

---

**Need Help?** Check `tests/README.md` or `tests/TEST_EXECUTION_GUIDE.md`
