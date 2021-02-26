const dateBR = (date) => {
  return new Intl.DateTimeFormat('pt-BR').format(
    date instanceof Date ? date : new Date(date)
  );
};

const realBR = (value) => {
  return parseFloat(value) === NaN
    ? value
    : new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(value);
};

module.exports = {
  dateBR,
  realBR,
};
