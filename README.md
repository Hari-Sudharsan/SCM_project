# Real-Time Feature Management in E-commerce Application using SCM Tools

> **University Project** — Demonstrates Software Configuration Management (SCM) using
> Git, GO Feature Flag Relay Proxy, and a Python Flask e-commerce application.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Environment Setup](#3-environment-setup)
4. [Running the System](#4-running-the-system)
5. [Git Workflow](#5-git-workflow)
6. [Demo Scenarios](#6-demo-scenarios)
7. [SCM Concept Mapping](#7-scm-concept-mapping)
8. [Troubleshooting](#8-troubleshooting)
9. [Test Plan](#9-test-plan)
10. [Presentation Notes](#10-presentation-notes)

---

## 1. Project Overview

This project shows how **feature flags** stored in a **Git repository** can control
the live behaviour of an e-commerce web application **without restarting the server**.

### Architecture

```
flags/flags.yaml  (Git-tracked)
        │
        ▼
GO Feature Flag Relay Proxy  (polls file every 5 s)
        │  REST API  POST /ofrep/v1/evaluate/flags/{key}
        ▼
Flask Application  (evaluates flags per request)
        │
        ▼
Web UI  (Bootstrap — banners, COD option, checkout layout)
```

### Features Controlled by Flags

| Flag | Effect |
|---|---|
| `discount-banner-enabled` | Shows/hides "FLAT X% OFF" banner |
| `discount-percentage` | Sets the discount % (10 / 20 / 30) |
| `cash-on-delivery-enabled` | Adds/removes COD payment option |
| `promo-banner-enabled` | Shows/hides promotional strip |
| `promo-banner-text` | Text shown in promotional banner |
| `new-checkout-layout` | Switches checkout between classic and two-column |

---

## 2. Directory Structure

```
ecommerce-scm/
├── app.py                  # Flask application (backend)
├── requirements.txt        # Python dependencies
├── goff-proxy.yaml         # GO Feature Flag relay proxy config
├── .gitignore
├── README.md
│
├── flags/
│   └── flags.yaml          # ← SCM-tracked feature flag configuration
│
├── templates/
│   ├── layout.html         # Base template (navbar, banners)
│   ├── index.html          # Homepage (product listing)
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Checkout (COD + layout flags)
│   ├── order_success.html  # Order confirmation
│   ├── admin_flags.html    # Live flag dashboard
│   └── admin_orders.html   # Order audit log
│
└── instance/
    └── shop.db             # SQLite database (auto-created, git-ignored)
```

---

## 3. Environment Setup

### Prerequisites
- macOS 12+ (also works on Linux/Windows WSL)
- Python 3.9+
- Git
- Homebrew (macOS)

### Step 1 — Install Python & pip packages

```bash
# Verify Python
python3 --version    # Should be 3.9+

# Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Flask and requests
pip install -r requirements.txt
```

### Step 2 — Install GO Feature Flag Relay Proxy

The relay proxy is a single binary. Download it for macOS:

```bash
# Option A: Homebrew (easiest)
brew install go-feature-flag-relay-proxy

# Option B: Direct binary download (Apple Silicon / M1/M2/M3)
curl -L https://github.com/thomaspoignant/go-feature-flag/releases/download/v1.26.0/go-feature-flag-relay-proxy_1.26.0_Darwin_arm64.tar.gz \
  -o goff.tar.gz
tar -xzf goff.tar.gz
chmod +x go-feature-flag-relay-proxy
sudo mv go-feature-flag-relay-proxy /usr/local/bin/

# Option C: Direct binary download (Intel Mac)
curl -L https://github.com/thomaspoignant/go-feature-flag/releases/download/v1.26.0/go-feature-flag-relay-proxy_1.26.0_Darwin_x86_64.tar.gz \
  -o goff.tar.gz
tar -xzf goff.tar.gz
chmod +x go-feature-flag-relay-proxy
sudo mv go-feature-flag-relay-proxy /usr/local/bin/

# Verify installation
go-feature-flag-relay-proxy --version
```

### Step 3 — Git Setup

```bash
cd ecommerce-scm/
git init
git add .
git commit -m "feat: initial project setup — all flags disabled by default"
```

---

## 4. Running the System

You need **two terminal windows** running simultaneously.

### Terminal 1 — Start GO Feature Flag Relay Proxy

```bash
cd ecommerce-scm/
go-feature-flag-relay-proxy --config goff-proxy.yaml
```

You should see:
```
time=... level=INFO msg="GO Feature Flag relay proxy started" port=1031
```

The proxy will reload `flags/flags.yaml` automatically every 5 seconds.

### Terminal 2 — Start Flask Application

```bash
cd ecommerce-scm/
source venv/bin/activate    # if using venv
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Open the Application

Visit: **http://localhost:5000**

- **Homepage** → http://localhost:5000/
- **Cart** → http://localhost:5000/cart
- **Checkout** → http://localhost:5000/checkout
- **Flag Dashboard** → http://localhost:5000/admin/flags
- **Order Audit Log** → http://localhost:5000/admin/orders

---

## 5. Git Workflow

### Initial Commit

```bash
git log --oneline
# Shows: abc1234 feat: initial project setup — all flags disabled by default
```

### Scenario 1 — Enable Discount Banner

```bash
# Edit flags/flags.yaml — change discount-banner-enabled defaultRule:
#   variation: disabled  →  variation: enabled

nano flags/flags.yaml   # or use VS Code / any editor

# Stage and commit
git add flags/flags.yaml
git commit -m "feat: enable discount banner — 10% off flash sale"
```

The relay proxy detects the change within 5 seconds. Refresh the browser —
the discount banner appears instantly with no server restart.

### Scenario 2 — Enable COD + Increase Discount

```bash
# Edit flags.yaml:
#   cash-on-delivery-enabled defaultRule: variation: enabled
#   discount-percentage defaultRule: variation: twenty

git add flags/flags.yaml
git commit -m "feat: enable COD and increase discount to 20%"
```

### Scenario 3 — Enable New Checkout Layout

```bash
# Edit flags.yaml:
#   new-checkout-layout defaultRule: variation: new

git add flags/flags.yaml
git commit -m "feat: activate new two-column checkout layout for A/B test"
```

### Scenario 4 — Activate Promo Banner

```bash
# Edit flags.yaml:
#   promo-banner-enabled defaultRule: variation: enabled
#   promo-banner-text defaultRule: variation: sale

git add flags/flags.yaml
git commit -m "feat: launch grand sale promotional banner"
```

### Scenario 5 — Rollback (Disable Everything)

```bash
# Revert all flags to disabled

git add flags/flags.yaml
git commit -m "fix: rollback all flags — end flash sale"

# OR hard rollback to initial commit
git revert HEAD~3..HEAD   # revert last 3 commits
```

### View Full Change History

```bash
# All commits touching the flags file
git log --oneline --follow flags/flags.yaml

# See exactly what changed in each commit
git log -p flags/flags.yaml

# Compare two commits
git diff HEAD~1 HEAD -- flags/flags.yaml

# Who changed what and when (audit)
git log --format="%H %ai %an: %s" -- flags/flags.yaml
```

---

## 6. Demo Scenarios

### Scenario A — Flash Sale

**Goal:** Start a flash sale instantly and end it after the professor sees it.

```bash
# Start sale
sed -i '' 's/variation: disabled.*# Change to "enabled" to activate discount/variation: enabled/' flags/flags.yaml
# (or manually edit)

git add flags/flags.yaml
git commit -m "feat: start flash sale — 10% off"
```

**Expected behaviour:** Within 5 s, refresh http://localhost:5000 →
- Red/orange discount banner appears at top
- Products show strikethrough original price + "10% OFF" badge
- Cart shows discount line in order summary

```bash
# End sale
# (Edit flags.yaml: variation: disabled)
git add flags/flags.yaml
git commit -m "fix: end flash sale"
```

**Expected behaviour:** Banner disappears, prices return to normal.

---

### Scenario B — Enable Cash on Delivery

**Goal:** Add COD payment option to checkout.

1. Edit `flags/flags.yaml`: `cash-on-delivery-enabled` → `variation: enabled`
2. `git add flags/flags.yaml && git commit -m "feat: enable COD payment"`
3. Open http://localhost:5000/checkout
4. **Expected:** Cash on Delivery radio button appears with green "Available" badge

Revert:
1. Edit `flags.yaml`: `variation: disabled`
2. Commit
3. Refresh checkout → COD option gone

---

### Scenario C — New Checkout Layout A/B Test

1. Edit `flags.yaml`: `new-checkout-layout` → `variation: new`
2. Commit
3. Go to checkout → **Expected:** Two-column layout (shipping left, summary right)
4. Revert → single-column classic layout returns

---

### Scenario D — Promotional Campaign

1. Edit `flags.yaml`:
   - `promo-banner-enabled` → `variation: enabled`
   - `promo-banner-text` → `variation: festive`
2. Commit
3. **Expected:** Purple banner strip at top of every page showing festive message

---

## 7. SCM Concept Mapping

| SCM Concept | Implementation in this Project |
|---|---|
| **Version Control** | Every change to `flags.yaml` is a Git commit with full history |
| **Configuration Identification** | Each commit SHA uniquely identifies a configuration state |
| **Configuration Status Accounting** | `/admin/flags` page shows live current state; `git log` shows history |
| **Change Control** | Changes require explicit `git add + git commit` — no accidental changes |
| **Audit Trail** | `git log --format="%H %ai %an: %s" -- flags/flags.yaml` shows who changed what |
| **Controlled Rollout** | Change one flag at a time via commits; rollback with `git revert` |
| **Baseline Management** | Tag a known-good state: `git tag v1.0-stable` |
| **Configuration Verification** | Relay proxy validates YAML on load; Flask falls back to defaults on error |

---

## 8. Troubleshooting

### Problem: Relay proxy not starting
```
Error: cannot read config file
```
**Fix:** Make sure you run the proxy from the `ecommerce-scm/` directory:
```bash
cd ecommerce-scm/
go-feature-flag-relay-proxy --config goff-proxy.yaml
```

---

### Problem: Flags not updating after editing flags.yaml
**Cause:** Proxy may not have polled yet.
**Fix:** Wait up to 5 seconds (the `pollingInterval`). If still not updating:
```bash
# Verify proxy is running and file path is correct
cat goff-proxy.yaml     # check "path: flags/flags.yaml"
ls flags/flags.yaml     # verify file exists
```

---

### Problem: Flask app shows default values (all flags false/disabled)
**Cause:** Relay proxy is not running or not reachable.
**Fix:** Start the relay proxy in Terminal 1 first, then run Flask.
The app degrades gracefully — all flags fall back to `False`/default strings.

---

### Problem: `brew: command not found`
**Fix:** Install Homebrew first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

### Problem: `ModuleNotFoundError: No module named 'flask'`
**Fix:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: Port 5000 already in use
**Fix:**
```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9
python app.py
```

---

### Problem: Port 1031 already in use
**Fix:**
```bash
lsof -ti:1031 | xargs kill -9
go-feature-flag-relay-proxy --config goff-proxy.yaml
```

---

### Problem: `go-feature-flag-relay-proxy: command not found` after download
**Fix:**
```bash
# Make binary executable and move to PATH
chmod +x ./go-feature-flag-relay-proxy
sudo mv ./go-feature-flag-relay-proxy /usr/local/bin/
# Retry
go-feature-flag-relay-proxy --version
```

---

## 9. Test Plan

### Test 1 — Application Starts
- [ ] `python app.py` runs without errors
- [ ] http://localhost:5000 loads with product grid
- [ ] 6 products visible

### Test 2 — Default Flag State (all flags off)
- [ ] No discount banner visible
- [ ] No promo banner visible
- [ ] Add item to cart → go to checkout → no COD option
- [ ] Checkout shows single-column layout
- [ ] `/admin/flags` shows all booleans as `false`

### Test 3 — Discount Banner Flag
1. Edit `flags.yaml`: `discount-banner-enabled` → `variation: enabled`
2. Commit
3. Wait 5 s, refresh homepage
4. [ ] Orange/red banner appears at top
5. [ ] Products show strikethrough prices + badge
6. [ ] Cart shows discount amount
7. [ ] Revert → banner disappears

### Test 4 — Cash on Delivery Flag
1. Edit `flags.yaml`: `cash-on-delivery-enabled` → `variation: enabled`
2. Commit, wait 5 s
3. Add item to cart, proceed to checkout
4. [ ] COD radio button visible with green badge
5. [ ] Select COD, place order → success
6. [ ] Check `/admin/orders` → payment = "cod"
7. [ ] Revert → COD option gone

### Test 5 — New Checkout Layout
1. Edit `flags.yaml`: `new-checkout-layout` → `variation: new`
2. Commit, wait 5 s
3. [ ] Checkout page shows two-column layout
4. [ ] Blue info banner says "New Checkout Layout Active"
5. [ ] Revert → single-column returns

### Test 6 — Promo Banner
1. Edit `flags.yaml`: `promo-banner-enabled` → `variation: enabled`
2. Commit
3. [ ] Purple promo strip appears on all pages
4. [ ] Text matches `promo-banner-text` variation

### Test 7 — Git Audit Trail
```bash
git log --oneline flags/flags.yaml
# Expected: multiple commits visible with descriptive messages

git diff HEAD~1 HEAD -- flags/flags.yaml
# Expected: shows exactly which lines changed (+ / - diff)
```

---

## 10. Presentation Notes

### Opening (1–2 min)
> "This project demonstrates how modern software teams manage feature releases
> using Git as the single source of truth. Instead of deploying new code to
> toggle features, we store feature flags in a YAML file tracked by Git.
> A relay proxy reads this file and serves flag values to our Flask app via REST."

### Live Demo Flow (5–7 min)

1. **Show the homepage** — all flags off, no banners, products normal
2. **Open `flags.yaml` in editor** — explain the YAML structure
3. **Enable `discount-banner-enabled`** → save → `git commit`
4. **Refresh browser** — point out the banner appeared without restart
5. **Show `/admin/flags`** — explain configuration status accounting
6. **Enable COD** → commit → show COD option in checkout
7. **Enable new layout** → commit → show two-column checkout
8. **Show `git log`** — explain the full audit trail
9. **Show `git diff`** — explain change tracking

### Closing (1 min)
> "Every change is traceable to a commit. We know exactly when each feature
> was enabled, who enabled it, and we can rollback instantly. This is SCM
> applied to runtime configuration — not just source code."

### SCM Talking Points
- **Configuration Identification**: "Each commit SHA is a unique config ID"
- **Status Accounting**: "The `/admin/flags` page shows current state; `git log` shows history"
- **Change Control**: "You can't change a flag without making a Git commit"
- **Audit**: "Run `git log -p flags/flags.yaml` to see every change ever made"
- **Rollback**: "`git revert` immediately undoes any flag change"

---

## License

MIT — Free to use for educational purposes.
