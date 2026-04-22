# Bachcare Operations Dashboard

A live operations dashboard for the Bachcare Guest Support and Reputations & Resolutions team. Hosted via GitHub Pages — accessible to anyone in the business via a browser link.

## How to use it

### Daily workflow (2 minutes)
1. Open the dashboard link (saved in your browser or SharePoint)
2. Go to the **Reputations & Resolutions** tab
3. Drag and drop the R&R Tracker Excel file onto the drop zone
4. Data appears instantly — no waiting, no export needed
5. For cancellations, go to **Guest Support** and drag in the Cancellation Report

### Monthly reporting
- Select the reporting month using the pill buttons at the top
- Enter the monthly booking volume in the **Monthly bookings** field (top right)
- All percentages update automatically
- Type your leadership commentary in the text boxes and click **Save note** — it stays saved in your browser

---

## What's in the dashboard

### 👤 Guest Support tab
- Total cancellations split by Customer / Owner / Office
- By-channel breakdown (Booking.com, Airbnb, HomeAway/VRBO, Bachcare) showing BAU vs Outside BAU
- Outside-BAU detail table — all short-notice cancellations ordered by days to check-in
- BAU windows: Booking.com = 7 days · HomeAway/VRBO = 14 days · Airbnb & Bachcare = 30 days
- Cancellation reason frequency chart
- Monthly summary commentary box for leadership narrative

### 🏠 Reputations & Resolutions tab

**Overview sub-tab**
- Top 5 trending issues this month (all case types)
- Month snapshot: % of bookings with claims/feedback, GEL spend, recovery, write-offs
- MSP Damage Focus cards — top 3 claim types with recommended actions
- Monthly issues commentary box

**Claims sub-tab**
- % of bookings with claims · % resolved via GEL
- Outstanding claims — why are they open? (by current status)
- Age of open claims (average and oldest)
- Write-offs and owner-absorbed costs

**Feedback sub-tab**
- % of bookings with feedback · GEL-funded feedback %
- Funding breakdown (GEL / Owner / Split / No cost)
- Issues raised — frequency ranking with trend flags

**Financial sub-tab**
- Full funds status breakdown
- Write-off and owner cost detail
- Net GEL exposure summary

---

## Updating the dashboard to GitHub

When the dashboard HTML is updated, upload it here to replace the existing file:

1. Go to your GitHub repository: `https://github.com/YOUR-USERNAME/rr-dashboard`
2. Click on `index.html`
3. Click the pencil ✏️ icon (Edit)
4. Or use **Add file → Upload files** to replace it
5. Click **Commit changes**
6. GitHub Pages publishes the update within ~2 minutes

**To upload for the first time:**
1. Go to `https://github.com/new` and create a repository called `rr-dashboard`
2. Set it to **Private**
3. Upload `index.html` from this package
4. Go to **Settings → Pages → Deploy from branch → main / root → Save**
5. Your dashboard URL will be: `https://YOUR-USERNAME.github.io/rr-dashboard/`

---

## Embedding in SharePoint

1. Edit a SharePoint page
2. Add a **web part → Embed**
3. Paste your GitHub Pages URL
4. Publish the page

Anyone with access to the SharePoint page can view the dashboard — no GitHub account needed.

---

## Notes

- Commentary notes (text you type in the summary boxes) are saved to the browser's local storage. They persist across sessions on the same device and browser, but won't sync between devices. If you want to share the commentary, copy it into your PowerPoint or Teams report.
- The bookings figure must be entered manually each month — there's no automated source for this.
- No data ever leaves your browser. All processing happens locally when you drop a file in.
