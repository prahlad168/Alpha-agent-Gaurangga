package com.gaurangga.alpha.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.gaurangga.alpha.databinding.ActivityMainBinding
import com.gaurangga.alpha.service.GaurangaVoiceService
import com.gaurangga.alpha.stt.OfflineSpeechRecognizer
import com.gaurangga.alpha.tts.OfflineTextToSpeech
import kotlinx.coroutines.launch
import java.util.*

/**
 * GAURANGA Main Activity
 * Handles UI and voice interactions
 */
class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var offlineSTT: OfflineSpeechRecognizer
    private lateinit var offlineTTS: OfflineTextToSpeech
    private var isServiceRunning = false
    
    // Permission launcher
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.all { it.value }
        if (allGranted) {
            initializeVoiceFeatures()
        } else {
            showPermissionDenied()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupUI()
        checkPermissions()
    }
    
    private fun setupUI() {
        // Service toggle button
        binding.btnServiceToggle.setOnClickListener {
            toggleService()
        }
        
        // Voice input button
        binding.btnVoiceInput.setOnClickListener {
            startVoiceInput()
        }
        
        // Stop listening button
        binding.btnStopListening.setOnClickListener {
            stopListening()
        }
        
        // Text input send button
        binding.btnSendText.setOnClickListener {
            val text = binding.etTextInput.text.toString()
            if (text.isNotBlank()) {
                processTextCommand(text)
                binding.etTextInput.text?.clear()
            }
        }
        
        // Update status
        updateStatus("Ready")
    }
    
    private fun checkPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.FOREGROUND_SERVICE,
            Manifest.permission.FOREGROUND_SERVICE_MICROPHONE
        )
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        
        val notGranted = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        
        if (notGranted.isEmpty()) {
            initializeVoiceFeatures()
        } else {
            permissionLauncher.launch(notGranted.toTypedArray())
        }
    }
    
    private fun initializeVoiceFeatures() {
        // Initialize TTS
        offlineTTS = OfflineTextToSpeech(this, this)
        
        // Initialize STT
        offlineSTT = OfflineSpeechRecognizer(this) { result ->
            runOnUiThread {
                handleSpeechResult(result)
            }
        }
        
        // Load model
        lifecycleScope.launch {
            offlineSTT.loadModel()
        }
        
        updateStatus("Voice Ready - Tap 🎤 to speak!")
        speak("Halo Pak Pur! GAURANGA Alpha aktif!")
    }
    
    private fun toggleService() {
        val intent = Intent(this, GaurangaVoiceService::class.java)
        
        if (isServiceRunning) {
            stopService(intent)
            isServiceRunning = false
            binding.btnServiceToggle.text = "▶ START 24/7"
            binding.tvServiceStatus.text = "Service Stopped"
            binding.tvServiceStatus.setTextColor(getColor(android.R.color.darker_gray))
        } else {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
            isServiceRunning = true
            binding.btnServiceToggle.text = "⏹ STOP 24/7"
            binding.tvServiceStatus.text = "Service Running 24/7"
            binding.tvServiceStatus.setTextColor(getColor(android.R.color.holo_green_dark))
        }
    }
    
    private fun startVoiceInput() {
        if (!::offlineSTT.isReady) {
            speak("Maaf, recognizer belum siap. Mohon tunggu sebentar.")
            return
        }
        
        updateStatus("🎤 Listening...")
        binding.btnVoiceInput.text = "⏳"
        binding.btnVoiceInput.isEnabled = false
        
        offlineSTT.startListening { result ->
            lifecycleScope.launch {
                offlineSTT.stopListening()
                binding.btnVoiceInput.text = "🎤"
                binding.btnVoiceInput.isEnabled = true
            }
        }
    }
    
    private fun stopListening() {
        if (::offlineSTT.isInitialized) {
            offlineSTT.stopListening()
            binding.btnVoiceInput.text = "🎤"
            binding.btnVoiceInput.isEnabled = true
            updateStatus("Stopped")
        }
    }
    
    private fun handleSpeechResult(text: String) {
        if (text.isBlank()) {
            updateStatus("Tidak ada suara terdeteksi")
            return
        }
        
        binding.tvLastCommand.text = "👤: $text"
        updateStatus("Processing...")
        
        // Process the command
        lifecycleScope.launch {
            val response = processCommand(text)
            if (response.isNotBlank()) {
                speak(response)
                binding.tvLastResponse.text = "🤖: $response"
            }
            updateStatus("Ready")
        }
    }
    
    private fun processTextCommand(text: String) {
        binding.tvLastCommand.text = "👤: $text"
        updateStatus("Processing...")
        
        lifecycleScope.launch {
            val response = processCommand(text)
            if (response.isNotBlank()) {
                speak(response)
                binding.tvLastResponse.text = "🤖: $response"
            }
            updateStatus("Ready")
        }
    }
    
    private suspend fun processCommand(command: String): String {
        val lower = command.lowercase()
        
        return when {
            lower.contains("laporan") || lower.contains("pagi") -> {
                getMorningReport()
            }
            lower.contains("siapa kamu") || lower.contains("gauranga") -> {
                "Saya GAURANGA, Agent Alpha untuk Pak Pur. Saya siap membantu 24 jam, bahkan saat offline!"
            }
            lower.contains("jadwal") -> {
                getSchedule()
            }
            lower.contains("status") -> {
                "Semua sistem normal. Voice recognition ${if (offlineSTT.isReady) "aktif" else "loading"}. Service ${if (isServiceRunning) "berjalan 24/7" else "belum aktif"}."
            }
            lower.contains("bantu") || lower.contains("tolong") -> {
                "Tentu! Saya siap membantu. Silakan bicara atau ketik perintah Anda, Pak Pur!"
            }
            lower.contains("stop") || lower.contains("berhenti") -> {
                stopListening()
                "Baik, saya berhenti mendengarkan."
            }
            lower.contains("matikan") && (lower.contains("suara") || lower.contains("tts")) -> {
                offlineTTS.stop()
                "Suara dimatikan."
            }
            lower.contains("nyalakan") && (lower.contains("suara") || lower.contains("tts")) -> {
                "Suara dinyalakan!"
            }
            else -> {
                "Perintah '$command' diterima. Maaf, saya masih belajar. Fitur AI lengkap akan segera ditambahkan!"
            }
        }
    }
    
    private fun getMorningReport(): String {
        val calendar = Calendar.getInstance()
        val hour = calendar.get(Calendar.HOUR_OF_DAY)
        val greeting = when {
            hour < 10 -> "Selamat Pagi"
            hour < 15 -> "Selamat Siang"
            hour < 18 -> "Selamat Sore"
            else -> "Selamat Malam"
        }
        
        return """
            $greeting, Pak Pur! 🌅
            
            📊 Laporan GAURANGA:
            • Genesis Day 3
            • System: ONLINE
            • Voice: ${if (::offlineSTT.isReady) "AKTIF" else "LOADING..."}
            • Service: ${if (isServiceRunning) "24/7 BERJALAN" else "STOPPED"}
            
            🚀 Status: SIAP MELAYANI!
        """.trimIndent()
    }
    
    private fun getSchedule(): String {
        return """
            📅 Jadwal Hari Ini:
            
            • 07:00 - Laporan Pagi
            • 09:00 - Check-in GAURANGA
            • 14:00 - Review Progress
            • 18:00 - Laporan Sore
            
            💡 Tip: Bilang "gauranga" untuk aktivasi!
        """.trimIndent()
    }
    
    private fun speak(text: String) {
        if (::offlineTTS.isReady) {
            offlineTTS.speak(text)
        }
    }
    
    private fun updateStatus(status: String) {
        binding.tvStatus.text = status
    }
    
    private fun showPermissionDenied() {
        Toast.makeText(this, "Izin diperlukan untuk voice assistant!", Toast.LENGTH_LONG).show()
        updateStatus("Permission Required")
    }
    
    // TextToSpeech.OnInitListener
    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = offlineTTS.setLanguage(Locale("id", "ID"))
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                offlineTTS.setLanguage(Locale.US)
            }
            offlineTTS.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) {
                    runOnUiThread {
                        updateStatus("🔊 Speaking...")
                    }
                }
                
                override fun onDone(utteranceId: String?) {
                    runOnUiThread {
                        updateStatus("Ready")
                    }
                }
                
                override fun onError(utteranceId: String?) {
                    runOnUiThread {
                        updateStatus("TTS Error")
                    }
                }
            })
        }
    }
    
    override fun onDestroy() {
        if (::offlineTTS.isInitialized) {
            offlineTTS.shutdown()
        }
        if (::offlineSTT.isInitialized) {
            offlineSTT.release()
        }
        super.onDestroy()
    }
}
