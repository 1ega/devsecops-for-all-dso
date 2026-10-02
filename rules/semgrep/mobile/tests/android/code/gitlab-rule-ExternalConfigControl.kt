// License: LGPL-3.0 License (c) find-sec-bugs
package unsafe

import java.sql.Connection
import java.util.*
import javax.servlet.http.HttpServletRequest

class ExternalConfigControl {
    private val globalReq: HttpServletRequest? = null
    private val globalConn: Connection? = null

    fun callSetCatalog(c: Connection, req: HttpServletRequest) {
        // ruleid: android.gitlab.kotlin_unsafe_rule-ExternalConfigControl
        val tainted: String = req.getParameter("input")
        c.setCatalog(tainted)
        c.setCatalog("safe") // ok
        c.setCatalog(("very " + "safe").uppercase(Locale.getDefault())) // ok
    }

    fun callSetCatalog2(c: Connection) {
        // ruleid: android.gitlab.kotlin_unsafe_rule-ExternalConfigControl
        val tainted: String? = globalReq?.getParameter("input")
        c.setCatalog(tainted)
        c.setCatalog("safe") // ok
        c.setCatalog(("very " + "safe").uppercase(Locale.getDefault())) // ok
    }

    fun callSetCatalog3() {
        // ruleid: android.gitlab.kotlin_unsafe_rule-ExternalConfigControl
        val tainted: String? = globalReq?.getParameter("input")
        globalConn?.setCatalog(tainted)
        globalConn?.setCatalog("safe") // ok
        globalConn?.setCatalog(("very " + "safe").uppercase(Locale.getDefault())) // ok
    }
}
