document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.urgency-btn');
    const input = document.getElementById('prioridade');

    buttons.forEach(btn => {
        btn.addEventListener('click', function () {
            buttons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            input.value = this.dataset.value;
        });
    });
});