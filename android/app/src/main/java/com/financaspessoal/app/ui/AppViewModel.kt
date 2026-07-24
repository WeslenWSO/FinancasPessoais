package com.financaspessoal.app.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.financaspessoal.app.data.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter

data class UiState<T>(
    val loading: Boolean = false,
    val data: T? = null,
    val error: String? = null,
)

class AppViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = FinancasRepository(application)

    private val _loggedIn = MutableStateFlow(false)
    val loggedIn: StateFlow<Boolean> = _loggedIn.asStateFlow()

    private val _loginError = MutableStateFlow<String?>(null)
    val loginError: StateFlow<String?> = _loginError.asStateFlow()

    private val _apiUrl = MutableStateFlow("")
    val apiUrl: StateFlow<String> = _apiUrl.asStateFlow()

    private val _dashboard = MutableStateFlow(UiState<DashboardDto>())
    val dashboard: StateFlow<UiState<DashboardDto>> = _dashboard.asStateFlow()

    private val _contas = MutableStateFlow(UiState<List<ContaDto>>())
    val contas: StateFlow<UiState<List<ContaDto>>> = _contas.asStateFlow()

    private val _receitas = MutableStateFlow(UiState<List<ReceitaDto>>())
    val receitas: StateFlow<UiState<List<ReceitaDto>>> = _receitas.asStateFlow()

    private val _despesas = MutableStateFlow(UiState<List<DespesaDto>>())
    val despesas: StateFlow<UiState<List<DespesaDto>>> = _despesas.asStateFlow()

    private val _cartoes = MutableStateFlow(UiState<List<CartaoDto>>())
    val cartoes: StateFlow<UiState<List<CartaoDto>>> = _cartoes.asStateFlow()

    private val _previsao = MutableStateFlow(UiState<List<PrevisaoLinhaDto>>())
    val previsao: StateFlow<UiState<List<PrevisaoLinhaDto>>> = _previsao.asStateFlow()

    init {
        viewModelScope.launch {
            repo.isLoggedInFlow.collect { token ->
                _loggedIn.value = !token.isNullOrBlank()
            }
        }
        viewModelScope.launch {
            repo.apiUrlFlow.collect { _apiUrl.value = it }
        }
    }

    fun login(username: String, password: String) {
        viewModelScope.launch {
            _loginError.value = null
            try {
                repo.login(username, password)
                _loggedIn.value = true
            } catch (e: Exception) {
                _loginError.value = "Usuário ou senha inválidos"
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            repo.logout()
            _loggedIn.value = false
        }
    }

    fun updateApiUrl(url: String) {
        viewModelScope.launch {
            repo.setApiUrl(url)
            _apiUrl.value = url
        }
    }

    fun loadDashboard(mes: String? = currentMonth()) {
        viewModelScope.launch {
            _dashboard.value = UiState(loading = true)
            try {
                _dashboard.value = UiState(data = repo.dashboard(mes))
            } catch (e: Exception) {
                _dashboard.value = UiState(error = e.message ?: "Erro ao carregar")
            }
        }
    }

    fun loadContas() = loadList(_contas) { repo.contas() }
    fun loadReceitas() = loadList(_receitas) { repo.receitas() }
    fun loadDespesas() = loadList(_despesas) { repo.despesas() }
    fun loadCartoes() = loadList(_cartoes) { repo.cartoes() }
    fun loadPrevisao() = loadList(_previsao) { repo.previsao() }

    private fun <T> loadList(state: MutableStateFlow<UiState<T>>, block: suspend () -> T) {
        viewModelScope.launch {
            state.value = UiState(loading = true)
            try {
                state.value = UiState(data = block())
            } catch (e: Exception) {
                state.value = UiState(error = e.message ?: "Erro ao carregar")
            }
        }
    }

    companion object {
        fun currentMonth(): String =
            LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM"))
    }
}
