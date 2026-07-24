package com.financaspessoal.app.data

import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface FinancasApi {
    @POST("api/auth/token/")
    suspend fun login(@Body body: LoginRequest): TokenResponse

    @GET("api/v1/dashboard/")
    suspend fun dashboard(@Query("mes") mes: String? = null): DashboardDto

    @GET("api/v1/saldo/")
    suspend fun saldo(): SaldoDto

    @GET("api/v1/previsao/")
    suspend fun previsao(): List<PrevisaoLinhaDto>

    @GET("api/v1/contas/")
    suspend fun contas(): List<ContaDto>

    @GET("api/v1/cartoes/")
    suspend fun cartoes(): List<CartaoDto>

    @GET("api/v1/categorias/")
    suspend fun categorias(): List<CategoriaDto>

    @GET("api/v1/receitas/")
    suspend fun receitas(): List<ReceitaDto>

    @GET("api/v1/despesas/")
    suspend fun despesas(): List<DespesaDto>

    @GET("api/v1/investimentos/")
    suspend fun investimentos(): List<InvestimentoDto>

    @GET("api/v1/bens/")
    suspend fun bens(): List<BemDto>

    @GET("api/v1/orcamentos/")
    suspend fun orcamentos(): List<OrcamentoDto>
}
