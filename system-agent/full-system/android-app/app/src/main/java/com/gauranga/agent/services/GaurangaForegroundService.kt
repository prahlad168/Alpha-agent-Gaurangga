package com.gauranga.agent.services

import android.app.*
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.gauranga.agent.MainActivity
import com.gauranga.agent.R
import java.io.BufferedReader
import java.io.InputStreamReader

class GaurangaForegroundService : Service() {

    companion object {
        const val TAG = "GAURANGA_SERVICE"
        const val CHANNEL_ID = "gauranga_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_COMMAND = "com.gauranga.agent.COMMAND"
        const val ACTION_SHUTDOWN = "com.gauranga.agent.SHUTDOWN"
    }

    private var pythonProcess: Process? = null
    private var isRunning = false

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        Log.d(TAG, "Service created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Service starting...")
        
        when (intent?.action) {
            ACTION_SHUTDOWN -> {
                stopSelf()
                return START_NOT_STICKY
            }
            else -> {
                startForeground(NOTIFICATION_ID, createNotification())
                startPythonBackend()
                return START_STICKY
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        stopPythonBackend()
        Log.d(TAG, "Service destroyed")
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "GAURANGA Agent",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "GAURANGA System Agent running"
                setShowBadge(false)
            }
            
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )

        val stopIntent = Intent(this, GaurangaForegroundService::class.java).apply {
            action = ACTION_SHUTDOWN
        }
        val stopPendingIntent = PendingIntent.getService(
            this,
            1,
            stopIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("🤖 GAURANGA Agent Alpha")
            .setContentText("Sistem Agent aktif - Ketuk untuk buka")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .addAction(R.drawable.ic_stop, "Stop", stopPendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun startPythonBackend() {
        try {
            Log.d(TAG, "Starting Python backend...")
            
            // Start Python script as subprocess
            val processBuilder = ProcessBuilder(
                "python3",
                filesDir.path + "/python/gauranga_agent.py",
                "--daemon"
            )
            
            processBuilder.redirectErrorStream(true)
            pythonProcess = processBuilder.start()
            
            // Read output in background thread
            Thread {
                val reader = BufferedReader(InputStreamReader(pythonProcess!!.inputStream))
                var line: String?
                while (isRunning && pythonProcess!!.isAlive) {
                    line = reader.readLine()
                    if (line != null) {
                        Log.d(TAG, "Python: $line")
                        processPythonOutput(line)
                    }
                }
            }.start()
            
            isRunning = true
            Log.d(TAG, "Python backend started")
            
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start Python: ${e.message}")
        }
    }

    private fun stopPythonBackend() {
        isRunning = false
        pythonProcess?.destroy()
        pythonProcess = null
        Log.d(TAG, "Python backend stopped")
    }

    private fun processPythonOutput(line: String) {
        // Handle Python script output
        // Could show overlay, play sound, etc.
        when {
            line.contains("RESPONSE:") -> {
                // Broadcast response to UI
                val response = line.removePrefix("RESPONSE:")
                broadcastResponse(response)
            }
            line.contains("ACTION:") -> {
                // Execute action via accessibility
                val action = line.removePrefix("ACTION:")
                executeAction(action)
            }
        }
    }

    private fun broadcastResponse(response: String) {
        val intent = Intent("com.gauranga.agent.RESPONSE").apply {
            putExtra("response", response)
        }
        sendBroadcast(intent)
    }

    private fun executeAction(action: String) {
        // This would trigger accessibility service to perform action
        val intent = Intent(this, GaurangaAccessibilityService::class.java).apply {
            putExtra("action", action)
        }
        startService(intent)
    }

    // Handle commands from MainActivity
    fun handleCommand(command: String) {
        pythonProcess?.let { process ->
            process.outputStream.write((command + "\n").toByteArray())
            process.outputStream.flush()
        }
    }
}