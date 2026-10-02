// License: LGPL-3.0 License (c) find-sec-bugs
package strings

import java.text.Normalizer
import java.util.regex.Pattern

class NormalizeAfterValidation {
    fun normalizeDanger(s: CharSequence?): String {
        // ruleid: android.gitlab.kotlin_strings_rule-NormalizeAfterValidation
        val pattern = Pattern.compile("[<>]") // Check for angle brackets
        val matcher = pattern.matcher(s)
        check(!matcher.find())
        return Normalizer.normalize(s, Normalizer.Form.NFKC) // normalized after validation
    }
}
