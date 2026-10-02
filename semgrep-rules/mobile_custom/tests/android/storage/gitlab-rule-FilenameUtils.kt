// License: LGPL-3.0 License (c) find-sec-bugs
package file

import java.io.File
import java.io.IOException
import org.apache.commons.io.FilenameUtils.*

object FilenameUtils {
    @Throws(IOException::class)
    @JvmStatic
    fun main(args: Array<String>) {
        val maliciousPath = "/test%00/././../../././secret/note.cfg\u0000example.jpg"

        testPath(maliciousPath)
    }

    @Throws(IOException::class)
    private fun testPath(maliciousPath: String) {
        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        val path: String = normalize(maliciousPath)
        println("Expected:" + path + " -> Actual:" + canonical(path))

        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        val extension: String = getExtension(maliciousPath)
        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        println("Expected:" + extension + " -> Actual:" + getExtension(canonical(path)))

        val isExtension: Boolean = isExtension(maliciousPath, "jpg")
        println("Expected:" + isExtension + " -> Actual:" + isExtension(canonical(path), "jpg"))

        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        val name: String = getName(maliciousPath)
        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        println("Expected:" + name + " -> Actual:" + getName(canonical(name)))

        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        val baseName: String = getBaseName(maliciousPath)
        // ruleid: android.gitlab.kotlin_file_rule-FilenameUtils
        println("Expected:" + baseName + " -> Actual:" + getBaseName(canonical(baseName)))
    }

    @Throws(IOException::class)
    private fun canonical(path: String): String {
        return File(path).canonicalPath
    }
}
