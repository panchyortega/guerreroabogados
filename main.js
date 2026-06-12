/* =============================================
   GUERRERO ABOGADOS — main.js
   ============================================= */

/* ---- Sticky header shadow ---- */
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

/* ---- Mobile menu toggle ---- */
const burger  = document.querySelector('.header__burger');
const mobileMenu = document.getElementById('mobile-menu');

burger.addEventListener('click', () => {
  const isOpen = mobileMenu.classList.toggle('open');
  burger.setAttribute('aria-expanded', isOpen);
  mobileMenu.setAttribute('aria-hidden', !isOpen);
});

// Close mobile menu when a link is clicked
document.querySelectorAll('.mobile-menu__link, .mobile-menu__cta').forEach(link => {
  link.addEventListener('click', () => {
    mobileMenu.classList.remove('open');
    burger.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
  });
});

/* ---- Active nav link on scroll ---- */
const sections  = document.querySelectorAll('section[id]');
const navLinks  = document.querySelectorAll('.header__nav-link');

const navObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(link => {
        link.classList.toggle(
          'active',
          link.getAttribute('href') === `#${entry.target.id}`
        );
      });
    }
  });
}, { rootMargin: '-40% 0px -55% 0px' });

sections.forEach(s => navObserver.observe(s));

/* ---- Scroll reveal ---- */
function initReveal() {
  // Generic .reveal elements
  const revealEls = document.querySelectorAll('.reveal');

  // Service cards
  const serviceCards = document.querySelectorAll('.service-card');
  serviceCards.forEach((card, i) => {
    card.style.transitionDelay = `${i * 60}ms`;
  });

  // Process steps
  const processSteps = document.querySelectorAll('.process__step');
  processSteps.forEach((step, i) => {
    step.style.transitionDelay = `${i * 100}ms`;
  });

  // Diff items
  const diffItems = document.querySelectorAll('.diff__item');
  diffItems.forEach((item, i) => {
    item.style.transitionDelay = `${i * 70}ms`;
  });

  const allReveal = [
    ...revealEls,
    ...serviceCards,
    ...processSteps,
    ...diffItems,
  ];

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  allReveal.forEach(el => revealObserver.observe(el));
}

/* ---- Hero parallax ---- */
function initParallax() {
  const parallaxEl = document.getElementById('hero-parallax');
  if (!parallaxEl) return;

  // Skip if reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    const heroH = document.querySelector('.hero')?.offsetHeight || 700;
    if (scrollY > heroH) return;
    const pct = scrollY / heroH;
    parallaxEl.style.transform = `translateY(${scrollY * 0.18}px)`;
  }, { passive: true });
}

/* ---- FAQ accordion ---- */
function initFAQ() {
  const items = document.querySelectorAll('.faq__item');

  items.forEach(item => {
    const btn    = item.querySelector('.faq__question');
    const answer = item.querySelector('.faq__answer');

    btn.addEventListener('click', () => {
      const isOpen = btn.getAttribute('aria-expanded') === 'true';

      // Close all others
      items.forEach(other => {
        const ob = other.querySelector('.faq__question');
        const oa = other.querySelector('.faq__answer');
        ob.setAttribute('aria-expanded', 'false');
        oa.hidden = true;
        oa.style.maxHeight = null;
      });

      // Toggle current
      if (!isOpen) {
        btn.setAttribute('aria-expanded', 'true');
        answer.hidden = false;
        // Animate open
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });
  });
}

/* ---- Smooth scroll for anchor links ---- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const targetId = anchor.getAttribute('href').slice(1);
      const target   = document.getElementById(targetId);
      if (!target) return;
      e.preventDefault();
      const headerH = header ? header.offsetHeight : 0;
      const top     = target.getBoundingClientRect().top + window.scrollY - headerH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });
}

/* ---- Init ---- */
document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  initParallax();
  initFAQ();
  initSmoothScroll();
});
