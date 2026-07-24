package com.financaspessoal.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = TealPrimary,
    onPrimary = Color.White,
    secondary = TealDark,
    background = BgLight,
    surface = Color.White,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    error = NegRed,
)

@Composable
fun FinancasTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColors,
        content = content,
    )
}
