/* eslint-disable no-console */
/* VARIÁVEIS PARA FUNÇÕES DE DEPÓSITOS */
let f_caixa_id, guiche_id, usuario_id;
let search_dep_obj_tmp; // busca do autocomplete pelos depositos
let selected_cliente_id; // busca do autocomplete pelos clientes
let selected_cliente_saldo; // salva temporariamente o saldo do cliente
let depositos = [];
let cheques = [];
let comprovantes = [];
let serv_clientes = [];
//variáveis para indicar itens removidos
let depositos_rem = [];
let cheques_rem = [];
let comprovantes_rem = [];
let serv_clientes_rem = [];

/* valida todos os inputs number para permitir APENAS NÚMEROS POSITIVOS */
$(document).on(
  'input propertychange paste',
  ':input[type="number"]',
  function () {
    if (isNaN(parseFloat($(this).val()))) {
      $(this).prop('value', '');
    }
  }
);

/* FUNÇÃO PARA CRIAR IDS ÚNICOS */
const ID = () => `_${Math.random().toString(36).substr(2, 9)}`;

/* RECEBE OS DADOS DO AJAX E CONFIGURA NO BROWSER */
function getFechamentoCaixaResult(data) {
  if (data.erro == null) {
    if (data.status_busca) {
      clean_f_caixa();
      console.log('Foi realizada uma busca por um fechamento de caixa.');
    }
    let t0 = performance.now();
    if (data['id'] != null) {
      f_caixa_id = data['id'];
      console.log(`Atribuído o ID: ${f_caixa_id}`);
    } else {
      console.log('Não foi retornado o ID do fechamento de caixa.');
    }

    if (data['guiche_nome'].length > 0) {
      guiche_id = data['guiche_id'];
      usuario_id = data['usuario_id'];
      console.log(`guiche_id: ${guiche_id} , usuario_id: ${usuario_id}`);

      let data_format = data['data'].split('-');
      data_format = `${data_format[2]}/${data_format[1]}/${data_format[0]}`;
      let f_caixa_desc = `${data['guiche_nome']} - ${data['usuario_login']} [ ${data_format} ]`;
      $('#f_caixa_desc').text(f_caixa_desc);
    } else {
      $('#f_caixa_desc').text('falhou');
    }

    if (data['saldo_inicial'] != null) {
      $('#saldo_inicial').html(parseFloat(data['saldo_inicial']).toFixed(2));
      valor_total_entrada();
    }

    if (data['valor_dinheiro_cofre'] != null) {
      $('#valor_dinheiro_cofre').prop(
        'value',
        data['valor_dinheiro_cofre'].toFixed(2)
      );
      valor_total_cofre();
    }

    if (data['valor_desp_futuras'] != null) {
      $('#valor_desp_futuras').prop(
        'value',
        data['valor_desp_futuras'].toFixed(2)
      );
      $('#valor_desp_futuras_indicador').html(
        parseFloat(data['valor_desp_futuras']).toFixed(2)
      );
      valor_total_cofre();
    }

    for (let moeda in data) {
      if (moeda.match('^qtd_moeda')) {
        $(`#${moeda}`).prop('value', data[moeda]);

        let obj_multiplier = $(`#${moeda}`).data('multiplier');
        $(`#val_${moeda}`).prop('value', data[moeda] * obj_multiplier);

        valor_dinheiro_caixa();
      }
    }

    if (data.valor_cartoes != null) {
      document.querySelector('span#valor_cartoes').innerHTML = parseFloat(
        data.valor_cartoes
      ).toFixed(2);
      cartoesRegistros(
        JSON.stringify(data.registros_cartoes),
        '/cartoes/reg/',
        '_blank',
        false
      );
      valor_comprovantes();
    }

    if (data.depositos != null) {
      for (let i = 0; i < data.depositos.length; i++) {
        add_card_item(
          'deposito',
          data.depositos[i]['id'],
          data.depositos[i]['valor_utilizado'],
          data.depositos[i]['identificacao'],
          set_obj_var('deposito', data.depositos[i])
        );

        valor_depositos();
      }
    }

    if (data.cheques != null) {
      for (let i = 0; i < data.cheques.length; i++) {
        add_card_item(
          'cheque',
          data.cheques[i]['id'],
          parseFloat(data.cheques[i]['valor']),
          `${data.cheques[i]['banco']} - ${data.cheques[i]['numero']}`,
          set_obj_var('cheque', data.cheques[i])
        );
        valor_cheques();
      }
    }

    if (data.comprovantes != null) {
      for (let i = 0; i < data.comprovantes.length; i++) {
        add_card_item(
          'comprovante',
          data.comprovantes[i]['id'],
          data.comprovantes[i]['valor'],
          data.comprovantes[i]['identificacao'],
          set_obj_var('comprovante', data.comprovantes[i])
        );
        valor_comprovantes();
      }
    }

    if (data.clientes_servicos != null) {
      for (let i = 0; i < data.clientes_servicos.length; i++) {
        add_card_item(
          'serv_cliente',
          data.clientes_servicos[i]['id'],
          data.clientes_servicos[i]['valor'],
          data.clientes_servicos[i]['tipo_protocolo'] +
            `.${data.clientes_servicos[i]['protocolo']}` +
            ` - ${data.clientes_servicos[i]['cliente_nome']}`,
          set_obj_var('serv_cliente', data.clientes_servicos[i])
        );
        valor_serv_cliente();
      }
    }

    if (data.valor_desp_futuras != null) {
      if (!isNaN(parseFloat(data.valor_desp_futuras))) {
        $('#valor_desp_futuras').prop(
          'value',
          parseFloat(data.valor_desp_futuras)
        );
        valor_total_entrada();
      }
    }

    if (data['valor_total_register'] == null) {
      if (data['valor_total_entrada'] != null && data['valor_quebra'] != null) {
        const valor = (
          parseFloat(data['valor_total_entrada']) -
          parseFloat(data['valor_quebra'])
        ).toFixed(2);

        $('#valor_total_register').prop('value', valor);
        valor_quebra();
      }
    } else {
      $('#valor_total_register').prop(
        'value',
        parseFloat(data['valor_total_register']).toFixed(2)
      );
      $('#valor_total_register').prop('disabled', true);
      valor_quebra();
    }

    set_historico(data['historico'], data['usuario_mod'], data['data_mod_reg']);

    if (data['qtd_devolucoes'] != null) {
      $('#qtd_devolucoes').prop('value', data['qtd_devolucoes']);
    }

    if (data['observacoes'] != null) {
      $('#observacoes').prop('value', data['observacoes']);
    }

    if (data['status_busca']) {
      const notasRodapeMessagesEl = document.getElementById(
        'notas_rodape_messages'
      );
      notasRodapeMessagesEl.innerHTML = '';
      lock_fcaixa();
      if (!data['fechado']) {
        const msg =
          'Este fechamento de caixa ainda encontra-se em aberto! ' +
          'Não será possível consolidar o caixa até que o caixa esteja fechado!';
        const dangerMessageText = document.createTextNode(msg);
        const dangerMessageEl = document.createElement('p');
        dangerMessageEl.classList.add('text-danger');
        dangerMessageEl.appendChild(dangerMessageText);
        notasRodapeMessagesEl.appendChild(dangerMessageEl);
      }
      if (data['fechado'] && !data['consolidado']) {
        setTimeout(function () {
          $('#btn_consolidar_fcaixa').prop('disabled', false).show('fast');
        }, 200);
      }
    } else {
      // VERIFICA SE É O CASO DE SER UM CAIXA ANTERIOR AINDA EM ABERTO
      let LocalDate = JSJoda.LocalDate;
      let dfc = LocalDate.parse(data['data']).atStartOfDay();
      let dtd = LocalDate.now().atStartOfDay();

      if (dfc.isBefore(dtd)) {
        alerta = `Identificado fechamento de caixa em aberto em data anterior à atual!`;
        alerta += `\nÉ necessário realizar o fechamento do caixa pendente antes de abrir`;
        alerta += ' novo caixa.';
        $('#f_caixa_desc').removeClass('text-muted').addClass('text-danger');
        console.log(alerta);
        alert(alerta);
      }

      if (data['fechado'] || data['consolidado']) {
        $('.caixa_editable').prop('disabled', 'true');
      } else {
        if (data['id'] == null) {
          $('#saldo_inicial').dblclick(function () {
            let saldo_inicial = prompt(
              'Insira o novo valor do saldo inicial do caixa:',
              '0.00'
            );
            if (!isNaN(parseFloat(saldo_inicial))) {
              $('#saldo_inicial').html(parseFloat(saldo_inicial).toFixed(2));
            }
            valor_total_entrada();
          });
        }

        $('#btn_fechar_fcaixa').show();
        $('#btn_salvar_fcaixa')
          .removeClass('border_curve')
          .prop('disabled', false);
      }

      if (data['fechado'] && !data['consolidado']) {
        $('#btn_abrir_fcaixa').css('display', 'block');
        $('#btn_consolidar_fcaixa')
          .prop('disabled', false)
          .css('display', 'block');
      } else if (data['consolidado']) {
        $('#btn_consolidar_fcaixa').css('display', 'block');
        $('#btn_salvar_fcaixa').css('display', 'none');
        $('#btn_fechar_fcaixa').css('display', 'none');
      }
    }

    let t1 = performance.now();
    console.log(
      'Preenchimento da tela de fechamento de caixa realizado em ' +
        `${t1 - t0} milissegundos.`
    );

    /* VALIDAÇÕES DOS VALORES DO CAIXA */
    setTimeout(function () {
      valida_caixa(data);
    }, 170);
  } else {
    clean_f_caixa();
    lock_fcaixa();
    console.log(`Houveram erros ao buscar os dados:\n${data['erro']}`);
    setTimeout(function () {
      alert(`Houve uma falha na solicitação:\n${data['erro']}`);
    }, 1000);
  }

  /* VALIDA OS VALORES DO CAIXA */
  function valida_caixa(data_f_caixa) {
    let itens = '';
    let erros = 0;
    // depositos
    if (
      data_f_caixa['valor_depositos'] != null &&
      $('#valor_depositos').val() != data_f_caixa['valor_depositos']
    ) {
      console.log(
        '[ERRO] O valor dos depositos informado pelo servidor é: R$ ' +
          data_f_caixa['valor_depositos']
      );
      itens += ' depositos,';
      erros += 1;
    }
    // cheques
    if (
      //verifica se o caixa está fechado ou consolidado
      ((data['fechado'] != null && data['fechado']) ||
        (data['consolidado'] != null && data['consolidado']) ||
        (data['status_busca'] != null && data['status_busca'])) &&
      data_f_caixa['valor_cheques'] != null &&
      $('#valor_cheques').val() != data['valor_cheques']
    ) {
      console.log(
        '[ERRO] O valor dos cheques informado pelo servidor é: R$ ' +
          data_f_caixa['valor_cheques']
      );
      console.log(
        `fechado ${data['fechado']} consolidado ${data['consolidado']} ` +
          `status_busca ${data['status_busca']}`
      );
      itens += ' cheques,';
      erros += 1;
    }
    // comprovantes
    if (
      //verifica se o caixa está fechado ou consolidado
      ((data['fechado'] != null && data['fechado']) ||
        (data['consolidado'] != null && data['consolidado']) ||
        (data['status_busca'] != null && data['status_busca'])) &&
      data_f_caixa['valor_comprovantes'] != null &&
      $('#valor_comprovantes').val() != data_f_caixa['valor_comprovantes']
    ) {
      console.log(
        '[ERRO] O valor dos comprovantes informado pelo servidor é: R$ ' +
          data_f_caixa['valor_comprovantes']
      );
      itens += ' comprovantes,';
      erros += 1;
    }
    // serviços de clientes / pagamentos posteriores
    if (
      //verifica se o caixa está fechado ou consolidado
      ((data['fechado'] != null && data['fechado']) ||
        (data['consolidado'] != null && data['consolidado']) ||
        (data['status_busca'] != null && data['status_busca'])) &&
      data_f_caixa['valor_total_servicos_clientes'] != null &&
      data_f_caixa['valor_total_servicos_clientes'] > 0 &&
      parseFloat($('#valor_serv_cliente').text()).toFixed(2) !=
        data_f_caixa['valor_total_servicos_clientes']
    ) {
      console.log(
        '[ERRO] O valor dos pagamentos posteriores informado pelo servidor é: R$ ' +
          `${data_f_caixa['valor_total_servicos_clientes']}. ` +
          `O valor calculado é: ${parseFloat(
            $('#valor_serv_cliente').text()
          ).toFixed(2)}`
      );
      itens += ' pagamentos posteriores,';
      erros += 1;
    }
    // dinheiro no caixa
    if (
      data_f_caixa['valor_dinheiro_caixa'] != null &&
      data_f_caixa['valor_dinheiro_caixa'] > 0 &&
      parseFloat($('#valor_dinheiro_caixa').text()).toFixed(2) !=
        data_f_caixa['valor_dinheiro_caixa']
    ) {
      console.log(
        '[ERRO] O valor do dinheiro em caixa informado pelo servidor é: R$ ' +
          data_f_caixa['valor_dinheiro_caixa']
      );
      itens += ' dinheiro em caixa,';
      erros += 1;
    }

    // verifica se há erros e chama os alerta
    if (erros > 0) {
      lock_fcaixa();
      alert_caixa(itens);
    } else {
      // entrada (sem interferência do total register)
      if (
        //verifica se o caixa está fechado ou consolidado
        ((data['fechado'] != null && data['fechado']) ||
          (data['consolidado'] != null && data['consolidado']) ||
          (data['status_busca'] != null && data['status_busca'])) &&
        data_f_caixa['valor_total_entrada'] != null &&
        $('#valor_total_entrada').val() != data_f_caixa['valor_total_entrada']
      ) {
        console.log(
          '[ERRO] O valor do total de entrada informado pelo servidor é: R$ ' +
            data_f_caixa['valor_total_entrada']
        );
        lock_fcaixa();
        alert_caixa('o total de entrada');
      }

      // total
      if (
        //verifica se o caixa está fechado ou consolidado
        ((data['fechado'] != null && data['fechado']) ||
          (data['consolidado'] != null && data['consolidado']) ||
          (data['status_busca'] != null && data['status_busca'])) && //e se o total mudou
        data_f_caixa['valor_quebra'] != null &&
        $('#valor_quebra').val() != data_f_caixa['valor_quebra']
      ) {
        console.log(
          '[ERRO] O valor do total geral do caixa informado pelo servidor é: R$ ' +
            data_f_caixa['valor_quebra']
        );
        alert_caixa('o valor de quebra de caixa');
      }
    }
  }

  /* FUNÇÃO DE ALERTAS PARA VALIDAÇÕES DOS VALORES DO CAIXA */
  function alert_caixa(itens) {
    msg = `FOI DETECTADO UM ERRO!\n\nHá uma diferença de valores referente a ${itens}`;
    msg += ` entre o que foi informado pelo servidor e o que foi calculado localmente.`;
    msg += `\n\nAtualize a página e verifique se o problema volta a ocorrer.\n'`;
    msg += '\nCaso o problema persista procure ajuda do suporte técnico!';

    console.log(msg);
    alert(msg);
  }

  // preenche os selects de busca
  if (
    data['list_guiches_busca'] != null &&
    data['list_usuarios_busca'] != null
  ) {
    if (
      data['list_guiches_busca'].length > 0 &&
      data['list_usuarios_busca'].length > 0
    ) {
      $('#busca_guiche').empty().append('<option value="">---</option>');
      $('#busca_usuario').empty().append('<option value="">---</option>');
      for (let i = 0; i < data['list_guiches_busca'].length; i++) {
        $('#busca_guiche').append(
          `<option value="${data['list_guiches_busca'][i]['id']}">` +
            `${data['list_guiches_busca'][i]['nome']}</option>`
        );
      }
      for (let i = 0; i < data['list_usuarios_busca'].length; i++) {
        $('#busca_usuario').append(
          `<option value="${data['list_usuarios_busca'][i]['id']}">` +
            `${data['list_usuarios_busca'][i]['username']}</option>`
        );
      }
    }
  }
}

function set_historico(historico, usuario_mod, data_mod_reg) {
  if (historico != null) {
    if ($('#show_historico').find('textarea').length) {
      $('#show_historico').find('textarea').val(historico);
    } else {
      $('#show_historico').append(
        '<div class="clearfix">' +
          '<textarea class="form-control form-control-sm float-right" disabled="true">' +
          `${historico}</textarea></div>`
      );
    }
  }

  if (usuario_mod != null) {
    if ($('#show_historico').find('small').length) {
      $('#show_historico')
        .find('small')
        .html(`Última modificação feita por ${usuario_mod} em ${data_mod_reg}`);
    } else {
      $('#show_historico').append(
        `<small class="text-muted">` +
          `Última modificação feita por ${usuario_mod} em ${data_mod_reg}` +
          `</small>`
      );
    }
  }
}

/* FUNÇÃO PARA VALIDAR CAMPOS DE BUSCA */
$(document).on('change', '.busca_validation_field', function (event) {
  let busca_data = $('#busca_data').val().length;
  let busca_guiche = $('#busca_guiche option:selected').val().length;
  let busca_usuario = $('#busca_usuario option:selected').val().length;
  let btn_busca = $('#btn_busca');

  if (
    (busca_data > 0 && busca_guiche > 0) ||
    (busca_data > 0 && busca_usuario > 0)
  ) {
    btn_busca.prop('disabled', false);
  } else {
    btn_busca.prop('disabled', true);
  }
});

$('#btn_busca').click(function () {
  let busca_data = $('#busca_data').val();
  let busca_guiche = $('#busca_guiche option:selected').val();
  let busca_usuario = $('#busca_usuario option:selected').val();

  getFechamentoCaixa(busca_data, busca_guiche, busca_usuario);
  $('#btn_busca').prop('disabled', true);
});

/* FUNÇÃO PARA VALIDAR CAMPOS DOS MODAIS DO COFRE! */
$(document).on(
  'input propertychange paste',
  'input.cofre_modal_validation_field',
  function (event) {
    let validator = 0;
    let counter = 0;
    const card_tipo = event.target.dataset.cardAdd;
    $(`[data-card-add="${card_tipo}"]`).each(function () {
      counter += 1;
      if ($(this).val() != null && $(this).val() != '') {
        if ($(this).attr('type') == 'number') {
          if ($(this).val() > 0) {
            validator += 1;
          }
          if ($(this).prop('max') != null) {
            if ($(this).val() > parseFloat($(this).attr('max'))) {
              validator -= 1;
            }
          }
          if ($(this).prop('min') != null) {
            if ($(this).val() < parseFloat($(this).attr('min'))) {
              validator -= 1;
            }
          }
        } else {
          if ($(this).val().length > 2) {
            validator += 1;
          }
        }
      }
    });

    if (counter > 0 && counter == validator) {
      $(`#${card_tipo}_button_add`).prop('disabled', false);
    } else {
      $(`#${card_tipo}_button_add`).prop('disabled', true);
    }
  }
);

/* FUNÇÃO PARA VALIDAR E ADICIONAR ITENS NO CARD DE COMPROVANTES */
$('#comprovante_button_add').click(function () {
  let local_obj = {};
  let duplicata = false;
  local_obj['identificacao'] = $('#add_item_comprovante_ident').val();
  local_obj['valor'] = $('#add_item_comprovante_valor').val();

  for (let i = 0; i < comprovantes.length; i++) {
    if (
      comprovantes[i].identificacao.toLowerCase() ===
      local_obj.identificacao.toLowerCase()
    ) {
      alert('Não é permitida a adição de itens duplicados.');
      console.log(
        'Foi identificada tentativa de adicionar comprovante duplicado! Impedido!'
      );
      duplicata = true;
      break;
    }
  }

  if (!duplicata) {
    add_card_item(
      'comprovante',
      null,
      parseFloat(local_obj.valor),
      local_obj.identificacao.toString(),
      set_obj_var('comprovante', local_obj)
    );
    valor_comprovantes();
  }

  $('#comprovante_button_add').prop('disabled', true);
  $('#add_item_comprovante_valor').val('0.00');
  $('#add_item_comprovante_ident').val('').focus();
});
/* FUNÇÃO PARA VALIDAR E ADICIONAR ITENS NO CARD DE CHEQUES */
$('#cheque_button_add').click(function () {
  let local_obj = {};
  let duplicata = false;
  local_obj['data'] = $('#add_item_cheque_data').val();
  local_obj['banco'] = $('#add_item_cheque_banco').val();
  local_obj['numero'] = $('#add_item_cheque_num').val();
  local_obj['emitente'] = $('#add_item_cheque_emitente').val();
  local_obj['valor'] = $('#add_item_cheque_valor').val();

  for (let i = 0; i < cheques.length; i++) {
    if (
      cheques[i].data === local_obj.data &&
      cheques[i].banco.toLowerCase() === local_obj.banco.toLowerCase() &&
      cheques[i].numero.toString().toLowerCase() ===
        local_obj.numero.toString().toLowerCase()
    ) {
      alert('Não é permitida a adição de itens duplicados.');
      console.log(
        'Foi identificada tentativa de adicionar cheque duplicado! Impedido!'
      );
      duplicata = true;
      break;
    }
  }

  if (!duplicata) {
    add_card_item(
      'cheque',
      null,
      parseFloat(local_obj.valor),
      `${local_obj.banco} - ${local_obj.numero}`,
      set_obj_var('cheque', local_obj)
    );
    valor_cheques();
  }

  $('#cheque_button_add').prop('disabled', true);
  $('#add_item_cheque_valor').val('0.00');
  $('.cheque_text_field').val('');
  $('#add_item_cheque_banco').focus();
});
/* FUNÇÃO PARA VALIDAR E ADICIONAR ITENS NO CARD DE DEPOSITOS */
$('#deposito_button_add').click(function () {
  let local_obj = search_dep_obj_tmp.item;
  local_obj['valor_utilizado'] = parseFloat(
    $('#deposito_valor_utilizado').val()
  );
  local_obj['adicao_local'] = 'yes';

  add_card_item(
    'deposito',
    null,
    local_obj.valor_utilizado,
    search_dep_obj_tmp.item.identificacao,
    set_obj_var('deposito', local_obj)
  );

  $('#deposito_button_add').prop('disabled', true);
  $('#deposito_valor_utilizado').val('0.00');
  $('#get_depositos').val('').focus();
  valor_depositos();
});
/* FUNÇÃO PARA VALIDAR E ADICIONAR ITENS NO CARD DE PAGAMENTO POSTERIOR */
$('#serv_cliente_button_add').click(function () {
  if (selected_cliente_id != null) {
    let local_obj = {};
    let duplicata = false;
    let util_saldo = 0;

    local_obj['cliente_nome'] = $('#get_cliente').val();
    local_obj['cliente_id'] = selected_cliente_id;
    local_obj['protocolo'] = $('#serv_cliente_protocolo').val();
    local_obj['tipo_protocolo'] = $('#serv_cliente_tipo_protocolo').val();
    local_obj['valor'] = $('#serv_cliente_valor').val();

    if (selected_cliente_saldo != null) {
      util_saldo = parseFloat(local_obj.valor); // utilização do saldo
    }

    for (let i = 0; i < serv_clientes.length; i++) {
      if (
        serv_clientes[i].cliente_id === local_obj.cliente_id &&
        serv_clientes[i].protocolo === local_obj.protocolo &&
        serv_clientes[i].tipo_protocolo === local_obj.tipo_protocolo
      ) {
        alert('Não é permitida a adição de itens duplicados.');
        console.log(
          'Foi identificada tentativa de adicionar pagamento posterior duplicado! Impedido!'
        );
        duplicata = true;
        break;
      }

      if (
        selected_cliente_saldo != null &&
        serv_clientes[i].cliente_id == local_obj.cliente_id
      ) {
        util_saldo += parseFloat(serv_clientes[i].valor);
      }
    }

    if (
      (!duplicata && selected_cliente_saldo == null) ||
      (!duplicata && selected_cliente_saldo - util_saldo >= 0)
    ) {
      add_card_item(
        'serv_cliente',
        null,
        parseFloat(local_obj.valor),
        `${local_obj.tipo_protocolo}.${local_obj.protocolo} - ${local_obj.cliente_nome}`,
        set_obj_var('serv_cliente', local_obj)
      );

      valor_serv_cliente();

      if (selected_cliente_saldo != null) {
        console.log(
          `Atualizado o saldo disponível para o cliente "${local_obj.cliente_nome}":` +
            ` ${selected_cliente_saldo - util_saldo}`
        );
      }
    } else if (selected_cliente_saldo - util_saldo < 0) {
      msg = `O cliente "${local_obj.cliente_nome}" não possui saldo suficiente para adicionar'`;
      msg += ` mais serviços.\nValide o saldo disponível do cliente antes de salvar o caixa!`;
      console.log(msg);
      alert(msg);
    }
  } else {
    msg = `Não foi possível identificar o ID do cliente ao tentar adicioná-lo aos`;
    msg += ' itens de pagamento posterior, portanto o item não foi adicionado!';
    msg += '\nTente atualizar a página e repetir o procedimento.';
    msg += ' Caso o problema persista, procure por suporte técnico!';
    console.log(msg);
    alert(msg);
  }

  $('#serv_cliente_button_add').prop('disabled', true);
  $('#serv_cliente_valor').val('');
  $('#get_cliente').val('').focus();
  $('#serv_cliente_cliente_id').val('');
  $('#serv_cliente_protocolo').val('');

  setTimeout(function () {
    // timeout para garantir que vai limpar as variáveis.
    selected_cliente_id = null;
    selected_cliente_saldo = null;
  }, 250);
});

/* FUNÇÃO PARA LIMPAR CAMPOS AO FECHAR O MODAL */
$('#addDeposito').on('hidden.bs.modal', function () {
  $('#deposito_valor_utilizado').val('0.00');
  $('#get_depositos').val('');
});
/* FUNÇÃO PARA CONFIGURAR FOCUS DO INPUT NO MODAL */
$('#addDeposito').on('shown.bs.modal', function () {
  $('#get_depositos').focus();
});
$('#addCheque').on('shown.bs.modal', function () {
  $('#add_item_cheque_banco').focus();
});
$('#addComprovante').on('shown.bs.modal', function () {
  $('#add_item_comprovante_ident').focus();
});

/* FUNÇÃO PARA SALVAR O OBJETO COM DEPOSITO SELECIONADO */
function save_selected_deposito(event, ui) {
  search_dep_obj_tmp = ui; //salva objeto para aguardar mais dados em outra função
  $('#deposito_valor_utilizado').val(
    parseFloat(ui.item.valor_deposito).toFixed(2)
  );
  $('#deposito_valor_utilizado').prop('max', ui.item.valor_deposito);
  $('#deposito_button_add').prop('disabled', false).focus();
}
/* FUNÇÃO PARA SALVAR O ID DO CLIENTE SELECIONADO */
function save_selected_cliente_id(event, ui) {
  selected_cliente_id = ui.item.id;

  console.log(
    `Salvo o ID: ${selected_cliente_id} referente ao cliente: ` +
      `${ui.item.value} para utilização no cadastro de novo pagamento posterior.`
  );

  if (
    ui.item.saldo != null &&
    ui.item.verifica_saldo != null &&
    ui.item.verifica_saldo == true
  ) {
    selected_cliente_saldo = parseFloat(ui.item.saldo);

    console.log(
      `Saldo disponível para o cliente "${ui.item.value}": ${selected_cliente_saldo}`
    );
  }
}

/* FUNÇÃO PARA REMOVER DEPOSITOS */
$('#show_deposito_btn_del').click(function () {
  const local_id = $('#show_deposito_btn_del').attr('data-localid');
  for (let i = 0; i < depositos.length; i++) {
    if (depositos[i].local_id == local_id) {
      /* se o depósito já estiver salvo no servidor (indicado pela ausência
                do elemento "adicao_local"), relaciona o id do depósito a excluir
                e envia o servidor para ser removido. */
      if (typeof depositos[i].adicao_local === 'undefined') {
        depositos_rem.push(depositos[i].id);
        console.log(
          `Relacionado o deposito ID: ${depositos[i].id} para ser removido do servidor.`
        );
      }

      console.log(
        `removido id: ${depositos[i].id}, ${depositos[i].identificacao}, local id: ` +
          `${depositos[i].local_id}  do array depositos.`
      );
      depositos.splice(i, 1);

      $('#show_deposito').modal('hide');
      $(`#${local_id}`).remove();
      if ($('#depositos_list a').children().length <= 0) {
        $('#depositos_list').remove();
      }
    }
  }
  valor_depositos();
});
/* FUNÇÃO PARA REMOVER CHEQUES */
$('#show_cheque_btn_del').click(function () {
  const local_id = $('#show_cheque_btn_del').attr('data-localid');
  for (let i = 0; i < cheques.length; i++) {
    if (cheques[i].local_id == local_id) {
      if (cheques[i].id != null) {
        cheques_rem.push(cheques[i].id);
        console.log(
          `Relacionado o cheque ID: ${cheques[i].id} para ser removido do servidor.`
        );
      }

      console.log(
        `removido id: ${cheques[i].id}, ${cheques[i].emitente}, local id: ` +
          `${cheques[i].local_id} do array cheques.`
      );
      cheques.splice(i, 1);

      $('#show_cheque').modal('hide');
      $(`#${local_id}`).remove();
      if ($('#cheques_list a').children().length <= 0) {
        $('#cheques_list').remove();
      }
    }
  }
  valor_cheques();
});
/* FUNÇÃO PARA REMOVER COMPROVANTES */
$('#show_comprovante_btn_del').click(function () {
  const local_id = $('#show_comprovante_btn_del').attr('data-localid');
  for (let i = 0; i < comprovantes.length; i++) {
    if (comprovantes[i].local_id == local_id) {
      if (comprovantes[i].id != null) {
        comprovantes_rem.push(comprovantes[i].id);
        console.log(
          `Relacionado o comprovante ID: ${comprovantes[i].id} para ser removido do servidor.`
        );
      }

      console.log(
        `removido id: ${comprovantes[i].id}, ${comprovantes[i].identificacao}, local id: ` +
          `${comprovantes[i].local_id} do array comprovantes.`
      );
      comprovantes.splice(i, 1);

      $('#show_comprovante').modal('hide');
      $(`#${local_id}`).remove();
      if ($('#comprovantes_list a').children().length <= 0) {
        $('#comprovantes_list').remove();
      }
    }
  }
  valor_comprovantes();
});
/* FUNÇÃO PARA REMOVER PAGAMENTOS POSTERIORES */
$('#show_serv_cliente_btn_del').click(function () {
  const local_id = $('#show_serv_cliente_btn_del').attr('data-localid');
  for (let i = 0; i < serv_clientes.length; i++) {
    if (serv_clientes[i].local_id == local_id) {
      if (serv_clientes[i].id != null) {
        serv_clientes_rem.push(serv_clientes[i].id);
        console.log(
          `Relacionado o serviço (pagamento posterior) ID: ${serv_clientes[i].id}` +
            ` para ser removido do servidor.`
        );
      }

      console.log(
        `removido id: ${serv_clientes[i].id}, ${serv_clientes[i].protocolo} - ` +
          `${serv_clientes[i].cliente_nome}, local id: ${serv_clientes[i].local_id}` +
          ` do array serv_clientes.`
      );
      serv_clientes.splice(i, 1);

      $('#show_serv_cliente').modal('hide');
      $(`#${local_id}`).remove();
    }
  }
  valor_serv_cliente();
});

/* FUNÇÃO PARA VERIFICAR E FILTRAR RESULTADOS DA BUSCA DE DEPÓSITOS*/
function get_depositos_filter(data) {
  let dep_rem = [];
  let dep_ids = [];
  for (let k = 0; k < depositos.length; k++) {
    dep_ids.push(depositos[k]['id']);
  }
  for (let i = 0; i < data.length; i++) {
    if (dep_ids.includes(data[i].id)) {
      dep_rem.push(i);
    }
  }
  for (let j = dep_rem.length - 1; j >= 0; j--) {
    console.log(
      `Item ( ${data[j].value} ) removido da lista, pois já consta como utilizado!`
    );
    data.splice(dep_rem[j], 1);
  }
  return data;
}
/* FUNÇÃO PARA SALVAR OBJETOS DO COFRE + ID LOCAL PARA USO NO MODAL */
function set_obj_var(tipo_singular, obj) {
  const local_id = ID();
  const local_obj = obj;
  local_obj['local_id'] = local_id;

  switch (tipo_singular) {
    case 'deposito':
      depositos.push(local_obj);
      break;
    case 'cheque':
      cheques.push(local_obj);
      break;
    case 'comprovante':
      comprovantes.push(local_obj);
      break;
    case 'serv_cliente':
      serv_clientes.push(local_obj);
      break;
  }
  console.log(
    `Adicionado objeto:\nTipo: ${tipo_singular} \nLocal ID: ${local_obj['local_id']}`
  );
  return local_id;
}
/* QUANDO SALVO O CAIXA, PEGAR IDS RETORNADOS PARA ATUALIZAR OS ITENS ADICIONADOS AO COFRE */
function set_id_cofre_obj(tipo_singular, local_id, id = null) {
  if (tipo_singular == 'deposito') {
    for (let i = 0; i < depositos.length; i++) {
      if (depositos[i].local_id == local_id) {
        if (typeof depositos[i].adicao_local !== 'undefined') {
          console.log(
            `Removido o indicador "adicao_local" do deposito ID Local: ${local_id}.`
          );
          delete depositos[i].adicao_local;
        }
        set_id_cofre_obj_change_card(local_id);
        console.log(
          `Deposito [ Local ID: ${local_id} ]: Confirmação local do salvamento no servidor.`
        );
      }
    }
  }
  if (tipo_singular == 'cheque') {
    for (let j = 0; j < cheques.length; j++) {
      if (cheques[j].local_id == local_id) {
        cheques[j].id = id;
        set_id_cofre_obj_change_card(local_id);
        console.log(
          `Cheque [ Local ID: ${local_id} ] [ ID: ${id} ]:` +
            ` Confirmação local do salvamento no servidor.`
        );
      }
    }
  }
  if (tipo_singular == 'comprovante') {
    for (let k = 0; k < comprovantes.length; k++) {
      if (comprovantes[k].local_id == local_id) {
        comprovantes[k].id = id;
        set_id_cofre_obj_change_card(local_id);
        console.log(
          `Comprovante [ Local ID: ${local_id} ] [ ID: ${id} ]: ` +
            `Confirmação local do salvamento no servidor.`
        );
      }
    }
  }
  if (tipo_singular == 'serv_cliente') {
    for (let l = 0; l < serv_clientes.length; l++) {
      if (serv_clientes[l].local_id == local_id) {
        serv_clientes[l].id = id;
        set_id_cofre_obj_change_card(local_id);
        console.log(
          `Pagamento Posterior [ Local ID: ${local_id} ] [ ID: ${id} ]: ` +
            `Confirmação local do salvamento no servidor.`
        );
      }
    }
  }
}
function set_id_cofre_obj_change_card(local_id) {
  $(`#${local_id}`).removeAttr('style');
}

/* POPULAR O MODAL DE DEPOSITOS COM INFORMAÇÕES DOS OBJETOS SALVOS*/
$('#show_deposito').on('show.bs.modal', function (event) {
  const depositoMessagesEl = document.getElementById('deposito_opt_messages');
  const local_id = $(event.relatedTarget).attr('data-localid');

  for (let i = 0; i < depositos.length; i++) {
    if (depositos[i].local_id == local_id) {
      console.log(`consolidado? ${depositos[i].consolidado}`);
      $('#show_deposito_valor_utilizado').val(
        parseFloat(depositos[i].valor_utilizado).toFixed(2)
      );
      $('#show_deposito_valor_deposito').val(
        parseFloat(depositos[i].valor_deposito).toFixed(2)
      );
      $('#show_deposito_data_deposito').val(depositos[i].data_deposito);
      $('#show_deposito_identificacao').val(depositos[i].identificacao);
      $('#show_deposito_observacoes').val(depositos[i].observacoes);
      depositoMessagesEl.innerHTML = '';
      if (depositos[i].consolidado) {
        $('#show_deposito_btn_del').prop('disabled', true);
        const msg =
          'Desabilitada a remoção do depósito pois já consta como consolidado!';
        const shyMessageElText = document.createTextNode(msg);
        const shyMessageEl = document.createElement('small');
        shyMessageEl.classList.add('text-muted');
        shyMessageEl.appendChild(shyMessageElText);
        depositoMessagesEl.appendChild(shyMessageEl);
      } else {
        $('#show_deposito_btn_del').attr('data-localid', local_id);
      }
      break;
    }
  }
});
/* POPULAR O MODAL DE CHEQUES COM INFORMAÇÕES DOS OBJETOS SALVOS*/
$('#show_cheque').on('show.bs.modal', function (event) {
  const local_id = $(event.relatedTarget).attr('data-localid');
  for (let i = 0; i < cheques.length; i++) {
    if (cheques[i].local_id == local_id) {
      $('#show_cheque_data').val(cheques[i].data);
      $('#show_cheque_valor').val(parseFloat(cheques[i].valor).toFixed(2));
      $('#show_cheque_banco').val(cheques[i].banco);
      $('#show_cheque_numero').val(cheques[i].numero);
      $('#show_cheque_emitente').val(cheques[i].emitente);
      $('#show_cheque_btn_del').attr('data-localid', local_id);
      break;
    }
  }
});
/* POPULAR O MODAL DE COMPROVANTES COM INFORMAÇÕES DOS OBJETOS SALVOS*/
$('#show_comprovante').on('show.bs.modal', function (event) {
  const local_id = $(event.relatedTarget).attr('data-localid');
  for (let i = 0; i < comprovantes.length; i++) {
    if (comprovantes[i].local_id == local_id) {
      $('#show_comprovante_valor').val(
        parseFloat(comprovantes[i].valor).toFixed(2)
      );
      $('#show_comprovante_ident').val(comprovantes[i].identificacao);
      $('#show_comprovante_btn_del').attr('data-localid', local_id);
      break;
    }
  }
});
/* POPULAR O MODAL DE SERVIÇOS AOS CLIENTES COM INFORMAÇÕES DOS OBJETOS SALVOS*/
$('#show_serv_cliente').on('show.bs.modal', function (event) {
  const local_id = $(event.relatedTarget).attr('data-localid');
  for (let i = 0; i < serv_clientes.length; i++) {
    if (serv_clientes[i].local_id == local_id) {
      $('#show_serv_cliente_valor').val(
        parseFloat(serv_clientes[i].valor).toFixed(2)
      );
      $('#show_serv_cliente_cliente_nome').val(serv_clientes[i].cliente_nome);
      $('#show_serv_cliente_protocolo').val(serv_clientes[i].protocolo);
      $('#show_serv_cliente_tipo_protocolo').html(
        serv_clientes[i].tipo_protocolo
      );
      $('#show_serv_cliente_cliente_observacoes').html(
        serv_clientes[i].observacoes
      );

      if (serv_clientes[i].liquidado) {
        $('#show_serv_cliente_btn_del').prop('disabled', true);
        if (!$(`#pos_pag_cons_${local_id}`).length) {
          $('#show_serv_cliente')
            .find('div.modal-footer')
            .prepend(
              `<div id="pos_pag_cons_${local_id}" class="w-100 text-align-left">` +
                '<small class="text-muted">' +
                'Desabilitada a remoção do serviço pois já consta como liquidado!' +
                '</small>' +
                '</div>'
            );
        }
      } else {
        $('#show_serv_cliente_btn_del').attr('data-localid', local_id);
      }
      break;
    }
  }
});

/* FUNÇÃO GENÉRICA PARA ADICIONAR ITENS NOS CARDS DO COFRE */
function add_card_item(
  tipo_singular,
  item_id,
  item_valor,
  item_identificacao,
  local_id
) {
  if (!$(`#${tipo_singular}s_list`).length) {
    // essa opção não contempla containers tal como o de serv_cliente.
    // a princípio isso não é um problema, visto que a div 's_list' do serv_cliente não é apagada em nenhum momento.
    // para garantir que não hajam problemas futuros em relação a isso, deve-se garantir que em funções tais como
    //  clean_f_caixa(), que apagam itens do html, façam a distinção desses casos específicos.
    $('#' + tipo_singular + 's_card').append(
      `<div class="proj-card-footer" id="${tipo_singular}s_list"></div>`
    );
  }

  $(`#${tipo_singular}s_list`).append(
    `<a href="#show_${tipo_singular}" class="proj-card-block-link"` +
      ` id="${local_id}" ${item_id ? '' : 'style="color: #ad00ba;"'}` +
      ` data-toggle="modal" data-target="#show_${tipo_singular}"` +
      ` data-localid="${local_id}"><div class="card d-flex flex-row">` +
      `<span class="px-0" style="width: .95rem;">R$ </span>` +
      `<span class="col-3 px-1 proj-car-item-list-wrap val_${tipo_singular}">` +
      `${item_valor.toFixed(2)}</span>` +
      `<span class="col-9 px-1 proj-car-item-list-wrap">${item_identificacao}` +
      `</span></div></a>`
  );
}

/* VERIFICA ALTERAÇÕES NAS QUANTIDADES DE MOEDAS E GERA OS TOTAIS */
$(document).on('input propertychange paste', 'input.qtd_moeda', function (
  event
) {
  const obj_id = event.target.id;
  $(`#${obj_id}`).val(parseInt($(`#${obj_id}`).val()));

  let obj_multiplier = $(`#${obj_id}`).data('multiplier');
  $(`#val_${obj_id}`).prop(
    'value',
    parseFloat($(`#${obj_id}`).val() * obj_multiplier).toFixed(2)
  );

  valor_dinheiro_caixa();
});

/* IMPEDE USO DE FLOAT NO QTD_DEVOLUCOES */
$(document).on('input propertychange paste', 'input#qtd_devolucoes', function (
  event
) {
  const obj_id = event.target.id;
  $('#' + obj_id).val(parseInt($('#' + obj_id).val()));
});

/* VERIFICA ALTERAÇÕES NO VALOR DO REGISTER */
$(document).on(
  'input propertychange paste',
  'input#valor_total_register',
  function (event) {
    valor_quebra();
  }
);

/* VERIFICA ALTERAÇÕES NOS VALORES DAS MOEDAS E ATUALIZA O TOTAL DE DINHEIRO NO CAIXA */
function valor_dinheiro_caixa() {
  let total = 0;

  $('.val_qtd_moeda').each(function () {
    if (!isNaN(parseFloat($(this).val()))) {
      total += parseFloat($(this).val());
    }
  });

  $('#valor_dinheiro_caixa').html(total.toFixed(2));

  valor_total_entrada();
}

/* VERIFICA ALTERAÇÕES NOS VALORES DO COFRE E ATUALIZA O TOTAL DE VALORE DO COFRE */
$(document).on('input propertychange paste', 'input.val_cofre', function () {
  valor_total_cofre();
});
function valor_total_cofre() {
  let total = 0;

  $('.val_cofre').each(function () {
    if (!isNaN(parseFloat($(this).val()))) {
      total += parseFloat($(this).val());
    }
  });

  $('#valor_total_cofre').html(total.toFixed(2));

  valor_total_entrada();
}

/* CALCULA O VALOR TOTAL DE DEPÓSITOS */
function valor_depositos() {
  let total = 0;
  const valDepositosEls = $('.val_deposito');

  valDepositosEls.each(function () {
    if (!isNaN(parseFloat($(this).text()))) {
      total += parseFloat($(this).text());
    }
  });

  $('#valor_depositos').prop('value', total.toFixed(2));
  $('#depositos_card_counter').html(valDepositosEls.length);

  valor_total_cofre();
}

/* CALCULA O VALOR TOTAL DE CHEQUES */
function valor_cheques() {
  let total = 0;
  const valChequeEls = $('.val_cheque');

  valChequeEls.each(function () {
    if (!isNaN(parseFloat($(this).text()))) {
      total += parseFloat($(this).text());
    }
  });

  $('#valor_cheques').prop('value', total.toFixed(2));
  $('#cheques_card_counter').html(valChequeEls.length);

  valor_total_cofre();
}

/* CALCULA O VALOR TOTAL DE COMPROVANTES */
function valor_comprovantes() {
  let total = 0;
  const valComprovantesEls = $('.val_comprovante');

  valComprovantesEls.each(function () {
    if (!isNaN(parseFloat($(this).text()))) {
      total += parseFloat($(this).text());
    }
  });

  $('#valor_comprovantes').prop('value', total.toFixed(2));
  if (valComprovantesEls.length > 1) {
    $('#comprovantes_card_counter').html(valComprovantesEls.length - 1);
  }

  valor_total_cofre();
}

/* CALCULA O VALOR TOTAL DE PAGAMENTOS POSTERIORES */
function valor_serv_cliente() {
  let total = 0;
  const classServClienteEls = $('.val_serv_cliente');

  classServClienteEls.each(function () {
    if (!isNaN(parseFloat($(this).text()))) {
      total += parseFloat($(this).text());
    }
  });

  $('#valor_serv_cliente').html(total.toFixed(2));
  $('#serv_cliente_card_counter').html(classServClienteEls.length);

  valor_total_entrada();
}
/* VERIFICA ALTERAÇÕES NOS VALORES DE DESPESAS FUTURAS */
$(document).on(
  'input propertychange paste',
  'input#valor_desp_futuras',
  function () {
    if (isNaN(parseFloat($(this).val()))) {
      $('#valor_desp_futuras_indicador').html(parseFloat(0).toFixed(2));
    } else {
      $('#valor_desp_futuras_indicador').html(
        parseFloat($(this).val()).toFixed(2)
      );
    }
    valor_total_entrada();
  }
);

/* CALCULA O VALOR TOTAL DO QUE ENTROU NO CAIXA */
function valor_total_entrada() {
  let total = 0;

  if (!isNaN(parseFloat($('#valor_dinheiro_caixa').text()))) {
    total += parseFloat($('#valor_dinheiro_caixa').text());
  }
  if (!isNaN(parseFloat($('#valor_total_cofre').text()))) {
    total += parseFloat($('#valor_total_cofre').text());
  }
  if (!isNaN(parseFloat($('#valor_serv_cliente').text()))) {
    total += parseFloat($('#valor_serv_cliente').text());
  }
  if (!isNaN($('#valor_desp_futuras').val())) {
    total -= $('#valor_desp_futuras').val();
  }
  if (!isNaN(parseFloat($('#saldo_inicial').text()))) {
    total -= parseFloat($('#saldo_inicial').text());
  }

  $('#valor_total_entrada').prop('value', total.toFixed(2));

  valor_quebra();
}

/* CALCULA O VALOR TOTAL DO FECHAMENTO DE CAIXA */
function valor_total() {
  let total = 0;

  if (!isNaN(parseFloat($('#valor_total_entrada').val()))) {
    total += parseFloat($('#valor_total_entrada').val());
  }
  if (!isNaN(parseFloat($('#saldo_inicial').text()))) {
    total += parseFloat($('#saldo_inicial').text());
  }

  $('#valor_total').prop('value', total.toFixed(2));
}

/* CALCULA O VALOR TOTAL DO QUEBRA DE CAIXA */
function valor_quebra() {
  let total = 0;

  if (!isNaN(parseFloat($('#valor_total_entrada').val()))) {
    total += parseFloat($('#valor_total_entrada').val());
  }
  if (!isNaN(parseFloat($('#valor_total_register').val()))) {
    total -= parseFloat($('#valor_total_register').val());
  }

  $('#valor_quebra').prop('value', total.toFixed(2));

  if (total < 0) {
    $('#valor_quebra').css({ color: 'red', 'font-weight': 'bold' });
  } else {
    $('#valor_quebra').css({ color: 'inherit', 'font-weight': 'inherit' });
  }

  valor_total();
}

function clean_f_caixa() {
  // limpa os cards do cofre para evitar acumulo de itens

  // é necessário remover o container todo (no caso dos cards do cofre), pois se
  // numa busca não houver itens naquele card, tal card deve desaparecer
  const cofre_list_container = ['deposito', 'cheque', 'comprovante'];
  const suffix = 's_list';
  const protectionAttr = 'noremove';

  cofre_list_container.forEach((name) => {
    const el = document.getElementById(`${name}${suffix}`);
    if (el) {
      if (el.children.length) {
        Array.from(el.children).forEach((childEl) => {
          if (!childEl.hasAttribute(protectionAttr)) childEl.remove();
        });
      }
      if (!el.children.length) el.remove();
    }
  });

  // para casos onde não é necessário remover o card/div inteiro mas somente seus
  // itens/filhos, usa-se esta função
  let items_container = ['serv_cliente'];
  $.each(items_container, function (index, element) {
    if ($(`#${element}s_list`).length) {
      $(`#${element}s_list`).children().remove();
    }
  });

  $('input').prop('value', '');
  $('#observacoes').prop('value', '');
  $('#saldo_inicial').text('');
  $('#valor_dinheiro_caixa').text('');
  $('#valor_total_cofre').text('');
  $('#valor_desp_futuras_indicador').text('');
  $('#valor_serv_cliente').text('');
}

function lock_fcaixa() {
  $('.caixa_editable').prop('disabled', 'true');
  $('#btn_consolidar_fcaixa').css('display', 'none');
  $('#btn_salvar_fcaixa').css('display', 'none');
  $('#btn_fechar_fcaixa').css('display', 'none');
  //$('#btn_abrir_fcaixa').css('display', "none");
}

/* FUNÇÃO PARA RECOLHER DADOS DO CLIENTE E ENVIAR AO SERVIDOR PARA SALVAR O CAIXA */
function setFechamentoCaixaResult(key = null, value = null) {
  let f_caixa = {};

  f_caixa['client_tz'] = client_tz;
  if (f_caixa_id != null) {
    f_caixa['id'] = f_caixa_id;
  }
  f_caixa['usuario_id'] = usuario_id;
  f_caixa['guiche_id'] = guiche_id;
  f_caixa['saldo_inicial'] = $('#saldo_inicial').text();
  f_caixa['valor_dinheiro_caixa'] = $('#valor_dinheiro_caixa').text();
  f_caixa['valor_dinheiro_cofre'] = $('#valor_dinheiro_cofre').val();
  f_caixa['valor_total_servicos_clientes'] = $('#valor_serv_cliente').text();
  f_caixa['valor_desp_futuras'] = $('#valor_desp_futuras').val();
  f_caixa['valor_total_entrada'] = $('#valor_total_entrada').val();
  f_caixa['valor_quebra'] = $('#valor_quebra').val();
  f_caixa['valor_total'] = $('#valor_total').val();
  f_caixa['valor_depositos'] = $('#valor_depositos').val();
  f_caixa['valor_cheques'] = $('#valor_cheques').val();
  f_caixa['valor_comprovantes'] = $('#valor_comprovantes').val();
  f_caixa['valor_cartoes'] = $('#valor_cartoes').text();
  f_caixa['qtd_devolucoes'] = $('#qtd_devolucoes').val();
  f_caixa['observacoes'] = $('#observacoes').val();

  if (depositos.length > 0) {
    f_caixa['depositos'] = depositos;
  }
  if (cheques.length > 0) {
    f_caixa['cheques'] = cheques;
  }
  if (comprovantes.length > 0) {
    f_caixa['comprovantes'] = comprovantes;
  }
  if (serv_clientes.length > 0) {
    f_caixa['clientes_servicos'] = serv_clientes;
  }

  if (depositos_rem.length > 0) {
    f_caixa['depositos_rem'] = depositos_rem;
  }
  if (cheques_rem.length > 0) {
    f_caixa['cheques_rem'] = cheques_rem;
  }
  if (comprovantes_rem.length > 0) {
    f_caixa['comprovantes_rem'] = comprovantes_rem;
  }
  if (serv_clientes_rem.length > 0) {
    f_caixa['clientes_servicos_rem'] = serv_clientes_rem;
  }

  $('input.qtd_moeda').each(function () {
    f_caixa[$(this).prop('id')] = $(this).val();
  });

  f_caixa['fechado'] = $('input#checkbox_fechar_fcaixa').is(':checked')
    ? true
    : false;

  if (key != null && value != null) {
    f_caixa[key] = value;
  }

  const fc = JSON.stringify(f_caixa);

  console.log('Enviando dados para serem salvos no servidor:');
  console.log(fc);

  return { f_caixa: fc };
}
/* FUNÇÃO PARA EXECUTAR AÇÃO NO CAIXA */
function setActionsCaixaResult(action = null) {
  if (f_caixa_id != null && action != null) {
    let f_caixa = {};
    f_caixa['client_tz'] = client_tz;
    f_caixa['id'] = f_caixa_id;

    if (action == 'abrir') {
      f_caixa['fechado'] = false;
    } else if (action == 'consolidar') {
      f_caixa['consolidado'] = true;
    }

    let fc = JSON.stringify(f_caixa);

    console.log('Enviando dados para serem salvos no servidor:');
    console.log(fc);

    return { f_caixa: fc };
  } else {
    alert(
      'Não foi possível enviar a requisição pois o ID do fechamento de caixa não foi encontrado!'
    );
  }
}
/* RECEBE RESPOSTA DA TENTATIVA DE ACIONAR O CAIXA E TOMA PROVIDÊNCIAS */
function setActionsCaixaResponse(data) {
  let success = data?.success ? 'ÊXITO' : 'FALHA';
  console.log(`Houve ${success} na tentativa de salvar o fechamento de caixa!`);

  if (data.success) {
    if (data.consolidado) {
      $('#btn_salvar_fcaixa').hide('fast');
      $('#btn_abrir_fcaixa').hide('fast');
      $('#btn_consolidar_fcaixa').prop('disabled', true);
      console.log('Caixa consolidado!');
    } else if (!data.fechado) {
      console.log('Caixa reaberto!');
      setFCaixaResponseAnimateButtonEnding(500);
      $('#btn_abrir_fcaixa').hide('fast');
      $('#btn_consolidar_fcaixa').hide('fast');
    }
    if (data.erro != null) {
      console.log(`O servidor relatou: ${data.erro}`);
    }

    set_historico(data.historico, data.usuario_mod, data.data_mod_reg);
  } else {
    if (data.consolidado) {
      clean_f_caixa();
      lock_fcaixa();
      console.log(`Erro informado pelo servidor: ${data.erro}`);
      setTimeout(function () {
        alert(`Houve um erro ao tentar executar ação!\n${data.erro}`);
      }, 1000);
    } else {
      clean_f_caixa();
      console.log(`Erro informado pelo servidor: ${data.erro}`);
      setTimeout(function () {
        alert(`Houve um erro ao tentar executar ação!\n${data.erro}`);
      }, 1000);
    }
  }
}
/* INICIA AÇÕES DO CAIXA */
$('#btn_abrir_fcaixa').on('click', function () {
  setActionsCaixa((action = 'abrir'));
});
$('#btn_consolidar_fcaixa').on('click', function () {
  setActionsCaixa((action = 'consolidar'));
});
/* INICIA PROCESSO DE SALVAMENTO DO CAIXA ANIMANDO O BOTÃO E CHAMANDO FUNÇÃO DE SALVAR */
$('#btn_salvar_fcaixa').on('click', function () {
  const $btn_salvar = $(this);
  const loadingText = 'Processando...';

  if ($btn_salvar.html() !== loadingText) {
    $('#btn_fechar_fcaixa').hide('fast');
    $('.caixa_editable').prop('disabled', true);
    $btn_salvar
      .attr('data-default-text', $btn_salvar.text())
      .prop('disabled', true)
      .addClass('border_curve');
    $btn_salvar
      .find('span')
      .fadeOut('fast', function () {
        $(this).html(loadingText);
      })
      .fadeIn('fast');
  }

  setFechamentoCaixa();
});
/* RECEBE RESPOSTA DA TENTATIVA DE SALVAR O CAIXA E TOMA PROVIDÊNCIAS */
function setFCaixaResponse(data) {
  const success = data?.success ? 'ÊXITO' : 'FALHA';
  console.log(
    `Houve ${success} na tentativa de salvar o fechamento de caixa!\nO servidor respondeu:`
  );
  console.log(JSON.stringify(data));

  if (data.success) {
    setFCaixaResponseAnimateButton('btn-success', 500);
    if (data.id != null && f_caixa_id == null) {
      f_caixa_id = data.id;
      console.log(`Atribuído o ID: ${f_caixa_id} ao fechamento de caixa!`);
    }
    if (data.erro != null && data.erro != '') {
      console.log(`Erro retornado: ${data.erro}`);
    }

    if (!data.fechado && !data.consolidado) {
      setFCaixaResponseAnimateButtonEnding();
    }
    if (data.fechado && !data.consolidado) {
      $('#btn_abrir_fcaixa').show('fast');
      $('#btn_consolidar_fcaixa').prop('disabled', false).show('fast');
    } else if (data.consolidado) {
      $('#btn_consolidar_fcaixa').prop('disabled', false).show('fast');
      $('#btn_fechar_fcaixa').hide('fast');
    }

    set_historico(data.historico, data.usuario_mod, data.data_mod_reg);

    // zerando as variáveis para prevenir envios indesejados
    depositos_rem = [];
    cheques_rem = [];
    comprovantes_rem = [];
    serv_clientes_rem = [];
  } else {
    if (data.consolidado) {
      clean_f_caixa();
      lock_fcaixa();
      console.log(`Erro informado pelo servidor: ${data.erro}`);
      setTimeout(function () {
        alert(`Houve um erro ao tentar executar ação!\n${data.erro}`);
      }, 1000);
    } else {
      setFCaixaResponseAnimateButton('btn-danger', 500);
      setFCaixaResponseAnimateButtonEnding();
      console.log(`Erro informado pelo servidor: ${data.erro}`);
      setTimeout(function () {
        alert(`Houve um erro ao tentar executar ação!\n${data.erro}`);
      }, 1000);
    }
  }

  if (data.depositos != null) {
    if (data.depositos.length > 0) {
      for (let i = 0; i < data.depositos.length; i++) {
        set_id_cofre_obj(
          'deposito',
          data.depositos[i].local_id,
          data.depositos[i].id
        );
      }
    }
  }
  if (data.cheques != null) {
    if (data.cheques.length > 0) {
      for (let j = 0; j < data.cheques.length; j++) {
        set_id_cofre_obj(
          'cheque',
          data.cheques[j].local_id,
          data.cheques[j].id
        );
      }
    }
  }

  if (data.comprovantes != null) {
    if (data.comprovantes.length > 0) {
      for (let k = 0; k < data.comprovantes.length; k++) {
        set_id_cofre_obj(
          'comprovante',
          data.comprovantes[k].local_id,
          data.comprovantes[k].id
        );
      }
    }
  }

  if (data.clientes_servicos != null) {
    if (data.clientes_servicos.length > 0) {
      for (let l = 0; l < data.clientes_servicos.length; l++) {
        set_id_cofre_obj(
          'serv_cliente',
          data.clientes_servicos[l].local_id,
          data.clientes_servicos[l].id
        );
      }
    }
  }
}
/* ANIMA O BOTÃO DE SALVAR DE ACORDO COM A RESPOSTA DO SERVIDOR */
function setFCaixaResponseAnimateButton(btn_decor, decor_time) {
  const defaultTextTag = 'data-default-text';
  const $btn_salvar = $('#btn_salvar_fcaixa');

  $btn_salvar
    .find('span')
    .fadeOut('fast', function () {
      $btn_salvar.removeClass('btn-primary').addClass(btn_decor);
      $(this).html($btn_salvar.attr(defaultTextTag));
    })
    .fadeIn('fast', function () {
      setTimeout(function () {
        $btn_salvar.removeClass(btn_decor).addClass('btn-primary');
      }, decor_time);
    });
}
function setFCaixaResponseAnimateButtonEnding(duration = 1300) {
  setTimeout(function () {
    // salvar o status do valor total register para mantê-lo após o procedimento.
    const valor_register_editable = $('#valor_total_register').prop('disabled');
    $('.caixa_editable').prop('disabled', false);
    $('#btn_salvar_fcaixa').removeClass('border_curve').prop('disabled', false);
    $('#valor_total_register').prop('disabled', valor_register_editable);
    $('#btn_fechar_fcaixa').show('fast');
    $('#btn_salvar_fcaixa').show('fast');
  }, duration);
}
