// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import com.opensymphony.xwork2.ognl.OgnlReflectionProvider
import com.opensymphony.xwork2.ognl.OgnlUtil
import com.opensymphony.xwork2.util.TextParseUtil
import com.opensymphony.xwork2.util.ValueStack
import java.beans.IntrospectionException
import javax.management.ReflectionException
import ognl.OgnlException

class OgnlInjection {
    @Throws(OgnlException::class, ReflectionException::class)
    fun unsafeOgnlUtil(ognlUtil: OgnlUtil, input: String, propsInput: Map<String, *>) {
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setValue(input, null, null, "12345")
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.getValue(input, null, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperty(input, "12345", null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperty(input, "12345", null, null, true)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperties(propsInput, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperties(propsInput, null, null, true)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperties(propsInput, null, true)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.setProperties(propsInput, null)
        // ognlUtil.callMethod(input, null, null);
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.compile(input)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        ognlUtil.compile(input)
    }

    @Throws(OgnlException::class, ReflectionException::class)
    fun safeOgnlUtil(ognlUtil: OgnlUtil) {
        val input = "thisissafe"

        ognlUtil.setValue(input, null, null, "12345")
        ognlUtil.getValue(input, null, null, null)
        ognlUtil.setProperty(input, "12345", null, null)
        ognlUtil.setProperty(input, "12345", null, null, true)
        ognlUtil.setProperties(HashMap<String, String>(), null, null)
        ognlUtil.setProperties(HashMap<String, String>(), null, null, true)
        ognlUtil.setProperties(HashMap<String, String>(), null, true)
        ognlUtil.setProperties(HashMap<String, String>(), null)
        // ognlUtil.callMethod(input, null, null);
        ognlUtil.compile(input)
        ognlUtil.compile(input)
    }

    @Throws(ReflectionException::class, IntrospectionException::class)
    fun unsafeOgnlReflectionProvider(
            input: String,
            propsInput: Map<String, String>,
            reflectionProvider: OgnlReflectionProvider,
            type: Class<*>
    ) {
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.getGetMethod(type, input)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.getSetMethod(type, input)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.getField(type, input)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.setProperties(propsInput, null, null, true)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.setProperties(propsInput, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.setProperties(propsInput, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.setProperty(input, "test", null, null)
        // reflectionProvider.setProperty( input, "test",null, null, true);
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.getValue(input, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        reflectionProvider.setValue(input, null, null, null)
    }

    @Throws(IntrospectionException::class, ReflectionException::class)
    fun safeOgnlReflectionProvider(reflectionProvider: OgnlReflectionProvider, type: Class<*>) {
        val input = "thisissafe"
        val constant1 = ""
        // val constant2 = ""
        reflectionProvider.getGetMethod(type, input)
        reflectionProvider.getSetMethod(type, input)
        reflectionProvider.getField(type, input)
        reflectionProvider.setProperties(HashMap<String, String>(), null, null, true)
        reflectionProvider.setProperties(HashMap<String, String>(), null, null)
        reflectionProvider.setProperties(HashMap<String, String>(), null)
        reflectionProvider.setProperty("test", constant1, null, null)
        // reflectionProvider.setProperty("test", constant2, null, null, true);
        reflectionProvider.getValue(input, null, null)
        reflectionProvider.setValue(input, null, null, null)
    }

    fun unsafeTextParseUtil(input: String) {
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        TextParseUtil.translateVariables(input, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        TextParseUtil.translateVariables(input, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        TextParseUtil.translateVariables('a', input, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        TextParseUtil.translateVariables('a', input, null, null)
        // ruleid: android.gitlab.kotlin_inject_rule-OgnlInjection
        TextParseUtil.translateVariables('a', input, null, null, null, 0)
    }

    fun safeTextParseUtil(
            stack: ValueStack,
            parsedValueEvaluator: TextParseUtil.ParsedValueEvaluator,
            type: Class<*>
    ) {
        val input = "1+1"
        TextParseUtil.translateVariables(input, stack)
        TextParseUtil.translateVariables(input, stack, parsedValueEvaluator)
        TextParseUtil.translateVariables('a', input, stack)
        TextParseUtil.translateVariables('a', input, stack, type)

        TextParseUtil.translateVariables('a', input, stack, type, parsedValueEvaluator, 0)
    }
}