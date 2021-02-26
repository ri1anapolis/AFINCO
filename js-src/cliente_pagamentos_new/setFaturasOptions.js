const faturasStore = require('./faturasStore');
const { dateBR, realBR } = require('../utils/intlFormatters');

const setFaturasOptions = (selectEl) => {
  const { data } = faturasStore.getState();

  if (data) {
    selectEl.textContent = null;

    data.forEach((data) => {
      const { id, data_fatura, valor_fatura } = data;

      const optionEl = document.createElement('option');
      optionEl.value = id;
      optionEl.text = `${id} - ${dateBR(data_fatura)} - ${realBR(
        valor_fatura
      )}`;
      optionEl.setAttribute('data-valor', valor_fatura);

      selectEl.add(optionEl);
    });
  }
};

module.exports = setFaturasOptions;
