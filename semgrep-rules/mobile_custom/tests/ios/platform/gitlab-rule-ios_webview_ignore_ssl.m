//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-webview-ignore-ssl
BOOL allowsAnyHTTPSCertificate = YES;
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-webview-ignore-ssl
BOOL allowsAnyHTTPSCertificateForHost = YES;

NSURLRequest *requestObj = [NSURLRequest requestWithURL:self.currentURL     cachePolicy:NSURLRequestReturnCacheDataElseLoad timeoutInterval:10.0];
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-webview-ignore-ssl
self.loadingUnvalidatedHTTPSPage = YES;
[self.webView loadRequest:requestObj];

@implementation NSURLRequest(OOA)
//ruleid: ios.gitlab.rules_lgpl_oc_other_rule-ios-webview-ignore-ssl
(BOOL)allowsAnyHTTPSCertificateForHost:(NSString *)host {
    return YES;
}
@end