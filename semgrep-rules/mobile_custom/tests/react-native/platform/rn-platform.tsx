function Screen({route, navigation, event}: any) {
  const url = route.params.url;
  // ruleid: react-native.platform.dynamic-linking-open-url
  Linking.openURL(url);
  // ruleid: react-native.platform.sensitive-navigation-params
  navigation.navigate("Profile", {token: route.params.token});
  // ruleid: react-native.platform.native-module-untrusted-input
  NativeModules.Admin.execute(route.params.command);
  // ruleid: react-native.platform.webview-javascript-injection
  webview.injectJavaScript(route.params.script);
  // ruleid: react-native.platform.webview-file-access
  const fileAccess = <WebView allowFileAccess={true} />;
  // ruleid: react-native.platform.webview-mixed-content
  const mixedContent = <WebView mixedContentMode="always" />;
  // ruleid: react-native.platform.webview-postmessage-no-origin-check
  const messageBridge = <WebView onMessage={handleMessage} />;
  // ruleid: react-native.platform.webview-unvalidated-uri
  const remoteContent = <WebView source={{uri: route.params.url}} />;
  return <>{fileAccess}{mixedContent}{messageBridge}{remoteContent}</>;
}
