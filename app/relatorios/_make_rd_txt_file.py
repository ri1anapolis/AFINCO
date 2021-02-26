from escribadbquery.views import query_with_fetchall
from ._create_output_file import create_output_file

from despesas.models import Despesa

import uuid


def make_rd_txt_file(data_ini, data_end):
    """
    Make Receitas e Despesas Text File / Cria Relatório de Receitas e Despesas em TXT.
    Busca pelas informações no banco de dados e gera o TXT para download.
    retorna status de erro e url para o arquivo.
    :param data_ini:
    :param data_end:
    :param result_db:
    :return error, output_file:
    """
    erro, output_file_url, qtd_rows, empty_queries = '', None, 0, True
    query_escriba = """
        SELECT *
        FROM (

            SELECT
                LPAD(CAST(DAY(cx.cx_data) AS CHAR), 2, '0') AS 'Dia',
                LPAD(CAST(MONTH(cx.cx_data) AS CHAR), 2, '0') AS 'Mes',
                IF(
                    cx.cx_valor < 0,
                    '9300008', # devolução ($$ vai para a conta de devolução)
                    '1000001' # receita serviço ($$ vai para o caixa)
                ) AS 'Conta Debito',
                IF(
                    cx.cx_valor < 0,
                    '1000001', # devolução ($$ sai do caixa)
                    '9010001' # receita serviço ($$ sai da conta de serviço)
                ) AS 'Conta Credito',
                CONCAT(
                    IF ( cx.Cx_Tipo = 'Registro', '99', '88' ),
                    '',
                    LPAD(CAST(cx.cx_protocolo AS CHAR), 7, '0')
                ) AS 'Documento',
                IF(
                    cx.cx_valor < 0,
                    ' 6', # hp de devolução
                    ' 1' # hp de serviço
                ) AS 'Hist. Padrao',
                IF(
                    cx.cx_valor > 0,
                    LPAD(REPLACE(CAST(ROUND(cx.cx_valor, 2) AS CHAR),'.',''), 12, '0'), # receita
                    LPAD(REPLACE(CAST(ROUND(cx.cx_valor * -1, 2) AS CHAR),'.',''), 12, '0') # devolucao
                ) AS 'Valor',
                RPAD(
                    CONCAT(
                        IF(
                            cx.cx_valor < 0,
                            'CX DEVOLUCAO',
                            'CX SERVICO'
                        ),
                        ' PROT. ',
                        CONCAT(
                            IF ( cx.Cx_Tipo = 'Registro', 'RE', 'CE' ),
                            '.',
                            CAST(cx.cx_protocolo AS CHAR)
                        )
                    ), 32, ' '
                ) AS 'Historico'
            FROM sqlreg3.cx AS cx
            WHERE cx.cx_valor != 0 AND cx.cx_data BETWEEN '{0}' AND '{1}'

            UNION ALL

            SELECT
                LPAD(CAST(DAY(final.ret_dataConfirmacao) AS CHAR), 2, '0') AS 'Dia',
                LPAD(CAST(MONTH(final.ret_dataConfirmacao) AS CHAR), 2, '0') AS 'Mes',
                '1010002' AS 'Conta Devedora',
                '1010001' AS 'Conta Credora',
                CONCAT(
                    IF(final.Tipo = 'Registro', '99', '88'),
                    '',
                    LPAD(CAST(final.Protocolo AS CHAR), 7, '0')
                ) AS 'Documento',
                ' 4' AS 'Hist. Padrao',
                LPAD(REPLACE(
                    CAST(ROUND(SUM(final.sel_valor_emolumentos), 2) AS CHAR),
                    '.',
                    ''
                ), 12, '0') AS 'Valor',
                RPAD(
                    CONCAT(
                        'DP EMOLUMENTO',
                        ' PROT. ',
                        CONCAT(
                            IF(final.Tipo = 'Registro', 'RE', 'CE'),
                            '.',
                            CAST(final.Protocolo AS CHAR)
                        )
                    ), 32, ' '
                ) AS 'Historico'
            FROM (

                SELECT DISTINCT
                    result.ret_dataConfirmacao,
                    result.Protocolo,
                    result.Tipo,
                    result.se_num,
                    result.sel_valor_emolumentos
                FROM (

                    SELECT DISTINCT
                        protocolos.ret_dataConfirmacao,
                        IF (
                            protocolos.Protocolo IS NULL AND sl1c.c1_protocolo IS NULL,
                            NULL,
                            IF (protocolos.ds_Escopo = 'esCe;', 'Certidão', 'Registro')
                        ) AS Tipo,
                        COALESCE(sl1c.c1_protocolo, protocolos.Protocolo) AS Protocolo,
                        protocolos.se_num, protocolos.sel_valor_emolumentos
                    FROM (

                        SELECT DISTINCT
                            COALESCE(sl1c.c1_protocolo, ssc.sc_protocolo) AS Protocolo,
                            destinos.pse_idCusta,
                            destinos.ds_Escopo,
                            destinos.ret_dataConfirmacao,
                            destinos.se_num,
                            destinos.sel_valor_emolumentos
                        FROM (

                            SELECT DISTINCT
                                sds.ds_destino,
                                sds.ds_Escopo,
                                sc1s.pse_idCusta,
                                selos.ret_dataConfirmacao,
                                selos.se_num,
                                selos.sel_valor_emolumentos
                            FROM (

                                SELECT DISTINCT
                                    er.ret_dataConfirmacao,
                                    ss.Se_Id, ss.se_num,
                                    es.sel_valor_emolumentos
                                FROM eselo.retorno er
                                INNER JOIN eselo.selo_retorno esr ON(er.ret_id = esr.ser_retorno)
                                INNER JOIN eselo.selo es ON(esr.ser_selo = es.sel_id)
                                LEFT JOIN sqlreg3.selo ss ON(es.sel_numero = ss.se_num)
                                WHERE er.ret_dataConfirmacao BETWEEN '{0}' AND '{1}'
                                    AND er.ret_situacao = 'PROCESSADO_COM_SUCESSO'
                                    AND es.sel_status != 'Cancelado'
                                    AND es.sel_valor_emolumentos != 0

                            ) AS selos
                            LEFT JOIN sqlreg3.destino_selo sds ON(
                                selos.Se_Id = sds.ds_selo
                                AND (sds.ds_Escopo = 'esAn;' OR sds.ds_Escopo = 'esCe;')
                            )
                            LEFT JOIN sqlreg3.c1_se sc1s ON(selos.Se_Id = sc1s.pse_idSe)

                            ) AS destinos
                        LEFT JOIN sqlreg3.l1custa sl1c ON(
                            destinos.ds_destino = sl1c.C1_IdAn
                            AND destinos.ds_Escopo = 'esAn;'
                        )
                        LEFT JOIN sqlreg3.sc ssc ON(
                            destinos.ds_destino = ssc.Sc_Id
                            AND destinos.ds_Escopo = 'esCe;'
                        )

                    ) AS protocolos
                    LEFT JOIN sqlreg3.l1custa sl1c ON(protocolos.pse_idCusta = sl1c.C1_Id)

                ) AS result
                LEFT JOIN sqlreg3.l1 sl1 ON(
                    result.Protocolo = sl1.L1_Protocolo
                    AND result.Tipo = 'Registro'
                )
                LEFT JOIN sqlreg3.rc src ON (
                    result.Protocolo = src.rc_protocolo
                    AND result.Tipo = 'Certidão'
                )
                WHERE result.Protocolo IS NOT NULL
                    AND sl1.L1_Ativo = 0 OR src.Rc_Ativo = 0

            ) AS final
            GROUP BY final.Protocolo

        )AS final
        ORDER BY final.Mes, final.Dia
    """

    try:
        result_db, qtd_rows = query_with_fetchall(
            query_escriba.format(
                data_ini,
                data_end,
            )
        )

        if qtd_rows > 0:  # if there's no row returned by the query
            empty_queries = False
        
    except Exception as e:
        erro += f'Houve um erro ao recuperar informações no banco de dados: \n{e}\n'

    try:
        despesas = Despesa.objects.filter(
            data_despesa__range=(data_ini, data_end),
            categoria_despesa__relatorios=True,
        )

        if despesas.count() > 0:
            empty_queries = False
            qtd_rows += despesas.count()

    except Exception as e:
        erro += f'Houve um erro ao recuperar informações no banco de dados: \n{e}\n'

    if empty_queries:
        erro += f'Não foram encontrados dados para a solicitação.\n'

    if not erro:
        output_file, output_file_url = create_output_file(
            f'RecDesp_{data_ini.strftime("%Y-%m-%d")}.'
            f'{data_end.strftime("%Y-%m-%d")}_{str(uuid.uuid4())[:4]}.txt'
        )

        with open(output_file, 'a') as f:
            for row in result_db:
                f.write(' '.join(row) + '\r\n')

                if row[5] == ' 6':  # devolução via caixa
                    """
                    Uma vez identificado uma devolução no caixa,
                    deve-se criar um registro adicional de devolução,
                    mas este ultimo deve creditar da conta de depósito
                    prévio e debitar na conta do caixa.
                    """
                    new_row = list(row)
                    new_row[2] = '1000001'  # conta do caixa
                    new_row[3] = '1010001'  # conta do depósito prévio
                    new_row[7] = 'DP' + new_row[7][2:]  # alteração no histórico do registro

                    f.write(' '.join(new_row) + '\r\n')
                    qtd_rows += 1  # adiciona 1 para cada registro extra de devolução

                if row[5] == ' 1':  # devolução via caixa
                    """
                    Uma vez identificado uma receita de serviço no caixa,
                    deve-se criar um registro adicional de receita
                    (débito) para o depósito prévio, creditando do valor do caixa.
                    """
                    new_row = list(row)
                    new_row[2] = '1010001'  # conta do depósito prévio
                    new_row[3] = '1000001'  # conta do caixa
                    new_row[5] = ' 2'  # historico padrão para esta operação
                    new_row[7] = 'DP' + new_row[7][2:]  # alteração no histórico do registro

                    f.write(' '.join(new_row) + '\r\n')
                    qtd_rows += 1  # adiciona 1 para cada registro extra de receita ao depósito prévio
            
            for despesa in despesas:
                f.write(
                    f'{str(despesa.data_despesa.day).rjust(2, "0")} '  # dia
                    f'{str(despesa.data_despesa.month).rjust(2, "0")} '  # mes
                    f'{str(despesa.categoria_despesa.conta_debito).rjust(7, "0")} ' # conta debito
                    f'{str(despesa.categoria_despesa.conta_credito).rjust(7, "0")} ' # conta credito
                    f'66{str(despesa.categoria_despesa.codigo_rf)[:7].rjust(7, "0")} '  # documento
                    f' 5 '  #historico padrão
                    f'{str(despesa.valor).replace(".", "").rjust(12, "0")} '  # valor
                    f'{str(despesa.identificacao.identificacao)[:32].upper().ljust(32, " ")}\r\n'  # historico
                )

    return erro, output_file_url, qtd_rows

