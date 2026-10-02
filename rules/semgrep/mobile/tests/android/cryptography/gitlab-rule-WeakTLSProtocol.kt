// License: LGPL-3.0 License (c) find-sec-bugs
@file:Suppress("DEPRECATION")

package crypto

import java.security.NoSuchAlgorithmException
import javax.net.ssl.SSLContext
import org.apache.http.impl.client.DefaultHttpClient

object WeakTLSProtocol {
  @JvmStatic
  fun main(args: Array<String>) {
    // ruleid: android.gitlab.kotlin_crypto_rule-WeakTLSProtocol
    DefaultHttpClient() // BAD

    try {
      // ruleid: android.gitlab.kotlin_crypto_rule-WeakTLSProtocol
      SSLContext.getInstance("SSL") // BAD
      SSLContext.getInstance("TLS") // BAD

      SSLContext.getInstance("TLSv1.0") // WARN - should be v1.2 or above
      SSLContext.getInstance("TLSv1.1") // WARN - should be v1.2 or above
      SSLContext.getInstance("DTLSv1.0") // WARN - should be v1.2 or above
      SSLContext.getInstance("DTLSv1.1") // WARN - should be v1.2 or above
      SSLContext.getInstance("TLSv1.2") // OK
      SSLContext.getInstance("TLSv1.3") // OK
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }

  fun danger2() {
    try {
      val serverSslContext = SSLContext.getInstance("TLS")
      val serverEngine = serverSslContext.createSSLEngine()
      serverEngine.enabledProtocols = arrayOf("TLSv1.1")
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }

  fun danger3() {
    try {
      val serverSslContext = SSLContext.getInstance("TLSv1.2")
      val serverEngine = serverSslContext.createSSLEngine()
      serverEngine.enabledProtocols = arrayOf("TLSv1.1") // STILL DANGER SINCE OVERRIDE
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }

  fun ok1() {
    try {
      val serverSslContext = SSLContext.getInstance("TLS")
      val serverEngine = serverSslContext.createSSLEngine()
      serverEngine.enabledProtocols = arrayOf("TLSv1.2", "TLSv1.3")
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }

  fun ok2() {
    try {
      val serverSslContext = SSLContext.getDefault()
      val serverEngine = serverSslContext.createSSLEngine()
      serverEngine.enabledProtocols = arrayOf("TLSv1.2")
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }

  fun ok3() {
    try {
      val serverSslContext = SSLContext.getInstance("TLSv1.1")
      val serverEngine = serverSslContext.createSSLEngine()
      serverEngine.enabledProtocols = arrayOf("DTLSv1.2") // OVERRIDES UNSAFE VERSION
    } catch (e: NoSuchAlgorithmException) {
      // TODO Auto-generated catch block
      e.printStackTrace()
    }
  }
}
