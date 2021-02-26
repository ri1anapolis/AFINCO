from ._create_output_file import create_output_file

from despesas.models import Despesa

import uuid


def make_cl_txt_file(data_ini, data_end):
    """
    Make Carnê Leão Text File / Cria Relatório de Carnê Leão em TXT.
    Busca pelas informações no banco de dados e gera o TXT para download.
    retorna status de erro e url para o arquivo.
    :param data_ini:
    :param data_end:
    :param result_db:
    :return error, output_file:
    """
    erro, output_file_url, qtd_rows, empty_queries = '', None, 0, True
    
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
        """
        O arquivo deve ter a seguinte regra de formação do seu nome:
        99999999999-2019*.TXT ou
        99999999999-2019*.CSV
        Onde:
        99999999999 - é o número de inscrição no CPF do contribuinte;
        2019 - refere-se ao ano-calendário das informações que se deseja importar.
        * - texto opcional para identificar o arquivo (por exemplo: mês dos lançamentos)
        TXT ou CSV - possíveis extensões do arquivo
        """
        output_file, output_file_url = create_output_file(
            f'00211297119-{data_end.strftime("%Y")}-{data_ini.strftime("%Y%m%d")}.'
            f'{data_end.strftime("%Y%m%d")}_{str(uuid.uuid4())[:4]}.txt'
        )

        with open(output_file, 'a') as f:            
            for despesa in despesas:
                f.write(
                    f'{despesa.data_despesa.strftime("%d/%m/%Y")};'  # data
                    f'{despesa.categoria_despesa.codigo_rf};'  # conta/código
                    f'{str(despesa.valor).replace(".", ",")};'  # valor
                    f';'  # CPF do Titular do Pagamento
                    f';'  # CPF do Beneficiário do Serviço
                    f'{despesa.identificacao.identificacao.upper()}\r\n'  # historico
                )

    return erro, output_file_url, qtd_rows

