// License: LGPL-3.0 License (c) find-sec-bugs
package file

import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import javax.servlet.ServletException
import javax.servlet.http.*
import org.apache.commons.fileupload.FileItem
import org.apache.commons.fileupload.FileUploadException
import org.apache.commons.fileupload.disk.DiskFileItemFactory
import org.apache.commons.fileupload.servlet.ServletFileUpload

class FileUploadFileName {
    @Throws(FileUploadException::class)
    fun handleFileCommon(req: javax.servlet.http.HttpServletRequest?) {
        val upload: ServletFileUpload = ServletFileUpload(DiskFileItemFactory())
        val fileItems: List<FileItem> = upload.parseRequest(req)

        for (item in fileItems) {
            // ruleid: android.gitlab.kotlin_file_rule-FileUploadFileName
            System.out.println(("Saving " + item.getName()).toString() + "...")
        }
    }
}

@javax.servlet.annotation.WebServlet("/upload")
@javax.servlet.annotation.MultipartConfig
internal class SimpleFileUploadServlet : javax.servlet.http.HttpServlet() {
    @Throws(ServletException::class, IOException::class)
    protected override fun doPost(
            request: javax.servlet.http.HttpServletRequest,
            response: javax.servlet.http.HttpServletResponse?
    ) {
        val filePart: javax.servlet.http.Part = request.getPart("file")
        // ruleid: android.gitlab.kotlin_file_rule-FileUploadFileName
        val fileName: String = filePart.getSubmittedFileName()

        // Define the path where you want to save the file
        val uploadPath: String = getServletContext().getRealPath("") + File.separator + "uploads"
        val uploadDir = File(uploadPath)
        if (!uploadDir.exists()) uploadDir.mkdir()

        filePart.getInputStream().use { fileContent ->
            FileOutputStream(uploadPath + File.separator + fileName).use { fos ->
                val buffer = ByteArray(1024)
                var bytesRead: Int
                while ((fileContent.read(buffer).also { bytesRead = it }) != -1) {
                    fos.write(buffer, 0, bytesRead)
                }
            }
        }
    }
}

@jakarta.servlet.annotation.WebServlet("/upload2")
@jakarta.servlet.annotation.MultipartConfig
internal class FileUploadServlet : jakarta.servlet.http.HttpServlet() {
    @Throws(IOException::class, jakarta.servlet.ServletException::class)
    protected override fun doPost(
            request: jakarta.servlet.http.HttpServletRequest,
            response: jakarta.servlet.http.HttpServletResponse?
    ) {
        val filePart: jakarta.servlet.http.Part = request.getPart("file")

        // ruleid: android.gitlab.kotlin_file_rule-FileUploadFileName
        val fileName: String = filePart.getSubmittedFileName() // Retrieves the file name

        val file = File("/path/to/uploads", fileName)
        filePart.getInputStream().use { fileContent ->
            Files.copy(fileContent, file.toPath(), StandardCopyOption.REPLACE_EXISTING)
        }
    }
}
