// License: LGPL-3.0 License (c) find-sec-bugs
package password

import com.hazelcast.config.SymmetricEncryptionConfig
import io.vertx.ext.web.handler.CSRFHandler
import java.net.PasswordAuthentication
import java.security.KeyStore
import java.sql.DriverManager
import javax.crypto.spec.PBEKeySpec
import javax.net.ssl.KeyManagerFactory
import javax.security.auth.callback.PasswordCallback
import javax.security.auth.kerberos.KerberosKey

class HardcodedPasswords {
    val passwordString: String = "secret"
    val passwordS = SymmetricEncryptionConfig()

    fun danger1(password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        KeyStore.PasswordProtection("secret".toCharArray())

        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        KeyStore.PasswordProtection(passwordString.toCharArray())
    }

    fun danger2(password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        KeyStore.getInstance(null).load(null, "secret".toCharArray())
    }

    fun danger3(ks: KeyStore, password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        ks.load(null, "secret".toCharArray())
    }

    fun danger4(password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        KeyManagerFactory.getInstance(null).init(null, "secret".toCharArray())
    }

    fun danger5(kmf: KeyManagerFactory, password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        kmf.init(null, "secret".toCharArray())
    }


    fun danger10(password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "root", "secret")

        // ok: android.gitlab.kotlin_password_rule-HardcodePassword
        DriverManager.getConnection("jdbc:mysql://localhost:3306/test", "root", password)
    }

    fun danger11(password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        CSRFHandler.create(null, "secret")
    }

    fun danger12(s: SymmetricEncryptionConfig, password: String) {
        // ruleid: android.gitlab.kotlin_password_rule-HardcodePassword
        s.setPassword("secret")

        // ok: android.gitlab.kotlin_password_rule-HardcodePassword
        s.setPassword(password)
    }
}