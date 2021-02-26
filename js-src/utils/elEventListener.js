const elEventListener = (el, event, callback) => {
  if (el) {
    el.addEventListener(event, callback);
  }
};

module.exports = elEventListener;
