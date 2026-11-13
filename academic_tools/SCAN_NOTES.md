# Investigation & Scan Notes: SEC Question Archive (sec.ac.bd)

## 1. Architecture & Content Delivery
- **Platform**: Bangladesh National Portal (V2Ministry platform, running on a CMS framework with Varnish HTTP cache).
- **API Status**: No separate public JSON/REST API exists for questions.
- **Delivery Mechanism**: Static pages are Server-Side Rendered (SSR) HTML.
- **Content Encoding**: Content details are rendered in standard HTML `<table>` elements and also embedded as Base64 in `<rt-renderer encoded-content="...">`. Standard regular expressions / HTML parsing over the response HTML can extract all tables and links reliably without executing JavaScript.
- **No external pip dependencies required**: Python standard library (`urllib.request` + `re` / `html.parser`) is 100% sufficient.

---

## 2. Page Discovery & Endpoint Mapping
The homepage (`https://sec.ac.bd`) contains a dedicated `service-box-widget` titled/alt:
`"প্রশ্নপত্রঃ সেমিস্টার ফাইনাল / ভর্তি পরীক্ষা"` (Question Papers: Semester Final / Admission Test).

From this widget, the direct URLs to the 4 archive pages are:

| Category | Category Name | Static Page URL |
|---|---|---|
| **CSE** | সিএসই বিভাগ (Computer Science & Engineering) | `https://sec.ac.bd/pages/static-pages/6922dcee933eb65569e12cea` |
| **EEE** | ইইই বিভাগ (Electrical & Electronic Engineering) | `https://sec.ac.bd/pages/static-pages/6922dcc7933eb65569e12025` |
| **Civil** | সিই বিভাগ (Civil Engineering) | `https://sec.ac.bd/pages/static-pages/6922dc8a933eb65569e10e30` |
| **Admission** | SEC Admission Test Previous Year Questions | `https://sec.ac.bd/pages/static-pages/6922deab933eb65569e1c7dd` |

*Note: The scanner can use these direct endpoint URLs while also supporting dynamic discovery from the homepage if the static page IDs ever rotate.*

---

## 3. Table Structure & Data Extraction

### A. Department Pages (CSE, EEE, Civil)
Each page contains multiple `<table>` elements (one table per academic session):
1. **Row 0 (Session Header)**: Contains session string matching `\d{4}-\d{4}` (e.g. `2024-2025`, `2023-2024`, `2022-2023`, `2021-2022`, `2020-2021`, `2019-2020`).
2. **Row 1 (Odd Semesters)**: Alternating pairs of `[Semester, PDF Link / Text]`:
   - `1-1` | `<a href="...pdf">PDF</a>` (or plain text `PDF` if unreleased)
   - `2-1` | `<a href="...pdf">PDF</a>`
   - `3-1` | `<a href="...pdf">PDF</a>`
   - `4-1` | `<a href="...pdf">PDF</a>`
3. **Row 2 (Even Semesters)**: Alternating pairs of `[Semester, PDF Link / Text]`:
   - `1-2` | `<a href="...pdf">PDF</a>`
   - `2-2` | `<a href="...pdf">PDF</a>`
   - `3-2` | `<a href="...pdf">PDF</a>`
   - `4-2` | `<a href="...pdf">PDF</a>`

### B. Admission Test Page
Contains a single table with standard tabular rows:
- Column 0: `SL. No` (e.g. `01`, `02`, `03`)
- Column 1: `Previous Year` / Session (`YYYY-YYYY`, e.g. `2025-2026`)
- Column 2: `Download` anchor tag `<a href="...pdf">PDF</a>`

---

## 4. Findings & Comparison with Hardcoded Catalog

Comparing the live site scan against the built-in `ALL_QUESTIONS`:

| Category | Hardcoded Count | Live Scanned Count | Difference |
|---|:---:|:---:|---|
| **CSE** | 14 | **17** | **+3 New Papers** |
| **EEE** | 9 | **10** | **+1 New Paper** |
| **Civil** | 15 | **15** | Matches (0 changes) |
| **Admission** | 3 | **3** | Matches (0 changes) |
| **Total** | **41** | **45** | **+4 New Papers Live** |

### Specific Findings:
- **New Papers Found on Site**:
  - `CSE_Session_2020-2021_Semester_1-1.pdf` (`.../540d426a-232e-4283-8702-2820766698c7.pdf`)
  - `CSE_Session_2019-2020_Semester_1-1.pdf` (`.../540d426a-232e-4283-8702-2820766698c7.pdf`)
  - `CSE_Session_2020-2021_Semester_4-2.pdf` (`.../e3455521-3e8f-4289-98d5-2bd350cb0e21.pdf`)
  - `EEE_Session_2020-2021_Semester_4-2.pdf` (`.../fe8ce101-80fd-4911-b11f-752ee81e3a1f.pdf`)
- **Updated URLs**:
  - Multiple CSE & EEE PDFs have updated Oracle Cloud Storage UUIDs on the live site (admin re-uploads).

---

## 5. Naming Convention Consistency
To ensure existing downloaded files stay cached and are not redownloaded:
- **CSE**: `CSE_Session_{session}_Semester_{semester}.pdf` inside `CSE/Semester_{semester}/`
- **EEE**: `EEE_Session_{session}_Semester_{semester}.pdf` inside `EEE/Semester_{semester}/`
- **Civil**: `CE_Session_{session}_Semester_{semester}.pdf` inside `CE/Semester_{semester}/` *(Tag is `CE`, Folder is `CE`)*
- **Admission**: `SEC_Admission_Test_Question_{session}.pdf` inside `Admission_Test/` *(no semester subfolder)*

---

## 6. Edge Cases & Fallback Handling
1. **Fallback Strategy**:
   - If internet is down, DNS fails, HTTP error occurs, or zero papers are parsed: print clear warning and seamlessly fall back to hardcoded `ALL_QUESTIONS`.
2. **Unsorted Parsing**:
   - If any PDF link is discovered whose department or semester cannot be resolved, place it in `Unsorted/` folder with fallback title rather than discarding it.
3. **De-duplication**:
   - De-duplicate papers by unique PDF URL (or destination filepath) to avoid redundant download tasks.
4. **Offline Cache**:
   - When `--scan` runs successfully, save catalog to `catalog_cache.json` with a timestamp so offline runs can use the newest discovered catalog.
