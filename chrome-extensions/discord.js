(() => {
  'use strict';

  const app = document.querySelector('#app-mount');
  const useCapture = true;
  app.addEventListener('keydown', (event) => {
    const isMsgTextbox = event.target.role === 'textbox' && event.target.ariaMultiline;
    if (isMsgTextbox === false) {
      return;
    }

    const pressedShiftEnter = event.shiftKey && event.key === 'Enter';
    if (pressedShiftEnter) {
      return;
    }

    const pressedEnter = event.altKey === false && event.ctrlKey === false && event.key === 'Enter';
    if (pressedEnter) {
      event.stopPropagation();
    }
  }, useCapture);

})();
