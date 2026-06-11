document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.urgency-btn');
    const input = document.querySelector('input[name="urgencia"]');
    const defaultUrgency = 'NO';

    if (!input || buttons.length === 0) {
        return;
    }

    function setActiveButton(value) {
        buttons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.value === value);
        });
    }

    if (!input.value) {
        input.value = defaultUrgency;
    }

    setActiveButton(input.value);

    buttons.forEach(btn => {
        btn.addEventListener('click', function () {
            input.value = this.dataset.value;
            setActiveButton(input.value);
        });
    });
});
