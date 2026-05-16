document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('cadastroModal');
    const btnNewTicket = document.querySelector('.btn-new-ticket');
    const btnClose = document.querySelector('.btn-close-modal');
    const btnCancel = document.querySelector('.btn-cancel');

    // Função para abrir o modal
    if (btnNewTicket) {
        btnNewTicket.addEventListener('click', function (e) {
            e.preventDefault();
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Impede scroll no fundo
        });
    }

    // Função para fechar o modal
    function closeModal() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    if (btnClose) {
        btnClose.addEventListener('click', closeModal);
    }

    if (btnCancel) {
        btnCancel.addEventListener('click', function (e) {
            e.preventDefault();
            closeModal();
        });
    }

    // Fechar ao clicar fora do conteúdo
    window.addEventListener('click', function (e) {
        if (e.target === modal) {
            closeModal();
        }
    });
});
