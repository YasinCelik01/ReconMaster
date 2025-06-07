// Loading göstergesi için fonksiyon
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

// Matrix rain effect
const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');

// Optimize edilmiş ayarlar
const FONT_SIZE = 20; // Daha büyük font boyutu
const ANIMATION_INTERVAL = 100; // Daha yavaş animasyon (100ms)
const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'; // Daha az karakter
const DROP_CHANCE = 0.98; // Daha az sıklıkta yeni damla oluşturma

// Canvas boyutlarını ayarla
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    // Sütun sayısını azalt
    columns = Math.floor(canvas.width / FONT_SIZE);
    // Drops array'ini yeniden oluştur
    drops = new Array(columns).fill(1);
}
resizeCanvas();

const charArray = CHARS.split('');
let animationFrameId = null;
let isPageVisible = true;

// Sayfa görünürlüğünü kontrol et
document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
    if (isPageVisible) {
        startAnimation();
    } else {
        stopAnimation();
    }
});

function startAnimation() {
    if (!animationFrameId) {
        draw();
    }
}

function stopAnimation() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

function draw() {
    if (!isPageVisible) return;

    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0F0';
    ctx.font = FONT_SIZE + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        // Rastgele karakter seç
        const text = charArray[Math.floor(Math.random() * charArray.length)];
        ctx.fillText(text, i * FONT_SIZE, drops[i] * FONT_SIZE);

        // Damlaları sıfırla
        if (drops[i] * FONT_SIZE > canvas.height && Math.random() > DROP_CHANCE) {
            drops[i] = 0;
        }
        drops[i]++;
    }

    animationFrameId = requestAnimationFrame(() => {
        setTimeout(draw, ANIMATION_INTERVAL);
    });
}

// Sayfa yüklendiğinde animasyonu başlat
startAnimation();

// Pencere yeniden boyutlandırıldığında
window.addEventListener('resize', () => {
    resizeCanvas();
});

function showLoading() {
    document.getElementById('loading').style.display = 'block';
} 