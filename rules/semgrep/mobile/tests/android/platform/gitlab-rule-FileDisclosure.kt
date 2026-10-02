// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import java.io.IOException
import javax.servlet.RequestDispatcher
import javax.servlet.http.HttpServlet
import javax.servlet.http.HttpServletRequest
import javax.servlet.http.HttpServletResponse
import org.apache.struts.action.ActionForward
import org.springframework.web.servlet.ModelAndView

@Suppress("UNUSED_VARIABLE")
class FileDisclosure : HttpServlet() {
    @Throws(IOException::class)
    override fun doGet(request: HttpServletRequest, response: HttpServletResponse?) {
        try {
            val returnURL: String = request.getParameter("returnURL")

            /** ****Struts ActionForward vulnerable code tests */
            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val forward: ActionForward = ActionForward(returnURL) // BAD

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val forward2: ActionForward = ActionForward(returnURL, true) // BAD

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val forward3: ActionForward = ActionForward("name", returnURL, true) // BAD

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val forward4: ActionForward = ActionForward("name", returnURL, true) // BAD

            val forward5: ActionForward = ActionForward()
            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            forward5.setPath(returnURL) // BAD

            // false positive test - returnURL moved from path to name (safe argument)
            val forward6: ActionForward = ActionForward(returnURL, "path", true) // OK

            /** ****Spring ModelAndView vulnerable code tests */
            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val mv: ModelAndView = ModelAndView(returnURL) // BAD

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val mv2: ModelAndView = ModelAndView(returnURL, HashMap<String, Any>()) // BAD

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            val mv3: ModelAndView = ModelAndView(returnURL, "modelName", Any()) // BAD

            val mv4: ModelAndView = ModelAndView()
            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            mv4.setViewName(returnURL) // BAD

            // false positive test - returnURL moved from viewName to modelName (safe argument)
            val mv5: ModelAndView = ModelAndView("viewName", returnURL, Any()) // OK
        } catch (e: Exception) {
            println(e)
        }
    }

    @Throws(IOException::class)
    fun doGet2(request: HttpServletRequest, response: HttpServletResponse?) {
        try {
            val jspFile: String = request.getParameter("jspFile")

            var requestDispatcher: RequestDispatcher = request.getRequestDispatcher(jspFile)

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            requestDispatcher.include(request, response)

            requestDispatcher =
                    request.getSession().getServletContext().getRequestDispatcher(jspFile)

            // ruleid: android.gitlab.kotlin_inject_rule-FileDisclosure
            requestDispatcher.forward(request, response)
        } catch (e: Exception) {
            println(e)
        }
    }
}
