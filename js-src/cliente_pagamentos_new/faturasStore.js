const createStore = require('../utils/simpleRedux');

const faturasReducer = (state = {}, action) => {
  switch (action.type) {
    case 'UPDATE_STATE':
      return { ...state, ...action.state };
    default:
      return state;
  }
};

const faturasStore = createStore(faturasReducer);

module.exports = faturasStore;
