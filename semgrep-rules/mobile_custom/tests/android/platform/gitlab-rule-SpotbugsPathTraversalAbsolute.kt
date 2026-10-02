// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import java.io.BufferedReader
import java.io.FileReader
import java.io.IOException
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Paths
import javax.servlet.ServletException
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

class Ideas_2010_12_06 : HttpServlet() {
    @Throws(IOException::class)
    fun getFileContent(req: HttpServletRequest): String {
        return String(readFile(req.getParameter("path")), StandardCharsets.UTF_8)
    }

    @Throws(IOException::class)
    private fun readFile(fileName: String): ByteArray {
        return Files.readAllBytes(Paths.get(fileName))
    }

    @Throws(ServletException::class, IOException::class)
    override fun doGet(request: HttpServletRequest, response: HttpServletResponse) {
        response.setContentType("text/plain")
        val out: PrintWriter = response.getWriter()
        val path: String = request.getParameter("path")
        // ruleid: android.gitlab.kotlin_inject_rule-SpotbugsPathTraversalAbsolute
        val r = BufferedReader(FileReader("data/$path"))
        while (true) {
            val txt = r.readLine() ?: break
            out.println(txt)
        }
        out.close()
        r.close()
    }

    @Throws(ServletException::class, IOException::class)
    override fun doPost(request: HttpServletRequest, response: HttpServletResponse) {
        response.setContentType("text/plain")
        val out: PrintWriter = response.getWriter()
        val path: String = request.getParameter("path")
        // ruleid: android.gitlab.kotlin_inject_rule-SpotbugsPathTraversalAbsolute
        val r = BufferedReader(FileReader(path))
        while (true) {
            val txt = r.readLine() ?: break
            out.println(txt)
        }
        out.close()
        r.close()
    }
}
