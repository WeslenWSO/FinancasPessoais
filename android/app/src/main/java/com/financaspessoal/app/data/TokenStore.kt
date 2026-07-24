package com.financaspessoal.app.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.financaspessoal.app.BuildConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking

private val Context.dataStore by preferencesDataStore("financas_prefs")

class TokenStore(private val context: Context) {
    private val accessKey = stringPreferencesKey("access_token")
    private val refreshKey = stringPreferencesKey("refresh_token")
    private val apiUrlKey = stringPreferencesKey("api_url")

    val accessToken: Flow<String?> = context.dataStore.data.map { it[accessKey] }
    val apiUrl: Flow<String> = context.dataStore.data.map {
        it[apiUrlKey] ?: BuildConfig.DEFAULT_API_URL
    }

    suspend fun saveTokens(access: String, refresh: String) {
        context.dataStore.edit {
            it[accessKey] = access
            it[refreshKey] = refresh
        }
    }

    suspend fun saveApiUrl(url: String) {
        context.dataStore.edit { it[apiUrlKey] = url }
    }

    suspend fun clear() {
        context.dataStore.edit {
            it.remove(accessKey)
            it.remove(refreshKey)
        }
    }

    fun getAccessTokenBlocking(): String? = runBlocking {
        context.dataStore.data.first()[accessKey]
    }

    fun getApiUrlBlocking(): String = runBlocking {
        context.dataStore.data.first()[apiUrlKey] ?: BuildConfig.DEFAULT_API_URL
    }
}
