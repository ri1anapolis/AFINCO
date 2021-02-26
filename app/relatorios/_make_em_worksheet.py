from escribadbquery.views import query_with_fetchall
from ._create_output_file import create_output_file
import xlsxwriter
import uuid


def make_em_worksheet(data_ini, data_end):
    """
    Make Emolumentos Worksheet / Cria planilha do relatório de emolumentos.
    Busca pelas informações no banco de dados e gera o XLSX para download.
    retorna status de erro e url para o arquivo.
    :param data_ini:
    :param data_end:
    :param result_db:
    :return error, output_file:
    """
    erro, output_file_url, qtd_rows = '', None, None
    query_escriba = (
        "SELECT final.ret_dataConfirmacao AS DataSeloGerado, CONCAT(final.Tipo, ' - Protocolo: ', CAST(final.Protocolo "
        "AS CHAR)) AS Servico, SUM(final.sel_valor_emolumentos) AS Emolumentos FROM (SELECT DISTINCT "
        "result.ret_dataConfirmacao, result.Protocolo, result.Tipo, result.se_num, result.sel_valor_emolumentos FROM "
        "(SELECT DISTINCT protocolos.ret_dataConfirmacao, IF (protocolos.Protocolo IS NULL AND sl1c.c1_protocolo IS "
        "NULL, NULL, IF (protocolos.ds_Escopo = 'esCe;', 'Certidão', 'Registro')) AS Tipo, COALESCE(sl1c.c1_protocolo, "
        "protocolos.Protocolo) AS Protocolo, protocolos.se_num, protocolos.sel_valor_emolumentos FROM (SELECT DISTINCT "
        "COALESCE(sl1c.c1_protocolo, ssc.sc_protocolo) AS Protocolo, destinos.pse_idCusta, destinos.ds_Escopo, "
        "destinos.ret_dataConfirmacao, destinos.se_num, destinos.sel_valor_emolumentos FROM (SELECT DISTINCT "
        "sds.ds_destino, sds.ds_Escopo, sc1s.pse_idCusta, selos.ret_dataConfirmacao, selos.se_num, "
        "selos.sel_valor_emolumentos FROM (SELECT DISTINCT er.ret_dataConfirmacao, ss.Se_Id, ss.se_num, "
        "es.sel_valor_emolumentos FROM eselo.retorno er INNER JOIN eselo.selo_retorno esr ON(er.ret_id = "
        "esr.ser_retorno) INNER JOIN eselo.selo es ON(esr.ser_selo = es.sel_id) LEFT JOIN sqlreg3.selo ss "
        "ON(es.sel_numero = ss.se_num) WHERE er.ret_dataConfirmacao BETWEEN '{0}' AND '{1}' AND  er.ret_situacao = "
        "'PROCESSADO_COM_SUCESSO' AND es.sel_status != 'Cancelado') AS selos LEFT JOIN sqlreg3.destino_selo sds "
        "ON(selos.Se_Id = sds.ds_selo AND (sds.ds_Escopo = 'esAn;' OR sds.ds_Escopo = 'esCe;')) LEFT JOIN "
        "sqlreg3.c1_se sc1s ON(selos.Se_Id = sc1s.pse_idSe)) AS destinos LEFT JOIN sqlreg3.l1custa sl1c "
        "ON(destinos.ds_destino = sl1c.C1_IdAn AND destinos.ds_Escopo = 'esAn;') LEFT JOIN sqlreg3.sc ssc "
        "ON(destinos.ds_destino = ssc.Sc_Id AND destinos.ds_Escopo = 'esCe;')) AS protocolos LEFT JOIN "
        "sqlreg3.l1custa sl1c ON(protocolos.pse_idCusta = sl1c.C1_Id)) AS result LEFT JOIN sqlreg3.l1 sl1 "
        "ON(result.Protocolo = sl1.L1_Protocolo AND result.Tipo = 'Registro') LEFT JOIN sqlreg3.rc src ON "
        "(result.Protocolo = src.rc_protocolo AND result.Tipo = 'Certidão') WHERE result.Protocolo IS NOT NULL AND "
        "sl1.L1_Ativo = 0 OR src.Rc_Ativo = 0) AS final GROUP BY final.Protocolo ORDER BY final.ret_dataConfirmacao, "
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
            f'RelEmol_{data_ini.strftime("%Y-%m-%d")}.{data_end.strftime("%Y-%m-%d")}_{str(uuid.uuid4())[:4]}.xlsx'
        )
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet('Emolumentos por Protocolo')

        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        currency_format = workbook.add_format({'num_format': 'R$#,##0.00;-R$#,##0.00'})
        start_line = 2
        total_lines = qtd_rows + start_line

        worksheet.add_table(
            f'B{start_line}:D{total_lines}',
            {
                'columns': [
                    {'header': 'Data'},
                    {'header': 'Serviço'},
                    {'header': 'Emolumentos'},
                ]
            }
        )
        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 14)

        for row in result_db:
            start_line += 1
            worksheet.write_row(f'B{start_line}', row)
            worksheet.write(f'B{start_line}', row[0], date_format)
            worksheet.write(f'D{start_line}', row[2], currency_format)

        workbook.close()

    return erro, output_file_url, qtd_rows
