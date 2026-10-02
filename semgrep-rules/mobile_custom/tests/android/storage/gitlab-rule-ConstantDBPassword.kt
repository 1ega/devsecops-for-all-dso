// License: LGPL-3.0 License (c) find-sec-bugs
package password

import java.sql.Connection
import java.sql.DriverManager

class ConstantDBPassword {
    fun dangerConnection1(): Connection {
        // ok: android.gitlab.kotlin_password_rule-ConstantDBPassword
        return DriverManager.getConnection("jdbc:hsqldb:mem:test", "sa", "")
    }
    fun dangerConnection2(): Connection {
        // ruleid: android.gitlab.kotlin_password_rule-ConstantDBPassword
        return DriverManager.getConnection("jdbc:hsqldb:mem:test", "sa", "secret")
    }

    fun okConnection1(password: String): Connection {
        // ok: android.gitlab.kotlin_password_rule-ConstantDBPassword
        return DriverManager.getConnection("jdbc:hsqldb:mem:test", "sa", password)
    }
    fun okConnection2(): Connection {
        // ok: android.gitlab.kotlin_password_rule-ConstantDBPassword
        return DriverManager.getConnection("jdbc:hsqldb:mem:test", "sa", System.getenv("PASSWORD"))
    }
}
