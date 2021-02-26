// configurações padrão do projeto para mascaras js de campos de telefone

var telefone_format = function (val) {
    return val.replace(/\D/g, '').length === 11 ? '(00) 0 0000-0000' : '(00) 0000-00009';
},
telefone_opts = {
    onKeyPress: function(val, e, field, options) {
        field.mask(telefone_format.apply({}, arguments), options);
    }
};

var money_format = 'Z#.Z#Z#Z#.Z#Z#Z#.Z#Z#0,00'
var money_opts = {
    reverse: true,
    translation: {
        'Z': {
            pattern: /-/, optional: true
        }
    }
}