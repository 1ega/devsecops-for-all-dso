// License: LGPL-3.0 License (c) find-sec-bugs
package endpoint

import java.security.KeyManagementException
import java.security.NoSuchAlgorithmException
import java.security.cert.CertificateException
import java.security.cert.X509Certificate
import javax.net.ssl.*

class WeakHostNameVerification {
  fun useAllHosts() {
    HttpsURLConnection.setDefaultHostnameVerifier(AllHosts())
  }

  @Throws(NoSuchAlgorithmException::class, KeyManagementException::class)
  fun useTrustAllManager() {
    val trustAllCerts = arrayOf(TrustAllManager())
    val sslContext = SSLContext.getInstance("SSL")
    sslContext.init(null, trustAllCerts, null)
    HttpsURLConnection.setDefaultSSLSocketFactory(sslContext.getSocketFactory())
  }

  fun useSecurityBypasser() {
    SecurityBypasser.destroyAllSSLSecurityForTheEntireVMForever()
  }
}

class AllHosts : HostnameVerifier {
  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  override fun verify(hostname: String, session: SSLSession): Boolean {
    return true
  }
}

class TrustAllManager : X509TrustManager {
  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  @Throws(CertificateException::class)
  override fun checkClientTrusted(cert: Array<X509Certificate>, authType: String) {}

  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  @Throws(CertificateException::class)
  override fun checkServerTrusted(cert: Array<X509Certificate>, authType: String) {}

  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  override fun getAcceptedIssuers(): Array<X509Certificate>? {
    return null
  }
}

class TrustAllManagerTwo : X509TrustManager {
  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  @Throws(CertificateException::class)
  override fun checkClientTrusted(cert: Array<X509Certificate>, authType: String) {}

  // ruleid: android.gitlab.kotlin_endpoint_rule-WeakHostNameVerification
  @Throws(CertificateException::class)
  override fun checkServerTrusted(cert: Array<X509Certificate>, authType: String) {}

  override fun getAcceptedIssuers(): Array<X509Certificate> {
    return arrayOf()
  }
}

object SecurityBypasser {
  fun destroyAllSSLSecurityForTheEntireVMForever() {
    try {
      val trustAllCerts = arrayOf(TrustAllManager())
      val sslContext = SSLContext.getInstance("SSL")
      sslContext.init(null, trustAllCerts, null)
      HttpsURLConnection.setDefaultSSLSocketFactory(sslContext.getSocketFactory())
      HttpsURLConnection.setDefaultHostnameVerifier(AllHosts())
    } catch (e: NoSuchAlgorithmException) {
      e.printStackTrace()
    } catch (e: KeyManagementException) {
      e.printStackTrace()
    }
  }
}
