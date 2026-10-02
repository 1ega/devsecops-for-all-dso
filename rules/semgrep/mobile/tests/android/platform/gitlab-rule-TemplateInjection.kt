// License: LGPL-3.0 License (c) find-sec-bugs
package templateinjection

import com.mitchellbosecke.pebble.PebbleEngine
import com.mitchellbosecke.pebble.error.PebbleException
import com.mitchellbosecke.pebble.template.PebbleTemplate
import freemarker.template.Configuration
import freemarker.template.Template
import freemarker.template.TemplateException
import java.io.*
import java.util.*
import org.apache.velocity.VelocityContext
import org.apache.velocity.app.Velocity

@Suppress("DEPRECATION", "UNUSED_VARIABLE")
class TemplateInjection {
    @Throws(FileNotFoundException::class)
    fun usage1(inputFile: String?) {
        Velocity.init()

        val context: VelocityContext = VelocityContext()

        context.put("author", "Elliot A.")
        context.put("address", "217 E Broadway")
        context.put("phone", "555-1337")

        val file = FileInputStream(inputFile)

        // Evaluate
        val swOut = StringWriter()
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        Velocity.evaluate(context, swOut, "test", file.toString())

        val result = swOut.buffer.toString()
        println(result)
    }

    @Throws(FileNotFoundException::class)
    fun allSignatures(inputStream: InputStream, fileReader: Reader?, template: String?) {
        val context: VelocityContext = VelocityContext()
        val swOut = StringWriter()

        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        Velocity.evaluate(context, swOut, "test", inputStream.toString())
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        Velocity.evaluate(context, swOut, "test", fileReader)
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        Velocity.evaluate(context, swOut, "test", template)
    }

    @Throws(FileNotFoundException::class)
    fun falsePositive() {
        val context: VelocityContext = VelocityContext()
        val swOut = StringWriter()

        Velocity.evaluate(context, swOut, "test", "Hello \$user !")
    }

    fun simple1(inputFile: String?) {
        // Freemarker configuration object

        val cfg: Configuration = Configuration()
        try {
            // Load template from source folder
            val template: Template = cfg.getTemplate(inputFile)

            // Build the data-model
            val data: MutableMap<String, Any> = HashMap()
            data["message"] = "Hello World!"

            // List parsing
            val countries: MutableList<String> = ArrayList()
            countries.add("India")
            countries.add("United States")
            countries.add("Germany")
            countries.add("France")

            data["countries"] = countries

            // Console output
            val out: Writer = OutputStreamWriter(System.out)
            // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
            template.process(data, out) // Vuln here
            out.flush()
        } catch (e: IOException) {
            e.printStackTrace()
        } catch (e: TemplateException) {
            e.printStackTrace()
        }
    }

    @Throws(IOException::class, TemplateException::class)
    fun allSignatures1(inputFile: String?) {
        val cfg: Configuration = Configuration()
        val template: Template = cfg.getTemplate(inputFile)
        val data: Map<String, Any> = HashMap()

        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        template.process(data, OutputStreamWriter(System.out)) // TP
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        template.process(data, OutputStreamWriter(System.out), null) // TP
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        template.process(data, OutputStreamWriter(System.out), null, null) // TP
    }

    @Throws(IOException::class)
    fun simple(inputFile: String?) {
        val engine: PebbleEngine = PebbleEngine.Builder().build()
        var compiledTemplate: PebbleTemplate? = null
        try {
            compiledTemplate = engine.getTemplate(inputFile)
        } catch (e: PebbleException) {
            e.printStackTrace()
        }

        val context: MutableMap<String, Any> = HashMap()
        context["name"] = "Shivam"

        val writer: Writer = StringWriter()
        try {
            compiledTemplate?.evaluate(writer, context)
        } catch (e: PebbleException) {
            e.printStackTrace()
        }

        val output = writer.toString()
    }

    @Throws(IOException::class, PebbleException::class)
    fun allSignatures(inputFile: String?) {
        val engine: PebbleEngine = PebbleEngine.Builder().build()
        var compiledTemplate: PebbleTemplate?

        compiledTemplate = engine.getTemplate(inputFile)

        val data: Map<String, Any> = HashMap()
        // ruleid: android.gitlab.kotlin_templateinjection_rule-TemplateInjection
        compiledTemplate.evaluate(StringWriter(), data, Locale.US)
    }
}