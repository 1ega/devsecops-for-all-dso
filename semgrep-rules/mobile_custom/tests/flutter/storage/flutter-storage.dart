void unsafeStorage(dynamic prefs, String token, String userEmail) {
  // ruleid: flutter.storage.shared-preferences-sensitive-data
  prefs.setString('auth_token', token);
  final password = token;
  // ruleid: flutter.storage.sensitive-clipboard-write
  Clipboard.setData(ClipboardData(text: password));
  // ruleid: flutter.storage.hardcoded-sensitive-constant
  const apiSecret = 'production-secret-value';
}
