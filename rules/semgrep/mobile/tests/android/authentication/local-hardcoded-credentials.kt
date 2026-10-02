fun webAuth(handler: HttpAuthHandler, user: String, password: String) {
    // ruleid: android.local.webview-hardcoded-http-auth
    handler.proceed("mobile-user", "mobile-password")
    // ok: android.local.webview-hardcoded-http-auth
    handler.proceed(user, password)
}

fun database(url: String, user: String, password: String) {
    // ruleid: android.local.jdbc-hardcoded-credentials
    DriverManager.getConnection(url, "admin", "secret")
    // ok: android.local.jdbc-hardcoded-credentials
    DriverManager.getConnection(url, user, password)
}
