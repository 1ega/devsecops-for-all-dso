let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: keychainService,
    kSecAttrAccount as String: "username",
    kSecValueData as String: "password".data(using: .utf8)!,
    //ruleid:ios.gitlab.rules_lgpl_swift_other_rule-ios-keychain-weak-accessibility-value
    kSecAttrAccessible as String: kSecAttrAccessibleAlways
]

let statusAddAlways = SecItemAdd(query as CFDictionary, nil)

let queryUpdate: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: keychainService,
    kSecAttrAccount as String: "username",
    //ruleid:ios.gitlab.rules_lgpl_swift_other_rule-ios-keychain-weak-accessibility-value
    kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
]

let updateAttributes: [String: Any] = [
    kSecValueData as String: "newPassword".data(using: .utf8)!
]

let statusUpdate = SecItemUpdate(queryUpdate as CFDictionary, updateAttributes as CFDictionary)
if statusUpdate == errSecSuccess {
    print("Item updated to use kSecAttrAccessibleAfterFirstUnlock accessibility")
} else {
    print("Error updating item in keychain: \(statusUpdate)")
}
