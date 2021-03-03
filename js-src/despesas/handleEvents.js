const handleClickEvent = (selectors, keys) => (event) => {
  const pseudoSelectEl = event.target;
  const elOpenedSearchBox = [
    pseudoSelectEl.hasAttribute('aria-owns'),
    pseudoSelectEl.parentElement.hasAttribute('aria-owns'),
  ];
  if (elOpenedSearchBox.some((el) => !!el)) {
    const pseudoInputEl = document.querySelector(selectors.pseudoInputEl);
    pseudoInputEl.addEventListener(
      'keydown',
      handleKeyDownEvent(keys, selectors.pseudoItemListEl, pseudoInputEl)
    );
  }
};

const handleKeyDownEvent = (keys, itemSelector, targetEl) => (event) => {
  const key = event.key;
  if (keys.includes(key)) {
    const pseudoItemListEl = document.querySelector(itemSelector);
    targetEl.value = pseudoItemListEl.textContent;
  }
};

module.exports = { handleClickEvent, handleKeyDownEvent };
