document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  form.addEventListener('submit', showLoading);
});

function showLoading() {
  document.getElementById('loading').style.display = 'block';
}
