let fileManager = FileManager.default
let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
let fileURL = documentsURL.appendingPathComponent("example.txt")

do {
    try "This is a test file.".write(to: fileURL, atomically: true, encoding: .utf8)
    //ruleid:ios.gitlab.rules_lgpl_swift_other_rule-ios-file-no-special
    try fileManager.setAttributes([.protectionKey: FileProtectionType.none], ofItemAtPath: fileURL.path)
    print("File created successfully with no file protection.")
} catch {
    print("Error: \(error.localizedDescription)")
}

do {
    try "This is a test file.".write(to: fileURL, atomically: true, encoding: .utf8)
    //ruleid:ios.gitlab.rules_lgpl_swift_other_rule-ios-file-no-special
    try fileManager.setAttributes([.noFileProtection: true], ofItemAtPath: fileURL.path)
    print("File created successfully with no file protection.")
} catch {
    print("Error: \(error.localizedDescription)")
}
