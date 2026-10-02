// License: LGPL-3.0 License (c) find-sec-bugs
package cookie

import java.io.IOException
import javax.servlet.ServletException
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse
import javax.servlet.http.HttpServletResponseWrapper

class RequestParamToHeader : HttpServlet() {
    @Throws(ServletException::class, IOException::class)
    protected override fun doGet(req: HttpServletRequest, resp: HttpServletResponse) {
        val input: String = req.getParameter("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", input)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", input)

        val paramNames: String = req.getParameterNames().nextElement()
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", paramNames)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", paramNames)

        val paramValues: String = req.getParameterValues("input").get(0)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", paramValues)

        val paramMap: String? = req.getParameterMap().get("input")?.get(0)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", paramMap)

        val header: String = req.getHeader("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", header)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", header)

        val contextPath: String = req.getPathInfo()
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", contextPath)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doPost(req: HttpServletRequest, resp: HttpServletResponse) {
        val input: String = req.getParameter("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", input)

        val header: String = req.getHeader("input")
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", header)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", header)

        val contextPath: String = req.getPathInfo()
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", contextPath)

        val tainted: String = req.getParameter("input")
        val wrapper: HttpServletResponseWrapper = HttpServletResponseWrapper(resp)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        wrapper.addHeader("test", tainted)
        // ruleid: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        wrapper.setHeader("test2", tainted)
    }

    @Throws(ServletException::class, IOException::class)
    protected override fun doPut(req: HttpServletRequest, resp: HttpServletResponse) {
        val data: String = req.getParameter("input")
        val input = data.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", input)
        // ok: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", input)

        var header: String = req.getHeader("input")
        header = header.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", header)
        // ok: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.setHeader("CUSTOM_HEADER", header)

        var contextPath: String = req.getPathInfo()
        contextPath = contextPath.replace("[\r\n]+".toRegex(), "")
        // ok: android.gitlab.kotlin_cookie_rule-RequestParamToHeader
        resp.addHeader("CUSTOM_HEADER", contextPath)
    }
}