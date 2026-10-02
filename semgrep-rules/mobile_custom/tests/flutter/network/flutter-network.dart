void unsafeNetwork(dynamic client, dynamic controller) {
  // ruleid: flutter.network.cleartext-http
  final url = Uri.parse('http://api.example.com');
  // ruleid: flutter.network.bad-certificate-callback-accepts-all
  client.badCertificateCallback = (cert, host, port) => true;
  // ruleid: flutter.network.insecure-websocket
  WebSocket.connect('ws://api.example.com');
  // ruleid: flutter.network.webview-unrestricted-javascript
  controller.setJavaScriptMode(JavaScriptMode.unrestricted);
  // ruleid: flutter.network.webview-unsafe-content
  controller.loadRequest(Uri.parse('file://private/data'));
}
