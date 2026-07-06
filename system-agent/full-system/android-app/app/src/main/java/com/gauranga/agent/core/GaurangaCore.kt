package com.gauranga.agent.core

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter

class GaurangaCore(private val context: Context) {

    companion object {
        const val TAG = "GAURANGA_CORE"
        const val PREFS_NAME = "gauranga_prefs"
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private var pythonProcess: Process? = null
    private var reader: BufferedReader? = null
    private var writer: OutputStreamWriter? = null

    // Owner info
    var ownerName = "I Made Purna Ananda"
    var ownerNickname = "Pak Pur"
    var companyName = "Maha Lakshmi Holdings"

    // Family
    data class FamilyMember(val name: String, val relation: String)
    val family = listOf(
        FamilyMember("Ni Wayan Lestiani", "Wife (Bunda Lila)"),
        FamilyMember("Putu Gaurangga Vishnu Bhakta", "Child 1"),
        FamilyMember("Kadek Srutakirti", "Child 2")
    )

    fun initialize() {
        Log.d(TAG, "Initializing GAURANGA Core...")
        loadPreferences()
        startPythonBackend()
    }

    private fun loadPreferences() {
        ownerName = prefs.getString("owner_name", ownerName) ?: ownerName
        ownerNickname = prefs.getString("owner_nickname", ownerNickname) ?: ownerNickname
        companyName = prefs.getString("company_name", companyName) ?: companyName
    }

    fun savePreferences() {
        prefs.edit().apply {
            putString("owner_name", ownerName)
            putString("owner_nickname", ownerNickname)
            putString("company_name", companyName)
            apply()
        }
    }

    // ========== PYTHON BACKEND ==========

    fun startPythonBackend() {
        try {
            Log.d(TAG, "Starting Python backend...")
            
            val pythonScript = context.filesDir.path + "/python/gauranga_agent.py"
            
            val processBuilder = ProcessBuilder(
                "python3",
                pythonScript,
                "--daemon",
                "--owner", ownerName
            )
            
            processBuilder.redirectErrorStream(true)
            pythonProcess = processBuilder.start()
            
            reader = BufferedReader(InputStreamReader(pythonProcess!!.inputStream))
            writer = OutputStreamWriter(pythonProcess!!.outputStream)
            
            // Start reading thread
            Thread {
                try {
                    var line: String?
                    while (pythonProcess!!.isAlive) {
                        line = reader?.readLine()
                        if (line != null) {
                            processPythonOutput(line)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Python reader error: ${e.message}")
                }
            }.start()
            
            Log.d(TAG, "Python backend started")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start Python: ${e.message}")
        }
    }

    fun stopPythonBackend() {
        try {
            writer?.write("exit\n")
            writer?.flush()
            pythonProcess?.destroy()
            pythonProcess = null
            reader?.close()
            writer?.close()
            Log.d(TAG, "Python backend stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping Python: ${e.message}")
        }
    }

    fun sendCommand(command: String): String {
        if (writer == null || pythonProcess?.isAlive != true) {
            return "ERROR: Python backend not running"
        }
        
        try {
            writer?.write("$command\n")
            writer?.flush()
            
            // Wait for response (with timeout)
            // In real implementation, this would use callbacks
            return "Command sent: $command"
            
        } catch (e: Exception) {
            Log.e(TAG, "Error sending command: ${e.message}")
            return "ERROR: ${e.message}"
        }
    }

    private fun processPythonOutput(line: String) {
        Log.d(TAG, "Python: $line")
        
        when {
            line.startsWith("RESPONSE:") -> {
                val response = line.removePrefix("RESPONSE:")
                broadcastResponse(response)
            }
            line.startsWith("ACTION:") -> {
                val action = line.removePrefix("ACTION:")
                executeAction(action)
            }
            line.startsWith("TTS:") -> {
                val text = line.removePrefix("TTS:")
                speakText(text)
            }
        }
    }

    // ========== ACTIONS ==========

    private fun broadcastResponse(response: String) {
        val intent = android.content.Intent("com.gauranga.agent.RESPONSE").apply {
            putExtra("response", response)
            setPackage(context.packageName)
        }
        context.sendBroadcast(intent)
    }

    private fun executeAction(action: String) {
        // Parse action JSON
        try {
            val json = JSONObject(action)
            val type = json.getString("type")
            
            when (type) {
                "click" -> {
                    val text = json.getString("text")
                    // Trigger accessibility service
                    triggerAccessibilityAction("click", text)
                }
                "type" -> {
                    val text = json.getString("text")
                    triggerAccessibilityAction("type", text)
                }
                "open_app" -> {
                    val packageName = json.getString("package")
                    triggerAccessibilityAction("open_app", packageName)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing action: ${e.message}")
        }
    }

    private fun triggerAccessibilityAction(action: String, value: String) {
        val intent = android.content.Intent("com.gauranga.agent.ACCESSIBILITY").apply {
            putExtra("action", action)
            putExtra("value", value)
            setPackage(context.packageName)
        }
        context.sendBroadcast(intent)
    }

    private fun speakText(text: String) {
        // Use Android TTS
        val intent = android.content.Intent("com.gauranga.agent.TTS").apply {
            putExtra("text", text)
            setPackage(context.packageName)
        }
        context.sendBroadcast(intent)
    }

    // ========== INTENTS ==========

    fun getGreeting(): String {
        return "Halo $ownerNickname! Saya GAURANGA, Agent Alpha. Ada yang bisa saya bantu?"
    }

    fun getStatus(): String {
        return buildString {
            appendLine("📊 Status GAURANGA:")
            appendLine("• Owner: $ownerName")
            appendLine("• Company: $companyName")
            appendLine("• Python: ${if (pythonProcess?.isAlive == true) "RUNNING" else "STOPPED"}")
        }
    }

    fun getFamily(): String {
        return buildString {
            appendLine("👨‍👩‍👧‍👦 Keluarga $ownerNickname:")
            family.forEach { member ->
                appendLine("• ${member.name} (${member.relation})")
            }
        }
    }

    // ========== MEMORY ==========

    fun remember(key: String, value: String) {
        prefs.edit().putString("memory_$key", value).apply()
    }

    fun recall(key: String): String? {
        return prefs.getString("memory_$key", null)
    }

    fun forget(key: String) {
        prefs.edit().remove("memory_$key").apply()
    }

    fun clearMemory() {
        prefs.edit().clear().apply()
    }
}