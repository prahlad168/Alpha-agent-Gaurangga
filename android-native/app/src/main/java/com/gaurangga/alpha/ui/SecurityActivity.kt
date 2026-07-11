package com.gaurangga.alpha.ui

import android.content.Intent
import android.os.Bundle
import android.os.CountDownTimer
import android.util.Log
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.gaurangga.alpha.databinding.ActivitySecurityBinding
import com.gaurangga.alpha.security.BiometricAuthManager

/**
 * SecurityActivity - GAURANGA Lock Screen
 * Handles biometric authentication before showing main app
 */
class SecurityActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySecurityBinding
    private lateinit var biometricManager: BiometricAuthManager
    private var isAuthenticating = false
    private var lockoutTimer: CountDownTimer? = null
    private var failedAttempts = 0
    private val maxAttempts = 5
    private val lockoutDuration = 30_000L // 30 seconds

    companion object {
        private const val TAG = "SecurityActivity"
        const val EXTRA_FROM_BOOT = "from_boot"
        const val EXTRA_LAUNCH_MAIN = "launch_main"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Make activity fullscreen and secure
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
        
        binding = ActivitySecurityBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        biometricManager = BiometricAuthManager(this)
        
        setupUI()
        checkBiometricStatus()
    }

    private fun setupUI() {
        // GAURANGA logo animation
        binding.ivGauranga.alpha = 0f
        binding.ivGauranga.animate()
            .alpha(1f)
            .setDuration(1000)
            .start()

        // Tap to authenticate
        binding.root.setOnClickListener {
            if (!isAuthenticating) {
                startAuthentication()
            }
        }

        binding.btnAuthenticate.setOnClickListener {
            if (!isAuthenticating) {
                startAuthentication()
            }
        }

        // Skip button (for testing only - can be removed in production)
        binding.btnSkip.setOnClickListener {
            Log.w(TAG, "Skip authentication (development mode)")
            proceedToMain()
        }
    }

    private fun checkBiometricStatus() {
        when (biometricManager.isBiometricAvailable()) {
            BiometricAuthManager.BiometricStatus.AVAILABLE -> {
                binding.tvStatus.text = "Sidik jari / wajah siap"
                binding.tvStatus.visibility = View.VISIBLE
                
                // Auto-start authentication after short delay
                binding.root.postDelayed({
                    if (!isAuthenticating) {
                        startAuthentication()
                    }
                }, 1500)
            }
            BiometricAuthManager.BiometricStatus.NOT_ENROLLED -> {
                binding.tvStatus.text = "⚠️ Setup biometric di Settings HP"
                binding.tvStatus.visibility = View.VISIBLE
                binding.btnSkip.visibility = View.VISIBLE
                Toast.makeText(
                    this,
                    "Agar lebih aman, silakan setup fingerprint/face di Settings HP",
                    Toast.LENGTH_LONG
                ).show()
            }
            BiometricAuthManager.BiometricStatus.NO_HARDWARE -> {
                binding.tvStatus.text = "No biometric hardware - using device passcode"
                binding.tvStatus.visibility = View.VISIBLE
                binding.root.postDelayed({
                    startAuthentication()
                }, 1500)
            }
            else -> {
                binding.tvStatus.text = "Biometric unavailable - proceed with caution"
                binding.tvStatus.visibility = View.VISIBLE
                binding.btnSkip.visibility = View.VISIBLE
            }
        }
    }

    private fun startAuthentication() {
        if (isAuthenticating) return
        
        if (failedAttempts >= maxAttempts) {
            showLockout()
            return
        }

        isAuthenticating = true
        binding.btnAuthenticate.isEnabled = false
        binding.tvStatus.text = "🔐 Mengautentikasi..."
        binding.progressBar.visibility = View.VISIBLE

        biometricManager.authenticate(
            activity = this,
            callback = object : BiometricAuthManager.BiometricAuthCallback {
                override fun onAuthSuccess() {
                    runOnUiThread {
                        Log.d(TAG, "Authentication successful!")
                        onAuthenticationSuccess()
                    }
                }

                override fun onAuthFailed(message: String) {
                    runOnUiThread {
                        failedAttempts++
                        Log.d(TAG, "Auth failed: $message (attempts: $failedAttempts)")
                        onAuthenticationFailed(message)
                    }
                }

                override fun onAuthError(errorCode: Int, message: String) {
                    runOnUiThread {
                        Log.e(TAG, "Auth error: $errorCode - $message")
                        onAuthenticationError(message)
                    }
                }

                override fun onAuthLocked(message: String) {
                    runOnUiThread {
                        Log.w(TAG, "Auth locked: $message")
                        showLockout()
                    }
                }
            },
            reason = "Verifikasi untuk akses GAURANGA"
        )
    }

    private fun onAuthenticationSuccess() {
        isAuthenticating = false
        binding.progressBar.visibility = View.GONE
        binding.tvStatus.text = "✅ Verifikasi berhasil!"
        binding.tvStatus.setTextColor(getColor(android.R.color.holo_green_dark))

        // Success animation
        binding.ivGauranga.animate()
            .scaleX(1.2f)
            .scaleY(1.2f)
            .setDuration(300)
            .withEndAction {
                binding.ivGauranga.animate()
                    .scaleX(1f)
                    .scaleY(1f)
                    .setDuration(200)
                    .withEndAction {
                        proceedToMain()
                    }
                    .start()
            }
            .start()
    }

    private fun onAuthenticationFailed(message: String) {
        isAuthenticating = false
        binding.progressBar.visibility = View.GONE
        binding.btnAuthenticate.isEnabled = true
        
        binding.tvStatus.text = "❌ $message"
        binding.tvStatus.setTextColor(getColor(android.R.color.holo_red_dark))
        
        // Shake animation
        binding.cardAuth.animate()
            .translationX(20f)
            .setDuration(50)
            .withEndAction {
                binding.cardAuth.animate()
                    .translationX(-20f)
                    .setDuration(50)
                    .withEndAction {
                        binding.cardAuth.animate()
                            .translationX(10f)
                            .setDuration(50)
                            .withEndAction {
                                binding.cardAuth.animate()
                                    .translationX(0f)
                                    .setDuration(50)
                                    .start()
                            }
                            .start()
                    }
                    .start()
            }
            .start()

        if (failedAttempts >= maxAttempts) {
            showLockout()
        } else {
            binding.tvAttempts.text = "Percobaan: $failedAttempts/$maxAttempts"
            binding.tvAttempts.visibility = View.VISIBLE
        }
    }

    private fun onAuthenticationError(message: String) {
        isAuthenticating = false
        binding.progressBar.visibility = View.GONE
        binding.btnAuthenticate.isEnabled = true
        binding.tvStatus.text = "⚠️ $message"
        binding.tvStatus.setTextColor(getColor(android.R.color.holo_orange_dark))
    }

    private fun showLockout() {
        isAuthenticating = true
        binding.btnAuthenticate.isEnabled = false
        binding.tvStatus.text = "🔒 Terlalu banyak percobaan!"
        binding.tvStatus.setTextColor(getColor(android.R.color.holo_red_dark))
        binding.tvAttempts.text = "Tunggu ${lockoutDuration / 1000} detik..."
        binding.tvAttempts.visibility = View.VISIBLE

        lockoutTimer?.cancel()
        lockoutTimer = object : CountDownTimer(lockoutDuration, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                val seconds = millisUntilFinished / 1000
                binding.tvAttempts.text = "Coba lagi dalam $seconds detik..."
            }

            override fun onFinish() {
                failedAttempts = 0
                isAuthenticating = false
                binding.btnAuthenticate.isEnabled = true
                binding.tvAttempts.visibility = View.GONE
                binding.tvStatus.text = "🔐 Tap untuk coba lagi"
                binding.tvStatus.setTextColor(getColor(android.R.color.darker_gray))
            }
        }.start()
    }

    private fun proceedToMain() {
        val fromBoot = intent.getBooleanExtra(EXTRA_FROM_BOOT, false)
        
        val mainIntent = Intent(this, MainActivity::class.java).apply {
            putExtra(EXTRA_FROM_BOOT, fromBoot)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        
        startActivity(mainIntent)
        finish()
        
        // Slide animation
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
    }

    override fun onDestroy() {
        lockoutTimer?.cancel()
        super.onDestroy()
    }

    override fun onBackPressed() {
        // Prevent back navigation - must authenticate
        Toast.makeText(this, "Verifikasi diperlukan untuk akses", Toast.LENGTH_SHORT).show()
    }
}
