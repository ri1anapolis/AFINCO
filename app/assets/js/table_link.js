/*
REQUER QUE A TABELA TENHA A CLASSE "table_link"

Este script visa possibilitar que cada linha da tabela seja um link que
será invocado via click, direcionando o usuário para o endereço indicado
no atributo data-href e utilizando o frame indicado no atributo data-target,
ambos na linha da tabela "tr".

Uma vez omitido o atribuito data-target, será usado "_self" (mesma janela)
por padrão!
*/

var $table_item = $('.table_link tr[data-href]')

$(function(){

    var target = '_self'

    $table_item.each(function(){

        if (typeof $(this).attr('data-target') !== 'undefined') {
            target = $(this).attr('data-target');
        }

        $(this).css('cursor','pointer').click( function(){
            window.open($(this).attr('data-href'), target);
        });
    });

});