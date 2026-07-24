package com.financaspessoal.app.data

import com.google.gson.annotations.SerializedName

data class TokenResponse(
    val access: String,
    val refresh: String,
)

data class PaginatedResponse<T>(
    val count: Int,
    val next: String?,
    val previous: String?,
    val results: List<T>,
)

data class ContaDto(
    val id: Long,
    val nome: String,
    val tipo: String,
    @SerializedName("saldo_inicial") val saldoInicial: String,
)

data class CartaoDto(
    val id: Long,
    val nome: String,
    @SerializedName("conta_pagamento") val contaPagamento: Long,
    val limite: String,
    @SerializedName("dia_fechamento") val diaFechamento: Int,
    @SerializedName("dia_vencimento") val diaVencimento: Int,
)

data class CategoriaDto(
    val id: Long,
    val nome: String,
    val cor: String,
    val tipo: String,
    val pai: Long?,
)

data class ReceitaDto(
    val id: Long,
    val descricao: String,
    val valor: String?,
    val categoria: Long?,
    val conta: Long,
    val tipo: String,
    val data: String?,
    val ativa: Boolean = true,
)

data class DespesaDto(
    val id: Long,
    val descricao: String,
    val valor: String?,
    @SerializedName("valor_fixo") val valorFixo: String?,
    val categoria: Long?,
    @SerializedName("forma_pagamento") val formaPagamento: String,
    val conta: Long?,
    val cartao: Long?,
    val tipo: String,
    val data: String?,
    val ativa: Boolean = true,
)

data class InvestimentoDto(
    val id: Long,
    val descricao: String,
    @SerializedName("tipo_investimento") val tipoInvestimento: String,
    val operacao: String,
    val conta: Long,
    val data: String,
    val valor: String,
)

data class BemDto(
    val id: Long,
    val descricao: String,
    val tipo: String,
    @SerializedName("valor_aquisicao") val valorAquisicao: String,
    @SerializedName("valor_estimado_atual") val valorEstimadoAtual: String?,
)

data class OrcamentoDto(
    val id: Long,
    val categoria: Long,
    @SerializedName("valor_planejado") val valorPlanejado: String,
)

data class DashboardDto(
    val ym: String,
    @SerializedName("saldo_total") val saldoTotal: Double,
    @SerializedName("total_receitas") val totalReceitas: Double,
    @SerializedName("total_despesas") val totalDespesas: Double,
    @SerializedName("saldo_mes") val saldoMes: Double,
    @SerializedName("investido_atual") val investidoAtual: Double,
    @SerializedName("patrimonio_bens") val patrimonioBens: Double,
    @SerializedName("chart_labels") val chartLabels: List<String>,
    @SerializedName("serie_receita") val serieReceita: List<Double>,
    @SerializedName("serie_despesa") val serieDespesa: List<Double>,
)

data class SaldoDto(
    @SerializedName("saldo_total") val saldoTotal: Double,
)

data class PrevisaoLinhaDto(
    val ym: String,
    @SerializedName("saldo_inicial_mes") val saldoInicialMes: Double,
    @SerializedName("receitas_fix") val receitasFix: Double,
    @SerializedName("receitas_var_reais") val receitasVarReais: Double,
    @SerializedName("despesas_fix") val despesasFix: Double,
    @SerializedName("despesas_var_projetadas") val despesasVarProjetadas: Double,
    @SerializedName("faturas_cartao") val faturasCartao: Double,
    @SerializedName("total_despesas") val totalDespesas: Double,
    @SerializedName("saldo_mes") val saldoMes: Double,
    @SerializedName("saldo_acumulado") val saldoAcumulado: Double,
)

data class LoginRequest(
    val username: String,
    val password: String,
)
