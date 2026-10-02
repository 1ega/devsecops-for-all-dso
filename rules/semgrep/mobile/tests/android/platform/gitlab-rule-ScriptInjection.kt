// License: LGPL-3.0 License (c) find-sec-bugs
// source:
// https://github.com/find-sec-bugs/find-sec-bugs/blob/master/findsecbugs-samples-java/src/test/java/testcode/script/ScriptEngineSample.java
// hash: a7694d0
package script

import javax.script.Invocable
import javax.script.ScriptEngineManager
import javax.script.ScriptException

// ref: android.gitlab.kotlin_script_rule-ScriptInjection
@Suppress("UNUSED_VARIABLE")
class ScriptInjection {
    @Throws(ScriptException::class)
    fun evalWithBindings(userFirstName: String, userLastName: String) {
        val manager = ScriptEngineManager()
        val engine = manager.getEngineByName("javascript")
        // Create bindings to pass into our script, forcing the values to be String.
        val bindings = engine.createBindings()
        bindings["fname"] = java.lang.String(userFirstName) as String
        bindings["lname"] = java.lang.String(userLastName) as String
        // Example script that concatenates a greeting with the user-supplied input first/last name
        val script =
                "var greeting='Hello ';" + // fname and lname variables will be resolved by bindings
                        // defined above
                        "greeting += fname + ' ' + lname;" + // prints greeting
                        "greeting"
        // ok: android.gitlab.kotlin_script_rule-ScriptInjection
        val result = engine.eval(script, bindings)
        println(result)
    }

    @Throws(Exception::class)
    fun invokeFunctionUsage(input: String) {
        val engineManager = ScriptEngineManager()
        val engine = engineManager.getEngineByName("javascript")
        val script = """function greetOne(name) {
    return "Hello, " + name + "!";
}"""
        // Evaluate the JavaScript code
        engine.eval(script)

        // Check if the engine supports the Invocable interface
        if (engine is Invocable) {
            val invocable: Invocable = engine
            // Invoke the "greet" function from the JavaScript file
            // ok: android.gitlab.kotlin_script_rule-ScriptInjection
            val resultOne = invocable.invokeFunction("greetOne", "John") as String
            // ruleid: android.gitlab.kotlin_script_rule-ScriptInjection
            val resultTwo = invocable.invokeFunction("greetOne", input) as String
            // Display the result
            println(resultOne)
            println(resultTwo)
        }
    }

    @Throws(Exception::class)
    fun invokeMethodUsage(input: String) {
        val engineManager = ScriptEngineManager()
        val engine = engineManager.getEngineByName("javascript")
        val script =
                """var obj = {
    greetTwo: function (name) {
        return 'Hello, ' + name;
    }
}"""
        engine.eval(script)

        // Get the object from the script
        val obj = engine["obj"]
        // Check if the engine supports the Invocable interface
        if (engine is Invocable) {
            val invocable: Invocable = engine
            // ok: android.gitlab.kotlin_script_rule-ScriptInjection
            val resultOne = invocable.invokeMethod(obj, "greetTwo", "World")
            // ruleid: android.gitlab.kotlin_script_rule-ScriptInjection
            val resultTwo = invocable.invokeMethod(obj, "greetTwo", input)
            // Print the result
            println(resultOne)
            println(resultTwo)
        }
    }

    companion object {
        @Throws(ScriptException::class)
        fun scripting(userInput: String) {
            val scriptEngineManager = ScriptEngineManager()
            val scriptEngine = scriptEngineManager.getEngineByExtension("js")
            // ruleid: android.gitlab.kotlin_script_rule-ScriptInjection
            val result = scriptEngine.eval("test=1;$userInput")
        }

        // The potential injection will require manual review of the code flow but some false
        // positive can be avoid.
        @Throws(ScriptException::class)
        fun scriptingSafe() {
            val scriptEngineManager = ScriptEngineManager()
            val scriptEngine = scriptEngineManager.getEngineByExtension("js")

            val code = "var test=3;test=test*2;"
            // ok: android.gitlab.kotlin_script_rule-ScriptInjection
            val result = scriptEngine.eval(code)
        }
    }
}
