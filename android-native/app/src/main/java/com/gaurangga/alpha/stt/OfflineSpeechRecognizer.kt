package com.gaurangga.alpha.stt

import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import com.alphacephei.vosk.AndroidAudioInputStream
import com.alphacephei.vosk.Model
import com.alphacephei.vosk.Recognizer
import com.alphacephei.vosk.Vosk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.util.zip.ZipInputStream

/**
 * Offline Speech-to-Text using Vosk
 * No internet required after model download
 */
class OfflineSpeechRecognizer(
    private val context: Context,
    private val onResult: (String) -> Unit
) {
    
    private var model: Model? = null
    private var recognizer: Recognizer? = null
    private var audioRecord: AudioRecord? = null
    private var isListening = false
    private var recognitionThread: Thread? = null
    
    private val sampleRate = 16000
    private val bufferSize = 4096
    
    val isReady: Boolean
        get() = model != null && recognizer != null
    
    companion object {
        private const val TAG = "OfflineSTT"
        private const val MODEL_FOLDER = "vosk-model-small-id"
    }
    
    suspend fun loadModel() = withContext(Dispatchers.IO) {
        try {
            val modelPath = File(context.filesDir, MODEL_FOLDER)
            
            if (!modelPath.exists()) {
                Log.d(TAG, "Downloading Vosk model...")
                // For first time, we'll use online model download
                // In production, bundle the model in assets
                downloadAndExtractModel(modelPath)
            }
            
            Log.d(TAG, "Loading model from: ${modelPath.absolutePath}")
            Vosk.SetLogLevel(-1) // Suppress logs
            
            model = Model(modelPath.absolutePath)
            recognizer = Recognizer(model, sampleRate.toFloat())
            
            Log.d(TAG, "Model loaded successfully!")
            
        } catch (e: Exception) {
            Log.e(TAG, "Error loading model: ${e.message}")
            e.printStackTrace()
        }
    }
    
    private fun downloadAndExtractModel(modelPath: File) {
        // Note: In production, include model in assets folder
        // This downloads from Vosk server (one-time)
        val modelUrl = "https://alphacephei.com/vosk/models/vosk-model-small-id-0.4.zip"
        
        try {
            val tempFile = File(context.cacheDir, "vosk-model.zip")
            
            // Download model
            val connection = java.net.URL(modelUrl).openConnection()
            connection.connect()
            
            val input = connection.getInputStream()
            val output = FileOutputStream(tempFile)
            
            val buffer = ByteArray(8192)
            var downloaded = 0L
            var bytesRead: Int
            
            while (input.read(buffer).also { bytesRead = it } != -1) {
                output.write(buffer, 0, bytesRead)
                downloaded += bytesRead
            }
            
            output.close()
            input.close()
            
            // Extract ZIP
            val zipInput = ZipInputStream(tempFile.inputStream())
            var entry = zipInput.nextEntry
            
            while (entry != null) {
                val newFile = File(modelPath.parentFile, entry.name.substringAfter("/"))
                
                if (entry.isDirectory) {
                    newFile.mkdirs()
                } else {
                    newFile.parentFile?.mkdirs()
                    val fos = FileOutputStream(newFile)
                    var read: Int
                    while (zipInput.read(buffer).also { read = it } != -1) {
                        fos.write(buffer, 0, read)
                    }
                    fos.close()
                }
                
                zipInput.closeEntry()
                entry = zipInput.nextEntry
            }
            
            tempFile.delete()
            Log.d(TAG, "Model extracted successfully")
            
        } catch (e: Exception) {
            Log.e(TAG, "Download failed: ${e.message}")
            throw e
        }
    }
    
    fun startListening(onPartialResult: ((String) -> Unit)? = null) {
        if (!isReady) {
            Log.w(TAG, "Model not ready yet")
            return
        }
        
        if (isListening) {
            stopListening()
        }
        
        isListening = true
        
        try {
            val channelConfig = AudioFormat.CHANNEL_IN_MONO
            val audioFormat = AudioFormat.ENCODING_PCM_16BIT
            
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                sampleRate,
                channelConfig,
                audioFormat,
                bufferSize * 2
            )
            
            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord not initialized")
                return
            }
            
            audioRecord?.startRecording()
            
            recognitionThread = Thread {
                val buffer = ShortArray(bufferSize / 2)
                val byteBuffer = ByteArray(bufferSize)
                
                while (isListening) {
                    val readCount = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    
                    if (readCount > 0) {
                        // Convert shorts to bytes
                        for (i in 0 until readCount) {
                            byteBuffer[i * 2] = (buffer[i].toInt() and 0xFF).toByte()
                            byteBuffer[i * 2 + 1] = (buffer[i].toInt() shr 8 and 0xFF).toByte()
                        }
                        
                        // Process with Vosk
                        recognizer?.acceptWaveForm(byteBuffer, readCount * 2)
                        
                        val result = recognizer?.finalResult
                        if (result != null) {
                            try {
                                val json = JSONObject(result)
                                val text = json.optString("text", "")
                                if (text.isNotBlank()) {
                                    onResult(text)
                                }
                            } catch (e: Exception) {
                                Log.e(TAG, "Parse error: ${e.message}")
                            }
                        }
                    }
                    
                    Thread.sleep(50)
                }
            }
            
            recognitionThread?.start()
            
        } catch (e: SecurityException) {
            Log.e(TAG, "Permission denied: ${e.message}")
        } catch (e: Exception) {
            Log.e(TAG, "Error starting: ${e.message}")
        }
    }
    
    fun stopListening() {
        isListening = false
        
        recognitionThread?.interrupt()
        recognitionThread = null
        
        try {
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping: ${e.message}")
        }
        
        // Reset recognizer for next use
        recognizer?.reset()
    }
    
    fun release() {
        stopListening()
        recognizer?.close()
        recognizer = null
        model?.close()
        model = null
    }
}
