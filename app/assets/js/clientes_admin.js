var contabil = contabil || {};
contabil.jQuery = jQuery;

(function($) {
    'use strict';

    function hide_div(){
        var div_tipo_doc = {
            'PJ': 'field-cnpj',
            'PF': 'field-cpf',
            'EX': 'field-estrangeiro'
        }

        var selected = $("#id_tipo_documento")
        selected.find('option').each(function(){
            var option = $(this)
            if (option.val() == selected.val()){
                $('.'  + div_tipo_doc[option.val()]).show();
            } else {
                $('.' + div_tipo_doc[option.val()]).hide();
            }
        });
    }

    $(document).ready(function() {

        hide_div();

        $("#id_tipo_documento").change(function(){
            hide_div();
        });
    });

}(contabil.jQuery));
