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

/* ---- Search with dropdown ---- */
document.addEventListener('DOMContentLoaded', () => {
  const input    = document.getElementById('searchInput');
  const dropdown = document.getElementById('searchDropdown');
  const clearBtn = document.getElementById('searchClear');
  if (!input || !dropdown || typeof SEARCH_INDEX === 'undefined') return;

  // Normalize: remove accents + lowercase
  function normalize(str) {
    return str.toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  // Highlight matched term in title
  function highlight(title, query) {
    const terms = query.trim().split(/\s+/).filter(Boolean);
    let result = title;
    terms.forEach(term => {
      const normTerm = normalize(term);
      const re = new RegExp(`(${normTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      // Match against normalized but replace in original
      result = result.replace(re, '<mark>$1</mark>');
    });
    return result;
  }

  function search(query) {
    const q = normalize(query.trim());
    if (!q || q.length < 2) return [];

    const terms = q.split(/\s+/).filter(Boolean);

    return SEARCH_INDEX
      .filter(art => terms.every(term => art.text.includes(term)))
      .slice(0, 8); // max 8 results
  }

  function renderDropdown(query) {
    const results = search(query);
    dropdown.innerHTML = '';

    if (!query.trim() || query.trim().length < 2) {
      dropdown.hidden = true;
      return;
    }

    if (results.length === 0) {
      dropdown.innerHTML = `<div class="search-empty">Sin resultados para <strong>"${query}"</strong>. Prueba con otra palabra.</div>`;
      dropdown.hidden = false;
      return;
    }

    results.forEach((art, i) => {
      const a = document.createElement('a');
      a.className = 'search-result';
      a.href = art.url;
      a.setAttribute('role', 'option');
      a.setAttribute('tabindex', '0');
      a.innerHTML = `
        <span class="search-result__cat">${art.cat}</span>
        <span class="search-result__title">${highlight(art.title, query)}</span>
      `;
      dropdown.appendChild(a);
    });

    dropdown.hidden = false;
  }

  // Input handler
  let debounceTimer;
  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const q = input.value;
    q ? clearBtn.classList.add('visible') : clearBtn.classList.remove('visible');
    debounceTimer = setTimeout(() => renderDropdown(q), 180);
  });

  // Clear button
  clearBtn.addEventListener('click', () => {
    input.value = '';
    clearBtn.classList.remove('visible');
    dropdown.hidden = true;
    input.focus();
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!input.closest('.search-wrapper').contains(e.target)) {
      dropdown.hidden = true;
    }
  });

  // Keyboard navigation
  input.addEventListener('keydown', e => {
    if (dropdown.hidden) return;
    const items = dropdown.querySelectorAll('.search-result');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      items[0].focus();
    } else if (e.key === 'Escape') {
      dropdown.hidden = true;
      input.focus();
    }
  });

  dropdown.addEventListener('keydown', e => {
    const items = [...dropdown.querySelectorAll('.search-result')];
    const idx = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      items[Math.min(idx + 1, items.length - 1)]?.focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (idx === 0) input.focus();
      else items[idx - 1]?.focus();
    } else if (e.key === 'Escape') {
      dropdown.hidden = true;
      input.focus();
    }
  });
});
