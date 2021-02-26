from escribadbquery.views import query_with_fetchall
from ._create_output_file import create_output_file
import xlsxwriter
import uuid


def make_dp_worksheet(data_ini, data_end):
    """
    Make Depósito Prévio Worksheet / Cria planilha do relatório de Depósito Prévio.
    Busca pelas informações no banco de dados e gera o XLSX para download.
    retorna status de erro e url para o arquivo.
    :param data_ini:
    :param data_end:
    :param result_db:
    :return error, output_file:
    """
    erro, output_file_url, qtd_rows = '', None, None
    query_escriba = (
        "SELECT final.Tipo, final.Protocolo, final.StatusProtocolo, final.DataInclusao, final.DepositoPrevio, "
        "final.DataEncerramento, final.ValorTotal, final.DataCompDev, final.CompDev, final.Saldo, "
        "final.Emolumentos, IF(final.Observacoes IS NOT NULL, final.Observacoes, IF(final.DataCompDev IS NULL AND  "
        "(final.CompDev IS NOT NULL AND final.CompDev != 0), 'Verificar Caixa', NULL ) ) AS Observacoes FROM ( "
        "SELECT DISTINCT result2.Tipo, result2.Protocolo, result2.StatusProtocolo, result2.DataInclusao, "
        "result2.DepositoPrevio, result2.DataEncerramento, result2.ValorTotal, scx.cx_data AS 'DataCompDev', "
        "result2.CompDev, result2.Saldo, result2.Emolumentos, result2.Observacoes FROM ( SELECT result.Tipo, "
        "result.Protocolo, IF(result.Cancelado = 1, 'Cancelado', IF(result.StatusProtocolo = 1, 'Ativo', "
        "'Encerrado')) AS StatusProtocolo, result.DataInclusao, IF(result.StatusProtocolo = 1, "
        "ROUND(SUM(scx.cx_valor), 2), ROUND(scx.cx_valor, 2)) AS DepositoPrevio, result.DataEncerramento,  "
        "IF(result.DataEncerramento IS NULL, NULL, ROUND(result.ValorTotal, 2)) AS ValorTotal, "
        "IF(result.DataEncerramento IS NULL, NULL, ROUND(result.ValorTotal - scx.cx_valor, 2)) AS CompDev, "
        "ROUND(SUM(scx.cx_valor), 2) AS Saldo, IF(result.DataEncerramento IS NULL, NULL, IF(SUM(scx.cx_valor) > 0, "
        "ROUND(result.Emolumentos, 2), 0.00)) AS Emolumentos,  IF( (COUNT(scx.Cx_Id) > 2 AND result.Cancelado = 0) "
        "OR  (scx.cx_valor IS NULL AND result.ValorTotal > 0 AND result.Cancelado = 0),  'Verificar Caixa',  "
        "IF(scx.cx_valor < 0, 'Escriba (Problema Custas)', NULL) ) as Observacoes FROM( SELECT 'Certidão' AS Tipo, "
        "ssc.sc_protocolo AS Protocolo, src.Rc_Ativo AS StatusProtocolo, src.rc_cancelado AS Cancelado, "
        "src.rc_dataInclusao AS DataInclusao, src.Rc_DataEncerramento AS DataEncerramento,  "
        "SUM(ssc.sc_valorUnitario * ssc.sc_qtd) AS ValorTotal, SUM(ssc.sc_valor1 * ssc.sc_qtd) AS Emolumentos FROM "
        "sqlreg3.rc src INNER JOIN sqlreg3.sc ssc ON (src.rc_protocolo = ssc.sc_protocolo) WHERE "
        "src.rc_dataInclusao BETWEEN '{0}' AND '{1}' GROUP BY ssc.sc_protocolo ) AS result LEFT JOIN sqlreg3.cx scx"
        " ON (result.Protocolo = scx.cx_protocolo AND scx.Cx_Tipo = 'Certidão') GROUP BY result.Protocolo ORDER BY "
        "scx.cx_valor ) AS result2 LEFT JOIN sqlreg3.cx scx ON (result2.Protocolo = scx.cx_protocolo AND "
        "scx.Cx_Tipo = 'Certidão' AND scx.cx_valor = result2.CompDev) UNION SELECT DISTINCT result2.Tipo, "
        "result2.Protocolo, result2.StatusProtocolo, result2.DataInclusao, result2.DepositoPrevio, "
        "result2.DataEncerramento, result2.ValorTotal, scx.cx_data AS 'DataCompDev', result2.CompDev, "
        "result2.Saldo, result2.Emolumentos, result2.Observacoes FROM ( SELECT result.Tipo, result.Protocolo, "
        "result.StatusProtocolo, result.DataInclusao, IF(result.StatusProtocolo = 'Ativo', ROUND(SUM(scx.cx_valor),"
        " 2), ROUND(result.DepositoPrevio, 2)) as DepositoPrevio, result.DataEncerramento, "
        "IF(result.DataEncerramento IS NULL, NULL, ROUND(result.ValorTotal, 2)) AS ValorTotal, "
        "IF(result.DataEncerramento IS NULL, NULL, ROUND(result.CompDev, 2)) AS CompDev, ROUND(SUM(scx.cx_valor), "
        "2) AS Saldo, IF(result.DataEncerramento IS NULL, NULL, IF(SUM(scx.cx_valor) > 0 , "
        "ROUND(result.Emolumentos, 2), 0.00)) AS Emolumentos, IF( (COUNT(scx.Cx_Id) > 2 and result.StatusProtocolo "
        "= 'Cancelado') or  (scx.cx_valor IS NULL and result.ValorTotal > 0 and result.StatusProtocolo = "
        "'Cancelado'),  'Verificar Caixa', NULL ) as Observacoes FROM ( SELECT protocolos.Tipo, "
        "protocolos.L1_Protocolo AS Protocolo, protocolos.StatusProtocolo, protocolos.DataInclusao, "
        "protocolos.DepositoPrevio, protocolos.DataEncerramento, SUM(sl1c.c1_total * sl1c.c1_qtd) AS ValorTotal, "
        "SUM(sl1c.c1_valor1 * sl1c.c1_qtd) AS Emolumentos, SUM(sl1c.c1_total * sl1c.c1_qtd) - "
        "protocolos.DepositoPrevio AS CompDev FROM ( SELECT 'Registro' AS Tipo, srr.Rr_Protocolo, sl1.L1_Protocolo,"
        " IF (sl1.L1_Anotacao like '%cancelado%', 'Cancelado', IF(sl1.l1_duvida = 1, 'Dúvida Registral', "
        "IF(sl1.L1_Ativo = 1, 'Ativo', 'Encerrado') ) ) AS StatusProtocolo, srr.rr_dataInclusao AS DataInclusao, "
        "SUM( ssr.sr_valorUnitario * ssr.sr_qtd) AS DepositoPrevio, sl1.L1_DataEncerramento AS DataEncerramento "
        "FROM sqlreg3.rr srr INNER JOIN sqlreg3.l1 sl1 ON(srr.Rr_Protocolo = sl1.L1_ProtRecep) LEFT JOIN sqlreg3.sr"
        " ssr on(srr.Rr_Protocolo = ssr.sr_protocolo) WHERE srr.rr_dataInclusao BETWEEN '{0}' AND '{1}' GROUP BY "
        "srr.Rr_Protocolo ) AS protocolos LEFT JOIN sqlreg3.l1custa sl1c on(protocolos.L1_Protocolo = "
        "sl1c.c1_protocolo) GROUP BY protocolos.L1_Protocolo ) AS result LEFT JOIN sqlreg3.cx scx "
        "ON(result.Protocolo = scx.cx_protocolo AND scx.Cx_Tipo = 'Registro') GROUP BY "
        "result.Protocolo ) AS result2 LEFT JOIN sqlreg3.cx scx ON(result2.Protocolo = scx.cx_protocolo AND "
        "scx.Cx_Tipo = 'Registro' AND scx.cx_valor = result2.CompDev) ) AS final ORDER BY final.DataInclusao, "
        "final.Tipo, final.Protocolo"
    )

    try:
        result_db, qtd_rows = query_with_fetchall(query_escriba.format(data_ini, data_end))
        if qtd_rows < 1:  # if there's no row returned by the query
            raise Exception('Não foram encontradas informações para a busca indicada.')
    except Exception as e:
        erro += f'Houve um erro ao recuperar informações no banco de dados: \n{e}'
    else:
        output_file, output_file_url = create_output_file(
            f'RelDepPrev_{data_ini.strftime("%Y-%m-%d")}.{data_end.strftime("%Y-%m-%d")}_{str(uuid.uuid4())[:4]}.xlsx'
        )
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet('Relatório de Depósito Prévio')

        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        currency_format = workbook.add_format({'num_format': 'R$#,##0.00;-R$#,##0.00'})
        start_line = 2
        total_lines = qtd_rows + start_line

        worksheet.add_table(
            f'C{start_line}:N{total_lines}',
            {
                'columns': [
                    {'header': 'Tipo'},
                    {'header': 'Protocolo'},
                    {'header': 'Status'},
                    {'header': 'Data Inc.'},
                    {'header': 'Depósito Prévio'},
                    {'header': 'Data Enc.'},
                    {'header': 'Valor Total'},
                    {'header': 'Data Comp-Dev'},
                    {'header': 'Comp-Dev'},
                    {'header': 'Saldo'},
                    {'header': 'Emolumentos'},
                    {'header': 'Observações'},
                ]
            }
        )
        worksheet.set_column('A:B', 3)
        worksheet.set_column('C:C', 9)
        worksheet.set_column('D:D', 13)
        worksheet.set_column('E:E', 11)
        worksheet.set_column('F:F', 13)
        worksheet.set_column('G:G', 19)
        worksheet.set_column('H:H', 13)
        worksheet.set_column('I:I', 14)
        worksheet.set_column('J:J', 18)
        worksheet.set_column('K:L', 14)
        worksheet.set_column('M:M', 17)
        worksheet.set_column('N:N', 23)

        for row in result_db:
            start_line += 1
            worksheet.write_row(f'C{start_line}', row)
            worksheet.write(f'F{start_line}', row[3], date_format)
            worksheet.write(f'H{start_line}', row[5], date_format)
            worksheet.write(f'J{start_line}', row[7], date_format)
            worksheet.write(f'G{start_line}', row[4], currency_format)
            worksheet.write(f'I{start_line}', row[6], currency_format)
            worksheet.write(f'K{start_line}', row[8], currency_format)
            worksheet.write(f'L{start_line}', row[9], currency_format)
            worksheet.write(f'M{start_line}', row[10], currency_format)

        workbook.close()

    return erro, output_file_url, qtd_rows
