package com.financaspessoal.app.ui

import java.text.NumberFormat
import java.util.Locale

object Formatters {
    private val br = Locale("pt", "BR")
    private val money = NumberFormat.getCurrencyInstance(br)

    fun money(value: Double?): String = money.format(value ?: 0.0)

    fun money(value: String?): String = money.format(value?.toDoubleOrNull() ?: 0.0)
}
