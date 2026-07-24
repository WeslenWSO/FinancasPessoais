import json
from decimal import Decimal

from django.db import transaction

from financas.defaults import DEFAULT_CATEGORIAS_DESPESA, DEFAULT_CATEGORIAS_RECEITA
from financas.models import (
    Bem,
    Cartao,
    Categoria,
    Conta,
    Despesa,
    Investimento,
    Orcamento,
    Receita,
    gerar_legacy_id,
)


def _legacy(item):
    return item.legacy_id or str(item.pk)


def _serialize_conta(c):
    return {
        'id': _legacy(c),
        'nome': c.nome,
        'tipo': c.tipo,
        'saldoInicial': float(c.saldo_inicial),
    }


def _serialize_cartao(c):
    return {
        'id': _legacy(c),
        'nome': c.nome,
        'contaPagamentoId': _legacy(c.conta_pagamento) if c.conta_pagamento else None,
        'limite': float(c.limite),
        'diaFechamento': c.dia_fechamento,
        'diaVencimento': c.dia_vencimento,
    }


def _serialize_categoria(c):
    data = {
        'id': _legacy(c),
        'nome': c.nome,
        'cor': c.cor,
    }
    if c.pai_id:
        data['paiId'] = _legacy(c.pai)
    return data


def _serialize_receita(r):
    data = {
        'id': _legacy(r),
        'descricao': r.descricao,
        'valor': float(r.valor) if r.valor is not None else None,
        'categoriaId': _legacy(r.categoria) if r.categoria_id else None,
        'contaId': _legacy(r.conta),
        'tipo': r.tipo,
        'ativa': r.ativa,
    }
    if r.data:
        data['data'] = r.data.isoformat()
    if r.dia_recebimento:
        data['diaRecebimento'] = r.dia_recebimento
    if r.data_inicio:
        data['dataInicio'] = r.data_inicio.isoformat()
    if r.data_fim:
        data['dataFim'] = r.data_fim.isoformat()
    if r.numero_parcelas:
        data['numeroParcelas'] = r.numero_parcelas
    if r.repeticao_id:
        data['repeticaoId'] = r.repeticao_id
    return data


def _serialize_despesa(d):
    data = {
        'id': _legacy(d),
        'descricao': d.descricao,
        'categoriaId': _legacy(d.categoria) if d.categoria_id else None,
        'formaPagamento': d.forma_pagamento,
        'tipo': d.tipo,
        'ativa': d.ativa,
    }
    if d.conta_id:
        data['contaId'] = _legacy(d.conta)
    if d.cartao_id:
        data['cartaoId'] = _legacy(d.cartao)
    if d.valor is not None:
        data['valor'] = float(d.valor)
    if d.valor_fixo is not None:
        data['valorFixo'] = float(d.valor_fixo)
    if d.data:
        data['data'] = d.data.isoformat()
    if d.dia_vencimento:
        data['diaVencimento'] = d.dia_vencimento
    if d.data_inicio:
        data['dataInicio'] = d.data_inicio.isoformat()
    if d.data_fim:
        data['dataFim'] = d.data_fim.isoformat()
    if d.numero_parcelas:
        data['numeroParcelas'] = d.numero_parcelas
    if d.compra_id:
        data['compraId'] = d.compra_id
    if d.parcela_atual:
        data['parcelaAtual'] = d.parcela_atual
    if d.parcela_total:
        data['parcelaTotal'] = d.parcela_total
    if d.repeticao_id:
        data['repeticaoId'] = d.repeticao_id
    return data


def _serialize_investimento(i):
    data = {
        'id': _legacy(i),
        'descricao': i.descricao,
        'tipoInvestimento': i.tipo_investimento,
        'operacao': i.operacao,
        'contaId': _legacy(i.conta),
        'data': i.data.isoformat(),
        'valor': float(i.valor),
    }
    if i.ativo_grupo:
        data['ativoGrupo'] = i.ativo_grupo
    if i.valor_estimado_atual is not None:
        data['valorEstimadoAtual'] = float(i.valor_estimado_atual)
    return data


def _serialize_bem(b):
    data = {
        'id': _legacy(b),
        'descricao': b.descricao,
        'tipo': b.tipo,
        'valorAquisicao': float(b.valor_aquisicao),
    }
    if b.data_aquisicao:
        data['dataAquisicao'] = b.data_aquisicao.isoformat()
    if b.valor_estimado_atual is not None:
        data['valorEstimadoAtual'] = float(b.valor_estimado_atual)
    return data


def _serialize_orcamento(o):
    return {
        'id': _legacy(o),
        'categoriaId': _legacy(o.categoria),
        'valorPlanejado': float(o.valor_planejado),
    }


def export_backup(user) -> dict:
    return {
        'contas': [_serialize_conta(c) for c in Conta.objects.filter(user=user)],
        'cartoes': [_serialize_cartao(c) for c in Cartao.objects.filter(user=user)],
        'catReceita': [
            _serialize_categoria(c)
            for c in Categoria.objects.filter(user=user, tipo=Categoria.TIPO_RECEITA)
        ],
        'catDespesa': [
            _serialize_categoria(c)
            for c in Categoria.objects.filter(user=user, tipo=Categoria.TIPO_DESPESA)
        ],
        'receitas': [_serialize_receita(r) for r in Receita.objects.filter(user=user)],
        'despesas': [_serialize_despesa(d) for d in Despesa.objects.filter(user=user)],
        'investimentos': [_serialize_investimento(i) for i in Investimento.objects.filter(user=user)],
        'bens': [_serialize_bem(b) for b in Bem.objects.filter(user=user)],
        'orcamentos': [_serialize_orcamento(o) for o in Orcamento.objects.filter(user=user)],
    }


def _mesclar_categorias_padrao(tipo, lista_importada):
    seed = DEFAULT_CATEGORIAS_RECEITA if tipo == Categoria.TIPO_RECEITA else DEFAULT_CATEGORIAS_DESPESA
    existentes = list(lista_importada or [])
    nomes = {(c.get('nome') or '').strip().lower() for c in existentes}
    for s in seed:
        if s['nome'].strip().lower() not in nomes:
            existentes.append({'id': gerar_legacy_id(), **s})
    return existentes


@transaction.atomic
def import_backup(user, data: dict):
    Despesa.objects.filter(user=user).delete()
    Receita.objects.filter(user=user).delete()
    Investimento.objects.filter(user=user).delete()
    Orcamento.objects.filter(user=user).delete()
    Bem.objects.filter(user=user).delete()
    Cartao.objects.filter(user=user).delete()
    Conta.objects.filter(user=user).delete()
    Categoria.objects.filter(user=user).delete()

    id_map = {}

    def map_id(old_id, obj):
        if old_id:
            id_map[str(old_id)] = obj

    cat_receita = _mesclar_categorias_padrao(Categoria.TIPO_RECEITA, data.get('catReceita'))
    cat_despesa = _mesclar_categorias_padrao(Categoria.TIPO_DESPESA, data.get('catDespesa'))

    categorias = {}
    for raw in cat_receita:
        c = Categoria.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            nome=raw['nome'],
            cor=raw.get('cor', '#0d9488'),
            tipo=Categoria.TIPO_RECEITA,
        )
        map_id(raw.get('id'), c)
        categorias[c.legacy_id] = c

    for raw in cat_despesa:
        c = Categoria.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            nome=raw['nome'],
            cor=raw.get('cor', '#e11d48'),
            tipo=Categoria.TIPO_DESPESA,
        )
        map_id(raw.get('id'), c)
        categorias[c.legacy_id] = c

    for raw in cat_receita + cat_despesa:
        pai_id = raw.get('paiId')
        if pai_id and str(pai_id) in id_map:
            cat = id_map.get(str(raw.get('id')))
            if cat:
                cat.pai = id_map[str(pai_id)]
                cat.save(update_fields=['pai'])

    contas = {}
    for raw in data.get('contas', []):
        c = Conta.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            nome=raw['nome'],
            tipo=raw.get('tipo', 'Conta Corrente'),
            saldo_inicial=Decimal(str(raw.get('saldoInicial', 0))),
        )
        map_id(raw.get('id'), c)
        contas[c.legacy_id] = c

    cartoes = {}
    for raw in data.get('cartoes', []):
        conta_ref = id_map.get(str(raw.get('contaPagamentoId')))
        if not conta_ref:
            continue
        c = Cartao.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            nome=raw['nome'],
            conta_pagamento=conta_ref,
            limite=Decimal(str(raw.get('limite', 0))),
            dia_fechamento=raw['diaFechamento'],
            dia_vencimento=raw['diaVencimento'],
        )
        map_id(raw.get('id'), c)
        cartoes[c.legacy_id] = c

    def resolve_cat(ref):
        return id_map.get(str(ref)) if ref else None

    def resolve_conta(ref):
        return id_map.get(str(ref)) if ref else None

    def resolve_cartao(ref):
        return id_map.get(str(ref)) if ref else None

    for raw in data.get('receitas', []):
        conta = resolve_conta(raw.get('contaId'))
        if not conta:
            continue
        Receita.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            descricao=raw['descricao'],
            valor=raw.get('valor'),
            categoria=resolve_cat(raw.get('categoriaId')),
            conta=conta,
            tipo=raw.get('tipo', 'variavel'),
            data=raw.get('data'),
            dia_recebimento=raw.get('diaRecebimento'),
            data_inicio=raw.get('dataInicio'),
            data_fim=raw.get('dataFim'),
            numero_parcelas=raw.get('numeroParcelas'),
            ativa=raw.get('ativa', True),
            repeticao_id=raw.get('repeticaoId', ''),
        )

    for raw in data.get('despesas', []):
        Despesa.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            descricao=raw['descricao'],
            categoria=resolve_cat(raw.get('categoriaId')),
            forma_pagamento=raw.get('formaPagamento', 'conta'),
            conta=resolve_conta(raw.get('contaId')),
            cartao=resolve_cartao(raw.get('cartaoId')),
            tipo=raw.get('tipo', 'variavel'),
            valor=raw.get('valor'),
            valor_fixo=raw.get('valorFixo'),
            data=raw.get('data'),
            dia_vencimento=raw.get('diaVencimento'),
            data_inicio=raw.get('dataInicio'),
            data_fim=raw.get('dataFim'),
            numero_parcelas=raw.get('numeroParcelas'),
            ativa=raw.get('ativa', True),
            compra_id=raw.get('compraId', ''),
            parcela_atual=raw.get('parcelaAtual'),
            parcela_total=raw.get('parcelaTotal'),
            repeticao_id=raw.get('repeticaoId', ''),
        )

    for raw in data.get('investimentos', []):
        conta = resolve_conta(raw.get('contaId'))
        if not conta:
            continue
        Investimento.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            descricao=raw['descricao'],
            tipo_investimento=raw.get('tipoInvestimento', 'Outro'),
            operacao=raw.get('operacao', 'aporte'),
            ativo_grupo=raw.get('ativoGrupo', ''),
            conta=conta,
            data=raw['data'],
            valor=raw['valor'],
            valor_estimado_atual=raw.get('valorEstimadoAtual'),
        )

    for raw in data.get('bens', []):
        Bem.objects.create(
            user=user,
            legacy_id=raw.get('id') or gerar_legacy_id(),
            descricao=raw['descricao'],
            tipo=raw.get('tipo', 'Terreno'),
            data_aquisicao=raw.get('dataAquisicao'),
            valor_aquisicao=raw['valorAquisicao'],
            valor_estimado_atual=raw.get('valorEstimadoAtual'),
        )

    for raw in data.get('orcamentos', []):
        cat = resolve_cat(raw.get('categoriaId'))
        if not cat:
            continue
        Orcamento.objects.update_or_create(
            user=user,
            categoria=cat,
            defaults={
                'legacy_id': raw.get('id') or gerar_legacy_id(),
                'valor_planejado': raw.get('valorPlanejado', 0),
            },
        )

    return True


def export_backup_json(user) -> str:
    return json.dumps(export_backup(user), indent=2, ensure_ascii=False)
