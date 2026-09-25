(() => {
  'use strict';

  window.addEventListener('keydown', (event) => {
    const isMsgTextbox = event.target.dataset.qa === 'texty_input';
    if (!isMsgTextbox) {
      return;
    }

    const pressedCtrlEnter = event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && event.key === 'Enter';
    if (pressedCtrlEnter && event.isTrusted) {
      event.stopImmediatePropagation();
      event.preventDefault();
      const messageInput = event.target.closest('[data-message-input="true"]');
      const sendBtn =
        messageInput?.parentElement?.querySelector('button[data-qa="texty_send_button"]') ??
        document.querySelector('button[data-qa="texty_send_button"]');
      if (sendBtn) {
        sendBtn.click();
      }
    }
  }, true);

})();
