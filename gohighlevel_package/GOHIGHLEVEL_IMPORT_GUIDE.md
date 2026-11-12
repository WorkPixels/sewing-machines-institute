# GoHighLevel (GHL) Import & Setup Guide
### Sewing Machines Institute Rebuilt Website ("Encouraging Master" Theme)

This package allows you to import the complete website into your **GoHighLevel (GHL)** account (or LeadConnector / white-labeled agency platform) in minutes.

---

## 📦 What Is in This Package?

1. **`ghl-custom-code-element.html`**:
   * The **all-in-one** drop-in file. Contains all HTML, embedded styles (`<style>`), and interactive scripts (`<script>`) for tabs, accordions, and the earnings ROI calculator.
2. **`ghl-custom-css.css`**:
   * Extracted stylesheet if you prefer placing CSS into **Page Settings > Custom CSS**.
3. **`ghl-footer-tracking.js`**:
   * Interactive script if you prefer placing JavaScript into **Page Settings > Tracking Code > Footer Tracking**.
4. **`images/` Folder**:
   * High-resolution, optimized images ready for one-click upload into your **GHL Media Library**.

---

## 🚀 How to Import into GoHighLevel (Step-by-Step)

### Method 1: The 2-Minute Drop-In (Recommended)

1. **Log in to GoHighLevel**:
   * Go to **Sites > Funnels** (or **Sites > Websites**).
   * Click **+ New Funnel** (or **+ New Website**) and name it `Sewing Machines Institute`.
   * Click **+ Add New Step** (e.g. Name: `Home` / Path: `/home`).

2. **Open the GHL Page Builder**:
   * Click **Create from Blank**.
   * Add a **Full Width Section** (`+ Add Section` > `Full Width`).
   * Inside the section, add a **1 Column Row** (`+ Add Row` > `1 Column`).
   * Inside the column, add an **Element** (`+ Add Element`).
   * Scroll down to **Custom Code** and choose **Custom JS/HTML**.

3. **Paste the Code**:
   * Click the **Custom JS/HTML** element to open its settings on the left sidebar.
   * Click **Open Code Editor**.
   * Open the file **`ghl-custom-code-element.html`** in Notepad (or any text editor), copy everything (`Ctrl + A`, `Ctrl + C`), and paste it into the GHL editor (`Ctrl + V`).
   * Click **Save**.

4. **Adjust Section Spacing in GHL**:
   * In the GHL builder, click on the Section settings (green border) and set **Padding Top: 0**, **Padding Bottom: 0**, **Padding Left: 0**, **Padding Right: 0** so the header and hero stretch smoothly edge-to-edge.

5. **Click Save & Preview** in the top-right corner of GHL!

---

### Method 2: Image Hosting in GHL Media Library (Optional)

The package currently references local `/images/` paths. When hosting permanently inside GHL:
1. In GoHighLevel, navigate to **Settings > Media** (or open the Media Library inside any GHL image element).
2. Click **Upload File** and select all 9 files from the **`images/`** folder in this package.
3. For each uploaded image in GHL, click **Copy Link**.
4. In your code, do a quick Find & Replace to swap `images/hero-workshop.jpg` with your GHL media link (e.g. `https://storage.googleapis.com/msgsndr/.../hero-workshop.jpg`).

---

### Method 3: Connecting Forms to GoHighLevel Workflows & CRM

In the code, the admissions and free course forms are pre-tagged with standard GHL field names:
* `name="first_name"`
* `name="email"`
* `name="phone"`

#### Connecting via Webhook (Easiest):
1. In GHL, go to **Automation > Workflows > + Create Workflow > Start from Scratch**.
2. Set the trigger to **Inbound Webhook**. Copy the generated Webhook URL.
3. In the code, search for `<form` and add:
   ```html
   <form action="PASTE_YOUR_GHL_WEBHOOK_URL_HERE" method="POST">
   ```
4. Submissions will automatically create Contacts, send SMS/Email notifications, and alert your team!

#### Connecting via GHL Native Form Embed:
If you already built a form in **Sites > Forms > Builder**:
1. In GHL, click **Integrate Form > Copy Embed Code** (`<iframe ...>`).
2. Search for `<!-- SECTION: ADMISSIONS / CONTACT -->` in the HTML code and paste your GHL embed iframe directly inside the form card!

---

## 🎯 Verification & Support
* **Responsive**: Fully optimized for Desktop, Tablet, and Mobile.
* **Palette Compliance**: Oxford Navy (`#1B263B`), Antique Parchment (`#F5E6D3`), Burnished Copper (`#9B5E3C`), Slate Charcoal (`#415A77`), Soft Linen (`#E0D1B7`), and Patina Mint (`#7EB09B`).
* **Fonts**: Loads Google Fonts (`Playfair Display` + `Lato`) automatically without needing extra site-wide header scripts.
