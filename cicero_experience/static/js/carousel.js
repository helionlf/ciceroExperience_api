// static/js/carousel.js
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    
    if (slides.length === 0) return; // Se não existir carrossel, sai
    
    let currentSlide = 0;
    
    function showSlide(n) {
        slides.forEach(slide => slide.style.opacity = '0');
        dots.forEach(dot => dot.classList.remove('active'));
        
        currentSlide = (n + slides.length) % slides.length;
        
        slides[currentSlide].style.opacity = '1';
        if (dots[currentSlide]) {
            dots[currentSlide].classList.add('active');
        }
    }
    
    // Navegação por dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showSlide(index);
        });
    });
    
    // Auto-play
    setInterval(() => {
        showSlide(currentSlide + 1);
    }, 5000);
});