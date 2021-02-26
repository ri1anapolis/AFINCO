const toBR = valor => {
    return parseFloat(valor).toLocaleString('pt-BR',{
        minimumFractionDigits:2,
        maximumFractionDigits:2
    })
}
