//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-self-signed-ssl
BOOL canAuthenticate = [NSURLConnection canAuthenticateAgainstProtectionSpace:challenge.protectionSpace];
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-self-signed-ssl
BOOL continueWithoutCredential = [NSURLConnection continueWithoutCredentialForAuthenticationChallenge:challenge];
BOOL allowsExpiredCertificates = NO; // This is set according to your requirements
BOOL allowsAnyRoot = NO; // This is set according to your requirements
BOOL allowsExpiredRoots = NO; // This is set according to your requirements
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-self-signed-ssl
BOOL validatesSecureCertificate = NO; // This is set according to your requirements
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-self-signed-ssl
BOOL allowInvalidCertificates = YES; // This is set according to your requirements
