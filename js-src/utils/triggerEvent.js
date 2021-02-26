const triggerEvent = (element, event) => {
  if ('createEvent' in document) {
    const _event = document.createEvent('HTMLEvents');
    _event.initEvent(event, false, true);
    element.dispatchEvent(_event);
  } else {
    element.fireEvent(`on${event}`);
  }
};

module.exports = triggerEvent;
