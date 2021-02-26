    /*
        *** requer que o link de voltar à lista tenha o id: "btn_voltar_para_lista" ***

        este script verifica se a ultima pagina visitada corresponde com
        a pagina indicada para no link para "voltar para a lista" e, caso
        corresponda, salva a url da ultima pagina visitada em uma variável
        que será verificada ao clicar no referido link.
        a ideia é garantir que o link redirecione o usuário pra lista na
        forma da ultima visualização que o usuário teve, ou seja, caso a
        lista estivesse filtrada, ao clicar no link o usuário deve ser
        redirecionado à lista filtrada!
    */

var pathname_lista_btn = null;

$(function(){
    pathname_lista_btn = new URL($('#btn_voltar_para_lista').prop('href')).pathname
    var pathname_ultima_url = null;

    if ( document.referrer != null && document.referrer.length > 0 ){
        pathname_ultima_url = new URL(document.referrer).pathname
    }
    if ( pathname_ultima_url === pathname_lista_btn ) {
        sessionStorage.setItem("url_voltar_para_lista", new URL(document.referrer));
    }
});

$('#btn_voltar_para_lista').on('click', function(event){
    event.preventDefault();
    var pathname_url_voltar = null;

    if ( sessionStorage.getItem("url_voltar_para_lista") != null ) {
        pathname_url_voltar = new URL(
            sessionStorage.getItem("url_voltar_para_lista")
        ).pathname
    }

    if (
        pathname_url_voltar != null &&
        ( pathname_url_voltar === pathname_lista_btn )
    ){
        window.location.href = sessionStorage.getItem("url_voltar_para_lista");
        sessionStorage.removeItem("url_voltar_para_lista");
    } else {
        window.location.href = $(this).prop('href');
    }

});
