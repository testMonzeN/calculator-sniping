document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.calculator-card, .history-card');
    let cardDelay = 0;
    cards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.5s ${index * 0.3}s ease-out forwards`;
        cardDelay = (index * 0.3) + 0.3;
        if (card.classList.contains('calculator-card')) {
            const formElements = card.querySelectorAll('.form-group, .buttons');
            formElements.forEach((el, elIndex) => {
                el.style.animation = `fadeInUp 0.5s ${cardDelay + (elIndex * 0.15)}s ease-out forwards`;
            });
        }
    });
    const tableRows = document.querySelectorAll('tbody tr');
    let tableDelay = cards.length > 0 ? 0.6 : 0;
    tableRows.forEach((row, index) => {
        row.style.animation = `fadeInUp 0.4s ${tableDelay + (index * 0.1)}s ease-out forwards`;
    });

    const eyeIcon = document.getElementById('eye-icon');
    const visitsNumber = document.getElementById('visits-number');
    
    if (eyeIcon && visitsNumber) {
        let isVisible = false;
        
        eyeIcon.addEventListener('click', function() {
            eyeIcon.classList.add('eye-icon-clicked');
            
            setTimeout(() => {
                eyeIcon.classList.remove('eye-icon-clicked');
            }, 300);
            
            if (isVisible) {
                visitsNumber.classList.remove('show');
                visitsNumber.classList.add('hide');
                isVisible = false;
            } else {
                visitsNumber.classList.remove('hide');
                visitsNumber.classList.add('show');
                isVisible = true;
            }
        });
    }
});
