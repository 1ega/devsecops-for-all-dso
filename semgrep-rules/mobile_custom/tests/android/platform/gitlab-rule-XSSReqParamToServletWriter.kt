// License: LGPL-3.0 License (c) find-sec-bugs
// scaffold: dependencies=org.owasp.encoder.encoder@1.2.3
package xss

import org.owasp.encoder.Encode
import java.io.IOException
import java.io.PrintWriter
import java.util.*
import javax.servlet.ServletException
import javax.servlet.ServletRequest
import javax.servlet.ServletResponse
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

// Also contains vulnerabilities found under ids: XSS_SERVLET,SERVLET_PARAMETER
@Suppress("UNUSED_VARIABLE")
class XSSReqParamToServletWriter : HttpServlet() {
    @Throws(ServletException::class, IOException::class)
    protected fun danger(req: HttpServletRequest, resp: HttpServletResponse) {
        val input1: String = req.getParameter("input1")
        // ruleid: android.gitlab.kotlin_xss_rule-XSSReqParamToServletWriter
        resp.getWriter().write(input1) // BAD
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doGet(req: HttpServletRequest, resp: HttpServletResponse) {
        val input1: String = req.getParameter("input1") // BAD
        val sessionId: String = req.getRequestedSessionId() // BAD
        val queryString: String = req.getQueryString() // BAD

        val referrer: String = req.getHeader("Referer") //Should have a higher priority
        if (referrer.startsWith("http://company.ca")) {
            // Header access
            val host: String = req.getHeader("Host") // BAD
            val referer: String = req.getHeader("Referer") // BAD
            val userAgent: String = req.getHeader("User-Agent") // BAD
        }

        val writer: PrintWriter = resp.getWriter()
        // ruleid: android.gitlab.kotlin_xss_rule-XSSReqParamToServletWriter
        writer.write(input1) // BAD
    }


    @Throws(ServletException::class, IOException::class)
    protected fun danger3(req: ServletRequest, resp: ServletResponse) {
        val input1: String = req.getParameter("input1") // BAD
        val map: Map<String, Array<String>> = req.getParameterMap() // BAD
        val vals: Array<String> = req.getParameterValues("input2") // BAD
        val names: Enumeration<String> = req.getParameterNames() // BAD
        val contentType: String = req.getContentType() // BAD
        val serverName: String = req.getServerName() // BAD
        resp.getWriter().write(input1)
    }


    @Throws(ServletException::class, IOException::class)
    protected fun ok(req: HttpServletRequest, resp: HttpServletResponse) {
        val input1: String = req.getParameter("input1")
        val writer: PrintWriter = resp.getWriter()
        writer.write(Encode.forHtml(input1)) // OK
    }


    @Throws(ServletException::class, IOException::class)
    protected fun ok2(req: HttpServletRequest, resp: HttpServletResponse) {
        val input1: String = req.getParameter("input1")
        val writer: PrintWriter = resp.getWriter()
        writer.write(Encode.forHtml(input1)) // OK
    }
}