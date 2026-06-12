/* =============================================
   GUERRERO ABOGADOS — ayuda.js
   JS compartido para el Centro de Ayuda
   ============================================= */

/* ---- Header sticky ---- */
const header = document.getElementById('header');
if (header) {
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

/* ---- Mobile menu ---- */
const burger     = document.querySelector('.header__burger');
const mobileMenu = document.getElementById('mobile-menu');
if (burger && mobileMenu) {
  burger.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('open');
    burger.setAttribute('aria-expanded', isOpen);
    mobileMenu.setAttribute('aria-hidden', !isOpen);
  });
  document.querySelectorAll('.mobile-menu__link, .mobile-menu__cta').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
      mobileMenu.setAttribute('aria-hidden', 'true');
    });
  });
}

/* ---- Scroll reveal ---- */
document.addEventListener('DOMContentLoaded', () => {
  const revealEls = document.querySelectorAll('.reveal');
  if (!revealEls.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  revealEls.forEach((el, i) => {
    el.style.transitionDelay = `${i * 60}ms`;
    obs.observe(el);
  });
});
