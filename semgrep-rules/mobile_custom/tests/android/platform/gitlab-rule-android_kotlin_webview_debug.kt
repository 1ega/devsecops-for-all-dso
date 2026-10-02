@file:Suppress("UNUSED_PARAMETER")

package webview

class MainActivity : AppCompatActivity() {
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val webView: WebView = findViewById(R.id.webView)
        // ruleid: android.gitlab.rules_lgpl_kotlin_other_rule-android-kotlin-webview-debug
        WebView.setWebContentsDebuggingEnabled(true)
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webView.loadUrl("https://www.example.com")
    }
}

// The remainder of this file is for scaffolding only, to enable compilation
annotation class SuppressLint(val s: String)

class R {
    companion object {
        class Layout {
            val activity_main = 0
        }
        val layout = Layout()
        class Id {
            val webView = 0
        }
        val id = Id()
    }
}

class WebView {
    fun loadUrl(s: String) {}

    val settings: WebSettings = WebSettings()

    companion object {
        fun setWebContentsDebuggingEnabled(b: Boolean) {}
    }
}

class Bundle

open class AppCompatActivity {
    open fun onCreate(savedInstanceState: Bundle?) {}
    fun setContentView(activityMain: Any) {}
    fun findViewById(webView: Any): WebView {
        return WebView()
    }
}

class WebSettings {
    var javaScriptEnabled: Boolean = false
}
