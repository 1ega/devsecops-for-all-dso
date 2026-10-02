// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import javax.crypto.Cipher

class CipherNoIntegrity {
    private var cipher: Cipher? = null
    fun x() {
        // ruleid: android.gitlab.kotlin_crypto_rule-CipherIntegrity
        cipher = Cipher.getInstance("AES/CTR/NoPadding")
    }

    companion object {
        fun main(args: Array<String>) {
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("AES/GCM/...") // ok
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("AES") // ECB and no integrity
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("DES/CTR/NoPadding", "BC") // no integrity
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("DESede/ECB/PKCS5Padding") // ECB and no integrity
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("AES/CBC/PKCS5Padding") // oracle and no integrity
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("RSA") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("RSA/ECB/PKCS1Padding") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance(args[0]) // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("ECIES") // ok this is elliptic curve
            // ok: android.gitlab.kotlin_crypto_rule-CipherIntegrity
            Cipher.getInstance("AES/GCM-SIV/NoPadding") // ok
        }
    }
}