document.documentElement.classList.add('js');

const menuButton = document.querySelector('[data-menu-button]');
const navigation = document.querySelector('#site-navigation');

function closeMenu() {
  if (!menuButton || !navigation) return;
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('is-open');
}

menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  navigation.classList.toggle('is-open', !isOpen);
});
navigation?.addEventListener('click', (event) => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuButton.focus();
  }
});
document.addEventListener('click', (event) => {
  if (!event.target.closest('.site-header')) closeMenu();
});
window.matchMedia('(min-width: 761px)').addEventListener('change', closeMenu);

const searchInput = document.querySelector('[data-post-search]');
const postCards = [...document.querySelectorAll('[data-search-text]')];
const searchEmpty = document.querySelector('[data-search-empty]');
searchInput?.addEventListener('input', () => {
  const query = searchInput.value.toLocaleLowerCase().trim();
  let visibleCount = 0;
  for (const card of postCards) {
    const matches = card.dataset.searchText.includes(query);
    card.hidden = !matches;
    if (matches) visibleCount++;
  }
  if (searchEmpty) searchEmpty.hidden = visibleCount > 0;
});
