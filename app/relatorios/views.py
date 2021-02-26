from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from rolepermissions.mixins import HasRoleMixin
from dateutil import parser

from ._make_dp_worksheet import make_dp_worksheet
from ._make_em_worksheet import make_em_worksheet
from ._make_rd_txt_file import make_rd_txt_file
from ._make_cl_txt_file import make_cl_txt_file


class RelatorioView(LoginRequiredMixin, HasRoleMixin, TemplateView):
    allowed_roles = ['oficial', 'contador']
    template_name = 'relatorios.html'


class GetRelatorioView(LoginRequiredMixin, HasRoleMixin, View):
    allowed_roles = ['oficial', 'contador']

    def get(self, request):
        """
        Recebe as data de início de fim do período a ser pesquisado e
        retorna a query em JSON
        """

        jsr = {}  # json response
        tipos_relatorios = {
            'receitas_despesas': 'rd',
            'deposito_previo': 'dp',
            'emolumentos': 'em',
            'carne_leao': 'cl',
        }

        try:
            data_ini = self.request.GET['data_ini']
            data_end = self.request.GET['data_end']
            relatorio = str(self.request.GET['relatorio'])

        except Exception as e:
            jsr['erro'] = f'\nHouve um erro ao receber as variáveis:\n{e}'

        else:
            try:
                data_ini = parser.parse(data_ini)
                data_end = parser.parse(data_end)

                if relatorio not in tipos_relatorios.values():
                    raise Exception

            except Exception as e:
                jsr['erro'] = f'Os valores informados não são válidos: \n{e}'

            else:
                if relatorio == tipos_relatorios['deposito_previo']:
                    jsr['erro'], jsr['file'], jsr['registros'] = make_dp_worksheet(data_ini, data_end)
                    jsr['relatorio'] = 'Relatório de Depósito Prévio'

                elif relatorio == tipos_relatorios['emolumentos']:
                    jsr['erro'], jsr['file'], jsr['registros'] = make_em_worksheet(data_ini, data_end)
                    jsr['relatorio'] = 'Relatório de Emolumentos'

                elif relatorio == tipos_relatorios['receitas_despesas']:
                    jsr['erro'], jsr['file'], jsr['registros'] = make_rd_txt_file(data_ini, data_end)
                    jsr['relatorio'] = 'Relatório de Receitas e Despesas'

                elif relatorio == tipos_relatorios['carne_leao']:
                    jsr['erro'], jsr['file'], jsr['registros'] = make_cl_txt_file(data_ini, data_end)
                    jsr['relatorio'] = 'Relatório de Importação de Escrituração do Carnê Leão'

                else:
                    jsr['erro'] = f'Não foi identificado o tipo de relatório indicado! ({relatorio})'

                jsr['periodo'] = f'{data_ini.strftime("%d/%m/%Y")} a {data_end.strftime("%d/%m/%Y")}'

        return JsonResponse(jsr)
