package com.gaurangga.alpha.ui

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.gaurangga.alpha.databinding.ActivityStartupSettingsBinding
import com.gaurangga.alpha.startup.AutoStartManager
import com.gaurangga.alpha.security.BiometricAuthManager

/**
 * StartupSettingsActivity - GAURANGA Auto-Start Settings
 * Configure startup behavior, biometric, and service settings
 */
class StartupSettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityStartupSettingsBinding
    private lateinit var autoStartManager: AutoStartManager
    private lateinit var biometricManager: BiometricAuthManager

    companion object {
        private const val TAG = "StartupSettings"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityStartupSettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        autoStartManager = AutoStartManager(this)
        biometricManager = BiometricAuthManager(this)

        setupToolbar()
        loadCurrentSettings()
        setupListeners()
        checkDeviceCapabilities()
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }

    private fun loadCurrentSettings() {
        // Load current settings
        binding.switchAutoStart.isChecked = autoStartManager.isAutoStartEnabled()
        binding.switchBiometric.isChecked = autoStartManager.isBiometricEnabled()
        binding.switchServiceAutoStart.isChecked = autoStartManager.isServiceAutoStart()

        // Load launch mode
        val currentMode = autoStartManager.getLaunchMode()
        val modes = listOf(
            AutoStartManager.MODE_FULL to "🔐 Full (Lock → Main → Service)",
            AutoStartManager.MODE_LOCK_ONLY to "🔒 Lock Only",
            AutoStartManager.MODE_SERVICE_ONLY to "🎙️ Service Only",
            AutoStartManager.MODE_DIRECT to "⚡ Direct (No Lock)"
        )

        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            modes.map { it.second }
        )
        binding.spinnerLaunchMode.adapter = adapter

        // Find current selection
        val selectedIndex = modes.indexOfFirst { it.first == currentMode }
        if (selectedIndex >= 0) {
            binding.spinnerLaunchMode.setSelection(selectedIndex)
        }

        // Load stats
        binding.tvLaunchCount.text = "Total launches: ${autoStartManager.getLaunchCount()}"

        // Update biometric status
        updateBiometricStatus()
    }

    private fun setupListeners() {
        // Auto-start switch
        binding.switchAutoStart.setOnCheckedChangeListener { _, isChecked ->
            autoStartManager.setAutoStartEnabled(isChecked)
            Toast.makeText(
                this,
                "Auto-start ${if (isChecked) "enabled" else "disabled"}",
                Toast.LENGTH_SHORT
            ).show()
        }

        // Biometric switch
        binding.switchBiometric.setOnCheckedChangeListener { _, isChecked ->
            autoStartManager.setBiometricEnabled(isChecked)
            Toast.makeText(
                this,
                "Biometric ${if (isChecked) "enabled" else "disabled"}",
                Toast.LENGTH_SHORT
            ).show()
        }

        // Service auto-start switch
        binding.switchServiceAutoStart.setOnCheckedChangeListener { _, isChecked ->
            autoStartManager.setServiceAutoStart(isChecked)
            Toast.makeText(
                this,
                "Service auto-start ${if (isChecked) "enabled" else "disabled"}",
                Toast.LENGTH_SHORT
            ).show()
        }

        // Launch mode spinner
        binding.spinnerLaunchMode.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val modes = listOf(
                    AutoStartManager.MODE_FULL,
                    AutoStartManager.MODE_LOCK_ONLY,
                    AutoStartManager.MODE_SERVICE_ONLY,
                    AutoStartManager.MODE_DIRECT
                )
                if (position in modes.indices) {
                    autoStartManager.setLaunchMode(modes[position])
                }
            }

            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        // Open device auto-start settings
        binding.btnOpenAutoStartSettings.setOnClickListener {
            openAutoStartSettings()
        }

        // Open biometric settings
        binding.btnOpenBiometricSettings.setOnClickListener {
            openBiometricSettings()
        }

        // Reset to defaults
        binding.btnResetDefaults.setOnClickListener {
            resetToDefaults()
        }

        // Test auto-start
        binding.btnTestStartup.setOnClickListener {
            testAutoStart()
        }
    }

    private fun checkDeviceCapabilities() {
        val capabilities = autoStartManager.checkDeviceCapabilities()

        binding.tvCapabilities.text = """
            📱 Device Capabilities:
            
            ✅ Fingerprint/Face: ${if (capabilities.hasBiometric) "Available" else "Not Available"}
            ✅ Microphone: ${if (capabilities.hasMicrophone) "Available" else "Not Available"}
            ✅ Speaker: ${if (capabilities.hasSpeaker) "Available" else "Not Available"}
            ✅ Foreground Service: API ${if (capabilities.supportsForegroundService) "26+" else "Below 26"}
            ✅ Background Apps: API ${if (capabilities.supportsBackgroundApps) "29+" else "Below 29"}
            
            📋 Manufacturer: ${android.os.Build.MANUFACTURER}
            📋 Android: ${android.os.Build.VERSION.SDK_INT}
        """.trimIndent()
    }

    private fun updateBiometricStatus() {
        val status = biometricManager.isBiometricAvailable()

        val statusText = when (status) {
            BiometricAuthManager.BiometricStatus.AVAILABLE -> "✅ Available"
            BiometricAuthManager.BiometricStatus.NO_HARDWARE -> "❌ No Biometric Hardware"
            BiometricAuthManager.BiometricStatus.NOT_ENROLLED -> "⚠️ Not Enrolled - Setup in Settings"
            BiometricAuthManager.BiometricStatus.HARDWARE_UNAVAILABLE -> "⚠️ Hardware Temporarily Unavailable"
            BiometricAuthManager.BiometricStatus.SECURITY_UPDATE_REQUIRED -> "⚠️ Security Update Required"
            else -> "❓ Unknown"
        }

        binding.tvBiometricStatus.text = statusText
        binding.switchBiometric.isEnabled = status == BiometricAuthManager.BiometricStatus.AVAILABLE
    }

    private fun openAutoStartSettings() {
        val success = autoStartManager.openAutoStartSettings()
        if (!success) {
            Toast.makeText(
                this,
                "Could not open auto-start settings. Please enable manually in your phone's app settings.",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private fun openBiometricSettings() {
        try {
            val intent = Intent(android.provider.Settings.ACTION_SECURITY_SETTINGS)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(
                this,
                "Could not open biometric settings. Please open manually in Settings.",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private fun resetToDefaults() {
        autoStartManager.resetToDefaults()
        loadCurrentSettings()
        Toast.makeText(this, "Settings reset to defaults", Toast.LENGTH_SHORT).show()
    }

    private fun testAutoStart() {
        Toast.makeText(this, "Testing auto-start sequence...", Toast.LENGTH_SHORT).show()
        autoStartManager.initialize()
        val result = autoStartManager.performAutoStart()

        val message = when (result) {
            AutoStartManager.StartResult.SUCCESS -> "✅ Auto-start test successful!"
            AutoStartManager.StartResult.SKIPPED -> "⏭️ Auto-start is disabled"
            AutoStartManager.StartResult.FAILED -> "❌ Auto-start test failed"
        }

        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        finish()
    }
}
