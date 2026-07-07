package com.gaurangga.alpha.service

import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Binder
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import androidx.core.app.NotificationCompat
import com.alphacephei.vosk.Model
import com.alphacephei.vosk.Recognizer
import com.alphacephei.vosk.Vosk
import com.gaurangga.alpha.GaurangaApp
import com.gauranga.alpha.R
import com.gaurangga.alpha.ui.MainActivity
import kotlinx.coroutines.*
import org.json.JSONObject
import java.io.File
import java.util.*

/**
 * GAURANGA Foreground Service
 * Runs 24/7 in background for always-on voice assistant
 */
class GaurangaVoiceService : Service() {
    
    private val binder = LocalBinder()
    private var wakeLock: PowerManager.WakeLock? = null
    
    // Vosk STT
    private var voskModel: Model? = null
    private var recognizer: Recognizer? = null
    
    // TTS
    private var tts: TextToSpeech? = null
    private var isTTSReady = false
    
    // Status
    private var isListening = false
    private var isAwakeWordDetected = false
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    companion object {
        private const val TAG = "GaurangaService"
        private const val NOTIFICATION_ID = 1001
        private const val MODEL_FOLDER = "vosk-model-small-id"
        
        const val ACTION_START_LISTENING = "com.gaurangga.alpha.START_LISTENING"
        const val ACTION_STOP_LISTENING = "com.gaurangga.alpha.STOP_LISTENING"
        const val ACTION_SPEAK = "com.gaurangga.alpha.SPEAK"
        const val ACTION_STOP_SERVICE = "com.gaurangga.alpha.STOP"
        
        const val EXTRA_SPEAK_TEXT = "speak_text"
    }
    
    inner class LocalBinder : Binder() {
        fun getService(): GaurangaVoiceService = this@GaurangaVoiceService
    }
    
    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Service created")
        
        // Acquire wake lock to keep CPU alive
        val powerManager = getSystemService(POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "GAURANGA::VoiceServiceWakeLock"
        ).apply {
            acquire(24 * 60 * 60 * 1000L) // 24 hours max
        }
        
        initializeServices()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_LISTENING -> startListening()
            ACTION_STOP_LISTENING -> stopListening()
            ACTION_SPEAK -> {
                val text = intent.getStringExtra(EXTRA_SPEAK_TEXT)
                if (!text.isNullOrBlank()) {
                    speak(text)
                }
            }
            ACTION_STOP_SERVICE -> {
                stopListening()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }
        
        // Start as foreground service
        startForegroundWithNotification()
        
        return START_STICKY // Restart if killed
    }
    
    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
    
    private fun startForegroundWithNotification() {
        val notification = createNotification()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }
    
    private fun createNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val stopIntent = PendingIntent.getService(
            this,
            1,
            Intent(this, GaurangaVoiceService::class.java).apply {
                action = ACTION_STOP_SERVICE
            },
            PendingIntent.FLAG_IMMUTABLE
        )
        
        val listenIntent = PendingIntent.getService(
            this,
            2,
            Intent(this, GaurangaVoiceService::class.java).apply {
                action = ACTION_START_LISTENING
            },
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, GaurangaApp.CHANNEL_ID)
            .setContentTitle("🤖 GAURANGA Alpha")
            .setContentText(if (isListening) "🎤 Mendengarkan..." else "Siap menerima perintah")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setShowWhen(false)
            .addAction(
                android.R.drawable.ic_btn_speak_now,
                if (isListening) "Stop" else "🎤 Dengar",
                listenIntent
            )
            .addAction(
                android.R.drawable.ic_menu_close_clear_cancel,
                "Stop",
                stopIntent
            )
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
    
    private fun initializeServices() {
        // Initialize TTS
        tts = TextToSpeech(this) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale("id", "ID")
                tts?.setSpeechRate(1.0f)
                tts?.setPitch(1.1f)
                isTTSReady = true
                Log.d(TAG, "TTS ready")
                
                // Announce ready
                speak("GAURANGA Alpha siap 24 jam. Bilang 'gauranga' untuk aktivasi.")
            }
        }
        
        // Load Vosk model
        serviceScope.launch {
            loadVoskModel()
        }
    }
    
    private suspend fun loadVoskModel() {
        try {
            val modelPath = File(filesDir, MODEL_FOLDER)
            
            if (!modelPath.exists()) {
                Log.d(TAG, "Model not found at: ${modelPath.absolutePath}")
                // Model will be downloaded by MainActivity
                return
            }
            
            Vosk.SetLogLevel(-1)
            voskModel = Model(modelPath.absolutePath)
            recognizer = Recognizer(voskModel, 16000f)
            
            Log.d(TAG, "Vosk model loaded")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load Vosk: ${e.message}")
        }
    }
    
    fun startListening() {
        if (isListening) return
        if (recognizer == null) {
            Log.w(TAG, "Recognizer not ready")
            speak("Maaf, recognizer belum siap.")
            return
        }
        
        isListening = true
        updateNotification()
        
        // Start actual listening (simplified - would need AudioRecord in production)
        Log.d(TAG, "Started listening...")
        
        // Send broadcast for UI to update
        sendBroadcast(Intent("com.gaurangga.alpha.LISTENING_STARTED"))
    }
    
    fun stopListening() {
        isListening = false
        isAwakeWordDetected = false
        recognizer?.reset()
        updateNotification()
        
        Log.d(TAG, "Stopped listening")
        sendBroadcast(Intent("com.gaurangga.alpha.LISTENING_STOPPED"))
    }
    
    fun speak(text: String) {
        if (!isTTSReady) {
            Log.w(TAG, "TTS not ready")
            return
        }
        
        val cleanedText = text
            .replace(Regex("<[^>]*>"), "")
            .replace(Regex("[📅📊📢💰🎯✅❌🔥🚀💪👑🤖🎤🔊]"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
        
        tts?.speak(cleanedText, TextToSpeech.QUEUE_FLUSH, null, UUID.randomUUID().toString())
    }
    
    private fun updateNotification() {
        val notification = createNotification()
        val notificationManager = getSystemService(NOTIFICATION_SERVICE) as android.app.NotificationManager
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
    
    override fun onDestroy() {
        Log.d(TAG, "Service destroyed")
        
        isListening = false
        wakeLock?.release()
        
        recognizer?.close()
        voskModel?.close()
        
        tts?.stop()
        tts?.shutdown()
        
        serviceScope.cancel()
        
        super.onDestroy()
    }
}
