package com.financaspessoal.app.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.financaspessoal.app.ui.Formatters
import com.financaspessoal.app.ui.theme.NegRed
import com.financaspessoal.app.ui.theme.PosGreen
import com.financaspessoal.app.ui.theme.TextMuted

@Composable
fun KpiCard(label: String, value: String, positive: Boolean? = null, modifier: Modifier = Modifier) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(Modifier.padding(16.dp)) {
            Text(label.uppercase(), fontSize = 11.sp, color = TextMuted, letterSpacing = 0.5.sp)
            Spacer(Modifier.height(6.dp))
            Text(
                value,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = when (positive) {
                    true -> PosGreen
                    false -> NegRed
                    null -> MaterialTheme.colorScheme.onSurface
                },
            )
        }
    }
}

@Composable
fun LoadingBox(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize(), contentAlignment = androidx.compose.ui.Alignment.Center) {
        CircularProgressIndicator()
    }
}

@Composable
fun ErrorBox(message: String, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = androidx.compose.ui.Alignment.CenterHorizontally,
    ) {
        Text(message, color = NegRed)
        Spacer(Modifier.height(12.dp))
        Button(onClick = onRetry) { Text("Tentar novamente") }
    }
}

@Composable
fun MoneyText(value: Double, positive: Boolean? = null) {
    Text(
        Formatters.money(value),
        color = when (positive) {
            true -> PosGreen
            false -> NegRed
            null -> MaterialTheme.colorScheme.onSurface
        },
        fontWeight = FontWeight.SemiBold,
    )
}
