# San Diego Tamil Sangam (SDTS) Website

This repository contains the source code and assets for the San Diego Tamil Sangam (SDTS) website.

---

## Bharathiyar Tamil School (BTS) Now Managed Here

The Bharathiyar Tamil School (BTS) website is now fully managed in this repository.

- The old `bts.sdts.org` repository is archived and will not receive further updates.
- All BTS content is located in the `bts/` directory:
  - `bts/index.html` — Main BTS homepage (updated a few times per year for school year info, enrollment, and announcements).
  - `bts/assets/` — BTS-specific images, CSS, JS, and vendor files.
- `bts.html` — Redirects to `bts/index.html` for backward compatibility.
- Redirects are in place so that both `bts.sdts.org` and `sdts.org/bts.html` point to the new `bts/` directory.

### How to Update BTS Content

1. **Edit BTS files:**  
   - For BTS homepage updates, edit `bts/index.html`.
   - For assets, update files in `bts/assets/`.

2. **Preview Locally:**  
   Use a simple Python HTTP server:
   ```sh
   python3 -m http.server 8000
   # Then visit http://localhost:8000/bts/ in your browser
   ```

3. **Commit and Push:**
   ```sh
   git add .
   git commit -m "Update BTS content (describe your change)"
   git push origin main
   ```

4. **Deploy:**  
   After pushing, deploy the updated files to your web hosting (GoDaddy/Plesk or other).

---

Thanks for downloading this template!

Template Name: Selecao  
Template URL: https://bootstrapmade.com/selecao-bootstrap-template/  
Author: BootstrapMade.com  
License: https://bootstrapmade.com/license/

---

# Standard Operating Procedures (SOP) for Updating Event Content

## Overview:
This document outlines the steps required to update the event-related content on the San Diego Tamil Sangam website. Follow these instructions to update the carousel (Hero Section) and the Past Events (Portfolio Section) accordingly.

**Note:**
- All images for past events must be uploaded to the folder:
  `assets/img/past-events/`

## 1. Updating the Carousel Section

- **Locate the Carousel Section:**
  Open the `index.html` file and scroll to the Hero Section (carousel), which is within the `<section id="hero" class="hero section dark-background">` tag.

- **Adding a New Slide:**
  - Create a new `<div class="carousel-item">` block for the new event.
  - Include the event title, description, and a call-to-action button.
  - Example:
    ```html
    <!-- New Event Slide -->
    <div class="carousel-item">
      <div class="carousel-container">
        <h2 class="animate__animated animate__fadeInDown">New Event Title</h2>
        <p class="animate__animated animate__fadeInUp">New event description goes here. Make it compelling!</p>
        <a href="new-event-page.html" class="btn-get-started animate__animated animate__fadeInUp scrollto">Read More</a>
      </div>
    </div>
    ```
  
- **Removing an Outdated Slide:**
  - Identify the outdated slide (typically the last one) and either remove or comment it out.
  - Ensure that the first slide has the `active` class if necessary.

- **Testing:**
  Preview the page locally in your browser to verify that the new slide appears correctly and that the outdated slide has been removed.

## 2. Updating the Past Events Section

- **Locate the Past Events Section:**
  Open the `index.html` file and find the "Past Events" section (Portfolio Section) which is within the `<section id="portfolio" class="portfolio section">` tag.

- **Image Updates:**
  - Upload new images to `assets/img/past-events/`. For example, your new images might be named like `image-10.jpg`, `image-09.jpg`, etc.
  - Remove or comment out the HTML blocks corresponding to outdated images.

- **Adding New Past Event Items:**
  - Follow the existing structure when adding new event items.
  - Example:
    ```html
    <!-- Example Past Event Item -->
    <div class="col-lg-4 col-md-6 portfolio-item isotope-item filter-app">
      <img src="assets/img/past-events/new-image.jpg" class="img-fluid" alt="Description of New Event">
      <div class="portfolio-info">
        <h4>New Event Title</h4>
        <p>Short description of the new event</p>
        <a href="assets/img/past-events/new-image.jpg" title="New Event Title" data-gallery="portfolio-gallery-app" class="glightbox preview-link">
          <i class="bi bi-zoom-in"></i>
        </a>
      </div>
    </div>
    ```

- **Ordering:**
  - Ensure the new images are arranged in the desired order (e.g., newest first).

- **Testing:**
  Verify that the new images display properly on the page and that the removed items no longer appear.

## 3. Additional Notes

- **Backup:** Always back up the original code before making any changes.
- **Version Control:** After updating and testing locally, commit your changes with a clear commit message (e.g., "Update carousel with new event; update past events images").
- **Static Hosting Note:** If the site is hosted on GitHub Pages (a static host), PHP-based functionality (like contact forms) will not run. However, the content sections (carousel, past events, etc.) will display correctly.
- **Future Maintenance:** This SOP serves as a guide for future maintainers to update event-related content without confusion.

End of SOP.

---

## Repository Structure

- `index.html` — Main SDTS homepage.  
  _Updated 4–5 times per year for events, announcements, and general SDTS information._

- `bts/` — Directory containing the Bharathiyar Tamil School website.
  - `bts/index.html` — Main BTS homepage.
    _Updated a few times per year for school year info, enrollment, and announcements._
  - `bts/assets/` — BTS-specific images, CSS, JS, and vendor files.

- `bts.html` — Redirects to `bts/index.html` for backward compatibility.

---

## How to Update the Website

### 1. **Clone the Repository**
```sh
git clone https://github.com/sdtsweb/SDTS.git
cd SDTS
```

### 2. **Make Your Changes**
- For SDTS homepage updates, edit `index.html`.
- For BTS updates, edit `bts/index.html` or other files in the `bts/` directory.

### 3. **Preview Locally**
You can use a simple Python HTTP server to preview changes:
```sh
# For Python 3.x
python3 -m http.server 8000
# Then visit http://localhost:8000 in your browser
```

### 4. **Commit and Push Changes**
```sh
git add .
git commit -m "Describe your update (e.g., Update BTS enrollment info for 2025-2026)"
git push origin main
```

### 5. **Deploy**
- After pushing, deploy the updated files to your web hosting (GoDaddy/Plesk or other).
- Make sure to upload both `index.html` and any updated files in the `bts/` directory.

---

## Notes

- **BTS is now fully managed in this repository.**  
  The old `bts.sdts.org` repository is archived and will not receive further updates.
- **Redirects** are in place so that both `bts.sdts.org` and `sdts.org/bts.html` point to the new `bts/` directory.
- **SSL Certificates:**  
  Both `sdts.org` and `bts.sdts.org` should have valid SSL certificates for secure access and proper redirects.

---

## Contact

For questions or contributions, please open an issue or contact the SDTS web team. 