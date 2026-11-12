/**
 * Sewing Machines Institute (FSMI) - Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Drawer Navigation
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const drawerClose = document.getElementById('drawerClose');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', () => {
      mobileDrawer.classList.add('open');
      document.body.style.overflow = 'hidden';
    });

    const closeDrawer = () => {
      mobileDrawer.classList.remove('open');
      document.body.style.overflow = '';
    };

    if (drawerClose) drawerClose.addEventListener('click', closeDrawer);

    mobileNavLinks.forEach(link => {
      link.addEventListener('click', closeDrawer);
    });

    // Close when clicking outside drawer
    document.addEventListener('click', (e) => {
      if (mobileDrawer.classList.contains('open') && 
          !mobileDrawer.contains(e.target) && 
          !mobileToggle.contains(e.target)) {
        closeDrawer();
      }
    });
  }

  // 2. Program Tabs Switching
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  const switchTab = (targetTabId) => {
    tabButtons.forEach(btn => {
      const isTarget = btn.getAttribute('data-tab') === targetTabId;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });

    tabPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `tab-${targetTabId}`);
    });
  };

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });

  // Handle external links targeting tabs (e.g. dropdown or footer)
  document.querySelectorAll('a[data-tab]').forEach(link => {
    link.addEventListener('click', (e) => {
      const targetTab = link.getAttribute('data-tab');
      if (targetTab) {
        switchTab(targetTab);
        const programsSection = document.getElementById('programs');
        if (programsSection) {
          programsSection.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });

  // 3. Technician ROI & Earnings Calculator
  const repairsSlider = document.getElementById('repairsSlider');
  const repairsValueBadge = document.getElementById('repairsValueBadge');
  const weeklyResult = document.getElementById('weeklyResult');
  const monthlyResult = document.getElementById('monthlyResult');
  const annualResult = document.getElementById('annualResult');
  const hoursPerWeek = document.getElementById('hoursPerWeek');

  const updateCalculator = () => {
    if (!repairsSlider) return;
    const repairsPerWeek = parseInt(repairsSlider.value, 10);
    const feePerRepair = 110; // Verified industry average from SMI

    const weekly = repairsPerWeek * feePerRepair;
    const monthly = Math.round(weekly * 4.333);
    const annual = weekly * 52;
    const hours = repairsPerWeek * 2;

    repairsValueBadge.textContent = `${repairsPerWeek} machines/wk`;
    weeklyResult.textContent = `$${weekly.toLocaleString()}`;
    monthlyResult.textContent = `$${monthly.toLocaleString()}`;
    annualResult.textContent = `$${annual.toLocaleString()}`;
    if (hoursPerWeek) {
      hoursPerWeek.textContent = `~${hours} hours of bench work`;
    }
  };

  if (repairsSlider) {
    repairsSlider.addEventListener('input', updateCalculator);
    updateCalculator(); // Initial calculation
  }

  // 4. FAQ Collapsible Accordion
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (!questionBtn) return;

    questionBtn.addEventListener('click', () => {
      const isOpen = item.classList.contains('active');

      // Close all items
      faqItems.forEach(otherItem => {
        otherItem.classList.remove('active');
        const otherBtn = otherItem.querySelector('.faq-question');
        if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
      });

      // Toggle current item
      if (!isOpen) {
        item.classList.add('active');
        questionBtn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // 5. Seat Reservation Modal
  const reserveModal = document.getElementById('reserveModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalReserveForm = document.getElementById('modalReserveForm');
  const modalSuccess = document.getElementById('modalSuccess');
  const modalTitle = document.getElementById('modalTitle');
  const modalSelectedSession = document.getElementById('modalSelectedSession');
  const reserveTriggers = document.querySelectorAll('.reserve-trigger');

  const openModal = (sessionName) => {
    if (!reserveModal) return;
    if (sessionName) {
      modalTitle.textContent = `Reserve: ${sessionName}`;
      if (modalSelectedSession) modalSelectedSession.value = sessionName;
    } else {
      modalTitle.textContent = 'Reserve Your Seat';
    }
    reserveModal.classList.add('open');
    reserveModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    if (!reserveModal) return;
    reserveModal.classList.remove('open');
    reserveModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (modalSuccess) modalSuccess.style.display = 'none';
    if (modalReserveForm) modalReserveForm.reset();
  };

  reserveTriggers.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const sessionDate = btn.getAttribute('data-date') || btn.getAttribute('data-program');
      openModal(sessionDate);
    });
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);

  if (reserveModal) {
    reserveModal.addEventListener('click', (e) => {
      if (e.target === reserveModal) closeModal();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && reserveModal.classList.contains('open')) {
        closeModal();
      }
    });
  }

  if (modalReserveForm) {
    modalReserveForm.addEventListener('submit', (e) => {
      e.preventDefault();
      modalReserveForm.style.display = 'none';
      if (modalSuccess) modalSuccess.style.display = 'block';

      setTimeout(() => {
        closeModal();
        modalReserveForm.style.display = 'flex';
      }, 4000);
    });
  }

  // 6. Free Maintenance Course Form
  const freeCourseForm = document.getElementById('freeCourseForm');
  if (freeCourseForm) {
    freeCourseForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = freeCourseForm.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = '✓ Access Granted! Redirecting...';
      btn.style.backgroundColor = '#047857';
      btn.disabled = true;

      setTimeout(() => {
        alert('Welcome! Your Free 7-Step Sewing Machine Maintenance Guide has been dispatched to your email address.');
        btn.textContent = originalText;
        btn.style.backgroundColor = '';
        btn.disabled = false;
        freeCourseForm.reset();
      }, 1000);
    });
  }

  // 7. Contact / Enrollment Form
  const contactForm = document.getElementById('contactForm');
  const formSuccessMessage = document.getElementById('formSuccessMessage');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Inquiry';
        contactForm.reset();
        if (formSuccessMessage) {
          formSuccessMessage.style.display = 'block';
          formSuccessMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          setTimeout(() => {
            formSuccessMessage.style.display = 'none';
          }, 8000);
        }
      }, 800);
    });
  }

  // 8. Sticky Header subtle shadow on scroll
  const siteHeader = document.getElementById('header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      siteHeader.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
    } else {
      siteHeader.style.boxShadow = 'none';
    }
  });
});
