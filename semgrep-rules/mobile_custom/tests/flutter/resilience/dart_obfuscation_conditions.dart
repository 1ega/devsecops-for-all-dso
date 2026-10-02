void f(int x, bool flag) {
  // ruleid: flutter.apiiro.dart-obfuscation-conditions
  if (true) {
    print('a');
  }
  // ruleid: flutter.apiiro.dart-obfuscation-conditions
  while (false) {
    print('b');
  }
  // ruleid: flutter.apiiro.dart-obfuscation-conditions
  switch (1) {
    case 1:
      print('c');
  }
  // ruleid: flutter.apiiro.dart-obfuscation-conditions
  switch ('k') {
    default:
      print('d');
  }
  // ok: flutter.apiiro.dart-obfuscation-conditions
  while (true) {
    break;
  }
  // ok: flutter.apiiro.dart-obfuscation-conditions
  if (flag) {
    print('e');
  }
  // ok: flutter.apiiro.dart-obfuscation-conditions
  switch (x) {
    case 1:
      print('f');
  }
}
