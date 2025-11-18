from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, Request, status
from tortoise.expressions import *
from tortoise.transactions import in_transaction

from src.controllers.sales.note import Note
from src.controllers.sales.sales import Checkout
from src.logs.infos import LOGGER
from src.model.caixa import Caixa
from src.model.cashmovement import CashMovement
from src.model.employee import Employees
from src.model.sale import Sales
from src.model.user import Usuario
from src.utils.user_or_functional import i_request


class CashController:
    @staticmethod
    async def abrir_caixa(
        funcionario_id: int, saldo_inicial: float, nome: str, company_id: int
    ):
        """
        Abre um caixa existente para um funcionário, garantindo que só um fique aberto
        O caixa já foi criado automaticamente no cadastro do funcionário
        """

        # Verifica se o funcionário existe e pertence à empresa
        employee = await Employees.get_or_none(
            usuario_id=company_id, id=funcionario_id
        )
        if not employee:
            raise Exception(
                f'Funcionário não encontrado ou não pertence à empresa'
            )

        # Busca o caixa do funcionário (deve existir pois foi criado automaticamente)
        caixa = await Caixa.filter(
            funcionario_id=funcionario_id, usuario_id=company_id
        ).first()

        if not caixa:
            raise Exception(
                f'Caixa não encontrado para o funcionário {employee.nome}'
            )

        # Verifica se já existe caixa ABERTO para este funcionário
        caixa_aberto_existente = await Caixa.filter(
            funcionario_id=funcionario_id, aberto=True, usuario_id=company_id
        ).first()

        if caixa_aberto_existente:
            # Retorna o caixa já aberto
            print(f'ℹ️  Caixa já está aberto para {employee.nome}')
            return caixa_aberto_existente

        # Se o caixa existe mas está FECHADO, reabre ele
        caixa.aberto = True
        caixa.saldo_inicial = saldo_inicial
        caixa.saldo_atual = saldo_inicial
        caixa.valor_fechamento = None
        caixa.valor_sistema = None
        caixa.diferenca = None
        caixa.atualizado_em = datetime.now(ZoneInfo('America/Sao_Paulo'))

        await caixa.save()

        # Registra movimentação de abertura
        await CashMovement.create(
            tipo='ABERTURA',
            valor=saldo_inicial,
            descricao=f'Abertura do caixa {nome}',
            caixa_id=caixa.id,
            usuario_id=company_id,
            funcionario_id=funcionario_id,
        )

        print(f'✅ Caixa aberto para {employee.nome}: ID {caixa.caixa_id}')
        return caixa

    @staticmethod
    async def registrar_venda_caixa(
        caixa_id: int,
        venda_obj: Sales,
        valor_venda: float,
        forma_pagamento: str,
    ):
        caixa = await Caixa.get_or_none(id=caixa_id)
        if not caixa or not caixa.aberto:
            raise Exception('Caixa não encontrado ou fechado')

        # Verifica se venda_obj é realmente uma instância de Sales
        if not isinstance(venda_obj, Sales):
            raise Exception(f'Objeto de venda inválido: {type(venda_obj)}')

        # Atualiza saldo
        caixa.saldo_atual += float(valor_venda)

        # Converte valor_venda para float se necessário
        if isinstance(valor_venda, str):
            try:
                valor_venda = float(
                    valor_venda.replace('R$', '')
                    .replace('.', '')
                    .replace(',', '.')
                    .strip()
                )
            except ValueError:
                raise Exception(f'Valor de venda inválido: {valor_venda}')

        # Registra movimentação
        await CashMovement.create(
            tipo='ENTRADA',
            valor=valor_venda,
            descricao=f'Venda #{venda_obj.id} - {forma_pagamento}',
            caixa=caixa,
            usuario=caixa.usuario,
            funcionario=caixa.funcionario,
            venda=venda_obj,
        )

        await caixa.save()

        return caixa

    @staticmethod
    async def get_caixa_status(user_id: int, funcionario_id: int = None):
        """
        Método melhorado para verificar status do caixa
        """
        try:
            # Primeiro tenta buscar por funcionário
            if funcionario_id:
                caixa_funcionario = await Caixa.filter(
                    funcionario_id=funcionario_id, aberto=True
                ).first()
                if caixa_funcionario:
                    return {
                        'aberto': True,
                        'caixa': caixa_funcionario,
                        'tipo': 'funcionario',
                        'funcionario_id': funcionario_id,
                    }

            # Se não encontrou por funcionário, busca por usuário/empresa
            caixa_usuario = await Caixa.filter(
                usuario_id=user_id, aberto=True
            ).first()

            if caixa_usuario:
                return {
                    'aberto': True,
                    'caixa': caixa_usuario,
                    'tipo': 'usuario',
                    'funcionario_id': caixa_usuario.funcionario_id,
                }

            # Nenhum caixa aberto encontrado
            return {
                'aberto': False,
                'caixa': None,
                'tipo': None,
                'funcionario_id': funcionario_id,
                'mensagem': 'Nenhum caixa aberto encontrado',
            }

        except Exception as e:
            raise Exception(f'Erro ao verificar status do caixa: {str(e)}')

    @staticmethod
    async def debug_caixa_status(user_id: int, funcionario_id: int = None):
        """
        Método para debug - mostra status de todos os caixas
        """
        caixas_usuario = await Caixa.filter(usuario_id=user_id).all()
        caixas_funcionario = (
            await Caixa.filter(funcionario_id=funcionario_id).all()
            if funcionario_id
            else []
        )

        debug_info = {
            'user_id': user_id,
            'funcionario_id': funcionario_id,
            'caixas_usuario': [
                {
                    'id': c.id,
                    'nome': c.nome,
                    'aberto': c.aberto,
                    'funcionario_id': c.funcionario_id,
                    'usuario_id': c.usuario_id,
                }
                for c in caixas_usuario
            ],
            'caixas_funcionario': [
                {
                    'id': c.id,
                    'nome': c.nome,
                    'aberto': c.aberto,
                    'funcionario_id': c.funcionario_id,
                    'usuario_id': c.usuario_id,
                }
                for c in caixas_funcionario
            ],
            'caixa_aberto_usuario': await Caixa.filter(
                usuario_id=user_id, aberto=True
            ).first(),
            'caixa_aberto_funcionario': await Caixa.filter(
                funcionario_id=funcionario_id, aberto=True
            ).first()
            if funcionario_id
            else None,
        }

        return debug_info

    async def close_checkout(
        employe_id: int, checkout_id: int, company_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Localiza o caixa aberto do funcionário na empresa e realiza o fechamento.

        Args:
            employe_id: ID do funcionário
            checkout_id: ID do caixa a ser fechado
            company_id: ID do usuário/empresa.

        Returns:
            Uma lista de dicionários com os detalhes do fechamento, ou None se nenhum caixa aberto for encontrado.
        """

        # Lista para retornar os dados
        response_data = []

        try:
            # 1. Localiza o caixa aberto
            checkout = await Caixa.filter(
                caixa_id=checkout_id,
                usuario_id=company_id,
            ).first()

            if not checkout:
                return None  # Nenhum caixa aberto encontrado

        except tortoise.expressions.DoesNotExist as error:
            LOGGER.info(
                f'Erro ao realizar busca. Provavelmente não existe [CashController]'
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Erro ao realizar busca do caixa: {error}',
            )

        try:
            # 2. Calcula entradas e saídas
            entries = await CashMovement.filter(
                caixa_id=checkout.id, tipo__in='ENTRADA'
            ).all()
            exits = await CashMovement.filter(
                caixa_id=checkout.id, tipo='SAIDA'
            ).all()

            total_entries = sum([int(movement.valor) for movement in entries])
            total_exits = sum([int(movement.valor) for movement in exits])

            LOGGER.info(
                f'TOTAL_ENTRADAS: {type(total_entries)} TOTAL_SAIDAS: {type(total_exits)}'
            )

            # O valor que o sistema calcula que DEVE estar no caixa
            if isinstance(total_entries, (int, float)) and isinstance(
                total_exits, (int, float)
            ):
                system_value = total_entries - total_exits
            else:
                LOGGER.warning('[VALOR SISTEMA] Valores não são numéricos')
                # Convert to float if they are strings
                try:
                    total_entries = (
                        float(total_entries) if total_entries else 0.0
                    )
                    total_exits = float(total_exits) if total_exits else 0.0
                    system_value = total_entries - total_exits
                except (ValueError, TypeError):
                    system_value = 0.0
                    LOGGER.error(
                        'Não foi possível converter valores para cálculo'
                    )

            # O valor que o funcionário está declarando para o fechamento
            closing_value = round(checkout.saldo_atual, 2)

            # 3. Atualiza caixa
            checkout.valor_fechamento = closing_value
            checkout.valor_sistema = system_value

            if isinstance(closing_value, (int, float)) and isinstance(
                system_value, (int, float)
            ):
                checkout.diferenca = closing_value - system_value
            else:
                LOGGER.warning('Valores de fechamento não são numéricos')

            checkout.aberto = False
            checkout.atualizado_em = datetime.now(
                ZoneInfo('America/Sao_Paulo')
            )

            # Salva as alterações no banco de dados
            await checkout.save()

            # 4. Registra movimentação de fechamento
            closing_description = (
                f'Fechamento do caixa - Sistema: {system_value:.2f}, '
                f'Fechamento: {closing_value:.2f}, Dif: {checkout.diferenca:.2f}'
            )

            await CashMovement.create(
                tipo='FECHAMENTO',
                valor=closing_value,
                descricao=closing_description,
                caixa_id=checkout.id,
                usuario_id=checkout.usuario_id,
                funcionario_id=checkout.funcionario_id,
            )

            # 5. Prepara os dados de retorno
            response_data.append(
                {
                    'type': 'FECHAMENTO',
                    'value': closing_value,
                    'name': checkout.nome,
                    'description': closing_description,
                    'checkout_id': checkout.id,
                    'user_id': checkout.usuario_id,
                    'employe_id': checkout.funcionario_id,
                }
            )

            return response_data

        except Exception as error:
            LOGGER.error(
                f'Erro ao processar fechamento do caixa [CashMovement] {error}'
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Erro interno ao processar fechamento: {error.__class__.__name__}',
            )

    @staticmethod
    async def get_caixa_details(caixa_id: int) -> Dict[str, Any]:
        """
        Retorna o resumo do caixa para fechamento automático:
        - Lista de movimentações do caixa
        - Total de entradas e saídas
        - Saldo atual
        """
        try:
            # Busca o caixa
            caixa = await Caixa.get_or_none(caixa_id=caixa_id).first()
            if not caixa:
                return {'error': 'Caixa não encontrado'}

            # Busca todas as movimentações do caixa
            movimentacoes = await CashMovement.filter(
                caixa_id=caixa_id
            ).order_by('-criado_em')

            # Calcula totais
            entradas = [
                mov
                for mov in movimentacoes
                if mov.tipo in ['ENTRADA', 'ABERTURA']
            ]
            saidas = [mov for mov in movimentacoes if mov.tipo == 'SAIDA']

            total_entradas = sum([int(float(mov.valor)) for mov in entradas])
            total_saidas = sum([int(float(mov.valor)) for mov in saidas])

            if isinstance(total_entradas, (int, float)) and isinstance(
                total_saidas, (int, float)
            ):

                saldo_sistema = total_entradas - total_saidas

            else:

                pass

            # Prepara dados de retorno
            dados = {
                'caixa_id': caixa.id,
                'nome': caixa.nome,
                'saldo_atual': caixa.saldo_atual,
                'saldo_inicial': caixa.saldo_inicial,
                'aberto': caixa.aberto,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_sistema': saldo_sistema,
                'movimentacoes': [
                    {
                        'id': mov.id,
                        'tipo': mov.tipo,
                        'valor': mov.valor,
                        'descricao': mov.descricao,
                        'data': mov.criado_em.strftime('%d/%m/%Y %H:%M'),
                    }
                    for mov in movimentacoes
                ],
            }

            return dados

        except Exception as e:
            LOGGER.error(
                f'Erro ao buscar detalhes do caixa {caixa_id}: {str(e)}'
            )
            return {'error': f'Erro ao buscar detalhes: {str(e)}'}

    @staticmethod
    async def get_caixa_aberto_funcionario(
        usuario_id: int, funcionario_id: int
    ):
        """
        Retorna o caixa aberto de um funcionário, se existir
        """
        return await Caixa.filter(
            usuario_id=usuario_id, funcionario_id=funcionario_id, aberto=True
        ).first()

    @staticmethod
    async def get_caixa_aberto_usuario(usuario_id: int):
        """
        Retorna o caixa aberto de um usuário, se existir
        """
        return await Caixa.filter(usuario_id=usuario_id, aberto=True).first()

    @staticmethod
    async def get_movimentacoes_caixa(caixa_id: int):
        """
        Retorna todas as movimentações de um caixa
        """
        return await CashMovement.filter(caixa_id=caixa_id).order_by(
            '-criado_em'
        )


class FinalizationObjcts:
    def __init__(self, checkout_instance: Checkout = None) -> None:
        self.checkout = checkout_instance
        self.dados_recibo = (
            checkout_instance.receipt_data if checkout_instance else None
        )
        # Adicione uma variável para a nota fiscal
        self.nota_fiscal = None

    async def Updating_cash_values(self, caixa_id: int):
        """
        Passando os campos necessários para atualizar o caixo E gerar a nota fiscal.
        """
        try:
            # 1. VALIDAÇÕES E OBTENÇÃO DE DADOS
            if not self.checkout:
                raise Exception('Instância do Checkout não fornecida')

            venda_obj = self.checkout.venda
            if not venda_obj:
                raise Exception('Venda não encontrada no processo de checkout')

            if not isinstance(venda_obj, Sales):
                raise Exception(
                    f'Tipo inválido para venda: {type(venda_obj)}. Esperado: Sales'
                )

            # 🔴 CORREÇÃO: Garantir que valor_total seja sempre float
            valor_total = 0.0

            if self.checkout.receipt_data and isinstance(
                self.checkout.receipt_data, list
            ):
                # Garantir conversão para float de cada item
                for item in self.checkout.receipt_data:
                    item_total = item.get('total_price', 0)
                    # Converter para float, removendo possíveis formatações de string
                    if isinstance(item_total, str):
                        # Remover formatação de moeda se existir
                        item_total = (
                            item_total.replace('R$', '')
                            .replace('.', '')
                            .replace(',', '.')
                            .strip()
                        )
                    valor_total += float(item_total)
            else:
                # Usar fallbacks com conversão segura
                fallback_value = getattr(
                    self.checkout,
                    'total_price',
                    getattr(venda_obj, 'total_price', 0),
                )
                if isinstance(fallback_value, str):
                    fallback_value = (
                        fallback_value.replace('R$', '')
                        .replace('.', '')
                        .replace(',', '.')
                        .strip()
                    )
                valor_total = float(fallback_value)

            forma_pagamento = getattr(
                self.checkout,
                'payment_method',
                getattr(venda_obj, 'payment_method', 'PIX'),
            )

            # Obtenção de caixa e validação de abertura
            caixa = await Caixa.get_or_none(id=caixa_id).prefetch_related(
                'usuario', 'funcionario'
            )
            if not caixa:
                raise Exception(f'Caixa com ID {caixa_id} não encontrado')
            if not caixa.aberto:
                raise Exception('Caixa está fechado')

            # 2. ATUALIZAÇÃO DO CAIXA - AGORA COM VALOR TOTAL CONVERTIDO
            caixa.saldo_atual += valor_total
            await caixa.save()

            # Preparação de movimento_data - GARANTIR QUE VALOR É FLOAT
            movimento_data = {
                'tipo': 'ENTRADA',
                'valor': float(valor_total),  # 🔴 GARANTIR FLOAT AQUI TAMBÉM
                'descricao': f'Venda #{venda_obj.id} - {forma_pagamento}',
                'caixa_id': caixa.caixa_id,
                'venda_id': venda_obj.id,
                'usuario_id': caixa.usuario.id if caixa.usuario else None,
                'funcionario_id': caixa.funcionario.id
                if caixa.funcionario
                else None,
            }

            # Salva total de vendas do funcionário - GARANTIR FLOAT
            if (
                movimento_data['funcionario_id']
                and movimento_data['usuario_id']
            ):
                await Employees.filter(
                    usuario_id=movimento_data['usuario_id'],
                    id=movimento_data['funcionario_id'],
                ).update(
                    result_of_all_sales=F('result_of_all_sales')
                    + float(movimento_data['valor'])
                )

            # 3. GERAÇÃO DA NOTA FISCAL (mantido igual)

            # 🟢 CORREÇÃO CRÍTICA: Priorizar o usuario_id da venda_obj
            checkout_user_id = self.checkout.user_id

            if not checkout_user_id and venda_obj.usuario_id:
                final_user_id = venda_obj.usuario_id
            else:
                final_user_id = checkout_user_id

            print(
                f'DEBUG FINALIZATION: user_id lido do Checkout: {self.checkout.user_id}'
            )
            print(
                f'DEBUG FINALIZATION: usuario_id lido da Venda_obj: {venda_obj.usuario_id}'
            )
            print(
                f'DEBUG FINALIZATION: user_id corrigido para Note: {final_user_id}'
            )

            # Instanciar Note usando os dados do Checkout
            note_generator = Note(
                user_id=final_user_id,
                product_name=self.checkout.product_name,
                produto_id=self.checkout.produto_id,
                quantity=self.checkout.quantity,
                payment_method=self.checkout.payment_method,
                total_price=valor_total,  # 🔴 USAR O VALOR TOTAL JÁ CONVERTIDO
                lucro_total=self.checkout.lucro_total,
                funcionario_id=self.checkout.funcionario_id,
                funcionario_nome=self.checkout.funcionario_nome,
                sale_code=self.checkout.sale_code,
                customer_id=self.checkout.customer_id,
                installments=self.checkout.installments,
                valor_recebido=self.checkout.valor_recebido,
                troco=self.checkout.troco,
                usuario=caixa.usuario,
            )

            # Transferir dados do recibo
            note_generator._set_receipt_data(self.checkout.receipt_data)

            # Chamar a função de criação da nota
            self.nota_fiscal = await note_generator.createNote()

            # 4. FINALIZAÇÃO E REGISTRO

            # Registra movimentação no CashMovement
            await CashMovement.create(**movimento_data)

            # Atualiza a venda com o caixa_id
            venda_obj.caixa_id = caixa.id
            await venda_obj.save()

            print(
                f'✅ Finalização concluída. Venda #{venda_obj.id}, Caixa atualizado, Nota gerada.'
            )

            # Retorna o caixa e a nota fiscal gerada
            return {'caixa': caixa, 'nota_fiscal': self.nota_fiscal}

        except Exception as e:
            import traceback

            print(f'❌ Erro detalhado ao atualizar caixo/gerar nota: {str(e)}')
            print(f'📋 Traceback: {traceback.format_exc()}')
            raise Exception(f'Erro ao finalizar venda (Caixa/Nota): {str(e)}')
