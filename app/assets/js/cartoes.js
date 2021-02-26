function cartoes(jsonCartoes){
    const cartoes = JSON.parse(jsonCartoes)
    const debito = "DB"
    const credito = "CR"


    // ::: ELEMENTS :::
    const inputValorServicoEl = document.querySelector('textarea#inputValorServico')
    const bandeiraEl = document.querySelector('select#bandeira')
    const operacaoEl = document.querySelector('select#operacao')
    const parcelasEl = document.querySelector('input#parcelas')
    const protocoloEl = document.querySelector('input#protocolo')

    const labelJurosParcelaEl = document.querySelector('p#label-valorJuros-valorParcelas')
    const valorJurosParcelasEl = document.querySelector('span#valorJuros-valorParcelas')
    const valorCobradoEl =  document.querySelector('span#valorCobrado')
    const taxaJurosEl = document.querySelector('span#taxaJuros')
    const valorServicoEl = document.querySelector('span#valorServico')

    const btnSalvaFormEl = document.querySelector('button#btnSalvaForm')
    const csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value
    const messagesEl = document.querySelector('div#messages')


    // ::: MEM. OBJ. STORAGE :::
    const cartoesForm = {
        _inputValorServico: inputValorServicoEl.value || [],
        _bandeira: bandeiraEl.value,
        _operacao: operacaoEl.value,
        _parcelas: parcelasEl.value,
        _protocolo: protocoloEl.value,
        _valorServico: 0,
        _valorCobrado: 0,
        _valorJuros: 0,
        _valorParcelas: 0,
        _taxaJuros: 0,
        
        // manter setters com os nomes dos IDs dos elementos

        get inputValorServico() { return this._inputValorServico },
        set inputValorServico(val) {
            const valoresCorrigidos = fixValores(val)
            this._inputValorServico = valoresCorrigidos.join(' ')
            this.valorServico = valoresCorrigidos
        },

        get valorServico() { return this._valorServico },
        set valorServico(val) {
            this._valorServico = parseFloat(val //valores
                            .map(getNumValidos)
                            .reduce(getSoma, 0)
                        ).toFixed(2)
        },

        get valorCobrado() { return this._valorCobrado },
        set valorCobrado({valorServico, taxaJuros, bandeira}) {
            if (bandeira){
                this._valorCobrado = parseFloat( valorServico / (1 - (taxaJuros / 100)) ).toFixed(2)
            } else {
                this._valorCobrado = 0
            }
        },

        get valorJuros() { return this._valorJuros },
        set valorJuros({valorServico, valorCobrado}) { 
            if (valorCobrado > valorServico) { 
                this._valorJuros = parseFloat(valorCobrado - valorServico).toFixed(2)
            } else { this._valorJuros = 0 }
        },
        
        get valorParcelas() { return this._valorParcelas },
        set valorParcelas({valorCobrado, parcelas}) {
            this._valorParcelas = parcelas > 1 ? parseFloat(valorCobrado / parcelas).toFixed(2) : 0
        },

        get taxaJuros() { return this._taxaJuros },
        set taxaJuros({bandeira, parcelas}) {
            if (bandeira) {
                this._taxaJuros = parseFloat( calcTaxa(bandeira, parcelas) ).toFixed(2)
            } else { this._taxaJuros = 0}
        },

        get bandeira() {
            return cartoes.bandeiras.find( b => this._bandeira == b.id )
        },
        set bandeira(idBandeira) { this._bandeira = idBandeira },
//
        get operacao() { return this._operacao },
        set operacao(operacao) {
            this._operacao = operacao
            if (isDebito()) this.parcelas = 0
        },
//
        get parcelas() { return this._parcelas },
        set parcelas(qtdParcelas) {
            const parcelamento = this.bandeira.parcelamento
            let parcela = parseInt(qtdParcelas) || ''
            if (parcela <= 0 || !isCredito()) parcela = ''
            if (parcela > parcelamento) parcela = parcelamento
            this._parcelas = parcela
        },

        get protocolo() { return this._protocolo },
        set protocolo(val) { this._protocolo = val }
    }


    // ::: AUX SETTERS :::
    const multiSetter = () => {
        // para valores que precisam ser calculados com 2 ou mais params
        cartoesForm.taxaJuros = cartoesForm
        cartoesForm.valorCobrado = cartoesForm
        cartoesForm.valorJuros = cartoesForm
        cartoesForm.valorParcelas = cartoesForm
    }


    // ::: STARTERS :::
    renderMessages(cartoes)


    // ::: HANDLERS :::
    inputValorServicoEl.oninput = atualizaValor
    bandeiraEl.onchange = atualizaValor
    operacaoEl.onchange = atualizaValor
    parcelasEl.oninput = atualizaValor
    protocoloEl.oninput = atualizaValor
    btnSalvaFormEl.onclick = enviaForm


    // ::: HANDLERS METHODS :::
    function atualizaValor(event) {
        // manter como function pois necessita do this não lexico
        // atualiza o atributo do obj com o valor do formulario
        cartoesForm[event.srcElement.id] = this.value

        multiSetter()
        renderValores(cartoesForm, cartoes.usuario)

        console.log('\n\n:::::::::::::::\n')
        console.log(cartoesForm)
        console.log(`::: Elemento: ${event.srcElement.id}; Valor: ${this.value} :::`)
    }
    function enviaForm(event) {
        event.preventDefault()
        const formUrl = btnSalvaFormEl.getAttribute("formaction", null)

        if (formUrl && csrf_token) {
            form = renderForm(cartoesForm, formUrl, csrf_token)
            form.submit()
        } else {
            alert('Não foi possível identificar as informações para envio do formulário.')
        }
    }


    // ::: COMMON METHODS :::
    const isDebito = () => cartoesForm._operacao === debito
    const isCredito = () => cartoesForm._operacao === credito

    const fixValores = valores => valores.split(' ').map(valoresPermitidos)

    const getSoma = (total, valor) => total += valor
    const getNumValidos = valor => {
        const numValidos = /^\d+(?:\.\d+)?$/
        let newValor = valor.replace(',', '.')

        if ( newValor.startsWith('.') ) newValor = `0${newValor}`
        if ( newValor.endsWith('.') ) newValor = `${newValor}0`

        return numValidos.test(newValor) ? parseFloat(newValor) : 0
    }
    const valoresPermitidos = valor => {
        const valorLimpo = valor.replace(/[^0-9,]/g, '').substr(0, 9)  //maximo 9 digitos
        let digitos = valorLimpo.split(',', 2) // divide dos digitos e casas decimais

        digitos[0] = digitos[0].substr(0, 6) // os digitos limitados a 6
        if (digitos.length > 1) digitos[1] = digitos[1].substr(0, 2) // casas decimais limitadas a 2

        return digitos.join(',') // junta dos digitos e casas decimais
    }

    const calcTaxa = (bandeira, parcelas) => {

        if (isDebito() && bandeira.usar_debito) {
            return bandeira.taxa_debito

        } else if (!bandeira.parcelar){
            return bandeira.taxa_credito_avista

        } else {

            if (bandeira.modo_6_6 && parcelas > 1) {
                if (parcelas <= 6){
                    return bandeira.taxa_credito_parcelado  // no modo 6/6, taxa para parc. até 6x
                } else {
                    return bandeira.taxa_credito_parcelado_porparcela  // no modo 6/6, taxa p/ parc. sup. a 6x
                }

            } else if (parcelas > 1) {
                // parseInt na parcela pra evitar números quebrados
                return bandeira.taxa_credito_parcelado + ( parcelas * bandeira.taxa_credito_parcelado_porparcela )

            } else {
                return bandeira.taxa_credito_avista
            }

        }
    }


    // ::: RENDER METHODS :::
    const toggleParcelas = bandeira => {
        if( bandeira && bandeira.usar_credito && bandeira.parcelar && isCredito() ){
            if( parcelasEl.getAttribute('disabled') ) {   
                parcelasEl.removeAttribute('disabled')
            }
        } else {
            parcelasEl.setAttribute('disabled', true)
        }
    }
    const toggleOperacoes = bandeira => {
        const event = new Event('change')

        if (bandeira.usar_credito) {
            operacaoEl.children[1].removeAttribute("disabled")
        } else {
            if (!operacaoEl.children[1].hasAttribute('disabled')) {
                operacaoEl.children[1].setAttribute("disabled", true)
                operacaoEl.value = debito
                operacaoEl.dispatchEvent(event)
            }
        }

        if (bandeira.usar_debito) {
            operacaoEl.children[0].removeAttribute("disabled")
        } else {
            if (!operacaoEl.children[0].hasAttribute('disabled')) {
                operacaoEl.children[0].setAttribute("disabled", true)
                operacaoEl.value = credito
                operacaoEl.dispatchEvent(event)
            }
        }
    }
    const renderValores = (
        {bandeira, parcelas, valorCobrado, valorServico, taxaJuros, valorJuros, inputValorServico, valorParcelas, protocolo},
        {guiche: {id: guiche}}) => {
        const valorJurosParcela = parcelas > 1 ? valorParcelas : valorJuros
        const labelJurosParcela = parcelas > 1 ? `Valor por Parcela (${parcelas}x)` : 'Valor dos Juros'

        if (bandeira) {
            toggleOperacoes(bandeira)
            toggleParcelas(bandeira)
        }
        renderBtnSalvarForm(bandeira, valorServico, protocolo, guiche)

        labelJurosParcelaEl.innerHTML = labelJurosParcela
        valorJurosParcelasEl.innerHTML = toBR(valorJurosParcela)
        valorCobradoEl.innerHTML = toBR(valorCobrado)
        taxaJurosEl.innerHTML = toBR(taxaJuros)
        inputValorServicoEl.value = inputValorServico
        valorServicoEl.innerHTML = toBR(valorServico)
        parcelasEl.value = parcelas

    }
    const renderBtnSalvarForm = (bandeira, valorServico, protocolo, guiche) =>{
        if (guiche && bandeira && protocolo && parseFloat(valorServico)){
            btnSalvaFormEl.removeAttribute("disabled")
        } else {
            btnSalvaFormEl.setAttribute("disabled", true)
        }
    }
    const renderForm = (
        {bandeira: {id: bandeira}, operacao, valorServico, valorCobrado, taxaJuros, parcelas, protocolo},
        formUrl, csrf_token
    ) => {
        const form = document.createElement('form')
        form.style.display = "none"
        form.setAttribute("method", "post")
        form.setAttribute("action", formUrl)

        const _csfr_token = document.createElement('input')
        _csfr_token.setAttribute("type", "hidden")
        _csfr_token.setAttribute("name", "csrfmiddlewaretoken")
        _csfr_token.setAttribute("value", csrf_token)
        form.appendChild(_csfr_token)

        const _bandeira = document.createElement('input')
        _bandeira.setAttribute("type", "hidden")
        _bandeira.setAttribute("name", "bandeira")
        _bandeira.setAttribute("value", bandeira)
        form.appendChild(_bandeira)

        const _operacao = document.createElement("input")
        _operacao.setAttribute("type", "hidden")
        _operacao.setAttribute("name", "operacao")
        _operacao.setAttribute("value", operacao)
        form.appendChild(_operacao)

        const _valorServico = document.createElement("input")
        _valorServico.setAttribute("type", "hidden")
        _valorServico.setAttribute("name", "valor_servico")
        _valorServico.setAttribute("value", valorServico)
        form.appendChild(_valorServico)

        const _valorCobrado = document.createElement("input")
        _valorCobrado.setAttribute("type", "hidden")
        _valorCobrado.setAttribute("name", "valor_cobrado")
        _valorCobrado.setAttribute("value", valorCobrado)
        form.appendChild(_valorCobrado)

        const _taxaJuros = document.createElement("input")
        _taxaJuros.setAttribute("type", "hidden")
        _taxaJuros.setAttribute("name", "taxa_juros")
        _taxaJuros.setAttribute("value", taxaJuros)
        form.appendChild(_taxaJuros)

        const _parcelas = document.createElement("input")
        _parcelas.setAttribute("type", "hidden")
        _parcelas.setAttribute("name", "parcelas")
        _parcelas.setAttribute("value", parcelas)
        form.appendChild(_parcelas)

        const _protocolo = document.createElement("input")
        _protocolo.setAttribute("type", "hidden")
        _protocolo.setAttribute("name", "protocolo")
        _protocolo.setAttribute("value", protocolo)
        form.appendChild(_protocolo)

        document.body.appendChild(form)

        return form
    }
    function renderMessages ({form_errors}) {
        if (form_errors) {
            const headingEl = document.createElement("h5")
            const headingText = document.createTextNode("Informações Inválidas!")
            headingEl.classList.add("alert-heading")
            headingEl.appendChild(headingText)
            messagesEl.appendChild(headingEl)

            const headingDescEl = document.createElement("p")
            const headingDescText = document.createTextNode(
                "Corrija os erros indicados e tente salvar novamente!")
            headingDescEl.appendChild(headingDescText)
            messagesEl.appendChild(headingDescEl)

            const hr = document.createElement("hr")
            messagesEl.appendChild(hr)


            Object.keys(form_errors).forEach(field =>{
                const erroEl = document.createElement("p")
                erroEl.classList.add("mb-0")
                const erroElText = document.createTextNode(`: ${form_errors[field][0].message}`)
                const erroFieldEl = document.createElement("strong")
                const erroFieldElText = document.createTextNode(field)
                erroFieldEl.appendChild(erroFieldElText)
                erroEl.appendChild(erroFieldEl)
                erroEl.appendChild(erroElText)
                messagesEl.appendChild(erroEl)
            })

            messagesEl.style.display = "block"
        }
    }


}
