package com.gauranga.agent

import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.gauranga.agent.services.BiometricAuth
import com.gauranga.agent.services.GaurangaForegroundService

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    
    private lateinit var biometricAuth: BiometricAuth
    private var isAuthenticated = false
    
    companion object {
        const val TAG = "GAURANGA"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        
        biometricAuth = BiometricAuth(this)
        
        when (biometricAuth.isBiometricAvailable()) {
            BiometricAuth.BiometricStatus.AVAILABLE -> {
                showBiometricScreen()
            }
            else -> {
                isAuthenticated = true
                showMainScreen()
            }
        }
    }

    private fun showBiometricScreen() {
        setContentView(R.layout.activity_biometric)
        
        val biometricStatusText = findViewById<TextView>(R.id.biometricStatus)
        val biometricButton = findViewById<Button>(R.id.authenticateButton)
        val skipButton = findViewById<Button>(R.id.skipButton)
        
        val biometricType = biometricAuth.getBiometricType()
        biometricStatusText.text = "🔐 Biometric Authentication Required\n\n" +
                "Gunakan $biometricType untuk verifikasi identitas\n" +
                "Owner: I Made Purna Ananda"
        
        biometricButton.setOnClickListener { authenticateWithBiometric() }
        skipButton.setOnClickListener { proceedWithoutAuth() }
    }

    private fun authenticateWithBiometric() {
        biometricAuth.authenticate(
            activity = this,
            title = "GAURANGA Agent Alpha",
            subtitle = "Verifikasi identitas Anda",
            negativeButtonText = "Batal",
            onSuccess = {
                isAuthenticated = true
                Toast.makeText(this, "✅ Autentikasi berhasil!", Toast.LENGTH_SHORT).show()
                showMainScreen()
            },
            onError = { error ->
                Toast.makeText(this, "❌ $error", Toast.LENGTH_SHORT).show()
            },
            onFallback = {
                Toast.makeText(this, "Batal", Toast.LENGTH_SHORT).show()
            }
        )
    }

    private fun proceedWithoutAuth() {
        isAuthenticated = true
        showMainScreen()
    }

    private fun showMainScreen() {
        setContentView(R.layout.activity_main)
        initViews()
        setupClickListeners()
        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        if (isAuthenticated) updateStatus()
    }

    private fun initViews() {
        statusText = findViewById(R.id.statusText)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
    }

    private fun setupClickListeners() {
        startButton.setOnClickListener {
            if (checkAllPermissions()) startGauranga() else requestPermissions()
        }
        stopButton.setOnClickListener { stopGauranga() }
        findViewById<View>(R.id.accessibilityCard)?.setOnClickListener { openAccessibilitySettings() }
        findViewById<View>(R.id.overlayCard)?.setOnClickListener { openOverlaySettings() }
    }

    private fun checkAllPermissions() = hasAccessibilityPermission() && hasOverlayPermission()

    private fun hasAccessibilityPermission(): Boolean {
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
        return enabledServices?.contains(packageName) == true
    }

    private fun hasOverlayPermission() = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) Settings.canDrawOverlays(this) else true

    private fun requestPermissions() {
        if (!hasAccessibilityPermission()) {
            Toast.makeText(this, "Aktifkan Accessibility Service", Toast.LENGTH_SHORT).show()
            openAccessibilitySettings()
        } else if (!hasOverlayPermission()) {
            Toast.makeText(this, "Izinkan Overlay", Toast.LENGTH_SHORT).show()
            openOverlaySettings()
        }
    }

    private fun openAccessibilitySettings() {
        try { startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) } 
        catch (e: Exception) { Toast.makeText(this, "Error", Toast.LENGTH_SHORT).show() }
    }

    private fun openOverlaySettings() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            startActivity(Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, android.net.Uri.parse("package:$packageName")))
        }
    }

    private fun startGauranga() {
        val intent = Intent(this, GaurangaForegroundService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent) else startService(intent)
        Toast.makeText(this, "🤖 GAURANGA Agent Alpha aktif!", Toast.LENGTH_SHORT).show()
        updateStatus()
    }

    private fun stopGauranga() {
        stopService(Intent(this, GaurangaForegroundService::class.java))
        Toast.makeText(this, "GAURANGA Agent dimatikan", Toast.LENGTH_SHORT).show()
        updateStatus()
    }

    private fun updateStatus() {
        if (!isAuthenticated) return
        val accessibilityOk = hasAccessibilityPermission()
        val overlayOk = hasOverlayPermission()
        val serviceRunning = isServiceRunning(GaurangaForegroundService::class.java)
        
        statusText.text = buildString {
            append("📋 Status Permissions:\n")
            append(if (accessibilityOk) "✅ Accessibility Service\n" else "❌ Accessibility Service\n")
            append(if (overlayOk) "✅ Overlay Permission\n" else "❌ Overlay Permission\n")
            append("\n🔄 Service Status:\n")
            append(if (serviceRunning) "✅ GAURANGA Agent RUNNING" else "⏸️ GAURANGA Agent STOPPED")
        }
        startButton.isEnabled = accessibilityOk && overlayOk
        stopButton.isEnabled = serviceRunning
    }

    private fun isServiceRunning(serviceClass: Class<*>): Boolean {
        val manager = getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        return manager.getRunningServices(Integer.MAX_VALUE).any { it.service.className == serviceClass.name }
    }

    fun sendCommand(command: String) {
        startService(Intent(this, GaurangaForegroundService::class.java).apply {
            action = "com.gauranga.agent.COMMAND"
            putExtra("command", command)
        })
    }
}
