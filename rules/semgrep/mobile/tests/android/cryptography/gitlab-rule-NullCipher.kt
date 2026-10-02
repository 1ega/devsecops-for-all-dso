// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import javax.crypto.Cipher
import javax.crypto.NullCipher

class NullCipherUse {
    fun danger() {
        // ok: android.gitlab.kotlin_crypto_rule-NullCipher
        val nonNullCipher = Cipher.getInstance("AES/CBC/NoPadding")

        // ruleid: android.gitlab.kotlin_crypto_rule-NullCipher
        val nullCipher = NullCipher()

        println(nonNullCipher)
        println(nullCipher)
    }
}
