package com.financaspessoal.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.financaspessoal.app.ui.AppViewModel
import com.financaspessoal.app.ui.theme.*

@Composable
fun LoginScreen(viewModel: AppViewModel) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var apiUrl by remember { mutableStateOf("") }
    var showSettings by remember { mutableStateOf(false) }
    val error by viewModel.loginError.collectAsState()
    val savedUrl by viewModel.apiUrl.collectAsState()

    LaunchedEffect(savedUrl) {
        if (apiUrl.isEmpty()) apiUrl = savedUrl
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(Color(0xFF0A1628), Color(0xFF0D9488).copy(alpha = 0.55f), Color(0xFF111A2E)),
                ),
            ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Icon(
                Icons.Default.AccountBalanceWallet,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(64.dp),
            )
            Spacer(Modifier.height(16.dp))
            Text("Finanças Pessoais", color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
            Text("Entre para continuar", color = Color.White.copy(alpha = 0.78f), fontSize = 15.sp)
            Spacer(Modifier.height(28.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(22.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.88f)),
            ) {
                Column(Modifier.padding(20.dp)) {
                    if (error != null) {
                        Text(error!!, color = NegRed, fontSize = 13.sp, modifier = Modifier.padding(bottom = 8.dp))
                    }
                    if (showSettings) {
                        OutlinedTextField(
                            value = apiUrl,
                            onValueChange = { apiUrl = it },
                            label = { Text("URL do servidor") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                        )
                        Spacer(Modifier.height(8.dp))
                        TextButton(onClick = { viewModel.updateApiUrl(apiUrl) }) {
                            Text("Salvar URL")
                        }
                        HorizontalDivider(Modifier.padding(vertical = 8.dp))
                    }
                    OutlinedTextField(
                        value = username,
                        onValueChange = { username = it },
                        label = { Text("Usuário") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                    )
                    Spacer(Modifier.height(10.dp))
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it },
                        label = { Text("Senha") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        visualTransformation = PasswordVisualTransformation(),
                    )
                    Spacer(Modifier.height(16.dp))
                    Button(
                        onClick = { viewModel.login(username, password) },
                        modifier = Modifier.fillMaxWidth().height(50.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = TealPrimary),
                    ) {
                        Text("Entrar", fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
            TextButton(onClick = { showSettings = !showSettings }) {
                Text("Configurar servidor", color = Color.White.copy(alpha = 0.85f))
            }
            Text(
                "Emulador: http://10.0.2.2:8000/\nCelular: http://IP_DO_PC:8000/",
                color = Color.White.copy(alpha = 0.55f),
                fontSize = 11.sp,
                modifier = Modifier.padding(top = 8.dp),
            )
        }
    }
}
