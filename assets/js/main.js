/**
* Template Name: Selecao
* Template URL: https://bootstrapmade.com/selecao-bootstrap-template/
* Updated: Aug 07 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  mobileNavToggleBtn.addEventListener('click', mobileNavToogle);

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Animation on scroll function and init
   */
  function aosInit() {
    AOS.init({
      duration: 600,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    });
  }
  window.addEventListener('load', aosInit);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /**
   * Init isotope layout and filters
   */
  document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
    let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
    let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
    let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';

    let initIsotope;
    imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
      initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
        itemSelector: '.isotope-item',
        layoutMode: layout,
        filter: filter,
        sortBy: sort
      });
    });

    isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
      filters.addEventListener('click', function() {
        isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
        this.classList.add('filter-active');
        initIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        if (typeof aosInit === 'function') {
          aosInit();
        }
      }, false);
    });

  });

 // This change is to load the photos dynamically 01/06 starts

 let swiper; // Global variable to hold Swiper instance

/**
 * Generate JSON list of image paths dynamically
 * @param {string} folderPath - Path to the images folder
 * @param {number} start - Starting index of images
 * @param {number} end - Ending index of images
 * @param {string} extension - Image file extension (e.g., 'jpg')
 * @returns {string[]} Array of image paths
 */

/**
 * Load dynamic portfolio images and initialize swiper
 */
function generateImageJSON(folderPath, start, end, extension = 'jpg') {
  const images = [];
  for (let i = end; i >= start; i--) {
    images.push(`${folderPath}image-${i}.${extension}`);
  }
  return images;
}


/**
 * Load dynamic portfolio images and append to the Swiper container
 * @param {number} startIndex - Starting index of images to load
 * @param {number} endIndex - Ending index of images to load
 */
function loadDynamicPortfolio(startIndex = 1, endIndex = 10) {
  const portfolioWrapper = document.getElementById('portfolio-swiper-wrapper');
  const folderPath = 'assets/img/masonry-portfolio/'; // Path to the images folder
  const imageJSON = generateImageJSON(folderPath, startIndex, endIndex); // Generate the JSON array

  console.log(swiper);

  if (!portfolioWrapper) return;

  // Append the new images as swiper-slide elements
  imageJSON.forEach(imageSrc => {
    const slide = document.createElement('div');
    slide.className = 'swiper-slide';
    slide.innerHTML = `<img src="${imageSrc}" alt="Portfolio Image">`;
    portfolioWrapper.appendChild(slide);
  });

  // Reinitialize Swiper or update it after adding new slides
  if (swiper) {
    swiper.update(); // Update Swiper instance with new slides
  } else {
    initSwiper(); // Initialize Swiper if not already initialized
  }
}

// Initialize currentImages globally to track the number of images loaded
let currentImages = 0; // Start with 0 or adjust according to your setup

// Initial load on page load
window.addEventListener('load', () => {
  loadDynamicPortfolio(1, 20); // Load the first 10 images
  //currentImages = 10; // Update currentImages after initial load
});
/* commented load more button 02/16
// Add "Load More" functionality
document.getElementById('load-more').addEventListener('click', () => {
  // Adjust the range to load the next set of images
  loadDynamicPortfolio(currentImages + 1, currentImages + 10); // Load 10 more images
  currentImages += 10; // Update the count of loaded images
});
*/
// This change is to load the photos dynamically 01/06 ends


/**
 * Init swiper sliders
 */
function initSwiper() {
  document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
    let config = JSON.parse(
      swiperElement.querySelector(".swiper-config").innerHTML.trim()
    );

    if (swiperElement.classList.contains("swiper-tab")) {
      initSwiperWithCustomPagination(swiperElement, config);
    } else {
      swiper = new Swiper(swiperElement, config); // Assign swiper instance to the global variable
    }
  });
}

window.addEventListener("load", initSwiper);


/**
 * Correct scrolling position upon page load for URLs containing hash links.
 */
window.addEventListener('load', function(e) {
  if (window.location.hash) {
    if (document.querySelector(window.location.hash)) {
      setTimeout(() => {
        let section = document.querySelector(window.location.hash);
        let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
        window.scrollTo({
          top: section.offsetTop - parseInt(scrollMarginTop),
          behavior: 'smooth'
        });
      }, 100);
    }
  }
});

  /**
   * Navmenu Scrollspy
   */
  let navmenulinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navmenulinks.forEach(navmenulink => {
      if (!navmenulink.hash) return;
      let section = document.querySelector(navmenulink.hash);
      if (!section) return;
      let position = window.scrollY + 200;
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
        navmenulink.classList.add('active');
      } else {
        navmenulink.classList.remove('active');
      }
    })
  }
  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);

})();