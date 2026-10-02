// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import java.util.*
import javax.naming.AuthenticationException
import javax.naming.Context
import javax.naming.NamingException
import javax.naming.directory.DirContext
import javax.naming.directory.InitialDirContext
import javax.naming.directory.SearchControls
import org.springframework.ldap.core.DefaultNameClassPairMapper
import org.springframework.ldap.core.DirContextProcessor
import org.springframework.ldap.core.LdapEntryIdentificationContextMapper
import org.springframework.ldap.core.LdapTemplate
import org.springframework.ldap.core.support.CountNameClassPairCallbackHandler
import org.springframework.ldap.core.support.DefaultIncrementalAttributesMapper

// ref: android.gitlab.kotlin_inject_rule-LDAPInjection
@Suppress("UNUSED_VARIABLE")
class LDAPInjection {
        /** *************** SPRING LDAP */
        @Throws(NamingException::class)
        fun queryVulnerableToInjection(
                        template: LdapTemplate,
                        jndiInjectMe: String,
                        searchControls: SearchControls?,
                        dirContextProcessor: DirContextProcessor?
        ) {
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(jndiInjectMe)
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(jndiInjectMe, DefaultNameClassPairMapper())
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(jndiInjectMe, CountNameClassPairCallbackHandler())

                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(jndiInjectMe)
                val mapper: DefaultIncrementalAttributesMapper =
                                DefaultIncrementalAttributesMapper("")
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(jndiInjectMe, mapper)
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(jndiInjectMe, LdapEntryIdentificationContextMapper())

                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                searchControls,
                                CountNameClassPairCallbackHandler()
                )
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", searchControls, mapper, dirContextProcessor)
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                searchControls,
                                LdapEntryIdentificationContextMapper(),
                                dirContextProcessor
                )
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                searchControls,
                                CountNameClassPairCallbackHandler(),
                                dirContextProcessor
                )
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                true,
                                CountNameClassPairCallbackHandler()
                )
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", CountNameClassPairCallbackHandler())
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                arrayOfNulls<String>(0),
                                mapper
                )
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", SearchControls.OBJECT_SCOPE, mapper)
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", mapper)
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                arrayOfNulls<String>(0),
                                LdapEntryIdentificationContextMapper()
                )
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                LdapEntryIdentificationContextMapper()
                )
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", LdapEntryIdentificationContextMapper())
                template.search(
                                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                jndiInjectMe,
                                "dn=1",
                                searchControls,
                                LdapEntryIdentificationContextMapper()
                )
                // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(jndiInjectMe, "dn=1", searchControls, mapper)
        }

        @Throws(NamingException::class)
        fun safeQuery(
                        template: LdapTemplate,
                        searchControls: SearchControls?,
                        dirContextProcessor: DirContextProcessor?
        ) {
                val safeQuery = "uid=test"
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(safeQuery)
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(safeQuery, DefaultNameClassPairMapper())
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.list(safeQuery, CountNameClassPairCallbackHandler())

                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(safeQuery)
                val mapper: DefaultIncrementalAttributesMapper =
                                DefaultIncrementalAttributesMapper("")
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(safeQuery, mapper)
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.lookup(safeQuery, LdapEntryIdentificationContextMapper())

                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                searchControls,
                                CountNameClassPairCallbackHandler()
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", searchControls, mapper, dirContextProcessor)
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                searchControls,
                                LdapEntryIdentificationContextMapper(),
                                dirContextProcessor
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                searchControls,
                                CountNameClassPairCallbackHandler(),
                                dirContextProcessor
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                true,
                                CountNameClassPairCallbackHandler()
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", CountNameClassPairCallbackHandler())
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                arrayOfNulls<String>(0),
                                mapper
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", SearchControls.OBJECT_SCOPE, mapper)
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", mapper)
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                arrayOfNulls<String>(0),
                                LdapEntryIdentificationContextMapper()
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                SearchControls.OBJECT_SCOPE,
                                LdapEntryIdentificationContextMapper()
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", LdapEntryIdentificationContextMapper())
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(
                                safeQuery,
                                "dn=1",
                                searchControls,
                                LdapEntryIdentificationContextMapper()
                )
                // ok: android.gitlab.kotlin_inject_rule-LDAPInjection
                template.search(safeQuery, "dn=1", searchControls, mapper)
        }

        companion object {
                private const val ldapURI = "ldaps://ldap.server.com/dc=ldap,dc=server,dc=com"
                private const val contextFactory = "com.sun.jndi.ldap.LdapCtxFactory"

                /** *************** JNDI LDAP */
                fun authenticate(username: String, password: String): Boolean {
                        try {
                                val props = Properties()
                                props[Context.INITIAL_CONTEXT_FACTORY] =
                                                "com.sun.jndi.ldap.LdapCtxFactory"
                                props[Context.PROVIDER_URL] = "ldap://ldap.example.com"
                                props[Context.REFERRAL] = "ignore"
                                props[Context.SECURITY_PRINCIPAL] = dnFromUser(username)
                                props[Context.SECURITY_CREDENTIALS] = password

                                InitialDirContext(props)
                                return true
                        } catch (e: NamingException) {
                                return false
                        }
                }

                @Throws(NamingException::class)
                private fun dnFromUser(username: String): String {
                        val props = Properties()
                        props[Context.INITIAL_CONTEXT_FACTORY] = "com.sun.jndi.ldap.LdapCtxFactory"
                        props[Context.PROVIDER_URL] = "ldap://ldap.example.com"
                        props[Context.REFERRAL] = "ignore"

                        val context = InitialDirContext(props)

                        val ctrls = SearchControls()
                        ctrls.returningAttributes = arrayOf("givenName", "sn")
                        ctrls.searchScope = SearchControls.SUBTREE_SCOPE

                        val answers =
                                        context.search(
                                                        "dc=People,dc=example,dc=com",
                                                        // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                                                        "(uid=" + username + ")",
                                                        ctrls
                                        )
                        val result = answers.next()

                        return result.nameInNamespace
                }

                @Throws(Exception::class)
                private fun ldapContext(env: Hashtable<String, String>): DirContext {
                        env[Context.INITIAL_CONTEXT_FACTORY] = contextFactory
                        env[Context.PROVIDER_URL] = ldapURI
                        env[Context.SECURITY_AUTHENTICATION] = "none"
                        val ctx: DirContext = InitialDirContext(env)
                        return ctx
                }

                @Throws(Exception::class)
                fun testBind(dn: String, password: String): Boolean {
                        val env = Hashtable<String, String>()
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

                /** *************** JNDI LDAP SPECIAL */
                @Throws(NamingException::class)
                fun main(ctx: DirContext, param: String) {
                        val base = "ou=users,ou=system"
                        val sc = SearchControls()
                        sc.searchScope = SearchControls.SUBTREE_SCOPE
                        val filter = "(&(objectclass=person))(|(uid=" + param + ")(street={0}))"
                        val filters = arrayOf<Any>("The streetz 4 Ms bar")
                        println("Filter " + filter + "")
                        // ruleid: android.gitlab.kotlin_inject_rule-LDAPInjection
                        val results = ctx.search(base, filter, filters, sc)
                }
        }
}