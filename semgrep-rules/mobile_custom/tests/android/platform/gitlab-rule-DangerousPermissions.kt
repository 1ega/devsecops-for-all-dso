// License: LGPL-3.0 License (c) find-sec-bugs
@file:Suppress("DEPRECATION", "UNUSED_PARAMETER")
package perm

import java.lang.reflect.ReflectPermission
import java.security.CodeSource
import java.security.PermissionCollection
import java.security.Policy

class DangerousPermissions : Policy() {
    fun danger(cs: CodeSource?) {
        val pc = super.getPermissions(cs)
        // ruleid: android.gitlab.kotlin_perm_rule-DangerousPermissions
        pc.add(ReflectPermission("suppressAccessChecks"))
    }

    fun danger2(pc: PermissionCollection) {
        // ruleid: android.gitlab.kotlin_perm_rule-DangerousPermissions
        pc.add(RuntimePermission("createClassLoader"))
    }

    fun danger3(pc: PermissionCollection) {
        // ruleid: android.gitlab.kotlin_perm_rule-DangerousPermissions
        val perm = RuntimePermission("createClassLoader")
        pc.add(perm)
    }

    fun danger4(pc: PermissionCollection) {
        // ruleid: android.gitlab.kotlin_perm_rule-DangerousPermissions
        val perm = ReflectPermission("suppressAccessChecks")
        pc.add(perm)
    }

    fun ok(cs: CodeSource?) {
        // ok: android.gitlab.kotlin_perm_rule-DangerousPermissions
        val perm = ReflectPermission("suppressAccessChecks")
        val list: MutableList<ReflectPermission> = ArrayList()
        list.add(perm)
    }
}