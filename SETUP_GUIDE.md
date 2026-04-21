# R&R Dashboard — Complete Setup Guide

This guide walks you through getting the dashboard live on the internet
and automatically updating from your SharePoint tracker. No technical background
needed — every step is explained.

---

## What you'll end up with

```
Your tracker (SharePoint/OneDrive Excel)
    ↓  Power Automate reads it nightly
    ↓  Runs generate_data.py → creates data.json
    ↓  Pushes data.json to GitHub
GitHub Pages → hosts the dashboard website
    ↓
Dashboard URL → embedded in SharePoint → everyone sees live data
```

**Time to set up:** About 60–90 minutes the first time.
**After that:** Fully automatic. You never touch it again.

---

## PART 1 — Create a GitHub account and repository

### Step 1: Create a free GitHub account

1. Go to **https://github.com/signup**
2. Enter your work email address
3. Choose a username (e.g. `bachcare-rr` or your name)
4. Complete the verification and confirm your email

### Step 2: Create a new repository (your dashboard's "folder")

1. Once logged in, click the **+** icon (top right) → **New repository**
2. Fill in:
   - **Repository name:** `rr-dashboard`
   - **Description:** `R&R 4DX Monthly Dashboard`
   - **Visibility:** Set to **Private** (your data stays private)
   - ✅ Tick **Add a README file**
3. Click **Create repository**

### Step 3: Upload the dashboard files

1. In your new repository, click **Add file** → **Upload files**
2. Drag and drop these three files from the folder I gave you:
   - `index.html`
   - `data.json`
   - `generate_data.py`
3. At the bottom, click **Commit changes**

### Step 4: Enable GitHub Pages (this makes it a live website)

1. In your repository, click **Settings** (top menu)
2. Scroll down to **Pages** in the left sidebar
3. Under **Source**, select **Deploy from a branch**
4. Branch: choose **main** | Folder: choose **/ (root)**
5. Click **Save**
6. Wait 2–3 minutes, then refresh. You'll see:
   > Your site is live at `https://YOUR-USERNAME.github.io/rr-dashboard/`

✅ **Test it** — open that URL. You should see the dashboard with sample data.

---

## PART 2 — Create a GitHub Personal Access Token

Power Automate needs permission to push updated data to GitHub.
You give it a "token" (like a special password for automation).

1. Go to **https://github.com/settings/tokens**
2. Click **Generate new token** → **Generate new token (classic)**
3. Fill in:
   - **Note:** `Power Automate RR Dashboard`
   - **Expiration:** 1 year (or no expiration)
   - **Scopes:** Tick only ✅ **repo** (gives access to your repositories)
4. Click **Generate token**
5. **IMPORTANT:** Copy the token now — you'll never see it again.
   It looks like: `ghp_xxxxxxxxxxxxxxxxxxxx`
6. Save it somewhere secure (e.g. your password manager or a private note)

---

## PART 3 — Set up Power Automate (the automation engine)

Power Automate is included in your Microsoft 365 licence.
It's the bridge between your SharePoint tracker and GitHub.

### Step 1: Open Power Automate

1. Go to **https://make.powerautomate.com**
2. Sign in with your work Microsoft account

### Step 2: Create a new scheduled flow

1. Click **+ Create** → **Scheduled cloud flow**
2. Fill in:
   - **Flow name:** `RR Dashboard Data Refresh`
   - **Starting:** today
   - **Repeat every:** 1 Day (or choose your preferred frequency)
3. Click **Create**

### Step 3: Add the steps

You'll be building a flow with these actions in order:

---

**Action 1 — Get the Excel file from SharePoint**

- Click **+ New step**
- Search for: `Get file content`
- Choose: **SharePoint — Get file content**
- Fill in:
  - **Site Address:** your SharePoint site URL
  - **File Identifier:** browse to your R&R tracker Excel file

---

**Action 2 — Run the Python script to convert data**

- Click **+ New step**
- Search for: `Run script`
- Choose: **Office Scripts — Run script** *(if your org has this)*

> **Alternative if Office Scripts isn't available:**
> Use **Azure Functions** (ask your IT team) or the simpler approach below.

**Simpler alternative — use Power Automate's built-in Excel parsing:**

Instead of Python, use Power Automate's Excel connector to read rows directly:

- **Action:** `List rows present in a table` (Excel Online — Business)
- **Location:** SharePoint
- **Document Library:** your library
- **File:** your tracker
- **Table:** your data table

Then use a **Compose** action to build the JSON manually from the listed rows.

> 💡 **Recommendation:** Ask your IT department to help set this up. The Python script approach is more powerful but requires a small Azure Function or a computer running as a scheduled task. The Office Scripts approach works entirely within Microsoft 365 with no extra cost.

---

**Action 3 — Push data.json to GitHub**

- Click **+ New step**
- Search for: `HTTP`
- Choose: **HTTP** (the generic HTTP action)
- Fill in:
  - **Method:** PUT
  - **URI:** `https://api.github.com/repos/YOUR-USERNAME/rr-dashboard/contents/data.json`
  - **Headers:**
    ```
    Authorization: token ghp_YOUR_TOKEN_HERE
    Content-Type: application/json
    Accept: application/vnd.github.v3+json
    ```
  - **Body:**
    ```json
    {
      "message": "Auto-update data.json",
      "content": "@{base64(body('Compose_JSON'))}",
      "sha": "@{body('Get_Current_SHA')['sha']}"
    }
    ```

> **Note on SHA:** GitHub requires you to include the current file's SHA when updating. Add a GET request before the PUT to fetch the current SHA:
> - **Method:** GET
> - **URI:** `https://api.github.com/repos/YOUR-USERNAME/rr-dashboard/contents/data.json`
> - **Headers:** same Authorization header as above
> This returns the current SHA — reference it as `body('HTTP')['sha']` in your PUT.

---

### Step 4: Test and save

1. Click **Save** (top right)
2. Click **Test** → **Manually** → **Run flow**
3. Check your GitHub repository — `data.json` should be updated
4. Open your dashboard URL — it should show fresh data

---

## PART 4 — Embed in SharePoint

### Option A — Embed as a full-page tab (recommended)

1. Open your SharePoint site
2. Go to the page where you want the dashboard
3. Click **Edit** (top right)
4. Click **+** to add a web part → search for **Embed**
5. Paste your GitHub Pages URL:
   `https://YOUR-USERNAME.github.io/rr-dashboard/`
6. Resize the embed area to fill the page
7. Click **Publish**

### Option B — Add as a navigation link

1. In SharePoint, click **Edit** on the navigation bar
2. Add a link → paste your dashboard URL
3. Label it: `R&R Dashboard`

---

## PART 5 — Keeping it up to date

### What happens automatically
- Power Automate runs on your chosen schedule (daily recommended)
- It reads your SharePoint tracker, converts it to JSON, pushes to GitHub
- GitHub Pages serves the updated file within minutes
- Anyone viewing the dashboard sees fresh data on next page load

### What you still do manually
- **Bookings figure:** Each month, type the booking volume into the dashboard's input field. There's no way to automate this unless bookings are tracked somewhere in your systems that Power Automate can read.
- **New months:** They appear automatically as data is added to the tracker.

### When something breaks
The most common issues:
1. **GitHub token expired** — regenerate at github.com/settings/tokens and update Power Automate
2. **Sheet name changed** — if you rename the `R&R - FY26` tab, update the script
3. **Power Automate flow failed** — check the flow run history at make.powerautomate.com

---

## Getting help from Claude

If any step is confusing, paste this guide back to Claude and say which step you're on.
Claude can also:
- Update the dashboard design
- Add new metrics as your reporting needs change
- Write the Power Automate JSON body formula for you
- Debug any errors that come up

---

## File reference

| File | Purpose |
|------|---------|
| `index.html` | The dashboard website — goes in your GitHub repo |
| `data.json` | The data file — Power Automate updates this automatically |
| `generate_data.py` | Python script to convert your Excel to JSON (optional — for IT/advanced setup) |
| `SETUP_GUIDE.md` | This guide |

---

*Generated by Claude · Anthropic · For internal use only*
