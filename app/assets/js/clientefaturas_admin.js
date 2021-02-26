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

    function hide_delete_link(){
        $('a.deletelink').each(function(){
            $(this).hide();
        })
    }

    function hide_save_links(){
        $('input[name="_addanother"]').each(function(){
            $(this).hide();
        })
        $('input[name="_save"]').each(function(){
            $(this).hide();
        })
    }

    $(document).ready(function(){

        if ( $('input[type="checkbox"]#id_liquidado').attr('disabled') ){
            hide_delete_link();
        }

        if ( ! $('select#id_cliente').attr('disabled') ){
            hide_save_links();
        }
    })

}(contabil.jQuery));
