// License: LGPL-3.0 License (c) find-sec-bugs
package xxe

import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import javax.xml.parsers.ParserConfigurationException
import org.xml.sax.InputSource
import org.xml.sax.SAXException
import org.xml.sax.helpers.DefaultHandler
import org.xml.sax.helpers.XMLReaderFactory

@Suppress("UNUSED_PARAMETER")
object XMLRdr {
    @Throws(ParserConfigurationException::class, SAXException::class, IOException::class)
    private fun receiveXMLStream(inStream: InputStream, defHandler: DefaultHandler) {
        // ...
        val reader = XMLReaderFactory.createXMLReader()
        // ruleid: android.gitlab.kotlin_xxe_rule-XMLRdr
        reader.parse(InputSource(inStream))
    }

    @Throws(ParserConfigurationException::class, SAXException::class, IOException::class)
    @JvmStatic
    fun main(args: Array<String>) {
        val xmlString =
                "<?xml version=\"1.0\"?>" +
                        "<!DOCTYPE test [ <!ENTITY foo SYSTEM \"C:/Code/public.txt\"> ]><test>&foo;</test>" // Tainted input

        val `is`: InputStream = ByteArrayInputStream(xmlString.toByteArray())
        receiveXMLStream(`is`, DefaultHandler())
    }
}
