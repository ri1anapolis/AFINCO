var contabil = contabil || {};
contabil.jQuery = jQuery;

(function($) {
    'use strict';    
    
    /*
    script tentar impedir edição de registros que tenham sido inseridos/vinculados
    a fechamentos de caixa, visando a integridade das informações do fechamento de
    caixa.

    a intenção é identificar se o registro é vinculado a algum fechamento de caixa.
    para tanto testamos os valores da variável caixa!

    uma vez identificado o vinculamento, desabilita-se os campos e links que permitam
    a edição do registro, com exceção dos checkbox "liquidado" e "contabilizar", que
    devem ser editados posteriormente pelo contador.
    */

    function disable_inputs(){
        var input_type = ['text', 'number', 'date']

        $.each(input_type, function(i, itype){
            $(':input[type=' + itype + ']').each(function() {
                $(this).attr('disabled', true);
            })
        })
        $('select').each(function() {
            $(this).attr('disabled', true);
        })
    }

    function hide_action_links(){
        setTimeout(function(){
            $('.datetimeshortcuts').each(function(){
                $(this).remove();
            })
        }, 100)
        $('.datetimeshortcuts').each(function(){
            $(this).remove();
        })
        $('a.related-widget-wrapper-link').each(function(){
            $(this).hide();
        })
        $('a.deletelink').each(function(){
            $(this).hide();
        })
    }

    $(document).ready(function(){

        var caixa = $('div.field-caixa div div.readonly').text();
        if ( caixa && caixa != null && caixa != '-' ){
            disable_inputs();
            hide_action_links();
        }
    })

}(contabil.jQuery));
