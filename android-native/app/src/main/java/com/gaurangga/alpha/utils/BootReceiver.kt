package com.gaurangga.alpha.utils

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.gaurangga.alpha.startup.AutoStartManager

/**
 * BootReceiver - GAURANGA Auto-Start on Device Boot
 * 
 * This receiver listens for boot completed events and starts GAURANGA
 * based on user preferences using the AutoStartManager.
 * 
 * Supported boot actions:
 * - android.intent.action.BOOT_COMPLETED
 * - android.intent.action.QUICKBOOT_POWERON
 * - android.intent.action.LOCKED_BOOT_COMPLETED
 */
class BootReceiver : BroadcastReceiver() {
    
    companion object {
        private const val TAG = "BootReceiver"
    }
    
    override fun onReceive(context: Context, intent: Intent) {
        // Check if this is a boot completed action
        if (!isBootAction(intent.action)) {
            Log.d(TAG, "Ignoring non-boot action: ${intent.action}")
            return
        }
        
        Log.d(TAG, "🔄 Boot event detected: ${intent.action}")
        Log.d(TAG, "🚀 Starting GAURANGA Auto-Start sequence...")
        
        // Use AutoStartManager to handle the startup logic
        val autoStartManager = AutoStartManager(context)
        
        // Initialize the startup system
        autoStartManager.initialize()
        
        // Perform auto-start based on configuration
        val result = autoStartManager.performAutoStart()
        
        when (result) {
            AutoStartManager.StartResult.SUCCESS -> {
                Log.d(TAG, "✅ GAURANGA started successfully!")
            }
            AutoStartManager.StartResult.SKIPPED -> {
                Log.d(TAG, "⏭️ GAURANGA auto-start was skipped (disabled by user)")
            }
            AutoStartManager.StartResult.FAILED -> {
                Log.e(TAG, "❌ GAURANGA auto-start failed!")
            }
        }
        
        // Log device info for debugging
        logDeviceInfo(context)
    }
    
    /**
     * Check if the intent action is a boot-related action
     */
    private fun isBootAction(action: String?): Boolean {
        return action in listOf(
            Intent.ACTION_BOOT_COMPLETED,
            "android.intent.action.QUICKBOOT_POWERON",
            "android.intent.action.LOCKED_BOOT_COMPLETED"
        )
    }
    
    /**
     * Log device information for debugging
     */
    private fun logDeviceInfo(context: Context) {
        val pm = context.packageManager
        val packageInfo = try {
            pm.getPackageInfo(context.packageName, 0)
        } catch (e: Exception) {
            null
        }
        
        Log.d(TAG, "📱 Device Info:")
        Log.d(TAG, "   - App Version: ${packageInfo?.versionName ?: "Unknown"}")
        Log.d(TAG, "   - Package: ${context.packageName}")
    }
}
