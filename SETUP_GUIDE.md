# GitHub Setup — Step by Step
## Bachcare Operations Dashboard

Follow these steps exactly. Takes about 15 minutes total.

---

## STEP 1 — Create your GitHub account

1. Go to **https://github.com/signup**
2. Enter your **work email address**
3. Create a **username** (e.g. `bachcare-ops` or your name)
4. Verify your email when prompted

---

## STEP 2 — Create the repository

1. Once logged in, click the **+** button (top right of any GitHub page)
2. Click **New repository**
3. Fill in:
   - **Repository name:** `bachcare-dashboard`
   - **Description:** `Bachcare Operations Dashboard`
   - **Visibility:** ✅ **Private** (your data stays internal)
   - ✅ Tick **Add a README file**
4. Click **Create repository**

---

## STEP 3 — Upload the dashboard files

You have a ZIP file called `Bachcare_Operations_Dashboard_GitHub.zip`. Unzip it — you'll see:

```
index.html
README.md
.gitignore
.github/
  workflows/
    deploy.yml
```

Upload them to GitHub:

1. In your new repository, click **Add file** → **Upload files**
2. Drag the **entire unzipped folder contents** into the upload area
   - `index.html`
   - `README.md`
   - `.gitignore`
3. For the `.github/workflows/deploy.yml` file — you need to create the folder structure:
   - Click **Add file** → **Create new file**
   - In the filename box, type: `.github/workflows/deploy.yml`
   - Copy and paste the contents of `deploy.yml` from your unzipped folder
   - Click **Commit new file**

4. Back on the main file list, commit your other files with the message: `Initial dashboard upload`

---

## STEP 4 — Enable GitHub Pages

1. In your repository, click **Settings** (top menu bar)
2. In the left sidebar, scroll down and click **Pages**
3. Under **Source**, select: **GitHub Actions**
4. The deploy workflow will run automatically

> Wait 2–3 minutes. Refresh the Settings → Pages page and you'll see:
> **"Your site is live at https://YOUR-USERNAME.github.io/bachcare-dashboard/"**

✅ **Test it** — open that URL in your browser. You should see the dashboard.

---

## STEP 5 — Embed in SharePoint

1. Go to your SharePoint site
2. Navigate to the page where you want the dashboard
3. Click **Edit** (top right)
4. Click the **+** button to add a web part
5. Search for **Embed** and select it
6. Paste your GitHub Pages URL:
   `https://YOUR-USERNAME.github.io/bachcare-dashboard/`
7. The dashboard will appear embedded in the page
8. Resize the embed web part to fill the page
9. Click **Publish**

Anyone with access to that SharePoint page can now view the dashboard — no GitHub account needed.

---

## STEP 6 — Updating the dashboard in future

When Claude gives you an updated `index.html`:

1. Go to your GitHub repository
2. Click on `index.html` in the file list
3. Click the **pencil icon** (Edit this file) — top right of the file view
4. Delete all the content and paste in the new HTML
5. Click **Commit changes** → **Commit directly to main**
6. GitHub Pages will automatically redeploy within 2 minutes

---

## Daily use — no GitHub needed

Once it's live, your daily workflow is:

1. Open the dashboard URL (bookmark it, or go via SharePoint)
2. **R&R tab:** Drag your R&R Tracker Excel onto the drop zone → data loads instantly
3. **Guest Support tab:** Drag your Cancellation Report onto the drop zone
4. Select the month (or set a date range for weekly views)
5. Enter your monthly bookings figure
6. Generate your 4DX report → copy → paste into your presentation

---

## Troubleshooting

**"Site not found" after setup**
- Wait 5 minutes and try again — first deploy can be slow
- Check Settings → Pages shows a green tick ✅

**"Actions failed" in repository**
- Click **Actions** tab in your repository
- Click the failed workflow to see the error
- Most common fix: make sure the `deploy.yml` file is exactly at `.github/workflows/deploy.yml`

**File won't upload in the dashboard**
- Make sure you're using Chrome, Edge, or Firefox (not Safari on older iOS)
- Try dragging the file onto the drop zone rather than clicking
- The file must be `.xlsx` format (not `.xls` or `.csv` for R&R)

**Dashboard shows but data is wrong**
- Check the R&R sheet tab is still named `R&R - FY26` in your tracker
- If the sheet name has changed, let Claude know and it can update the code

---

*Bachcare Operations Dashboard · Built with Claude by Anthropic*
