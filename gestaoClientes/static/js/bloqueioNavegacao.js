/**
 * LÓGICA DE BLOQUEIO DE NAVEGAÇÃO
 * Use este arquivo apenas nas páginas onde o bloqueio é obrigatório.
 */
document.addEventListener("DOMContentLoaded", function () {
  const navLinks = document.querySelectorAll('.nav-link, .sidebar a');
  navLinks.forEach(link => {
    link.style.pointerEvents = 'none';
    link.style.opacity = '0.5';
    link.style.cursor = 'not-allowed';
    link.removeAttribute('href');
  });

  history.pushState(null, null, location.href);
  window.onpopstate = function () {
    history.go(1);
  };
});