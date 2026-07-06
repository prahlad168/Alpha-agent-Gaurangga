package com.gauranga.agent.services

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Intent
import android.graphics.Rect
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class GaurangaAccessibilityService : AccessibilityService() {

    companion object {
        const val TAG = "GAURANGA_ACCESS"
        var instance: GaurangaAccessibilityService? = null
    }

    private var lastProcessedText = ""
    
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.d(TAG, "Accessibility Service connected")
        
        // Configure service info
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_ALL_EVENTS
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or
                    AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
            notificationTimeout = 100
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event ?: return
        
        // Process events
        when (event.eventType) {
            AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED -> {
                handleTextChange(event)
            }
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                handleWindowChange(event)
            }
            AccessibilityEvent.TYPE_VIEW_CLICKED -> {
                handleClick(event)
            }
        }
    }

    override fun onInterrupt() {
        Log.w(TAG, "Accessibility service interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.d(TAG, "Accessibility Service destroyed")
    }

    // ========== SCREEN READING ==========
    
    fun getScreenContent(): String {
        val rootNode = rootInActiveWindow ?: return ""
        val content = StringBuilder()
        
        // Extract all text content
        extractTextContent(rootNode, content)
        
        rootNode.recycle()
        return content.toString()
    }
    
    private fun extractTextContent(node: AccessibilityNodeInfo, sb: StringBuilder) {
        val text = node.text?.toString()
        val contentDesc = node.contentDescription?.toString()
        
        if (!text.isNullOrEmpty()) {
            sb.append(text).append(" ")
        }
        if (!contentDesc.isNullOrEmpty()) {
            sb.append(contentDesc).append(" ")
        }
        
        // Recurse to children
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                extractTextContent(child, sb)
                child.recycle()
            }
        }
    }
    
    // ========== UI INTERACTION ==========
    
    fun clickElement(text: String): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val result = findAndClickElement(rootNode, text)
        rootNode.recycle()
        return result
    }
    
    private fun findAndClickElement(node: AccessibilityNodeInfo, text: String): Boolean {
        val nodeText = node.text?.toString() ?: ""
        val contentDesc = node.contentDescription?.toString() ?: ""
        
        if (text.contains(nodeText) || nodeText.contains(text) ||
            text.contains(contentDesc) || contentDesc.contains(text)) {
            
            if (node.isClickable) {
                node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                Log.d(TAG, "Clicked: $text")
                return true
            }
        }
        
        for (i in 0 until node.childCount) {
            val child = node.getChild(i)
            if (child != null) {
                if (findAndClickElement(child, text)) {
                    child.recycle()
                    return true
                }
                child.recycle()
            }
        }
        
        return false
    }
    
    fun typeText(text: String): Boolean {
        val arguments = android.os.Bundle()
        arguments.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
        
        val rootNode = rootInActiveWindow ?: return false
        val focusedNode = rootNode.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        
        val result = if (focusedNode != null) {
            focusedNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
        } else {
            rootNode.performAction(AccessibilityNodeInfo.ACTION_FOCUS) &&
            rootNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
        }
        
        rootNode.recycle()
        return result
    }
    
    fun scrollDown(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val result = rootNode.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        rootNode.recycle()
        return result
    }
    
    fun scrollUp(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        val result = rootNode.performAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)
        rootNode.recycle()
        return result
    }
    
    fun pressBack(): Boolean {
        val result = performGlobalAction(GLOBAL_ACTION_BACK)
        Log.d(TAG, "Back pressed: $result")
        return result
    }
    
    fun pressHome(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_HOME)
    }
    
    fun pressRecent(): Boolean {
        return performGlobalAction(GLOBAL_ACTION_RECENTS)
    }
    
    // ========== APP CONTROL ==========
    
    fun openApp(packageName: String): Boolean {
        val intent = packageManager.getLaunchIntentForPackage(packageName)
        if (intent != null) {
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
            return true
        }
        return false
    }
    
    fun getCurrentApp(): String? {
        return rootInActiveWindow?.window?.title?.toString()
    }
    
    // ========== ELEMENT FINDING ==========
    
    fun findElementById(id: String): AccessibilityNodeInfo? {
        val rootNode = rootInActiveWindow ?: return null
        val node = rootNode.findAccessibilityNodeInfosByViewId(id).firstOrNull()
        rootNode.recycle()
        return node
    }
    
    fun findElementsByText(text: String): List<AccessibilityNodeInfo> {
        val rootNode = rootInActiveWindow ?: return emptyList()
        val nodes = rootNode.findAccessibilityNodeInfosByText(text)
        rootNode.recycle()
        return nodes
    }
    
    // ========== PRIVATE HANDLERS ==========
    
    private fun handleTextChange(event: AccessibilityEvent) {
        val text = event.text.joinToString(" ")
        if (text.isNotEmpty() && text != lastProcessedText) {
            lastProcessedText = text
            Log.d(TAG, "Text changed: $text")
        }
    }
    
    private fun handleWindowChange(event: AccessibilityEvent) {
        val className = event.className?.toString() ?: ""
        val packageName = event.packageName?.toString() ?: ""
        Log.d(TAG, "Window changed: $className ($packageName)")
    }
    
    private fun handleClick(event: AccessibilityEvent) {
        val text = event.text.joinToString(" ")
        val contentDesc = event.contentDescription?.toString() ?: ""
        Log.d(TAG, "Clicked: $text | $contentDesc")
    }
}