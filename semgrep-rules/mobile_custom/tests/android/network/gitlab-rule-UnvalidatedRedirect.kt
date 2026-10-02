package endpoint

import java.io.IOException
import javax.servlet.ServletException
import javax.servlet.annotation.*
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

@Suppress("UNUSED_VARIABLE")
class UnvalidatedRedirect : HttpServlet() {
    @Throws(ServletException::class, IOException::class)
    protected override fun doGet(request: HttpServletRequest, response: HttpServletResponse) {
        val c: String = request.getParameter("case")

        var url: String

        if (c == "1") {
            url = request.getParameter("redirectTo")
            if (url != null) {
                // ruleid: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect
                response.sendRedirect(url)
            }
        } else if (c == "2") {
            url = request.getParameter("redirectTo")
            // ruleid: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect
            response.addHeader("Location", url)
            response.sendError(302)
        } else if (c == "3") {
            url = "/ServletSample/UnvalidatedRedirect"
            // ok: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect
            response.sendRedirect(url)
        } else if (c == "4") {
            // ok: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect

            response.addHeader("Location", "/ServletSample/UnvalidatedRedirect")
            response.sendError(302)
        } else if (c == "6") {
            val safeUrls: MutableList<String> = ArrayList()
            safeUrls.add("/ServletSample/UnvalidatedRedirect")
            safeUrls.add("/ServletSample/")

            val redirectUrl: String = request.getParameter("redirectTo")

            if (safeUrls.contains(redirectUrl)) {
                // ok: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect
                response.sendRedirect(redirectUrl)
            } else {
                response.sendError(404)
            }
        }
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doPost(request: HttpServletRequest, response: HttpServletResponse) {
        val c: String = request.getParameter("case")

        var url: String

        if (c == "5") {
            url = request.getParameter("url")
            if (url != null && !url.isEmpty()) {
                // ruleid: android.gitlab.kotlin_endpoint_rule-UnvalidatedRedirect
                response.sendRedirect(url)
            }
        }
    }
}