package com.gauranga.agent.services

import android.annotation.SuppressLint
import android.app.Service
import android.content.Intent
import android.graphics.PixelFormat
import android.os.IBinder
import android.view.*
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import com.gauranga.agent.R

class GaurangaOverlayService : Service() {

    companion object {
        var instance: GaurangaOverlayService? = null
        const val ACTION_TOGGLE = "com.gauranga.agent.TOGGLE_OVERLAY"
    }

    private var windowManager: WindowManager? = null
    private var floatingView: View? = null
    private var chatView: View? = null
    private var isChatOpen = false

    override fun onCreate() {
        super.onCreate()
        instance = this
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_TOGGLE -> toggleChat()
            else -> showFloatingButton()
        }
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        removeFloatingButton()
        removeChatView()
        instance = null
    }

    // ========== FLOATING BUTTON ==========
    
    @SuppressLint("ClickableViewAccessibility")
    private fun showFloatingButton() {
        if (floatingView != null) return

        val inflater = LayoutInflater.from(this)
        floatingView = inflater.inflate(R.layout.overlay_floating, null)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.END
            x = 20
            y = 200
        }

        // Drag functionality
        var initialX = 0
        var initialY = 0
        var initialTouchX = 0f
        var initialTouchY = 0f

        floatingView?.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x
                    initialY = params.y
                    initialTouchX = event.rawX
                    initialTouchY = event.rawY
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    params.x = initialX - (event.rawX - initialTouchX).toInt()
                    params.y = initialY + (event.rawY - initialTouchY).toInt()
                    windowManager?.updateViewLayout(floatingView, params)
                    true
                }
                MotionEvent.ACTION_UP -> {
                    if (event.rawX - initialTouchX < 50 && event.rawY - initialTouchY < 50) {
                        toggleChat()
                    }
                    true
                }
                else -> false
            }
        }

        floatingView?.findViewById<Button>(R.id.fabButton)?.setOnClickListener {
            toggleChat()
        }

        try {
            windowManager?.addView(floatingView, params)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun removeFloatingButton() {
        floatingView?.let {
            try {
                windowManager?.removeView(it)
            } catch (e: Exception) {
                e.printStackTrace()
            }
            floatingView = null
        }
    }

    // ========== CHAT INTERFACE ==========
    
    private fun showChat() {
        if (chatView != null) return

        val inflater = LayoutInflater.from(this)
        chatView = inflater.inflate(R.layout.overlay_chat, null)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
            PixelFormat.TRANSLUCENT
        )

        val closeButton = chatView?.findViewById<Button>(R.id.closeButton)
        val sendButton = chatView?.findViewById<Button>(R.id.sendButton)
        val inputField = chatView?.findViewById<EditText>(R.id.inputField)

        closeButton?.setOnClickListener {
            hideChat()
        }

        sendButton?.setOnClickListener {
            val text = inputField?.text?.toString() ?: ""
            if (text.isNotEmpty()) {
                sendCommand(text)
                inputField.text?.clear()
            }
        }

        try {
            windowManager?.addView(chatView, params)
            isChatOpen = true
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun hideChat() {
        chatView?.let {
            try {
                windowManager?.removeView(it)
            } catch (e: Exception) {
                e.printStackTrace()
            }
            chatView = null
        }
        isChatOpen = false
    }

    private fun removeChatView() {
        hideChat()
    }

    private fun toggleChat() {
        if (isChatOpen) {
            hideChat()
        } else {
            showChat()
        }
    }

    // ========== COMMAND HANDLING ==========
    
    private fun sendCommand(command: String) {
        // Send to foreground service
        val intent = Intent(this, GaurangaForegroundService::class.java).apply {
            action = "com.gauranga.agent.COMMAND"
            putExtra("command", command)
        }
        startService(intent)
        
        // Show confirmation
        Toast.makeText(this, "Command sent: $command", Toast.LENGTH_SHORT).show()
    }

    fun showResponse(response: String) {
        // Update chat view with response
        chatView?.findViewById<TextView>(R.id.responseText)?.text = response
    }
}