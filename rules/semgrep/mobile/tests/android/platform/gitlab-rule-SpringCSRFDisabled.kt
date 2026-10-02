// License: LGPL-3.0 License (c) find-sec-bugs
package csrf

import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter
import org.springframework.security.config.annotation.web.configurers.CsrfConfigurer

@EnableWebSecurity
class SpringCSRFDisabled : WebSecurityConfigurerAdapter() {
    @Throws(Exception::class)
    protected override fun configure(http: HttpSecurity) {
        // instance 1
        // ruleid: android.gitlab.kotlin_csrf_rule-SpringCSRFDisabled
        http.csrf().disable()

        // instance 2
        val csrf: CsrfConfigurer<HttpSecurity> = http.csrf()
        // ...
        // ruleid: android.gitlab.kotlin_csrf_rule-SpringCSRFDisabled
        csrf.disable()
    }
}