Future<void> unsafe(dynamic request, dynamic route, dynamic db, dynamic channel) async {
  final input = request.queryParameters['value'];
  // ruleid: flutter.code.sqflite-sql-injection
  await db.rawQuery('SELECT * FROM users WHERE id=' + input);
  // ruleid: flutter.code.process-run-untrusted-input
  await Process.run(input, []);
  // ruleid: flutter.code.path-traversal
  final file = File(input);
  final response = await fetchPage();
  // ruleid: flutter.code.flutter-html-untrusted-data
  final html = Html(data: response.body);
  // ruleid: flutter.code.method-channel-untrusted-arguments
  await channel.invokeMethod('execute', input);
  // ruleid: flutter.code.isolate-untrusted-message
  await Isolate.spawn(worker, input);
}
