package com.gaurangga.alpha.startup

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.provider.Settings
import android.util.Log
import androidx.biometric.BiometricManager
import com.gaurangga.alpha.security.BiometricAuthManager
import com.gaurangga.alpha.service.GaurangaVoiceService
import com.gaurangga.alpha.ui.MainActivity
import com.gaurangga.alpha.ui.SecurityActivity

/**
 * AutoStartManager - GAURANGA Auto Start & Auto Deploy Manager
 * Handles all auto-start scenarios and startup configuration
 */
class AutoStartManager(private val context: Context) {

    companion object {
        private const val TAG = "AutoStartManager"
        
        // Preference keys
        private const val PREFS_NAME = "gauranga_startup_prefs"
        private const val KEY_AUTO_START = "auto_start_enabled"
        private const val KEY_LAUNCH_MODE = "launch_mode"
        private const val KEY_FIRST_LAUNCH = "first_launch"
        private const val KEY_SETUP_COMPLETE = "setup_complete"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_LAUNCH_COUNT = "launch_count"
        private const val KEY_LAST_LAUNCH_TIME = "last_launch_time"
        private const val KEY_SERVICE_AUTO_START = "service_auto_start"
        
        // Launch modes
        const val MODE_FULL = "full"           // Lock → Main → Service
        const val MODE_LOCK_ONLY = "lock_only" // Lock screen only
        const val MODE_SERVICE_ONLY = "service_only" // Background service only
        const val MODE_DIRECT = "direct"       // Direct to main (no lock)
        
        // Timeouts
        private const val TRUSTED_SESSION_DURATION = 5 * 60 * 1000L // 5 minutes
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val biometricManager = BiometricAuthManager(context)
    private val packageManager: PackageManager = context.packageManager

    /**
     * Initialize startup system - call on app first launch
     */
    fun initialize() {
        Log.d(TAG, "🚀 Initializing GAURANGA Auto-Start System...")
        
        if (isFirstLaunch()) {
            Log.d(TAG, "📱 First launch detected - setting up defaults")
            setupDefaults()
        }
        
        incrementLaunchCount()
        updateLastLaunchTime()
        
        Log.d(TAG, "✅ Auto-Start System initialized")
        Log.d(TAG, "   - Launch mode: ${getLaunchMode()}")
        Log.d(TAG, "   - Biometric enabled: ${isBiometricEnabled()}")
        Log.d(TAG, "   - Service auto-start: ${isServiceAutoStart()}")
    }

    /**
     * Setup default values for first launch
     */
    private fun setupDefaults() {
        prefs.edit().apply {
            putBoolean(KEY_AUTO_START, true)
            putString(KEY_LAUNCH_MODE, MODE_FULL)
            putBoolean(KEY_FIRST_LAUNCH, false)
            putBoolean(KEY_SETUP_COMPLETE, false)
            putBoolean(KEY_BIOMETRIC_ENABLED, true)
            putBoolean(KEY_SERVICE_AUTO_START, true)
        }
        Log.d(TAG, "📋 Default settings applied")
    }

    /**
     * Perform complete auto-start sequence
     * This is the main entry point for boot/startup
     */
    fun performAutoStart(): StartResult {
        Log.d(TAG, "🎯 Performing auto-start sequence...")
        
        // Check if auto-start is enabled
        if (!isAutoStartEnabled()) {
            Log.d(TAG, "⏭️ Auto-start disabled by user")
            return StartResult.SKIPPED
        }

        val mode = getLaunchMode()
        Log.d(TAG, "📌 Launch mode: $mode")

        return when (mode) {
            MODE_FULL -> startFullMode()
            MODE_LOCK_ONLY -> startLockOnlyMode()
            MODE_SERVICE_ONLY -> startServiceOnlyMode()
            MODE_DIRECT -> startDirectMode()
            else -> startFullMode() // Default fallback
        }
    }

    /**
     * Full mode: Lock Screen → Main Activity → Voice Service
     */
    private fun startFullMode(): StartResult {
        Log.d(TAG, "🔐 Starting in FULL mode (Lock → Main → Service)")
        
        // If biometric required and not trusted, show lock screen
        if (isBiometricEnabled() && !isTrustedSession()) {
            Log.d(TAG, "🔒 Biometric required - starting SecurityActivity")
            startSecurityActivity(fromBoot = true)
        } else {
            Log.d(TAG, "✅ Session trusted - starting MainActivity directly")
            startMainActivity(fromBoot = true)
        }
        
        // Auto-start voice service in background
        if (isServiceAutoStart()) {
            startVoiceService()
        }
        
        return StartResult.SUCCESS
    }

    /**
     * Lock only mode: Show lock screen only
     */
    private fun startLockOnlyMode(): StartResult {
        Log.d(TAG, "🔐 Starting in LOCK ONLY mode")
        startSecurityActivity(fromBoot = true)
        return StartResult.SUCCESS
    }

    /**
     * Service only mode: Start background service without UI
     */
    private fun startServiceOnlyMode(): StartResult {
        Log.d(TAG, "🎙️ Starting in SERVICE ONLY mode")
        startVoiceService()
        return StartResult.SUCCESS
    }

    /**
     * Direct mode: Skip lock screen, go directly to main
     */
    private fun startDirectMode(): StartResult {
        Log.d(TAG, "⚡ Starting in DIRECT mode")
        startMainActivity(fromBoot = true)
        if (isServiceAutoStart()) {
            startVoiceService()
        }
        return StartResult.SUCCESS
    }

    /**
     * Start SecurityActivity (Lock Screen)
     */
    private fun startSecurityActivity(fromBoot: Boolean) {
        val intent = Intent(context, SecurityActivity::class.java).apply {
            putExtra(SecurityActivity.EXTRA_FROM_BOOT, fromBoot)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
        }
        
        context.startActivity(intent)
        Log.d(TAG, "✅ SecurityActivity started")
    }

    /**
     * Start MainActivity
     */
    private fun startMainActivity(fromBoot: Boolean) {
        val intent = Intent(context, MainActivity::class.java).apply {
            putExtra("fromBoot", fromBoot)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
        }
        
        context.startActivity(intent)
        Log.d(TAG, "✅ MainActivity started")
    }

    /**
     * Start Voice Service in foreground
     */
    private fun startVoiceService() {
        val intent = Intent(context, GaurangaVoiceService::class.java)
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent)
        } else {
            context.startService(intent)
        }
        
        Log.d(TAG, "✅ VoiceService started")
    }

    /**
     * Check if current session is trusted (within validity period)
     */
    fun isTrustedSession(): Boolean {
        if (!isBiometricEnabled()) return true
        
        val lastAuth = prefs.getLong("last_auth_time", 0)
        val now = System.currentTimeMillis()
        
        return (now - lastAuth) < TRUSTED_SESSION_DURATION
    }

    /**
     * Mark session as authenticated
     */
    fun markSessionAuthenticated() {
        prefs.edit().putLong("last_auth_time", System.currentTimeMillis()).apply()
        Log.d(TAG, "✅ Session marked as authenticated")
    }

    /**
     * Get current launch mode
     */
    fun getLaunchMode(): String {
        return prefs.getString(KEY_LAUNCH_MODE, MODE_FULL) ?: MODE_FULL
    }

    /**
     * Set launch mode
     */
    fun setLaunchMode(mode: String) {
        val validModes = listOf(MODE_FULL, MODE_LOCK_ONLY, MODE_SERVICE_ONLY, MODE_DIRECT)
        if (mode in validModes) {
            prefs.edit().putString(KEY_LAUNCH_MODE, mode).apply()
            Log.d(TAG, "📌 Launch mode set to: $mode")
        } else {
            Log.w(TAG, "⚠️ Invalid launch mode: $mode")
        }
    }

    /**
     * Check if auto-start is enabled
     */
    fun isAutoStartEnabled(): Boolean {
        return prefs.getBoolean(KEY_AUTO_START, true)
    }

    /**
     * Enable/disable auto-start
     */
    fun setAutoStartEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_AUTO_START, enabled).apply()
        Log.d(TAG, "📌 Auto-start ${if (enabled) "enabled" else "disabled"}")
    }

    /**
     * Check if biometric is enabled
     */
    fun isBiometricEnabled(): Boolean {
        return prefs.getBoolean(KEY_BIOMETRIC_ENABLED, true)
    }

    /**
     * Enable/disable biometric authentication
     */
    fun setBiometricEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
        Log.d(TAG, "📌 Biometric ${if (enabled) "enabled" else "disabled"}")
    }

    /**
     * Check if service auto-start is enabled
     */
    fun isServiceAutoStart(): Boolean {
        return prefs.getBoolean(KEY_SERVICE_AUTO_START, true)
    }

    /**
     * Enable/disable service auto-start
     */
    fun setServiceAutoStart(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_SERVICE_AUTO_START, enabled).apply()
        Log.d(TAG, "📌 Service auto-start ${if (enabled) "enabled" else "disabled"}")
    }

    /**
     * Check if this is first launch
     */
    fun isFirstLaunch(): Boolean {
        return prefs.getBoolean(KEY_FIRST_LAUNCH, true)
    }

    /**
     * Check if setup is complete
     */
    fun isSetupComplete(): Boolean {
        return prefs.getBoolean(KEY_SETUP_COMPLETE, false)
    }

    /**
     * Mark setup as complete
     */
    fun markSetupComplete() {
        prefs.edit().putBoolean(KEY_SETUP_COMPLETE, true).apply()
        Log.d(TAG, "✅ Setup marked as complete")
    }

    /**
     * Get launch count
     */
    fun getLaunchCount(): Int {
        return prefs.getInt(KEY_LAUNCH_COUNT, 0)
    }

    private fun incrementLaunchCount() {
        val count = prefs.getInt(KEY_LAUNCH_COUNT, 0)
        prefs.edit().putInt(KEY_LAUNCH_COUNT, count + 1).apply()
    }

    private fun updateLastLaunchTime() {
        prefs.edit().putLong(KEY_LAST_LAUNCH_TIME, System.currentTimeMillis()).apply()
    }

    /**
     * Check if device supports required features
     */
    fun checkDeviceCapabilities(): DeviceCapabilities {
        val biometricStatus = biometricManager.isBiometricAvailable()
        
        return DeviceCapabilities(
            hasBiometric = biometricStatus == BiometricAuthManager.BiometricStatus.AVAILABLE,
            hasMicrophone = context.packageManager.hasSystemFeature(PackageManager.FEATURE_MICROPHONE),
            hasSpeaker = context.packageManager.hasSystemFeature(PackageManager.FEATURE_AUDIO_OUTPUT),
            supportsForegroundService = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O,
            supportsBackgroundApps = Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q
        )
    }

    /**
     * Open device-specific auto-start settings
     */
    fun openAutoStartSettings(): Boolean {
        Log.d(TAG, "🔧 Opening auto-start settings...")
        
        val autoStartIntents = getAutoStartIntents()
        
        for (intent in autoStartIntents) {
            try {
                if (intent.resolveActivity(packageManager) != null) {
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    context.startActivity(intent)
                    Log.d(TAG, "✅ Opened: ${intent.component}")
                    return true
                }
            } catch (e: Exception) {
                Log.w(TAG, "⚠️ Cannot open: ${intent.component}")
            }
        }
        
        // Fallback to app settings
        try {
            val settingsIntent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                data = android.net.Uri.parse("package:${context.packageName}")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(settingsIntent)
            return true
        } catch (e: Exception) {
            Log.e(TAG, "❌ Cannot open settings", e)
            return false
        }
    }

    /**
     * Get list of manufacturer-specific auto-start intents
     */
    private fun getAutoStartIntents(): List<Intent> {
        val intents = mutableListOf<Intent>()
        val manufacturer = Build.MANUFACTURER.lowercase()
        
        // Xiaomi
        if (manufacturer.contains("xiaomi") || manufacturer.contains("redmi")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.miui.securitycenter",
                    "com.miui.permcenter.autostart.AutoStartManagementActivity"
                )
            ))
        }
        
        // Samsung
        if (manufacturer.contains("samsung")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.samsung.android.lool",
                    "com.samsung.android.sm.ui.battery.BatteryActivity"
                )
            ))
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.samsung.android.sm",
                    "com.samsung.android.sm.ui.battery.BatteryActivity"
                )
            ))
        }
        
        // Huawei
        if (manufacturer.contains("huawei") || manufacturer.contains("honor")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.huawei.systemmanager",
                    "com.huawei.systemmanager.startupmgr.ui.StartupNormalAppListActivity"
                )
            ))
        }
        
        // Oppo
        if (manufacturer.contains("oppo") || manufacturer.contains("realme") || manufacturer.contains("oneplus")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.coloros.safecenter",
                    "com.coloros.safecenter.permission.startup.StartupAppListActivity"
                )
            ))
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.coloros.safecenter",
                    "com.coloros.safecenter.startupapp.StartupAppListActivity"
                )
            ))
        }
        
        // Vivo
        if (manufacturer.contains("vivo")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.vivo.permissionmanager",
                    "com.vivo.permissionmanager.activity.BgStartUpManagerActivity"
                )
            ))
        }
        
        // Asus
        if (manufacturer.contains("asus")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.asus.mobilemanager",
                    "com.asus.mobilemanager.autostart.AutoStartActivity"
                )
            ))
        }
        
        // Lenovo
        if (manufacturer.contains("lenovo")) {
            intents.add(Intent().setComponent(
                ComponentName(
                    "com.lenovo.security",
                    "com.lenovo.security.purebackground.PureBackgroundActivity"
                )
            ))
        }
        
        return intents
    }

    /**
     * Reset all startup settings to defaults
     */
    fun resetToDefaults() {
        prefs.edit().clear().apply()
        setupDefaults()
        Log.d(TAG, "🔄 All settings reset to defaults")
    }

    /**
     * Get startup configuration summary
     */
    fun getConfigurationSummary(): Map<String, Any> {
        return mapOf(
            "autoStartEnabled" to isAutoStartEnabled(),
            "launchMode" to getLaunchMode(),
            "biometricEnabled" to isBiometricEnabled(),
            "serviceAutoStart" to isServiceAutoStart(),
            "isTrustedSession" to isTrustedSession(),
            "launchCount" to getLaunchCount(),
            "isFirstLaunch" to isFirstLaunch(),
            "isSetupComplete" to isSetupComplete(),
            "manufacturer" to Build.MANUFACTURER,
            "androidVersion" to Build.VERSION.SDK_INT
        )
    }

    /**
     * Start Result
     */
    enum class StartResult {
        SUCCESS,
        SKIPPED,
        FAILED
    }

    /**
     * Device Capabilities
     */
    data class DeviceCapabilities(
        val hasBiometric: Boolean,
        val hasMicrophone: Boolean,
        val hasSpeaker: Boolean,
        val supportsForegroundService: Boolean,
        val supportsBackgroundApps: Boolean
    )
}
