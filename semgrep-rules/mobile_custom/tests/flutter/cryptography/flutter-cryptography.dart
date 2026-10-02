void unsafeCrypto(dynamic data) {
  // ruleid: flutter.cryptography.weak-hash
  final digest = md5.convert(data);
  // ruleid: flutter.cryptography.insecure-random-secret
  final sessionToken = Random().nextInt(1000000);
}
