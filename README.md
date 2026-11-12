# Sewing Machines Institute & SMI University Template 🧵🎓

> **"Master the Machine. Preserve the Craft."**  
> A modern, heritage-artisan website template and integrated learning suite for sewing machine repair education, based on 30 years of daily bench wisdom from the **Sewing Machines Institute (FSMI)** in Temple, Texas.

---

## 🌟 Highlights & Features

### 1. Modern Heritage-Artisan Marketing Website
* **Brand Persona**: *"The Encouraging Master"* — expert, grounded, patient, and practical.
* **Palette Tokens**:
  * **Oxford Navy (`#1B263B`)**: Headers, footers, dark authority containers, primary titles.
  * **Antique Parchment (`#F5E6D3`)**: Warm, tactile background canvas (replaces cold corporate white).
  * **Burnished Copper (`#9B5E3C`)**: Metallic accent, primary CTA buttons (*"Claim Your Seat at the Bench"*), active tabs.
  * **Slate Charcoal (`#415A77`)**: Blueprint metadata, card subtitles, and technical details.
  * **Soft Linen (`#E0D1B7`)**: Card backgrounds, subtle section bands, and borders.
  * **Patina Mint (`#7EB09B`)**: High-contrast mineral oxidized copper accents, status badges, and links.
* **Typography**:
  * **Headings**: `Playfair Display` (Serif) — sharp needle-like lines and timeless elegance.
  * **Body & Buttons**: `Lato` (Sans-Serif) — warm, legible, approachable.
* **Interactive Components**:
  * **Technician Earnings ROI Estimator**: Live calculator based on the authentic industry benchmark of **~$110 per 2-hour machine tune-up**.
  * **Curriculum Pathway Explorer**: Interactive tabs for the Live 5-Day Class (Temple, TX), Home Correspondence Course ($699), Industrial On-Site Training, Multi-Needle Embroidery, and the Free 7-Step Course.
  * **Live Studio Schedule**: Real-time session dates with seat reservation dialogs.
  * **FAQ Accordion & Studio Photo Gallery**: High-resolution workshop imagery.

---

### 2. SMI University (Full Learning Suite / LMS)
A custom institutional learning management suite built with a streamlined 2-pane video learning UX:
* **Student Dashboard**: Enrolled programs, completion percentage bars, and a *"Continue Where You Left Off"* quick-jump banner.
* **2-Pane Video Classroom**:
  * **Left Side**: Theater video player, navigation controls, and comprehensive content tabs:
    * *🛠️ Workbench Notes*: Step-by-step mechanical tolerances (0.05mm hook clearance, 2.0mm needle rise).
    * *📐 Schematics & Blueprints*: Downloadable authorized PDFs and exploded mechanical assembly diagrams.
    * *💬 Ask Jeremiah (Q&A)*: Interactive student inquiry and community discussion board.
  * **Right Side (Curriculum Drawer)**: Collapsible module accordions with lesson duration badges and live completion checkboxes.
* **Institutional Video Anti-Download Protection**:
  * **Authenticated Stream Proxy (`/api/stream/<id>`)**: Video files are streamed via chunked byte ranges only after validating active session entitlements (direct scraping returns `401/403 Forbidden`).
  * **Browser Hardening**: Download buttons stripped (`controlsList="nodownload noplaybackrate"`), Picture-in-Picture disabled, right-click menu blocked, and inspection hotkeys (`Ctrl+S`, `Ctrl+U`, `F12`) intercepted.
  * **Dynamic Forensics Floating Watermark**: Floating watermark displaying the logged-in student's **Name, Email, and Timestamp** slowly drifting across playback coordinates to permanently deter screen capture tools.

---

### 3. Master Admin Studio
* **Wix CSV Bulk Account Migration**:
  * Upload your CSV export from Wix Contacts or Wix Orders.
  * Automatically matches course titles (*Correspondence* $\rightarrow$ ProTraining 1; *Computerized* $\rightarrow$ ProTraining 2; *Live Class* $\rightarrow$ Bench Companion; *Industrial* $\rightarrow$ Industrial Lockstitch).
  * Automatically generates hashed credentials, provisions student profiles, and outputs a migration log.
* **Student Directory & 1-Click Access Control**:
  * Search and filter students by name, email, or source.
  * Interactive course toggle pills: **click once** to instantly grant or revoke any course entitlement with live database sync.
* **Course & Curriculum Builder**:
  * Add new programs, define modules, and upload video lessons with duration, bench notes, and preview tags.

---

### 4. GoHighLevel (GHL) Import Package
Includes ready-to-deploy files for **GoHighLevel**:
* `ghl-custom-code-element.html`: 1-click drop-in for GHL's Custom JS/HTML Element.
* `ghl-custom-css.css`: Pre-formatted for Page Settings > Custom CSS.
* `ghl-footer-tracking.js`: Interactive scripts for GHL Footer Tracking Code.
* Pre-configured lead capture fields (`first_name`, `email`, `phone`) ready for GHL Webhooks & Workflows.

---

## 🚀 Getting Started Locally

### 1. Run the Main Marketing Website
You can open `index.html` directly in any web browser, or serve it via Python:
```bash
python -m http.server 3000
```
Open **`http://localhost:3000`** in your browser.

### 2. Run SMI University (LMS)
```bash
cd lms
python app.py
```
Open **`http://localhost:5000`** in your browser.

#### Demo Credentials:
* **Admin (Jeremiah Trumble)**: `admin@sewingmachinesinstitute.com` / `SMIadmin2026!`
* **Student (Sarah Jenkins)**: `student@sewingmachinesinstitute.com` / `Student2026!`

---

## 📁 Repository Structure

```
sewingmachinesinstitute/
├── index.html                   # Modern Heritage Marketing Website
├── styles.css                   # Encouraging Master design system & tokens
├── app.js                       # Frontend interactive logic
├── images/                      # High-resolution original photography & logos
├── gohighlevel_package/         # Complete GoHighLevel import templates & guide
├── lms/                         # SMI University Learning Suite (LMS)
│   ├── app.py                   # Flask LMS application & API endpoints
│   ├── models.py                # Database schema, initialization & seeders
│   ├── auth.py                  # Session auth & access control
│   ├── video_security.py        # Authenticated streaming proxy & chunker
│   ├── wix_importer.py          # Wix CSV bulk account migration engine
│   ├── static/
│   │   ├── css/lms.css          # University theme & classroom styles
│   │   ├── js/classroom.js      # Video player, watermarking & tabs
│   │   └── sample_wix_export.csv# Pre-loaded sample Wix customer export
│   └── templates/
│       ├── base.html            # Core navigation layout
│       ├── dashboard.html       # Student portal & enrolled courses
│       ├── classroom.html       # 2-Pane video learning suite
│       ├── catalog.html         # Program catalog
│       ├── login.html           # Authentication portal
│       └── admin/
│           ├── overview.html    # LMS analytics & stats
│           ├── users.html       # User directory & 1-click access control
│           ├── courses.html     # Curriculum & lesson builder
│           └── wix_migration.html# Wix CSV bulk migration uploader
└── README.md
```

---

## 📄 License & Attribution
Designed for the **Sewing Machines Institute (FSMI)**. All rights reserved.
