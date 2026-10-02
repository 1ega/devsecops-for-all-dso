// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import java.security.NoSuchAlgorithmException
import javax.crypto.KeyGenerator

class BlowfishKeySize {
    fun danger() {
        // ruleid: android.gitlab.kotlin_crypto_rule-BlowfishKeySize
        val keyGen = KeyGenerator.getInstance("Blowfish")
        keyGen.init(64)
    }

    fun ok() {
        // ok: android.gitlab.kotlin_crypto_rule-BlowfishKeySize
        val keyGen = KeyGenerator.getInstance("Blowfish")
        keyGen.init(128)
    }
}