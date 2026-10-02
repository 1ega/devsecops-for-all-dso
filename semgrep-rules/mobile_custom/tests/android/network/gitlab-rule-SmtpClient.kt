// License: LGPL-3.0 License (c) find-sec-bugs
// source:
// https://github.com/find-sec-bugs/find-sec-bugs/blob/master/findsecbugs-samples-java/src/test/java/testcode/script/SmtpClient.java
// hash: a7694d0
package smtp

import java.net.PasswordAuthentication
import java.net.URLEncoder
import java.util.*
import javax.activation.FileDataSource
import javax.mail.Authenticator
import javax.mail.Message
import javax.mail.MessagingException
import javax.mail.Session
import javax.mail.Transport
import javax.mail.internet.InternetAddress
import javax.mail.internet.MimeMessage
import javax.servlet.http.HttpServletRequest
import org.apache.commons.text.StringEscapeUtils

@Suppress("DEPRECATION")
object SmtpClient {
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
        // Example of payload that would prove the injection
        sendEmail(
                "Testing Subject\nX-Test: Override",
                "test\nDEF:2",
                "SVW:2\nXYZ",
                "ou\nlalala:22\n\rlili:22",
                "123;\n456=889",
                "../../../etc/passwd"
        )
    }

    @Throws(Exception::class)
    fun sendEmail(
            input1: String?,
            input2: String?,
            input3: String?,
            input4: String?,
            input5: String?,
            input6: String
    ) {
        val username = "email@gmail.com" // Replace by test account
        val password = "" // Replace by app password

        val props = Properties()
        props["mail.smtp.auth"] = "true"
        props["mail.smtp.starttls.enable"] = "true"
        props["mail.smtp.host"] = "smtp.gmail.com"
        props["mail.smtp.port"] = "587"

        val session: Session =
                Session.getInstance(
                        props,
                        object : Authenticator() {
                            protected val passwordAuthentication: PasswordAuthentication
                                get() = PasswordAuthentication(username, password.toCharArray())
                        }
                )

        val message: Message = MimeMessage(session)
        message.setFrom(InternetAddress("source@gmail.com"))
        message.setRecipients(
                Message.RecipientType.TO,
                arrayOf<InternetAddress>(InternetAddress("destination@gmail.com"))
        )
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setSubject(input1) // Injectable API
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.addHeader("ABC", input2) // Injectable API (value parameter)
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.addHeader(input3, "aa") // Injectable API (key parameter)
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setDescription(input4) // Injectable API
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setDisposition(input5) // Injectable API
        message.setText("This is just a test 2.")
        Transport.send(message)
        FileDataSource("/path/traversal/here/$input6")

        println("Done")
    }

    @Throws(MessagingException::class)
    fun sendEmailTainted(session: Session?, req: HttpServletRequest) {
        val message: Message = MimeMessage(session)
        // ruleid: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setSubject(req.getParameter("user") + " is following you")
    }

    @Throws(MessagingException::class)
    fun sendEmailOK(session: Session?, input: String?) {
        val message: Message = MimeMessage(session)
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.addHeader("abc", URLEncoder.encode(input))
    }

    @Throws(Exception::class)
    fun fixedVersions(session: Session?, input: String?) {
        val message: Message = MimeMessage(session)
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setSubject(StringEscapeUtils.escapeJava(input))
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.addHeader("lol", StringEscapeUtils.escapeJava(input))
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setDescription(StringEscapeUtils.escapeJava(input))
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setDisposition(StringEscapeUtils.escapeJava(input))
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setText(StringEscapeUtils.escapeJava(input))
        // ok: android.gitlab.kotlin_smtp_rule-SmtpClient
        message.setText("" + 42)
    }
}