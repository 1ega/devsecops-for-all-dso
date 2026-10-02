// License: LGPL-3.0 License (c) find-sec-bugs
package xml

import java.io.FileInputStream
import java.io.IOException
import javax.xml.transform.Source
import javax.xml.transform.TransformerException
import javax.xml.transform.TransformerFactory
import javax.xml.transform.stream.StreamResult
import javax.xml.transform.stream.StreamSource
import org.apache.commons.io.IOUtils

class XsltTransform {
    @Throws(TransformerException::class)
    fun xslt1SafeStaticResource() {
        val factory = TransformerFactory.newInstance()
        val xslt: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "xsl_safe.xsl"))
        val transformer = factory.newTransformer(xslt)

        val text: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "input.xml"))
        transformer.transform(text, StreamResult(System.out))
    }

    @Throws(TransformerException::class)
    fun xslt2UnsafeResource(input: String) {
        val factory = TransformerFactory.newInstance()
        val xslt: Source = StreamSource(javaClass.getResourceAsStream(input))
        // ruleid: android.gitlab.kotlin_xml_rule-XsltTransform
        val transformer = factory.newTransformer(xslt)

        val text: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "input.xml"))
        transformer.transform(text, StreamResult(System.out))
    }

    @Throws(TransformerException::class)
    fun xslt3UnsafeResource(input: String) {
        val factory = TransformerFactory.newInstance()
        val xslt: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + input))
        // ruleid: android.gitlab.kotlin_xml_rule-XsltTransform
        val transformer = factory.newTransformer(xslt)

        val text: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "input.xml"))
        transformer.transform(text, StreamResult(System.out))
    }

    @Throws(TransformerException::class)
    fun xslt4UnsafeResource(input: String) {
        val factory = TransformerFactory.newInstance()
        var inStream: FileInputStream? = null
        try {
            inStream = FileInputStream(FOLDER + input)
            val xslt: Source = StreamSource(inStream)
            // ruleid: android.gitlab.kotlin_xml_rule-XsltTransform
            val transformer = factory.newTransformer(xslt)

            val text: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "input.xml"))
            transformer.transform(text, StreamResult(System.out))
        } catch (e: IOException) {
            e.printStackTrace()
        } finally {
            IOUtils.closeQuietly(inStream)
        }
    }

    @Throws(TransformerException::class)
    fun xslt5SafeResource() {
        val input = "/safe.xsl"
        val factory = TransformerFactory.newInstance()
        var inStream: FileInputStream? = null
        try {
            inStream = FileInputStream(FOLDER + input)
            val xslt: Source = StreamSource(inStream)
            val transformer = factory.newTransformer(xslt)

            val text: Source = StreamSource(javaClass.getResourceAsStream(FOLDER + "input.xml"))
            transformer.transform(text, StreamResult(System.out))
        } catch (e: IOException) {
            e.printStackTrace()
        } finally {
            IOUtils.closeQuietly(inStream)
        }
    }

    companion object {
        const val FOLDER: String = "/testcode/xsl/"
    }
}