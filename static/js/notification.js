/**
 * Sistema de Notificações Toast
 * Gerencia exibição de mensagens de erro, sucesso, aviso e informação
 */

class NotificationManager {
  constructor() {
    this.container = null;
    this.notifications = [];
    this.init();
  }

  /**
   * Inicializa o container de notificações
   */
  init() {
    // Verifica se o container já existe
    this.container = document.getElementById('notification-container');
    
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'notification-container';
      this.container.className = 'notification-container';
      document.body.appendChild(this.container);
    }
  }

  /**
   * Cria e exibe uma notificação
   * @param {string} type - Tipo: 'error', 'warning', 'success', 'info'
   * @param {string} title - Título da notificação
   * @param {string} message - Mensagem da notificação
   * @param {number} duration - Tempo de exibição em ms (0 = sem auto-fechamento)
   * @param {function} onClose - Callback ao fechar
   */
  show(type = 'info', title = '', message = '', duration = 5000, onClose = null) {
    // Validar tipo
    const validTypes = ['error', 'warning', 'success', 'info'];
    if (!validTypes.includes(type)) {
      type = 'info';
    }

    // Criar elemento da notificação
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Definir ícone baseado no tipo
    const iconMap = {
      error: '✕',
      warning: '⚠',
      success: '✓',
      info: 'ℹ'
    };

    const icon = iconMap[type] || 'ℹ';

    // HTML da notificação
    notification.innerHTML = `
      <div class="notification-icon">${icon}</div>
      <div class="notification-content">
        ${title ? `<div class="notification-title">${this.escapeHtml(title)}</div>` : ''}
        ${message ? `<div class="notification-message">${this.escapeHtml(message)}</div>` : ''}
      </div>
      <button class="notification-close" aria-label="Fechar notificação">×</button>
      ${duration > 0 ? `<div class="notification-progress" style="animation: progressBar ${duration}ms linear forwards;"></div>` : ''}
    `;

    // Adicionar ao container
    this.container.appendChild(notification);
    this.notifications.push(notification);

    // Evento de clique no botão fechar
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
      this.close(notification, onClose);
    });

    // Auto-fechamento
    if (duration > 0) {
      setTimeout(() => {
        this.close(notification, onClose);
      }, duration);
    }

    return notification;
  }

  /**
   * Fecha uma notificação com animação
   * @param {HTMLElement} notification - Elemento da notificação
   * @param {function} onClose - Callback ao fechar
   */
  close(notification, onClose = null) {
    if (!notification || !notification.parentNode) return;

    // Adicionar classe de remoção para animar
    notification.classList.add('removing');

    // Remover após animação
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
      
      // Remover do array
      this.notifications = this.notifications.filter(n => n !== notification);

      // Executar callback
      if (typeof onClose === 'function') {
        onClose();
      }
    }, 400);
  }

  /**
   * Fecha todas as notificações
   */
  closeAll() {
    const notificationsToClose = [...this.notifications];
    notificationsToClose.forEach(notification => {
      this.close(notification);
    });
  }

  /**
   * Exibe notificação de erro
   */
  error(title = 'Erro', message = '', duration = 5000, onClose = null) {
    return this.show('error', title, message, duration, onClose);
  }

  /**
   * Exibe notificação de aviso
   */
  warning(title = 'Aviso', message = '', duration = 5000, onClose = null) {
    return this.show('warning', title, message, duration, onClose);
  }

  /**
   * Exibe notificação de sucesso
   */
  success(title = 'Sucesso', message = '', duration = 5000, onClose = null) {
    return this.show('success', title, message, duration, onClose);
  }

  /**
   * Exibe notificação de informação
   */
  info(title = 'Informação', message = '', duration = 5000, onClose = null) {
    return this.show('info', title, message, duration, onClose);
  }

  /**
   * Escapa caracteres HTML para evitar XSS
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Instância global do gerenciador de notificações
let notificationManager;

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
  notificationManager = new NotificationManager();
});

// Função auxiliar global para fácil acesso
window.showNotification = function(type = 'info', title = '', message = '', duration = 5000, onClose = null) {
  if (!notificationManager) {
    notificationManager = new NotificationManager();
  }
  return notificationManager.show(type, title, message, duration, onClose);
};

// Funções auxiliares específicas
window.showError = function(title = 'Erro', message = '', duration = 5000, onClose = null) {
  return window.showNotification('error', title, message, duration, onClose);
};

window.showWarning = function(title = 'Aviso', message = '', duration = 5000, onClose = null) {
  return window.showNotification('warning', title, message, duration, onClose);
};

window.showSuccess = function(title = 'Sucesso', message = '', duration = 5000, onClose = null) {
  return window.showNotification('success', title, message, duration, onClose);
};

window.showInfo = function(title = 'Informação', message = '', duration = 5000, onClose = null) {
  return window.showNotification('info', title, message, duration, onClose);
};
