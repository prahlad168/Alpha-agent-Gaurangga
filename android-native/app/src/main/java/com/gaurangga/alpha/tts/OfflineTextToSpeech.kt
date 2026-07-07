package com.gaurangga.alpha.tts

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Build
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import android.util.Log
import java.util.*

/**
 * Offline Text-to-Speech using Android TTS Engine
 * Works completely offline with bundled/system voices
 */
class OfflineTextToSpeech(
    private val context: Context,
    private val listener: TextToSpeech.OnInitListener
) {
    
    private var tts: TextToSpeech? = null
    private var isInitialized = false
    
    // Audio player for pre-recorded responses
    private var mediaPlayer: MediaPlayer? = null
    
    val isReady: Boolean
        get() = isInitialized && tts != null
    
    companion object {
        private const val TAG = "OfflineTTS"
    }
    
    init {
        initializeTTS()
    }
    
    private fun initializeTTS() {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                isInitialized = true
                
                // Try to set Indonesian locale
                val indonesianResult = tts?.setLanguage(Locale("id", "ID"))
                
                if (indonesianResult == TextToSpeech.LANG_MISSING_DATA || 
                    indonesianResult == TextToSpeech.LANG_NOT_SUPPORTED) {
                    // Fallback to English
                    Log.d(TAG, "Indonesian not supported, using default")
                    tts?.setLanguage(Locale.US)
                }
                
                // Set speech parameters for better quality
                setSpeechRate(1.0f)
                setPitch(1.1f)
                
                // Try to find a good voice
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                    selectBestVoice()
                }
                
                Log.d(TAG, "TTS initialized successfully!")
                listener.onInit(TextToSpeech.SUCCESS)
                
            } else {
                Log.e(TAG, "TTS initialization failed")
                listener.onInit(TextToSpeech.ERROR)
            }
        }
    }
    
    private fun selectBestVoice() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            val voices = tts?.voices
            if (voices != null) {
                // Prefer Indonesian female voices
                val indonesianVoices = voices.filter { 
                    it.locale.language == "id" && 
                    it.name.lowercase().contains("female")
                }
                
                if (indonesianVoices.isNotEmpty()) {
                    tts?.voice = indonesianVoices.first()
                    Log.d(TAG, "Selected voice: ${indonesianVoices.first().name}")
                    return
                }
                
                // Try any Indonesian voice
                val anyIndonesian = voices.filter { it.locale.language == "id" }
                if (anyIndonesian.isNotEmpty()) {
                    tts?.voice = anyIndonesian.first()
                    Log.d(TAG, "Selected Indonesian voice: ${anyIndonesian.first().name}")
                    return
                }
                
                // Fallback to any available voice
                val defaultVoice = voices.firstOrNull()
                if (defaultVoice != null) {
                    tts?.voice = defaultVoice
                    Log.d(TAG, "Using default voice: ${defaultVoice.name}")
                }
            }
        }
    }
    
    fun speak(text: String, queueMode: Int = TextToSpeech.QUEUE_FLUSH) {
        if (!isInitialized) {
            Log.w(TAG, "TTS not initialized yet")
            return
        }
        
        // Clean text for speech
        val cleanedText = cleanText(text)
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            tts?.speak(cleanedText, queueMode, null, UUID.randomUUID().toString())
        } else {
            @Suppress("DEPRECATION")
            tts?.speak(cleanedText, queueMode, null)
        }
    }
    
    fun speakWithCallbacks(
        text: String,
        onStart: (() -> Unit)? = null,
        onDone: (() -> Unit)? = null,
        onError: ((String) -> Unit)? = null
    ) {
        if (!isInitialized) {
            Log.w(TAG, "TTS not initialized yet")
            return
        }
        
        val utteranceId = UUID.randomUUID().toString()
        
        tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                onStart?.invoke()
            }
            
            override fun onDone(utteranceId: String?) {
                onDone?.invoke()
            }
            
            override fun onError(utteranceId: String?) {
                onError?.invoke(utteranceId ?: "Unknown error")
            }
            
            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?, errorCode: Int) {
                onError?.invoke("Error code: $errorCode")
            }
        })
        
        speak(text)
    }
    
    fun stop() {
        tts?.stop()
    }
    
    fun setSpeechRate(rate: Float) {
        tts?.setSpeechRate(rate.coerceIn(0.5f, 2.0f))
    }
    
    fun setPitch(pitch: Float) {
        tts?.setPitch(pitch.coerceIn(0.5f, 2.0f))
    }
    
    fun shutdown() {
        stop()
        tts?.shutdown()
        tts = null
        isInitialized = false
    }
    
    private fun cleanText(text: String): String {
        return text
            .replace(Regex("<[^>]*>"), "") // Remove HTML tags
            .replace(Regex("[📅📊📢💰🎯✅❌🔥🚀💪👑🤖🎤🔊📱]"), "") // Remove emojis
            .replace(Regex("\\*+"), "") // Remove markdown
            .replace(Regex("#+"), "") // Remove headers
            .replace(Regex("`+"), "") // Remove code blocks
            .replace(Regex("\\s+"), " ") // Normalize spaces
            .trim()
    }
    
    /**
     * Check if offline voices are available
     */
    fun hasOfflineVoice(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            val voices = tts?.voices ?: return false
            val offlineVoices = voices.filter { !it.isNetworkConnectionRequired }
            return offlineVoices.isNotEmpty()
        }
        return true // Pre-Lollipop assumes offline
    }
}
