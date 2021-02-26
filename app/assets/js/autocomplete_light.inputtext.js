// #staff_name search input placeholder
// https://gist.github.com/peterwegren/493c878df1aa2785ac7e9cefcc69f6d9
// adaptado para pegar o valor do item destacado e inserí-lo no input

function select2_highlighted() {
    var item = $('.select2-results__option--highlighted').text()

    if (item.indexOf('"') < 0 && item.indexOf('#') < 0) {  // previne que a opção de criar item seja selecionada.
        $('.select2-search--dropdown .select2-search__field').prop(
            'value',
            item
        ).focus();
    }
}

$(document).on('keydown.select2', function(e) {
    // somente busca os valores ao pressionar seta pra cima ou pra baixo ou ctrl
    if(e.keyCode == 38 || e.keyCode == 40 || e.keyCode == 17) {
        select2_highlighted()
    }
});
$('select').on('select2:open', function() {
    select2_highlighted();
});
