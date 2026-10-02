// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.security.MessageDigest

// ruleid: android.gitlab.kotlin_crypto_rule-CustomMessageDigest
class CustomMessageDigest protected constructor() : MessageDigest("WEAK") {
    private val buffer = ByteArrayOutputStream()

    override fun engineUpdate(input: Byte) {
        buffer.write(input.toInt())
    }

    override fun engineUpdate(input: ByteArray, offset: Int, len: Int) {
        try {
            buffer.write(input)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    override fun engineDigest(): ByteArray {
        val content = buffer.toByteArray()
        return content.copyOf(8)
    }

    override fun engineReset() {
        buffer.reset()
    }
}
