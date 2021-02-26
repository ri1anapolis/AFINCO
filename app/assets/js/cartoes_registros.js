function cartoesRegistros(
  cartoesRegistrosJson,
  givenBaseRegURL,
  urlTarget = null,
  showActions = true
) {
  const registros_obj = JSON.parse(cartoesRegistrosJson) || {};
  if (!registros_obj.hasOwnProperty('registros')) registros_obj.registros = [];
  let baseRegURL = null;
  if (typeof givenBaseRegURL === 'string' && givenBaseRegURL) {
    baseRegURL = !givenBaseRegURL.endsWith('/')
      ? givenBaseRegURL + '/'
      : givenBaseRegURL;
  }

  // ::: ELEMENTS :::
  const registrosEl = document.querySelector('section#collapseRegistros');
  const bntCollapseEl = document.querySelector("a[href='#collapseRegistros']")
    .parentNode;

  // ::: STARTERS :::
  tooggleBtn(registros_obj, bntCollapseEl);
  renderRegistros(
    registros_obj,
    registrosEl,
    baseRegURL,
    urlTarget,
    showActions
  );

  // ::: RENDERS :::
  function tooggleBtn({ registros }, btnEl) {
    if (registros.length) {
      btnEl.style.display = 'block';
    } else {
      btnEl.style.display = 'none';
    }
  }
  function renderRegistros(
    registros_obj,
    registrosEl,
    baseRegURL,
    urlTarget,
    showActions
  ) {
    if (registros_obj.registros.length) {
      const thBandeira = document.createElement('th');
      const thBandeiraText = document.createTextNode('Bandeira');
      thBandeira.setAttribute('nowrap', true);
      thBandeira.appendChild(thBandeiraText);

      const thOperacao = document.createElement('th');
      const thOperacaoText = document.createTextNode('Operação');
      thOperacao.setAttribute('nowrap', true);
      thOperacao.appendChild(thOperacaoText);

      const thParcelas = document.createElement('th');
      const thParcelasText = document.createTextNode('Parcelas');
      thParcelas.setAttribute('nowrap', true);
      thParcelas.appendChild(thParcelasText);

      const thTaxa = document.createElement('th');
      const thTaxaText = document.createTextNode('Taxa Adm.');
      thTaxa.setAttribute('nowrap', true);
      thTaxa.appendChild(thTaxaText);

      const thValorServico = document.createElement('th');
      const thValorServicoText = document.createTextNode('Valor Serviço');
      thValorServico.setAttribute('nowrap', true);
      thValorServico.appendChild(thValorServicoText);

      const thValorCobrado = document.createElement('th');
      const thValorCobradoText = document.createTextNode('Valor Cobrança');
      thValorCobrado.setAttribute('nowrap', true);
      thValorCobrado.appendChild(thValorCobradoText);

      const thProtocolo = document.createElement('th');
      const thProtocoloText = document.createTextNode('Protocolo');
      thProtocolo.setAttribute('nowrap', true);
      thProtocolo.appendChild(thProtocoloText);

      const thAcoes = document.createElement('th');
      const thAcoesText = document.createTextNode('');
      thAcoes.setAttribute('nowrap', true);
      thAcoes.appendChild(thAcoesText);

      const trHeader = document.createElement('tr');
      trHeader.appendChild(thBandeira);
      trHeader.appendChild(thOperacao);
      trHeader.appendChild(thParcelas);
      trHeader.appendChild(thTaxa);
      trHeader.appendChild(thValorServico);
      trHeader.appendChild(thValorCobrado);
      trHeader.appendChild(thProtocolo);
      if (showActions) trHeader.appendChild(thAcoes);

      const thead = document.createElement('thead');
      thead.appendChild(trHeader);

      const tbody = document.createElement('tbody');

      registros_obj.registros.forEach((el) => {
        const tdBandeira = document.createElement('td');
        const tdBandeiraText = document.createTextNode(el.bandeira.nome);
        tdBandeira.setAttribute('nowrap', true);
        tdBandeira.appendChild(tdBandeiraText);

        const tdOperacao = document.createElement('td');
        const tdOperacaoText = document.createTextNode(el.operacao);
        tdOperacao.setAttribute('nowrap', true);
        tdOperacao.appendChild(tdOperacaoText);

        const tdParcelas = document.createElement('td');
        const tdParcelasText = document.createTextNode(el.parcelas);
        tdParcelas.setAttribute('nowrap', true);
        tdParcelas.appendChild(tdParcelasText);

        const tdTaxa = document.createElement('td');
        const tdTaxaText = document.createTextNode(`${toBR(el.taxa_juros)}%`);
        tdTaxa.setAttribute('nowrap', true);
        tdTaxa.appendChild(tdTaxaText);

        const tdValorServico = document.createElement('td');
        const tdValorServicoText = document.createTextNode(
          `R$ ${toBR(el.valor_servico)}`
        );
        tdValorServico.setAttribute('nowrap', true);
        tdValorServico.appendChild(tdValorServicoText);

        const tdValorCobrado = document.createElement('td');
        const tdValorCobradoText = document.createTextNode(
          `R$ ${toBR(el.valor_cobrado)}`
        );
        tdValorCobrado.setAttribute('nowrap', true);
        tdValorCobrado.appendChild(tdValorCobradoText);

        const tdProtocolo = document.createElement('td');
        const tdProtocoloText = document.createTextNode(el.protocolo);
        tdProtocolo.setAttribute('nowrap', true);
        tdProtocolo.appendChild(tdProtocoloText);

        const trEl = document.createElement('tr');
        trEl.appendChild(tdBandeira);
        trEl.appendChild(tdOperacao);
        trEl.appendChild(tdParcelas);
        trEl.appendChild(tdTaxa);
        trEl.appendChild(tdValorServico);
        trEl.appendChild(tdValorCobrado);
        trEl.appendChild(tdProtocolo);

        const tdAcoes = document.createElement('td');
        tdAcoes.setAttribute('nowrap', true);

        if (baseRegURL && showActions) {
          const tdImprimirIco = document.createElement('img');
          tdImprimirIco.setAttribute('src', '/static/svg/si-glyph-print.svg');
          tdImprimirIco.setAttribute('alt', 'Imprimir');
          tdImprimirIco.classList.add('glyph-icon', 'mb-1');

          const tdImprimirLnk = document.createElement('a');
          tdImprimirLnk.setAttribute('href', `${baseRegURL}${el.id}/recibo`);
          if (urlTarget) tdImprimirLnk.setAttribute('target', `${urlTarget}`);
          tdImprimirLnk.appendChild(tdImprimirIco);
          tdAcoes.appendChild(tdImprimirLnk);

          if (el.delete) {
            const tdDelIco = document.createElement('img');
            tdDelIco.setAttribute('src', '/static/svg/si-glyph-delete.svg');
            tdDelIco.setAttribute('alt', 'Apagar');
            tdDelIco.classList.add('glyph-icon', 'mb-1');

            const tdDelLnk = document.createElement('a');
            tdDelLnk.setAttribute('href', `${baseRegURL}${el.id}/delete`);
            if (urlTarget) tdDelLnk.setAttribute('target', `${urlTarget}`);
            tdDelLnk.appendChild(tdDelIco);

            const tdEspacador = document.createTextNode(' | ');

            tdAcoes.appendChild(tdEspacador);
            tdAcoes.appendChild(tdDelLnk);
          }
        }

        if (showActions) trEl.appendChild(tdAcoes);
        tbody.appendChild(trEl);
      });

      const tdColSpan01 = document.createElement('td');
      tdColSpan01.setAttribute('colspan', '3');

      const tdColSpan02 = document.createElement('td');
      tdColSpan02.setAttribute('colspan', '2');

      const thValorTaxa = document.createElement('th');
      const thValorTaxaText = document.createTextNode(
        `R$ ${toBR(
          registros_obj.total_valor_cobrado - registros_obj.total_valor_servico
        )}`
      );
      thValorTaxa.setAttribute('nowrap', true);
      thValorTaxa.appendChild(thValorTaxaText);

      const thTotalValorServico = document.createElement('th');
      const thTotalValorServicoText = document.createTextNode(
        `R$ ${toBR(registros_obj.total_valor_servico)}`
      );
      thTotalValorServico.setAttribute('nowrap', true);
      thTotalValorServico.appendChild(thTotalValorServicoText);

      const thTotalValorCobrado = document.createElement('th');
      const thTotalValorCobradoText = document.createTextNode(
        `R$ ${toBR(registros_obj.total_valor_cobrado)}`
      );
      thTotalValorCobrado.setAttribute('nowrap', true);
      thTotalValorCobrado.appendChild(thTotalValorCobradoText);

      const trTotais = document.createElement('tr');
      trTotais.appendChild(tdColSpan01);
      trTotais.appendChild(thValorTaxa);
      trTotais.appendChild(thTotalValorServico);
      trTotais.appendChild(thTotalValorCobrado);
      trTotais.appendChild(tdColSpan02);

      const tfoot = document.createElement('tfoot');
      tfoot.appendChild(trTotais);

      const tabela = document.createElement('table');
      tabela.classList.add('table', 'table-sm', 'table-hover', 'text-center');
      tabela.appendChild(thead);
      tabela.appendChild(tbody);
      tabela.appendChild(tfoot);

      registrosEl.innerHTML = '';
      registrosEl.appendChild(tabela);
    } else {
      const theresNothingElText = document.createTextNode(
        'Não há registros a serem apresentados.'
      );

      const theresNothingEl = document.createElement('p');
      theresNothingEl.appendChild(theresNothingElText);

      const sectionEl = document.createElement('section');
      sectionEl.classList.add('text-center');
      sectionEl.appendChild(theresNothingEl);

      registrosEl.innerHTML = '';
      registrosEl.appendChild(sectionEl);
    }
  }
}
