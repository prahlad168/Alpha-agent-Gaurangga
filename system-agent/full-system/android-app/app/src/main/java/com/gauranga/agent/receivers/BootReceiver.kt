package com.gauranga.agent.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import android.os.Build
import com.gauranga.agent.services.GaurangaForegroundService

class BootReceiver : BroadcastReceiver() {

    companion object {
        const val TAG = "GAURANGA_BOOT"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            Log.d(TAG, "Boot completed, starting GAURANGA...")
            
            val serviceIntent = Intent(context, GaurangaForegroundService::class.java)
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(serviceIntent)
            } else {
                context.startService(serviceIntent)
            }
            
            Log.d(TAG, "GAURANGA started successfully")
        }
    }
}