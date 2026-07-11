package com.gaurangga.alpha.utils

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log
import com.gaurangga.alpha.service.GaurangaVoiceService
import com.gaurangga.alpha.security.BiometricAuthManager
import com.gaurangga.alpha.ui.SecurityActivity

/**
 * Boot Receiver - Starts GAURANGA with biometric auth when device boots
 */
class BootReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "BootReceiver"
        private const val PREFS_NAME = "gauranga_prefs"
        private const val KEY_AUTO_START = "auto_start_enabled"
        private const val KEY_LAUNCH_MODE = "launch_mode" // "full", "service_only", "lock_only"
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED ||
            intent.action == "android.intent.action.QUICKBOOT_POWERON") {
            
            Log.d(TAG, "🔄 Boot completed, starting GAURANGA...")
            
            // Check if auto-start is enabled
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val autoStart = prefs.getBoolean(KEY_AUTO_START, true) // Default: enabled
            
            if (!autoStart) {
                Log.d(TAG, "Auto-start disabled, skipping...")
                return
            }
            
            val biometricManager = BiometricAuthManager(context)
            val launchMode = prefs.getString(KEY_LAUNCH_MODE, "full") ?: "full"
            
            Log.d(TAG, "Launch mode: $launchMode")
            
            when (launchMode) {
                "service_only" -> {
                    // Start only the background service (no UI)
                    startVoiceService(context)
                }
                "lock_only" -> {
                    // Start lock screen only
                    startSecurityActivity(context, fromBoot = true)
                }
                "full" -> {
                    // Full launch: Lock screen -> Main Activity -> Service
                    startSecurityActivity(context, fromBoot = true)
                }
                else -> {
                    // Default: Full launch with biometric
                    startSecurityActivity(context, fromBoot = true)
                }
            }
        }
    }
    
    private fun startVoiceService(context: Context) {
        Log.d(TAG, "Starting voice service only...")
        val serviceIntent = Intent(context, GaurangaVoiceService::class.java)
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(serviceIntent)
        } else {
            context.startService(serviceIntent)
        }
    }
    
    private fun startSecurityActivity(context: Context, fromBoot: Boolean) {
        Log.d(TAG, "Starting security activity (biometric auth)...")
        
        val securityIntent = Intent(context, SecurityActivity::class.java).apply {
            putExtra(SecurityActivity.EXTRA_FROM_BOOT, fromBoot)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        
        context.startActivity(securityIntent)
    }
}
