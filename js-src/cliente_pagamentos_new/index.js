const elEventListener = require('../utils/elEventListener');
const {
  handleDisplayFaturas,
  handleDisplayTotalFaturas,
} = require('./eventHandlers');

const main = () => {
  const clienteEl = document.getElementById('id_cliente');
  const valorEl = document.getElementById('id_valor');
  const selectEl = document.getElementById('id_liquidar_faturas');

  elEventListener(selectEl, 'change', handleDisplayTotalFaturas);
  elEventListener(clienteEl, 'change', handleDisplayFaturas(selectEl));
  elEventListener(valorEl, 'change', handleDisplayFaturas(selectEl));

  clienteEl.dispatchEvent(new Event('change'));
  valorEl.dispatchEvent(new Event('change'));
  selectEl.dispatchEvent(new Event('change'));
};

main();
