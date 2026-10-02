// License: LGPL-3.0 License (c) find-sec-bugs
package strings

import java.security.MessageDigest

// ref: android.gitlab.kotlin_strings_rule-BadHexConversion
class BadHexConversion {
    @kotlin.ExperimentalStdlibApi
    fun danger(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        for (b in resultBytes) {
            stringBuilder.append(Integer.toHexString(b.toInt()))
        }

        stringBuilder.clear()
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        for (b in resultBytes) {
            stringBuilder.append(Integer.toHexString(b.toInt()))
        }

        stringBuilder.clear()
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        for (b in resultBytes) {
            stringBuilder.append(b.toHexString())
        }

        return stringBuilder.toString()
    }


    fun danger2(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        val resultBytesLength = resultBytes.size
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        while (i < resultBytesLength) {
            val b = resultBytes[i]
            stringBuilder.append(Integer.toHexString(b.toInt()))
            i++
        }
        return stringBuilder.toString()
    }

    fun danger3(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        val resultBytesLength = resultBytes.size
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        while (i < resultBytesLength) {
            stringBuilder.append(Integer.toHexString(resultBytes[i].toInt()))
            i++
        }
        return stringBuilder.toString()
    }

    fun danger4(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        while (i < resultBytes.size) {
            stringBuilder.append(Integer.toHexString(resultBytes[i].toInt()))
            i++
        }
        return stringBuilder.toString()
    }

    fun danger5(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        do {
            stringBuilder.append(Integer.toHexString(resultBytes[i].toInt()))
            i++
        } while (i < resultBytes.size)
        return stringBuilder.toString()
    }

    fun danger6(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        while (i < resultBytes.size) {
            val resultByte = resultBytes[i]
            stringBuilder.append(Integer.toHexString(resultByte.toInt()))
            i++
        }
        return stringBuilder.toString()
    }

    fun danger7(text: String): String {
        val md: MessageDigest = MessageDigest.getInstance("SHA-256")
        val resultBytes: ByteArray = md.digest(text.toByteArray(charset("UTF-8")))

        val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
        var i = 0
        // ruleid: android.gitlab.kotlin_strings_rule-BadHexConversion
        do {
            val resultByte = resultBytes[i]
            stringBuilder.append(Integer.toHexString(resultByte.toInt()))
            i++
        } while (i < resultBytes.size)
        return stringBuilder.toString()
    }

    companion object {
        fun safeOne(password: String): String {
            val md: MessageDigest = MessageDigest.getInstance("SHA-1")
            val resultBytes: ByteArray = md.digest(password.toByteArray(charset("UTF-8")))

            val stringBuilder: java.lang.StringBuilder = java.lang.StringBuilder()
            // ok: android.gitlab.kotlin_strings_rule-BadHexConversion
            for (b in resultBytes) {
                stringBuilder.append(String.format("%02X", b))
            }

            return stringBuilder.toString()
        }
    }
}