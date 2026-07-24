package com.financaspessoal.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.viewmodel.compose.viewModel
import com.financaspessoal.app.ui.AppViewModel
import com.financaspessoal.app.ui.screens.LoginScreen
import com.financaspessoal.app.ui.screens.MainScreen
import com.financaspessoal.app.ui.theme.FinancasTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FinancasTheme {
                val vm: AppViewModel = viewModel()
                val loggedIn by vm.loggedIn.collectAsState(initial = false)
                if (loggedIn) {
                    MainScreen(vm)
                } else {
                    LoginScreen(vm)
                }
            }
        }
    }
}
