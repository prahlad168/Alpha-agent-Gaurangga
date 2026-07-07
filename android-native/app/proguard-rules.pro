# Add project specific ProGuard rules here.

# Keep Vosk classes
-keep class com.alphacephei.vosk.** { *; }

# Keep TensorFlow Lite classes
-keep class org.tensorflow.lite.** { *; }

# Keep Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Keep model classes
-keep class com.gaurangga.alpha.model.** { *; }
