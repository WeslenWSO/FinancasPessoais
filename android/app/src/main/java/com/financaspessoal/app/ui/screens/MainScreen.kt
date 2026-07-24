package com.financaspessoal.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Logout
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.financaspessoal.app.ui.AppViewModel
import com.financaspessoal.app.ui.Formatters
import com.financaspessoal.app.ui.components.ErrorBox
import com.financaspessoal.app.ui.components.KpiCard
import com.financaspessoal.app.ui.components.LoadingBox

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(viewModel: AppViewModel) {
    var tab by remember { mutableIntStateOf(0) }
    val tabs = listOf("Início", "Contas", "Receitas", "Despesas", "Mais")

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Finanças Pessoais", fontWeight = FontWeight.SemiBold) },
                actions = {
                    IconButton(onClick = { viewModel.logout() }) {
                        Icon(Icons.AutoMirrored.Filled.Logout, contentDescription = "Sair")
                    }
                },
            )
        },
        bottomBar = {
            NavigationBar {
                tabs.forEachIndexed { index, label ->
                    NavigationBarItem(
                        selected = tab == index,
                        onClick = { tab = index },
                        icon = {
                            Icon(
                                when (index) {
                                    0 -> Icons.Default.Home
                                    1 -> Icons.Default.AccountBalance
                                    2 -> Icons.Default.ArrowUpward
                                    3 -> Icons.Default.ArrowDownward
                                    else -> Icons.Default.MoreHoriz
                                },
                                contentDescription = label,
                            )
                        },
                        label = { Text(label) },
                    )
                }
            }
        },
    ) { padding ->
        Box(Modifier.padding(padding)) {
            when (tab) {
                0 -> DashboardTab(viewModel)
                1 -> ContasTab(viewModel)
                2 -> ReceitasTab(viewModel)
                3 -> DespesasTab(viewModel)
                else -> MoreTab(viewModel)
            }
        }
    }
}

@Composable
private fun DashboardTab(viewModel: AppViewModel) {
    val state by viewModel.dashboard.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadDashboard() }

    when {
        state.loading -> LoadingBox()
        state.error != null -> ErrorBox(state.error!!) { viewModel.loadDashboard() }
        state.data != null -> {
            val d = state.data!!
            LazyColumn(
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                item {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        KpiCard("Saldo hoje", Formatters.money(d.saldoTotal), d.saldoTotal >= 0, Modifier.weight(1f))
                        KpiCard("Saldo mês", Formatters.money(d.saldoMes), d.saldoMes >= 0, Modifier.weight(1f))
                    }
                }
                item {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        KpiCard("Receitas", Formatters.money(d.totalReceitas), true, Modifier.weight(1f))
                        KpiCard("Despesas", Formatters.money(d.totalDespesas), false, Modifier.weight(1f))
                    }
                }
                item {
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        KpiCard("Investido", Formatters.money(d.investidoAtual), null, Modifier.weight(1f))
                        KpiCard("Patrimônio", Formatters.money(d.patrimonioBens), null, Modifier.weight(1f))
                    }
                }
                item {
                    Card(Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp)) {
                            Text("Últimos 6 meses", fontWeight = FontWeight.SemiBold)
                            Spacer(Modifier.height(8.dp))
                            d.chartLabels.zip(d.serieReceita.zip(d.serieDespesa)).forEach { (label, pair) ->
                                Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text(label)
                                    Text("↑ ${Formatters.money(pair.first)}  ↓ ${Formatters.money(pair.second)}")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ContasTab(viewModel: AppViewModel) {
    val state by viewModel.contas.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadContas() }
    EntityList(state, onRetry = { viewModel.loadContas() }) { contas ->
        items(contas) { c ->
            ListItem(
                headlineContent = { Text(c.nome) },
                supportingContent = { Text(c.tipo) },
                trailingContent = { Text(Formatters.money(c.saldoInicial)) },
            )
            HorizontalDivider()
        }
    }
}

@Composable
private fun ReceitasTab(viewModel: AppViewModel) {
    val state by viewModel.receitas.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadReceitas() }
    EntityList(state, onRetry = { viewModel.loadReceitas() }) { items ->
        items(items) { r ->
            ListItem(
                headlineContent = { Text(r.descricao) },
                supportingContent = { Text("${r.tipo} • ${r.data ?: "—"}") },
                trailingContent = { Text(Formatters.money(r.valor), color = MaterialTheme.colorScheme.primary) },
            )
            HorizontalDivider()
        }
    }
}

@Composable
private fun DespesasTab(viewModel: AppViewModel) {
    val state by viewModel.despesas.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadDespesas() }
    EntityList(state, onRetry = { viewModel.loadDespesas() }) { items ->
        items(items) { d ->
            ListItem(
                headlineContent = { Text(d.descricao) },
                supportingContent = { Text("${d.formaPagamento} • ${d.tipo}") },
                trailingContent = { Text(Formatters.money(d.valor ?: d.valorFixo)) },
            )
            HorizontalDivider()
        }
    }
}

@Composable
private fun MoreTab(viewModel: AppViewModel) {
    var section by remember { mutableIntStateOf(0) }
    TabRow(selectedTabIndex = section) {
        Tab(selected = section == 0, onClick = { section = 0 }, text = { Text("Cartões") })
        Tab(selected = section == 1, onClick = { section = 1 }, text = { Text("Previsão") })
    }
    when (section) {
        0 -> CartoesTab(viewModel)
        1 -> PrevisaoTab(viewModel)
    }
}

@Composable
private fun CartoesTab(viewModel: AppViewModel) {
    val state by viewModel.cartoes.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadCartoes() }
    EntityList(state, onRetry = { viewModel.loadCartoes() }) { items ->
        items(items) { c ->
            ListItem(
                headlineContent = { Text(c.nome) },
                supportingContent = { Text("Fecha dia ${c.diaFechamento} • Vence dia ${c.diaVencimento}") },
                trailingContent = { Text(Formatters.money(c.limite)) },
            )
            HorizontalDivider()
        }
    }
}

@Composable
private fun PrevisaoTab(viewModel: AppViewModel) {
    val state by viewModel.previsao.collectAsState()
    LaunchedEffect(Unit) { viewModel.loadPrevisao() }
    EntityList(state, onRetry = { viewModel.loadPrevisao() }) { linhas ->
        items(linhas) { l ->
            ListItem(
                headlineContent = { Text(l.ym) },
                supportingContent = {
                    Text("Rec: ${Formatters.money(l.receitasFix + l.receitasVarReais)} • Desp: ${Formatters.money(l.totalDespesas)}")
                },
                trailingContent = { Text(Formatters.money(l.saldoAcumulado)) },
            )
            HorizontalDivider()
        }
    }
}

@Composable
private fun <T> EntityList(
    state: com.financaspessoal.app.ui.UiState<T>,
    onRetry: () -> Unit,
    content: @Composable androidx.compose.foundation.lazy.LazyListScope.(T) -> Unit,
) {
    when {
        state.loading -> LoadingBox()
        state.error != null -> ErrorBox(state.error!!, onRetry)
        state.data != null -> LazyColumn(content = { content(state.data!!) })
    }
}
