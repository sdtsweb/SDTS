Thanks for downloading this template!

Template Name: Selecao
Template URL: https://bootstrapmade.com/selecao-bootstrap-template/
Author: BootstrapMade.com
License: https://bootstrapmade.com/license/

Standard Operating Procedures (SOP) for Updating Event Content
=================================================================

Overview:
---------
This document outlines the steps required to update the event-related content on the San Diego Tamil Sangam website. Follow these instructions to update the carousel (Hero Section) and the Past Events (Portfolio Section) accordingly.

Note:
- All images for past events must be uploaded to the folder:
  assets/img/past-events/

1. Updating the Carousel Section
----------------------------------
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

2. Updating the Past Events Section
-------------------------------------
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

3. Additional Notes
-------------------
- **Backup:** Always back up the original code before making any changes.
- **Version Control:** After updating and testing locally, commit your changes with a clear commit message (e.g., "Update carousel with new event; update past events images").
- **Static Hosting Note:** If the site is hosted on GitHub Pages (a static host), PHP-based functionality (like contact forms) will not run. However, the content sections (carousel, past events, etc.) will display correctly.
- **Future Maintenance:** This SOP serves as a guide for future maintainers to update event-related content without confusion.

End of SOP.
