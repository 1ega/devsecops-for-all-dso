// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import java.security.*

@Suppress("DEPRECATION")
object WeakMessageDigest {
    @Throws(NoSuchProviderException::class, NoSuchAlgorithmException::class)
    fun weakDigestMoreSig() {
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD5", "SUN")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD4", "SUN")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD2", "SUN")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD5")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD4")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD2")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD5", ExampleProvider())
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD4", ExampleProvider())
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("MD2", ExampleProvider())
        MessageDigest.getInstance("SHA", "SUN")
        MessageDigest.getInstance("SHA", ExampleProvider())
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("SHA1", "SUN")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("SHA1", ExampleProvider())
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("SHA-1", "SUN")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        MessageDigest.getInstance("SHA-1", ExampleProvider())
        MessageDigest.getInstance("sha-384", "SUN") // OK!
        MessageDigest.getInstance("SHA-512", "SUN") // OK!

        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        Signature.getInstance("MD5withRSA")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        Signature.getInstance("MD2withDSA", "X")
        // ruleid: android.gitlab.kotlin_crypto_rule-WeakMessageDigest
        Signature.getInstance("SHA1withRSA", ExampleProvider())
        Signature.getInstance("SHA256withRSA") // OK
        Signature.getInstance("uncommon name", "") // OK
    }

    internal class ExampleProvider : Provider("example", 1.0, "")
}