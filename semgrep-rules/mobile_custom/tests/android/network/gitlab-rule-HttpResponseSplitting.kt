// License: LGPL-3.0 License (c) find-sec-bugs
package cookie

import java.io.IOException
import javax.servlet.ServletException
import javax.servlet.http.Cookie
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse
import javax.servlet.http.HttpServletResponseWrapper
import org.apache.commons.text.StringEscapeUtils

class HttpResponseSplitting : HttpServlet() {
    @Suppress("UNUSED_VARIABLE")
    @Throws(ServletException::class, IOException::class)
    protected override fun doGet(req: HttpServletRequest, resp: HttpServletResponse) {
        val input: String = req.getParameter("input")
        val c = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        c.setValue(input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        val paramNames: String = req.getParameterNames().nextElement()
        val cParamNames = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        cParamNames.setValue(paramNames)
        cParamNames.setHttpOnly(true)
        cParamNames.setSecure(true)
        resp.addCookie(cParamNames)

        val paramValues: String = req.getParameterValues("input").get(0)
        val cParamValues = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        cParamValues.setValue(paramValues)
        cParamValues.setHttpOnly(true)
        cParamValues.setSecure(true)
        resp.addCookie(cParamValues)

        val paramMap: String? = req.getParameterMap().get("input")?.get(0)
        val cParamMap = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        cParamMap.setValue(paramMap)
        cParamMap.setHttpOnly(true)
        cParamMap.setSecure(true)
        resp.addCookie(cParamMap)

        val header: String = req.getHeader("input")
        val cHeader = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        c.setValue(header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        val contextPath: String = req.getPathInfo()
        val cPath = Cookie("name", null)
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        c.setValue(contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doPost(req: HttpServletRequest, resp: HttpServletResponse) {
        val input: String = req.getParameter("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val c = Cookie("name", input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        val header: String = req.getHeader("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cHeader = Cookie("name", header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        val contextPath: String = req.getPathInfo()
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cPath = Cookie("name", contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doDelete(req: HttpServletRequest, resp: HttpServletResponse) {
        val data: String = req.getParameter("input")
        val input = data.replace("\n".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val c = Cookie("name", input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        var header: String = req.getHeader("input")
        header = header.replace("\n".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cHeader = Cookie("name", header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        var contextPath: String = req.getPathInfo()
        contextPath = contextPath.replace("\n".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cPath = Cookie("name", contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doHead(req: HttpServletRequest, resp: HttpServletResponse) {
        val data: String = req.getParameter("input")
        val input = data.replace("\r".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val c = Cookie("name", input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        var header: String = req.getHeader("input")
        header = header.replace("\r".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cHeader = Cookie("name", header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        var contextPath: String = req.getPathInfo()
        contextPath = contextPath.replace("\r".toRegex(), "")
        // ruleid: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cPath = Cookie("name", contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doPut(req: HttpServletRequest, resp: HttpServletResponse) {
        val data: String = req.getParameter("input")
        val input = data.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val c = Cookie("name", input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        var header: String = req.getHeader("input")
        header = header.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cHeader = Cookie("name", header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        var contextPath: String = req.getPathInfo()
        contextPath = contextPath.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cPath = Cookie("name", contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doTrace(req: HttpServletRequest, resp: HttpServletResponse) {
        val data: String = req.getParameter("input")
        val input: String = StringEscapeUtils.escapeJava(data)
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val c = Cookie("name", input)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(c)

        var header: String = req.getHeader("input")
        header = StringEscapeUtils.escapeJava(header)
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cHeader = Cookie("name", header)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cHeader)

        var contextPath: String = req.getPathInfo()
        contextPath = StringEscapeUtils.escapeJava(contextPath)
        // ok: android.gitlab.kotlin_cookie_rule-HttpResponseSplitting
        val cPath = Cookie("name", contextPath)
        c.setHttpOnly(true)
        c.setSecure(true)
        resp.addCookie(cPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doOptions(req: HttpServletRequest, resp: HttpServletResponse) {
        // BAD
        val tainted: String = req.getParameter("input")
        resp.setHeader("test", tainted)

        // OK: False negative but reported by spotbugs
        val data: String = req.getParameter("input")
        val normalized = data.replace("\n".toRegex(), "\n")
        resp.setHeader("test", normalized)

        // OK: False negative but reported by spotbugs
        val normalized2: String = data.replace("\n".toRegex(), req.getParameter("test"))
        resp.setHeader("test2", normalized2)

        // OK
        val normalized3: String = org.apache.commons.text.StringEscapeUtils.unescapeJava(tainted)
        resp.setHeader("test3", normalized3)

        // BAD
        val normalized4 = getString(tainted)
        resp.setHeader("test4", normalized4)

        // BAD
        val wrapper: HttpServletResponseWrapper = HttpServletResponseWrapper(resp)
        wrapper.addHeader("test", tainted)
        wrapper.setHeader("test2", tainted)
    }

    private fun getString(s: String): String {
        return s
    }
}
