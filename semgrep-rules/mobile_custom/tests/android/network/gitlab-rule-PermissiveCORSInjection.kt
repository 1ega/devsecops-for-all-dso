// License: LGPL-3.0 License (c) find-sec-bugs
package cors

import java.io.IOException
import java.util.*
import javax.servlet.ServletException
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

// ref: android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
// sample get req:
// http://localhost:8080/ServletSample/PermissiveCORSInjection/*?tainted=*f&URL=*&URL=*&url=*
class PermissiveCORSInjection : HttpServlet() {
    @Throws(ServletException::class, IOException::class)
    protected override fun doGet(request: HttpServletRequest, response: HttpServletResponse) {
        request.setAttribute("attributeName", request.getParameter("tainted"))
        request.getSession().setAttribute("attributeName", request.getParameter("tainted"))
        request.getServletContext().setAttribute("attributeName", request.getParameter("tainted"))

        val paramValue: String? = request.getParameter("tainted")
        val header: String = request.getHeader("tainted")
        val requestAttribute = request.getAttribute("attributeName") as String
        val sessionAttribute = request.getSession().getAttribute("attributeName") as String
        val contextAttribute = request.getServletContext().getAttribute("attributeName") as String
        val pathInfo: String = request.getPathInfo()
        val modifiedPath = pathInfo.replaceFirst("/".toRegex(), "")
        val queryString: String = request.getQueryString()

        val parameterValues: Array<String> = request.getParameterValues("URL")
        val parameterNames: Enumeration<String> = request.getParameterNames()
        val parameterMap: Map<String, Array<String>> = request.getParameterMap()

        val valueFromPV = parameterValues[0]
        val valueFromPN = parameterNames.nextElement()
        val valueFromPM = parameterMap["URL"]!![0]

        val keyValuePairs =
                queryString.split("=".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
        val lastPair = keyValuePairs[keyValuePairs.size - 1]

        if (paramValue != null) {
            // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.setHeader("X-Example-Header", paramValue)

            // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("X-Example-Header", paramValue)

            // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("X-Example-Header", valueFromPV)

            // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("Some-Example-Header", valueFromPN)

            // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("X-Example-Header", valueFromPM)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.setHeader("Access-Control-Allow-Origin", paramValue)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("Access-Control-Allow-Origin", paramValue)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("Access-Control-Allow-Origin", modifiedPath)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", paramValue)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", header)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", requestAttribute)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", sessionAttribute)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", contextAttribute)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", valueFromPV)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", valueFromPN)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", valueFromPM)

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader("access-control-allow-origin", lastPair)

            val headerName = "ACCESS-CONTROL-ALLOW-ORIGIN"

            // ruleid:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
            response.addHeader(headerName, paramValue)

            return
        }

        // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
        response.setHeader("Access-Control-Allow-Origin", "https://example.com")

        // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
        response.addHeader("Access-Control-Allow-Origin", "https://example.com")

        // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
        response.addHeader("Access-Control-Allow-Origin", getFromList("key"))

        // ok:android.gitlab.kotlin_cors_rule-PermissiveCORSInjection
        response.addHeader("Access-Control-Allow-Origin", "*")
    }

    fun getFromList(key: String): String? {
        val corsList = HashMap<String, String>()
        corsList["key"] = "https://example.com"

        return corsList[key]
    }
}
