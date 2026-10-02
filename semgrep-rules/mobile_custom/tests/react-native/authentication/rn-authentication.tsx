function auth(token: string) {
  // ruleid: react-native.authentication.expo-auth-session-pkce-disabled
  AuthSession.startAsync({authUrl: "https://id.example.com", usePKCE: false});
  // ruleid: react-native.authentication.jwt-decoded-without-expiry-check
  const payload = jwtDecode(token);
  // ruleid: react-native.authentication.insecure-random-token
  const sessionToken = Math.random();
  // ruleid: react-native.authentication.textinput-sensitive-not-secure
  return (
    <TextInput placeholder="Password" />
  );
}
