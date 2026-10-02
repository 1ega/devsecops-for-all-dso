// License: LGPL-3.0 License (c) find-sec-bugs
package strings

import java.text.Normalizer
import java.util.regex.Pattern

class ModifyAfterValidation {
    fun modifyDangerReplaceAll(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)
        val pattern = Pattern.compile("<script>")

        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        // ruleid: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replace("[\\p{Cn}]".toRegex(), "") // modified after validation
        return s
    }

    fun modifyDangerConcat(str: String?, stringVal: String): String {
        val isTrue = false
        val s = Normalizer.normalize(str, Normalizer.Form.NFKC)
        val pattern = Pattern.compile("<script>")

        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        if (isTrue) {
            // ruleid: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
            someMethod(s + stringVal)
        }
        return s
    }

    fun modifyDangerReplace(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)
        val pattern = Pattern.compile("<script>")

        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        // ruleid: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replace("[\\p{Cn}]", "") // modified after validation
        return s
    }

    fun modifyDangerReplaceFirst(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)
        val pattern = Pattern.compile("<script>")

        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        // ruleid: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replaceFirst("[\\p{Cn}]".toRegex(), "") // modified after validation
        return s
    }

    fun modifySafeReplaceAll(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)

        // ok: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replace("[\\p{Cn}]".toRegex(), "")

        val pattern = Pattern.compile("<script>")
        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        return s
    }

    fun modifySafeReplace(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)

        // ok: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replace("[\\p{Cn}]", "")

        val pattern = Pattern.compile("<script>")
        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        return s
    }

    fun modifySafeReplaceFirst(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)

        // ok: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s.replaceFirst("[\\p{Cn}]".toRegex(), "")

        val pattern = Pattern.compile("<script>")
        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        return s
    }

    fun modifySafeConcat(str: String?): String {
        var s = Normalizer.normalize(str, Normalizer.Form.NFKC)

        // ok: android.gitlab.kotlin_strings_rule-ModifyAfterValidation
        s = s + "test"

        val pattern = Pattern.compile("<script>")
        val matcher = pattern.matcher(s)

        require(!matcher.find()) { "Invalid input" }
        return s
    }

    fun someMethod(input: String): String {
        return input
    }
}

fun main() {}