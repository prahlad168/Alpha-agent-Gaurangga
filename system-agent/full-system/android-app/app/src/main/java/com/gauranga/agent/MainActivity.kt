package com.gauranga.agent

import android.accessibilityservice.AccessibilityServiceInfo
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.gauranga.agent.services.GaurangaForegroundService

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    
    companion object {
        const val TAG = "GAURANGA"
        const val SERVICE_NAME = "com.gauranga.agent.services.GaurangaForegroundService"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)
        initViews()
        setupClickListeners()
        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun initViews() {
        statusText = findViewById(R.id.statusText)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
    }

    private fun setupClickListeners() {
        startButton.setOnClickListener {
            if (checkAllPermissions()) {
                startGauranga()
            } else {
                requestPermissions()
            }
        }

        stopButton.setOnClickListener {
            stopGauranga()
        }
        
        findViewById<View>(R.id.accessibilityCard)?.setOnClickListener {
            openAccessibilitySettings()
        }
        
        findViewById<View>(R.id.overlayCard)?.setOnClickListener {
            openOverlaySettings()
        }
    }

    private fun checkAllPermissions(): Boolean {
        return hasAccessibilityPermission() && hasOverlayPermission()
    }

    private fun hasAccessibilityPermission(): Boolean {
        val enabledServices = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )
        return enabledServices?.contains(packageName) == true
    }

    private fun hasOverlayPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Settings.canDrawOverlays(this)
        } else {
            true
        }
    }

    private fun requestPermissions() {
        if (!hasAccessibilityPermission()) {
            Toast.makeText(this, "Aktifkan Accessibility Service", Toast.LENGTH_SHORT).show()
            openAccessibilitySettings()
            return
        }
        
        if (!hasOverlayPermission()) {
            Toast.makeText(this, "Izinkan Overlay", Toast.LENGTH_SHORT).show()
            openOverlaySettings()
            return
        }
    }

    private fun openAccessibilitySettings() {
        try {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Tidak bisa buka settings", Toast.LENGTH_SHORT).show()
        }
    }

    private fun openOverlaySettings() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        }
    }

    private fun startGauranga() {
        val intent = Intent(this, GaurangaForegroundService::class.java)
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        
        Toast.makeText(this, "🤖 GAURANGA Agent Alpha aktif!", Toast.LENGTH_SHORT).show()
        updateStatus()
    }

    private fun stopGauranga() {
        val intent = Intent(this, GaurangaForegroundService::class.java)
        stopService(intent)
        Toast.makeText(this, "GAURANGA Agent dimatikan", Toast.LENGTH_SHORT).show()
        updateStatus()
    }

    private fun updateStatus() {
        val accessibilityOk = hasAccessibilityPermission()
        val overlayOk = hasOverlayPermission()
        val serviceRunning = isServiceRunning(GaurangaForegroundService::class.java)
        
        val status = buildString {
            append("📋 Status Permissions:\n")
            append(if (accessibilityOk) "✅ Accessibility Service\n" else "❌ Accessibility Service\n")
            append(if (overlayOk) "✅ Overlay Permission\n" else "❌ Overlay Permission\n")
            append("\n🔄 Service Status:\n")
            append(if (serviceRunning) "✅ GAURANGA Agent RUNNING" else "⏸️ GAURANGA Agent STOPPED")
        }
        
        statusText.text = status
        startButton.isEnabled = accessibilityOk && overlayOk
        stopButton.isEnabled = serviceRunning
    }

    private fun isServiceRunning(serviceClass: Class<*>): Boolean {
        val manager = getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        for (service in manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.name == service.service.className) {
                return true
            }
        }
        return false
    }

    fun sendCommand(command: String) {
        val intent = Intent(this, GaurangaForegroundService::class.java).apply {
            action = "com.gauranga.agent.COMMAND"
            putExtra("command", command)
        }
        startService(intent)
    }
}