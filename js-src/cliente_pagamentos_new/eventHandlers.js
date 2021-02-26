const faturasStore = require('./faturasStore');
const getFaturas = require('./getFaturas');
const setFaturasOptions = require('./setFaturasOptions');
const updateFaturasTotalValueLabel = require('./updateFaturasTotalValueLabel');

const calcTotalFaturas = (selectEl) => {
  const optionsEls = selectEl.querySelectorAll('option:checked');

  const reducer = (total, el) =>
    total + parseFloat(el.getAttribute('data-valor'));

  return Array.from(optionsEls).reduce(reducer, 0);
};

const handleDisplayFaturas = (targetEl) => async (event) => {
  const sourceEl = event.currentTarget;

  const newState = {};
  newState[sourceEl.id] = sourceEl.value || null;
  newState.valor_total_faturas = 0;
  faturasStore.dispatch({ type: 'UPDATE_STATE', state: newState });

  await getFaturas();
  setFaturasOptions(targetEl);
  updateFaturasTotalValueLabel();
};

const handleDisplayTotalFaturas = (event) => {
  const selectEl = event.currentTarget;
  const valor_faturas = calcTotalFaturas(selectEl);

  updateFaturasTotalValueLabel(valor_faturas);
};

module.exports = {
  handleDisplayFaturas,
  handleDisplayTotalFaturas,
};
