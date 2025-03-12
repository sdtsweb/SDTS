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
 * Check if an image exists by trying to load it
 * @param {string} url - URL of the image to check
 * @returns {Promise<boolean>} - Promise that resolves to true if image exists
 */
function checkImageExists(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
}

/**
 * Generate JSON list of image paths dynamically
 */
async function generateImageJSON(folderPath, start, end, extension = 'jpg') {
  const images = [];
  const validImages = [];

  // Generate all possible image paths
  for (let i = end; i >= start; i--) {
    images.push(`${folderPath}image-${i}.${extension}`);
  }

  // Check each image in parallel
  const imageChecks = await Promise.all(
    images.map(async (imagePath) => {
      const exists = await checkImageExists(imagePath);
      if (exists) {
        validImages.push(imagePath);
      } else {
        console.warn(`Image not found: ${imagePath}`);
      }
    })
  );

  return validImages;
}

/**
 * Load dynamic portfolio images and append to the Swiper container
 */
async function loadDynamicPortfolio(startIndex = 1, endIndex = 10) {
  const portfolioWrapper = document.getElementById('portfolio-swiper-wrapper');
  if (!portfolioWrapper) {
    console.warn('Portfolio wrapper not found');
    return;
  }

  // Use absolute path from root
  const folderPath = '/assets/img/past-events/';
  
  try {
    // Wait for valid images to be identified
    const validImages = await generateImageJSON(folderPath, startIndex, endIndex);
    
    if (validImages.length === 0) {
      console.warn('No valid images found in the specified range');
      return;
    }

    // Clear existing slides if needed
    // portfolioWrapper.innerHTML = ''; // Uncomment if you want to clear existing slides

    // Add only valid images as slides
    validImages.forEach(imageSrc => {
      const slide = document.createElement('div');
      slide.className = 'swiper-slide';
      slide.innerHTML = `
        <a href="${imageSrc}" class="glightbox preview-link">
          <img src="${imageSrc}" alt="Portfolio Image" 
               onerror="this.onerror=null; this.src='/assets/img/placeholder.jpg';">
        </a>`;
      portfolioWrapper.appendChild(slide);
    });

    // Update or initialize Swiper
    if (swiper) {
      swiper.update();
    } else {
      initSwiper();
    }

  } catch (error) {
    console.error('Error loading portfolio images:', error);
  }
}

// Modified event listener to handle async function
window.addEventListener('load', () => {
  loadDynamicPortfolio(1, 10)
    .catch(error => console.error('Error in initial portfolio load:', error));
  currentImages = 10;
});

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