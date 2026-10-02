// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import com.google.common.net.UrlEscapers.urlPathSegmentEscaper
import java.io.IOException
import java.net.URLEncoder
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse
import org.apache.commons.httpclient.methods.GetMethod
import org.apache.http.client.methods.HttpGet

class HttpParameterPollution : HttpServlet() {
    @Suppress(
            "DEPRECATION",
            "UNUSED_VARIABLE"
    ) // URLEncoder.encode is deprecated but use to specially test this API.
    @Throws(IOException::class)
    override fun doGet(request: HttpServletRequest, response: HttpServletResponse?) {
        try {
            val item: String = request.getParameter("item")

            // in HttpClient 4.x, there is no GetMethod anymore. Instead there is HttpGet
            val httpget: HttpGet = HttpGet("http://host.com?param=" + URLEncoder.encode(item)) // OK
            // ruleid: android.gitlab.kotlin_inject_rule-HttpParameterPollution
            val httpget2: HttpGet = HttpGet("http://host.com?param=$item") // BAD
            val httpget3: HttpGet =
                    HttpGet("http://host.com?param=" + urlPathSegmentEscaper().escape(item)) // OK

            // ruleid: android.gitlab.kotlin_inject_rule-HttpParameterPollution
            val get: GetMethod = GetMethod("http://host.com?param=$item") // BAD
            // ruleid: android.gitlab.kotlin_inject_rule-HttpParameterPollution
            get.setQueryString("item=$item") // BAD
            // get.execute();
        } catch (e: Exception) {
            println(e)
        }
    }
}