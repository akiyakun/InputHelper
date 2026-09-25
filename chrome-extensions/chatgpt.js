(() => {
  'use strict';

  console.info('[CustomEnter] ChatGPT handler loaded (1.3.1)');

  window.addEventListener('keydown', (event) => {
    // The event target may be a paragraph inside the contenteditable editor.
    const editor = event.target instanceof Element
      ? event.target.closest([
        '#prompt-textarea',
        'form[data-chatgpt-composer] [contenteditable="true"][data-composer-markdown]',
      ].join(', '))
      : null;
    if (!editor || (event.key !== 'Enter' && event.keyCode !== 13)) {
      return;
    }

    // Preserve IME confirmation without letting ChatGPT submit the message.
    if (event.isComposing || event.keyCode === 229) {
      event.stopImmediatePropagation();
      return;
    }

    if (event.shiftKey || event.altKey || event.metaKey) {
      return;
    }

    event.stopImmediatePropagation();
    event.preventDefault();

    if (event.ctrlKey) {
      if (event.repeat) return;

      // Only match send buttons: the composer also contains a stop button
      // while a response is being generated.
      const scope = editor.closest('form') || document;
      const sendButton = scope.querySelector([
        'button[data-testid="send-button"]',
        'button[aria-label="Send prompt"]',
        'button[aria-label="Send message"]',
        'button[aria-label="Send"]',
        'button[aria-label="送信"]',
        'button[aria-label="プロンプトを送信"]',
        'button[aria-label="メッセージを送信"]',
      ].join(', '));
      if (sendButton && !sendButton.disabled &&
          sendButton.getAttribute('aria-disabled') !== 'true') {
        sendButton.click();
      }
      return;
    }

    // Let the rich-text editor handle its own Shift+Enter command. Include
    // legacy key codes because editor keymaps can still depend on them.
    const unhandled = editor.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      shiftKey: true,
      bubbles: true,
      cancelable: true,
      composed: true,
    }));

    // Synthetic events have no native editing action. If the editor did not
    // consume Shift+Enter, explicitly insert a line break at the selection.
    if (unhandled) {
      if (editor instanceof HTMLTextAreaElement) {
        editor.setRangeText('\n', editor.selectionStart, editor.selectionEnd, 'end');
        editor.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        document.execCommand('insertLineBreak');
      }
    }
  }, true);

})();
