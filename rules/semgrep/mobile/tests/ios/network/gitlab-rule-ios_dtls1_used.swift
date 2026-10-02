let tlsProtocolVersion = "tls_protocol_version_t.DTLSv10"
print(tlsProtocolVersion)

let sessionConfig = URLSessionConfiguration.default
//ruleid:ios.gitlab.rules_lgpl_swift_other_rule-ios-dtls1-used
sessionConfig.TLSMinimumSupportedProtocolVersion = .DTLSv1_0
