// License: LGPL-3.0 License (c) find-sec-bugs
package perm

import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.attribute.PosixFilePermissions

class OverlyPermissiveFilePermissionInline {
  @Throws(IOException::class)
  fun dangerInline(path: Path?) {
    // ruleid: android.gitlab.kotlin_perm_rule-OverlyPermissiveFilePermissionInline
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-rw-rw-"))
  }

  @Throws(IOException::class)
  fun dangerInline2(path: Path?) {
    // ruleid: android.gitlab.kotlin_perm_rule-OverlyPermissiveFilePermissionInline
    val perms = PosixFilePermissions.fromString("rw-rw-rw-")
    Files.setPosixFilePermissions(path, perms)
  }

  @Throws(IOException::class)
  fun okInline(path: Path?) {
    Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rw-rw----"))
  }
}