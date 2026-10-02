// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import java.io.IOException
import java.util.*

@Suppress("DEPRECATION")
class CommandInjection {
    @Throws(IOException::class)
    fun danger(cmd: String) {
        val r = Runtime.getRuntime()
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        val cmds = arrayOf("/bin/sh", "-c", cmd)

        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        r.exec(cmd)
        r.exec(arrayOf("test"))
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        r.exec(arrayOf("bash", cmd), arrayOf())
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        r.exec(arrayOf("bash$cmd"), arrayOf())

        val tainted = "bash" + cmd + "test"
        r.exec(tainted)
        r.exec(tainted + "custom")
        r.exec(arrayOf("bash", tainted), arrayOf())
        r.exec(arrayOf("/bin/sh", "-c$tainted"), arrayOf())

        r.exec(cmds)
        r.exec(cmds, arrayOf())
        r.exec(cmds, arrayOf("test"))
    }

    fun danger2(cmd: String) {
        val b = ProcessBuilder()
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command(cmd)
        // ok: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command("test")
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command(Arrays.asList("/bin/sh", "-c", cmd))

        val tainted = "test2" + cmd + "test"
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command("test2" + cmd + "test")
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command(tainted)
        // ruleid: android.gitlab.kotlin_inject_rule-CommandInjection
        b.command(Arrays.asList("/bin/sh", "-c", tainted))
    }
}