const svg = document.getElementById('matrix-bg');
const width = window.innerWidth;
const height = window.innerHeight;
const fontSize = 14;
const columns = Math.floor(width / fontSize);
const rows = Math.floor(height / fontSize);
const characters = [];

function getRandomChar() {
return String.fromCharCode(33 + Math.floor(Math.random() * 94));
}

for (let i = 0; i < columns; i++) {
for (let j = 0; j < rows; j++) {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', i * fontSize);
    text.setAttribute('y', j * fontSize);
    text.setAttribute('font-size', `${fontSize}px`);
    text.setAttribute('font-family', 'IBM Plex Mono, monospace');
    text.setAttribute('fill', `rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1})`);
    text.textContent = getRandomChar();
    svg.appendChild(text);
    characters.push(text);
}
}

function updateMatrix() {
characters.forEach(char => {
    if (Math.random() < 0.03) { // 3% chance to change each character
    char.textContent = getRandomChar();
    char.setAttribute('fill', `rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1})`);
    }
});
requestAnimationFrame(updateMatrix);
}

updateMatrix();

// Update on resize
window.addEventListener('resize', () => location.reload());
