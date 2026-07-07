package com.gaurangga.alpha

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

/**
 * GAURANGA - Agent Alpha Android Application
 * Always-on Voice Assistant
 */
class GaurangaApp : Application() {
    
    companion object {
        const val CHANNEL_ID = "gauranga_voice_channel"
        const val CHANNEL_NAME = "GAURANGA Voice Assistant"
        lateinit var instance: GaurangaApp
            private set
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        createNotificationChannel()
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "GAURANGA Voice Assistant - Always listening for commands"
                setShowBadge(false)
                enableVibration(false)
                setSound(null, null)
            }
            
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
}
