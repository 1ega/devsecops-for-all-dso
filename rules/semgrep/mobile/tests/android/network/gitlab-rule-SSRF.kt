// License: LGPL-3.0 License (c) find-sec-bugs
package ssrf

import java.io.IOException
import java.net.*
import javax.net.ssl.SSLContext

/** @author Tomas Polesovsky */
@Suppress("DEPRECATION")
object SSRF {
    private const val TIMEOUT_IN_SECONDS = 20

    @Throws(IOException::class)
    fun testURL(url: String?) {
        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).openConnection().connect()

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL("http://safe.com")
                // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
                .openConnection(Proxy(Proxy.Type.HTTP, InetSocketAddress(url, 8080)))
                .connect()

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).openConnection().getInputStream()

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).openConnection().lastModified

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).openStream()

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).content

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).getContent()

        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URL(url).getContent(arrayOfNulls(0))
    }

    @Throws(IOException::class, URISyntaxException::class)
    fun testURI(url: String?) {
        // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
        URI(url).toURL().openConnection().connect()
    }

    @Throws(IOException::class)
    fun connect(url: URI, ctx: SSLContext) {
        var port = url.port
        port = if (port > 0) port else 443
        ctx.socketFactory.createSocket().use { s ->
            // ruleid: android.gitlab.kotlin_ssrf_rule-SSRF
            val socketAddress = InetSocketAddress(url.host, port)
            s.connect(socketAddress, TIMEOUT_IN_SECONDS * 1000)
            s.getOutputStream().use { os -> os.write("GET / HTTP/1.1\n\n".toByteArray()) }
        }
    }
}
