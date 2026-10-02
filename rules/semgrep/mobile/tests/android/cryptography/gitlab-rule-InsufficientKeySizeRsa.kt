// License: LGPL-3.0 License (c) find-sec-bugs
package crypto

import java.security.*
import java.security.spec.RSAKeyGenParameterSpec

/**
 * The key size might need to be adjusted in the future.
 * http://en.wikipedia.org/wiki/Key_size#Asymmetric_algorithm_key_lengths
 */
@Suppress("DEPRECATION")
class InsufficientKeySizeRsa {
    @Throws(NoSuchAlgorithmException::class)
    fun weakKeySize1(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(512) // BAD

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class)
    fun weakKeySize2(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(128, SecureRandom()) // BAD //Different signature

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class, InvalidAlgorithmParameterException::class)
    fun weakKeySize3ParameterSpec(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(RSAKeyGenParameterSpec(128, RSAKeyGenParameterSpec.F4)) // BAD

        val key = keyGen.generateKeyPair()
        return key
    }

    @Throws(NoSuchAlgorithmException::class, InvalidAlgorithmParameterException::class)
    fun weakKeySize4ParameterSpec(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        keyGen.initialize(
                // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
                RSAKeyGenParameterSpec(128, RSAKeyGenParameterSpec.F4),
                SecureRandom()
        ) // BAD

        val key = keyGen.generateKeyPair()
        return key
    }

    @Throws(NoSuchAlgorithmException::class)
    fun weakKeySize5Recommended(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(1024) // BAD with lower priority

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class, InvalidAlgorithmParameterException::class)
    fun okKeySizeParameterSpec(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA")
        keyGen.initialize(
                RSAKeyGenParameterSpec(2048, RSAKeyGenParameterSpec.F4)
        ) // Different signature

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class, NoSuchProviderException::class)
    fun weakKeySizeWithProviderString(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA", "BC")
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(1024) // BAD with lower priority

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class)
    fun weakKeySizeWithProviderObject1(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA", ExampleProvider())
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(1024) // BAD with lower priority

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class)
    fun weakKeySizeWithProviderObject2(): KeyPair {
        val p: Provider = ExampleProvider("info")
        val keyGen = KeyPairGenerator.getInstance("RSA", p)
        // ruleid: android.gitlab.kotlin_crypto_rule-InsufficientKeySizeRsa
        keyGen.initialize(1024) // BAD with lower priority

        return keyGen.generateKeyPair()
    }

    @Throws(NoSuchAlgorithmException::class, NoSuchProviderException::class)
    fun strongKeySizeWithProviderString(): KeyPair {
        val keyGen = KeyPairGenerator.getInstance("RSA", "BC")
        keyGen.initialize(2048) // OK: n >= 2048

        return keyGen.generateKeyPair()
    }

    private inner class ExampleProvider @JvmOverloads constructor(info: String? = "example") :
            Provider("example", 0.0, info)
}
