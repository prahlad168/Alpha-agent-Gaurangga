package com.gauranga.agent.services

import android.content.Context
import android.os.Build
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Log
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

class BiometricAuth(private val context: Context) {

    companion object {
        const val TAG = "GAURANGA_BIOMETRIC"
        private const val KEY_NAME = "gauranga_biometric_key"
    }

    private val biometricManager = BiometricManager.from(context)

    /**
     * Check if biometric authentication is available
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
                BiometricStatus.SECURITY_UPDATE_REQUIRED
            }
            else -> BiometricStatus.UNKNOWN
        }
    }

    /**
     * Show biometric prompt
     */
    fun authenticate(
        activity: FragmentActivity,
        title: String = "GAURANGA Authentication",
        subtitle: String = "Verifikasi identitas Anda",
        negativeButtonText: String = "Batal",
        onSuccess: () -> Unit,
        onError: (String) -> Unit,
        onFallback: () -> Unit = {}
    ) {
        val executor = ContextCompat.getMainExecutor(context)

        val callback = object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                super.onAuthenticationSucceeded(result)
                Log.d(TAG, "Biometric authentication succeeded")
                onSuccess()
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                Log.d(TAG, "Biometric error: $errString")
                
                when (errorCode) {
                    BiometricPrompt.ERROR_NEGATIVE_BUTTON,
                    BiometricPrompt.ERROR_USER_CANCELED -> {
                        onFallback()
                    }
                    else -> {
                        onError(errString.toString())
                    }
                }
            }

            override fun onAuthenticationFailed() {
                super.onAuthenticationFailed()
                Log.w(TAG, "Biometric authentication failed")
            }
        }

        val biometricPrompt = BiometricPrompt(activity, executor, callback)

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText(negativeButtonText)
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.BIOMETRIC_WEAK or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        biometricPrompt.authenticate(promptInfo)
    }

    /**
     * Generate encryption key for secure storage
     */
    fun generateSecretKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)

        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val keyGenParameterSpec = KeyGenParameterSpec.Builder(
            KEY_NAME,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(true)
            .setInvalidatedByBiometricEnrollment(true)
            .build()

        keyGenerator.init(keyGenParameterSpec)
        return keyGenerator.generateKey()
    }

    /**
     * Get biometric type name
     */
    fun getBiometricType(): String {
        val pm = context.packageManager
        
        return when {
            pm.hasSystemFeature("android.hardware.fingerprint") -> "Fingerprint"
            pm.hasSystemFeature("android.hardware.iris") -> "Iris"
            pm.hasSystemFeature("android.hardware.biometrics") -> "Biometric"
            pm.hasSystemFeature("android.hardware.face") -> "Face"
            else -> "Unknown"
        }
    }

    enum class BiometricStatus {
        AVAILABLE,
        NO_HARDWARE,
        HARDWARE_UNAVAILABLE,
        NOT_ENROLLED,
        SECURITY_UPDATE_REQUIRED,
        UNKNOWN
    }
}