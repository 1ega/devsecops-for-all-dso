// License: LGPL-3.0 License (c) find-sec-bugs
package xml

import org.opensaml.xml.parse.BasicParserPool
import org.opensaml.xml.parse.ParserPool
import org.springframework.context.annotation.Bean

class SAMLIgnoreComments {
  @Bean
  fun parserPool(): ParserPool {
    val pool: BasicParserPool = BasicParserPool()
    // ruleid: android.gitlab.kotlin_xml_rule-SAMLIgnoreComments
    pool.setIgnoreComments(false)
    return pool
  }

  @Bean
  fun parserPool2() {
    val shouldIgnore = false
    val pool: BasicParserPool = BasicParserPool()
    // ruleid: android.gitlab.kotlin_xml_rule-SAMLIgnoreComments
    pool.setIgnoreComments(shouldIgnore)
  }
}
