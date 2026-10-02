// License: LGPL-3.0 License (c) find-sec-bugs
package xxe

import java.io.InputStream
import javax.xml.stream.XMLInputFactory
import javax.xml.stream.XMLStreamException
import kotlin.Throws

class XMLStreamRdr {
    @Throws(XMLStreamException::class)
    fun loadXml() {
        val `in` = javaClass.getResourceAsStream("/testcode/xxe/simple_xxe.xml")
        val dos_in = javaClass.getResourceAsStream("/testcode/xxe/dos_xxe.xml")

        if (`in` == null) println("Oups XML file not found.")
        if (dos_in == null) println("Oups XML DoS file not found.")
    }

    @Throws(XMLStreamException::class)
    fun parseXMLSafe1(input: InputStream?) {
        val factory = XMLInputFactory.newFactory()
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false)
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false)
        // ok: android.gitlab.kotlin_xxe_rule-XMLStreamRdr
        val reader = factory.createXMLStreamReader(input)
        while (reader.hasNext()) {
            reader.next()
        }
    }

    @Throws(XMLStreamException::class)
    fun parseXMLSafe2(input: InputStream?) {
        val factory = XMLInputFactory.newFactory()
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false)
        // ok: android.gitlab.kotlin_xxe_rule-XMLStreamRdr
        val reader = factory.createXMLStreamReader(input)
        while (reader.hasNext()) {
            reader.next()
        }
    }

    @Throws(XMLStreamException::class)
    fun parseXMLSafe3(input: InputStream?) {
        val factory = XMLInputFactory.newFactory()
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false)
        // ok: android.gitlab.kotlin_xxe_rule-XMLStreamRdr
        val reader = factory.createXMLStreamReader(input)
        while (reader.hasNext()) {
            reader.next()
        }
    }

    @Throws(XMLStreamException::class)
    fun parseXMLSafe4(input: InputStream?) {
        val factory = XMLInputFactory.newFactory()
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false)
        // ok: android.gitlab.kotlin_xxe_rule-XMLStreamRdr
        val reader = factory.createXMLStreamReader(input)
        while (reader.hasNext()) {
            reader.next()
        }
    }

    @Throws(XMLStreamException::class)
    fun parseXMLUnSafe(input: InputStream?) {
        val factory = XMLInputFactory.newFactory()
        // ruleid: android.gitlab.kotlin_xxe_rule-XMLStreamRdr
        val reader = factory.createXMLStreamReader(input)
        while (reader.hasNext()) {
            reader.next()
        }
    }
}
