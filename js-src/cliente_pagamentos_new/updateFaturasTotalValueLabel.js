const faturasStore = require('./faturasStore');
const { realBR } = require('../utils/intlFormatters');

const isFaturasTotalValueValid = (valor_faturas) => {
  const { id_valor } = faturasStore.getState();
  const valor_pagamento = parseFloat(id_valor);

  // if there's no value set for payment, let it go
  if (valor_pagamento === NaN || valor_pagamento <= 0) return true;

  return valor_faturas > valor_pagamento ? false : true;
};

const updateFaturasTotalValueLabel = (valor_faturas = 0) => {
  const spanId = 'valor_total_faturas';
  const existingLabel = document.getElementById(spanId);

  if (existingLabel) existingLabel.remove();

  if (valor_faturas) {
    const is_valor_valid = isFaturasTotalValueValid(valor_faturas);

    const valorEl = document.createElement('span');
    valorEl.id = spanId;
    valorEl.textContent = `(${realBR(valor_faturas)})`;
    valorEl.classList.add('ml-2');
    valorEl.classList.add(is_valor_valid ? 'text-secondary' : 'text-danger');

    const selectLabelEl = document.querySelector(
      '#div_id_liquidar_faturas label'
    );
    selectLabelEl.appendChild(valorEl);
  }
};

module.exports = updateFaturasTotalValueLabel;
