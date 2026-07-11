package com.gaurangga.alpha.security

import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import android.util.Log
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import java.util.concurrent.Executor

/**
 * BiometricAuthManager - GAURANGA Biometric Authentication
 * Handles fingerprint and face recognition authentication
 */
class BiometricAuthManager(private val context: Context) {

    companion object {
        private const val TAG = "BiometricAuthManager"
        private const val PREFS_NAME = "gauranga_security_prefs"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_BIOMETRIC_SETUP_COMPLETE = "biometric_setup_complete"
        private const val KEY_TRUSTED_DEVICE = "trusted_device"
        private const val KEY_LAST_AUTH_TIME = "last_auth_time"
        private const val AUTH_VALIDITY_DURATION = 5 * 60 * 1000L // 5 minutes
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val biometricManager = BiometricManager.from(context)
    private lateinit var executor: Executor
    private var callback: BiometricAuthCallback? = null

    /**
     * Check if device supports biometric authentication
     */
    fun isBiometricAvailable(): BiometricStatus {
        return when (biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
            BiometricManager.Authenticators.BIOMETRIC_WEAK
        )) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                Log.d(TAG, "Biometric authentication available")
                BiometricStatus.AVAILABLE
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                Log.w(TAG, "No biometric hardware")
                BiometricStatus.NO_HARDWARE
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                Log.w(TAG, "Biometric hardware unavailable")
                BiometricStatus.HARDWARE_UNAVAILABLE
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                Log.w(TAG, "No biometric enrolled")
                BiometricStatus.NOT_ENROLLED
            }
            BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED -> {
                Log.w(TAG, "Security update required")
                BiometricStatus.SECURITY_UPDATE_REQUIRED
            }
            else -> BiometricStatus.UNKNOWN
        }
    }

    /**
     * Check if biometric is enabled by user
     */
    fun isBiometricEnabled(): Boolean {
        return prefs.getBoolean(KEY_BIOMETRIC_ENABLED, true)
    }

    /**
     * Enable/disable biometric authentication
     */
    fun setBiometricEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
        Log.d(TAG, "Biometric enabled: $enabled")
    }

    /**
     * Check if biometric setup is complete
     */
    fun isSetupComplete(): Boolean {
        return prefs.getBoolean(KEY_BIOMETRIC_SETUP_COMPLETE, false)
    }

    /**
     * Mark biometric setup as complete
     */
    fun markSetupComplete() {
        prefs.edit().putBoolean(KEY_BIOMETRIC_SETUP_COMPLETE, true).apply()
    }

    /**
     * Check if current device is trusted (no auth needed for X minutes)
     */
    fun isTrustedDevice(): Boolean {
        if (!isBiometricEnabled()) return true
        
        val lastAuth = prefs.getLong(KEY_LAST_AUTH_TIME, 0)
        val now = System.currentTimeMillis()
        
        return (now - lastAuth) < AUTH_VALIDITY_DURATION
    }

    /**
     * Update last authentication time
     */
    fun updateLastAuthTime() {
        prefs.edit().putLong(KEY_LAST_AUTH_TIME, System.currentTimeMillis()).apply()
    }

    /**
     * Start biometric authentication
     */
    fun authenticate(
        activity: FragmentActivity,
        callback: BiometricAuthCallback,
        reason: String = "Verifikasi identitas Anda untuk GAURANGA"
    ) {
        this.callback = callback
        this.executor = ContextCompat.getMainExecutor(context)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("GAURANGA - Verifikasi")
            .setSubtitle(reason)
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.BIOMETRIC_WEAK or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        val biometricPrompt = BiometricPrompt(activity, executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    Log.d(TAG, "Auth error: $errorCode - $errString")
                    when (errorCode) {
                        BiometricPrompt.ERROR_USER_CANCELED,
                        BiometricPrompt.ERROR_NEGATIVE_BUTTON -> {
                            callback.onAuthFailed("Dibatalkan oleh pengguna")
                        }
                        BiometricPrompt.ERROR_LOCKOUT,
                        BiometricPrompt.ERROR_LOCKOUT_PERMANENT -> {
                            callback.onAuthLocked("Terlalu banyak percobaan. Coba lagi nanti.")
                        }
                        else -> {
                            callback.onAuthError(errorCode, errString.toString())
                        }
                    }
                }

                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    Log.d(TAG, "Auth success!")
                    updateLastAuthTime()
                    callback.onAuthSuccess()
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    Log.d(TAG, "Auth failed")
                    callback.onAuthFailed("Sidik jari / wajah tidak cocok. Coba lagi.")
                }
            })

        biometricPrompt.authenticate(promptInfo)
    }

    /**
     * Check if authentication is required
     */
    fun requiresAuthentication(): Boolean {
        return isBiometricEnabled() && !isTrustedDevice()
    }

    /**
     * Clear authentication trust (force re-auth)
     */
    fun clearTrust() {
        prefs.edit().putLong(KEY_LAST_AUTH_TIME, 0).apply()
    }

    /**
     * Get enrolled biometric types
     */
    fun getEnrolledBiometricTypes(): List<BiometricType> {
        val types = mutableListOf<BiometricType>()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val enrolled = biometricManager.getEnrolledAuthenticators
            if (enrolled and BiometricManager.Authenticators.BIOMETRIC_STRONG != 0) {
                types.add(BiometricType.FINGERPRINT_STRONG)
            }
            if (enrolled and BiometricManager.Authenticators.BIOMETRIC_WEAK != 0) {
                types.add(BiometricType.FINGERPRINT_WEAK)
                types.add(BiometricType.FACE)
            }
        }
        
        return types
    }

    /**
     * Reset all security settings
     */
    fun resetSecurity() {
        prefs.edit().clear().apply()
        Log.d(TAG, "Security settings reset")
    }

    /**
     * Biometric Status
     */
    enum class BiometricStatus {
        AVAILABLE,
        NO_HARDWARE,
        HARDWARE_UNAVAILABLE,
        NOT_ENROLLED,
        SECURITY_UPDATE_REQUIRED,
        UNKNOWN
    }

    /**
     * Biometric Type
     */
    enum class BiometricType {
        FINGERPRINT_STRONG,
        FINGERPRINT_WEAK,
        FACE,
        IRIS
    }

    /**
     * Authentication Callback
     */
    interface BiometricAuthCallback {
        fun onAuthSuccess()
        fun onAuthFailed(message: String)
        fun onAuthError(errorCode: Int, message: String)
        fun onAuthLocked(message: String)
    }
}
