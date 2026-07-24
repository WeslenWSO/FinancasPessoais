package com.financaspessoal.app.data

import android.content.Context

class FinancasRepository(context: Context) {
    private val apiClient = ApiClient(context)
    private val tokenStore = apiClient.tokenStore()

    private fun api(): FinancasApi = apiClient.createApi()

    val isLoggedInFlow = tokenStore.accessToken
    val apiUrlFlow = tokenStore.apiUrl

    suspend fun login(username: String, password: String) {
        val response = api().login(LoginRequest(username, password))
        tokenStore.saveTokens(response.access, response.refresh)
    }

    suspend fun logout() {
        tokenStore.clear()
    }

    suspend fun setApiUrl(url: String) {
        tokenStore.saveApiUrl(url)
    }

    suspend fun dashboard(mes: String? = null) = api().dashboard(mes)

    suspend fun saldo() = api().saldo()

    suspend fun previsao() = api().previsao()

    suspend fun contas() = api().contas()

    suspend fun cartoes() = api().cartoes()

    suspend fun categorias() = api().categorias()

    suspend fun receitas() = api().receitas()

    suspend fun despesas() = api().despesas()

    suspend fun investimentos() = api().investimentos()

    suspend fun bens() = api().bens()

    suspend fun orcamentos() = api().orcamentos()
}
