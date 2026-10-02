function unsafeNetwork(token: string) {
  // ruleid: react-native.network.cleartext-http
  fetch("http://api.example.com/data");
  // ruleid: react-native.network.insecure-websocket
  const socket = new WebSocket("ws://api.example.com/socket");
  // ruleid: react-native.network.request-without-timeout
  const client = axios.create({baseURL: "https://api.example.com"});
  // ruleid: react-native.network.certificate-validation-disabled
  const tls = {rejectUnauthorized: false};
  // ruleid: react-native.network.oauth-token-in-url
  fetch(`https://api.example.com/me?access_token=${token}`);
}
