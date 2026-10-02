// License: LGPL-3.0 License (c) find-sec-bugs
package xpathi

import org.w3c.dom.Document
import org.w3c.dom.NodeList
import javax.xml.namespace.QName
import javax.xml.xpath.*

// ref: android.gitlab.kotlin_xpathi_rule-XpathInjection
@Suppress("UNUSED_VARIABLE", "UNUSED_VALUE", "UNUSED_PARAMETER", "ASSIGNED_BUT_NEVER_ACCESSED_VARIABLE")
object XpathInjection {
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
        val doc: Document? = null
        val input = if (args.size != 0) args[1] else "guess' or '1'='1"
        val query = "//groups/group[@id='$input']/writeAccess/text()"

        println(">> XPath.compile()")
        run {
            val xpath = XPathFactory.newInstance().newXPath()
            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            val expr = xpath.compile(query)
        }

        println(">> XPath.evaluate()")
        run {
            val xpath = XPathFactory.newInstance().newXPath()
            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            val result = xpath.evaluate(query, doc)
            println("result=$result")
        }

        //Safe (The next sample should not be mark)
        println(">> Safe")
        run {
            val xpath = XPathFactory.newInstance().newXPath()
            // ok: android.gitlab.kotlin_xpathi_rule-XpathInjection
            val expr = xpath.compile("//groups/group[@id='admin']/writeAccess/text()")
        }
    }

    @Throws(Exception::class)
    fun test(args: Array<String>) {
        val doc: Document? = null
        val input = if (args.size != 0) args[1] else "guess' or '1'='1"
        val query = "//groups/group[@id='$input']/writeAccess/text()"
        val query2 = "//author[contains(., \$author)]"

        println(">> XPath.compile()")
        run {
            val xpath = XPathFactory.newInstance().newXPath()
            val resolver = SimpleXPathVariableResolver()
            resolver.setVariable(QName("author"), input)
            xpath.xPathVariableResolver = resolver

            // ok: android.gitlab.kotlin_xpathi_rule-XpathInjection
            var result = xpath.compile("//groups/group[@id='admin']/writeAccess/text()").evaluate(doc)
            // ok: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile(query2).evaluate(doc)
            // ok: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile("//author[contains(., \$author)]").evaluate(doc)

            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile(query).evaluate(doc)
            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile("//groups/group[@id='$input']/writeAccess/text()").evaluate(doc)
            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile(query).evaluate(doc)
            // ruleid: android.gitlab.kotlin_xpathi_rule-XpathInjection
            result = xpath.compile("//author[contains(., \$author)]$input").evaluate(doc)
        }
    }
}

internal class SimpleXPathVariableResolver : XPathVariableResolver {
    // Use a map or lookup table to store variables for resolution
    private val variables = HashMap<QName, String>()

    // Allow caller to set variables
    fun setVariable(name: QName, value: String) {
        variables[name] = value
    }

    // Implement the resolveVariable to return the value
    override fun resolveVariable(name: QName): Any {
        return variables.getOrDefault(name, "")
    }
}