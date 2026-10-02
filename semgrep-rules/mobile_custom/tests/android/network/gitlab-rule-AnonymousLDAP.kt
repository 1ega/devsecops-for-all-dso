// License: LGPL-3.0 License (c) find-sec-bugs
package ldap

import java.util.*
import javax.naming.AuthenticationException
import javax.naming.Context
import javax.naming.directory.DirContext
import javax.naming.directory.InitialDirContext

object AnonymousLDAP {
    private const val ldapURI = "ldaps://ldap.server.com/dc=ldap,dc=server,dc=com"
    private const val contextFactory = "com.sun.jndi.ldap.LdapCtxFactory"

    @Throws(Exception::class)
    private fun ldapContext(env: Hashtable<String, String>): DirContext {
        env[Context.INITIAL_CONTEXT_FACTORY] = contextFactory
        env[Context.PROVIDER_URL] = ldapURI
        // ruleid: android.gitlab.kotlin_ldap_rule-AnonymousLDAP
        env[Context.SECURITY_AUTHENTICATION] = "none"
        val ctx: DirContext = InitialDirContext(env)
        return ctx
    }

    @Throws(Exception::class)
    fun testBind(dn: String, password: String): Boolean {
        val env = Hashtable<String, String>()
        // ok: android.gitlab.kotlin_ldap_rule-AnonymousLDAP
        env[Context.SECURITY_AUTHENTICATION] = "simple" // false positive
        env[Context.SECURITY_PRINCIPAL] = dn
        env[Context.SECURITY_CREDENTIALS] = password

        try {
            ldapContext(env)
        } catch (e: AuthenticationException) {
            return false
        }
        return true
    }
}