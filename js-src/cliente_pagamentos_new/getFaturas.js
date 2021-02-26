const superagent = require('superagent');
require('superagent-cache')(superagent);
const faturasStore = require('./faturasStore');

const getFaturas = async () => {
  const { id_cliente, id_valor } = faturasStore.getState();
  const url = `/clientes/faturas/get`;
  const query = { cliente_id: id_cliente, valor_fatura: id_valor };

  if (id_cliente) {
    try {
      const response = await superagent.get(url).query(query);

      if (response.status === 200) {
        faturasStore.dispatch({
          type: 'UPDATE_STATE',
          state: { data: response.body },
        });
      } else {
        throw Error(response.statusText);
      }
    } catch (error) {
      console.error(`Algo deu errado ao buscar faturas do cliente:`);
      console.error(error);
    }
  }

  return null;
};

module.exports = getFaturas;
