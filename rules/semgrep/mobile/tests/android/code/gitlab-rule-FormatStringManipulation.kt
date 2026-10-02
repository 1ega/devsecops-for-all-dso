// License: LGPL-3.0 License (c) find-sec-bugs
package strings

import java.io.IOException
import java.util.*
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse

class FormatStringManipulation : HttpServlet() {
    @Throws(IOException::class)
    override fun doGet(request: HttpServletRequest, response: HttpServletResponse?) {
        // create a new formatter

        val buffer = StringBuffer()
        val formatter = Formatter(buffer, Locale.US)
        val input: String = request.getParameter("suffix")
        val format = "The customer: %s %s" + input

        // test cases
        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        formatter.format(format, "John", "Smith", "Jr") // BAD
        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        formatter.format(Locale.US, format, "John", "Smith") // BAD
        // ok: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        formatter.format("The customer: %s %s", "John", request.getParameter("testParam")) // OK

        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        System.out.printf(format, "John", "Smith") // BAD
        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        System.out.printf(Locale.US, format, "John", "Smith") // BAD

        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        System.out.format(format, "John", "Smith") // BAD
        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        System.out.format(Locale.US, format, "John", "Smith") // BAD

        val format2 = "The customer: %s %s" + request.getParameter("suffix")

        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        String.format(format2, "John", "Smith") // BAD
        // ruleid: android.gitlab.kotlin_strings_rule-FormatStringManipulation
        String.format(Locale.US, format2, "John", "Smith") // BAD
    }
}
