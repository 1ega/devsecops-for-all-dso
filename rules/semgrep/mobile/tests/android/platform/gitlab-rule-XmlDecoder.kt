// License: LGPL-3.0 License (c) find-sec-bugs
package xml

import java.beans.XMLDecoder
import java.io.IOException

@Suppress("UNUSED_VARIABLE")
internal class TestXmlDecoder {
    var safeStr: String = ""

    // This will just create a file in your /tmp/ folder named Hacked1.txt
    @Throws(IOException::class)
    fun decodeObjectUnsafe1() {
        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce.xml")
        val decoder = XMLDecoder(inputStream)
        // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
        val o = decoder.readObject()
        decoder.close()
        println("Check your /tmp/ folder for Hacked1.txt file")
    }

    // This will just create a file in your /tmp/ folder named Hacked2.txt
    @Throws(IOException::class)
    fun decodeObjectUnsafe2() {
        val customClassLoader: ClassLoader? = null
        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        val decoder =
                XMLDecoder(
                        inputStream,
                        null,
                        { exception: Exception ->
                            System.err.println("Exception occurred: " + exception.message)
                        },
                        customClassLoader
                )
        // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
        val o = decoder.readObject()
        decoder.close()
        println("Check your /tmp/ folder for Hacked2.txt file")
    }

    @Throws(IOException::class)
    fun decodeObjectUnsafe3() {
        println("Running Unsafe3(): (Unsafe ClassLoader implementation)")
        val customClassLoader: ClassLoader =
                object : ClassLoader() {
                    @Throws(ClassNotFoundException::class)
                    override fun loadClass(name: String, resolve: Boolean): Class<*> {
                        return super.loadClass(name, resolve)
                    }
                }

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            customClassLoader
                    )
            // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectUnsafe4() {
        println("Running Unsafe4(): (Unsafe ClassLoader implementation)")
        val customClassLoader: ClassLoader =
                object : ClassLoader() {
                    @Throws(ClassNotFoundException::class)
                    override fun loadClass(name: String, resolve: Boolean): Class<*> {
                        if (name != TestXmlDecoder::class.java.name &&
                                        name != XMLDecoder::class.java.name
                        ) {
                            return super.loadClass(name, resolve)
                        }
                        return super.loadClass(name, resolve)
                    }
                }

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            customClassLoader
                    )
            // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectUnsafe5() {
        println("Running Unsafe5(): (Unsafe ClassLoader implementation)")

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            object : ClassLoader() {
                                @Throws(ClassNotFoundException::class)
                                override fun loadClass(name: String, resolve: Boolean): Class<*> {
                                    return super.loadClass(name, resolve)
                                }
                            }
                    )
            // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectUnsafe6() {
        println("Running Unsafe6(): (Unsafe ClassLoader implementation)")

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            object : ClassLoader() {
                                @Throws(ClassNotFoundException::class)
                                override fun loadClass(name: String, resolve: Boolean): Class<*> {
                                    if (name != TestXmlDecoder::class.java.name &&
                                                    name != XMLDecoder::class.java.name
                                    ) {
                                        return super.loadClass(name, resolve)
                                    }
                                    return super.loadClass(name, resolve)
                                }
                            }
                    )
            // ruleid: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectSafe1() {
        println("Running Safe1(): (Exceptions will be thrown)")
        val customClassLoader: ClassLoader =
                object : ClassLoader() {
                    @Throws(ClassNotFoundException::class)
                    override fun loadClass(name: String, resolve: Boolean): Class<*> {
                        if (name != TestXmlDecoder::class.java.name &&
                                        name != XMLDecoder::class.java.name
                        ) {
                            throw RuntimeException("Unauthorized deserialization attempt: $name")
                        }
                        return super.loadClass(name, resolve)
                    }
                }

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            customClassLoader
                    )
            // ok: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectSafe2() {
        println(
                "Running Safe2(): (This should run normally as xml file does not contain malicious payload.)"
        )

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-safe.xml")

        val decoder =
                XMLDecoder(
                        inputStream,
                        null,
                        { exception: Exception ->
                            System.err.println("Exception occurred: " + exception.message)
                        },
                        object : ClassLoader() {
                            @Throws(ClassNotFoundException::class)
                            override fun loadClass(name: String, resolve: Boolean): Class<*> {
                                if (name != TestXmlDecoder::class.java.name &&
                                                name != XMLDecoder::class.java.name
                                ) {
                                    throw RuntimeException(
                                            "Unauthorized deserialization attempt: $name"
                                    )
                                }
                                return super.loadClass(name, resolve)
                            }
                        }
                )
        // ok: android.gitlab.kotlin_xml_rule-XmlDecoder
        val o = decoder.readObject()
        decoder.close()
    }

    @Throws(IOException::class)
    fun decodeObjectSafe3() {
        val allowedClasses: MutableList<String> = ArrayList()
        allowedClasses.add(TestXmlDecoder::class.java.name)
        allowedClasses.add(XMLDecoder::class.java.name)

        println("Running Safe3(): (Exceptions will be thrown)")
        val customClassLoader: ClassLoader =
                object : ClassLoader() {
                    @Throws(ClassNotFoundException::class)
                    override fun loadClass(name: String, resolve: Boolean): Class<*> {
                        if (!allowedClasses.contains(name)) {
                            throw RuntimeException("Unauthorized deserialization attempt: $name")
                        }
                        return super.loadClass(name, resolve)
                    }
                }

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            customClassLoader
                    )
            // ok: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }

    @Throws(IOException::class)
    fun decodeObjectSafe4() {
        val allowedClasses: MutableList<String> = ArrayList()
        allowedClasses.add(TestXmlDecoder::class.java.name)
        allowedClasses.add(XMLDecoder::class.java.name)

        println("Running Safe4(): (Exceptions will be thrown)")

        val inputStream =
                TestXmlDecoder::class.java.classLoader.getResourceAsStream("xmldecoder-rce2.xml")

        try {
            val decoder =
                    XMLDecoder(
                            inputStream,
                            null,
                            { exception: Exception ->
                                System.err.println("Exception occurred: " + exception.message)
                            },
                            object : ClassLoader() {
                                @Throws(ClassNotFoundException::class)
                                override fun loadClass(name: String, resolve: Boolean): Class<*> {
                                    if (!allowedClasses.contains(name)) {
                                        throw RuntimeException(
                                                "Unauthorized deserialization attempt: $name"
                                        )
                                    }
                                    return super.loadClass(name, resolve)
                                }
                            }
                    )
            // ok: android.gitlab.kotlin_xml_rule-XmlDecoder
            val o = decoder.readObject()
            decoder.close()
        } catch (e: Exception) {
            System.err.println("Exception occurred: " + e.message)
        }
    }
}