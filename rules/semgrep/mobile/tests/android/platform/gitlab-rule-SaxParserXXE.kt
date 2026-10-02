// License: LGPL-3.0 License (c) find-sec-bugs
package xxe

import java.io.ByteArrayInputStream
import java.io.IOException
import java.io.InputStream
import javax.xml.parsers.ParserConfigurationException
import javax.xml.parsers.SAXParserFactory
import org.xml.sax.SAXException
import org.xml.sax.helpers.DefaultHandler

object SaxParserXXE {
    @Throws(ParserConfigurationException::class, SAXException::class, IOException::class)
    private fun receiveXMLStream(inStream: InputStream, defHandler: DefaultHandler) {
        // ...
        val spf = SAXParserFactory.newInstance()
        val saxParser = spf.newSAXParser()
        // ruleid: android.gitlab.kotlin_xxe_rule-SaxParserXXE
        saxParser.parse(inStream, defHandler)
    }

    @Throws(ParserConfigurationException::class, SAXException::class, IOException::class)
    @JvmStatic
    fun main(args: Array<String>) {
        val xmlString =
                "<?xml version=\"1.0\"?>" +
                        "<!DOCTYPE test [  <!ENTITY foo SYSTEM \"C:/Code/public.txt\"> ]><test>&foo;</test>" // Tainted input

        val `is`: InputStream = ByteArrayInputStream(xmlString.toByteArray())
        receiveXMLStream(`is`, DefaultHandler())
    }
}
