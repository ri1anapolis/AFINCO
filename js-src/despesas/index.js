const documentReady = require('./documentReady');
const { handleClickEvent } = require('./handleEvents');

const copyValueActionKeys = ['ArrowRight', 'ArrowLeft'];
const selectors = {
  pseudoSelectEl:
    'span.selection>span.select2-selection>span#select2-id_identificacao-container',
  pseudoInputEl: 'span.select2-search--dropdown>input.select2-search__field',
  pseudoItemListEl: 'li.select2-results__option--highlighted',
};

const main = async (selectors, keys) => {
  await documentReady();
  const el = document.querySelector(selectors.pseudoSelectEl);

  el.addEventListener('click', handleClickEvent(selectors, keys));
  el.parentElement.addEventListener('click', handleClickEvent(selectors, keys));
};

main(selectors, copyValueActionKeys);
