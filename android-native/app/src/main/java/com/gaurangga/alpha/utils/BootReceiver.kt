package com.gaurangga.alpha.utils

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import com.gaurangga.alpha.service.GaurangaVoiceService

/**
 * Boot Receiver - Starts GAURANGA service when device boots
 */
class BootReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "BootReceiver"
        private const val PREFS_NAME = "gauranga_prefs"
        private const val KEY_AUTO_START = "auto_start_enabled"
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED ||
            intent.action == "android.intent.action.QUICKBOOT_POWERON") {
            
            Log.d(TAG, "Boot completed, checking auto-start preference...")
            
            // Check if auto-start is enabled
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val autoStart = prefs.getBoolean(KEY_AUTO_START, true) // Default: enabled
            
            if (autoStart) {
                Log.d(TAG, "Auto-start enabled, launching GAURANGA service...")
                
                val serviceIntent = Intent(context, GaurangaVoiceService::class.java)
                
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    context.startForegroundService(serviceIntent)
                } else {
                    context.startService(serviceIntent)
                }
            } else {
                Log.d(TAG, "Auto-start disabled, skipping...")
            }
        }
    }
}
