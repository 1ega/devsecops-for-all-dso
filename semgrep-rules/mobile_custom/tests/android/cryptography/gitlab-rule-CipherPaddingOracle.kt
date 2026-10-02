// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import javax.crypto.Cipher

class CipherPaddingOracle {
    private var cipher: Cipher? = null
    @Throws(Exception::class)
    fun x() {
        cipher = Cipher.getInstance("AES/CTR/NoPadding")
    }

    companion object {
        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("AES/GCM/...") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("AES") // ECB and no integrity
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("DES/CTR/NoPadding", "BC") // no integrity
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("DESede/ECB/PKCS5Padding") // ECB and no integrity
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("DESede/CBC/PKCS5Padding") // CBC and no integrity
            // ruleid: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("AES/CBC/PKCS5Padding") // oracle and no integrity
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("ECIES/CBC/PKCS5Padding") // oracle and no integrity
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("RSA") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("RSA/CBC/PKCS1Padding") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("RSA/ECB/PKCS1Padding") // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance(args[0]) // ok
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("ECIES") // ok this is elliptic curve
            // ok: android.gitlab.kotlin_crypto_rule-CipherPaddingOracle
            Cipher.getInstance("AES/GCM-SIV/NoPadding") // ok
        }
    }
}