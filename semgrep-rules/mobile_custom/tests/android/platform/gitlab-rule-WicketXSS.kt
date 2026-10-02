// License: LGPL-3.0 License (c) find-sec-bugs
@file:Suppress("DEPRECATION", "UNUSED_PARAMETER")

package xss

// import org.apache.wicket.extensions.markup.html.form.select.SelectOptions.SimpleSelectOption;
import java.util.Arrays
import org.apache.wicket.Component
import org.apache.wicket.extensions.ajax.markup.html.modal.ModalWindow
import org.apache.wicket.markup.html.WebPage
import org.apache.wicket.markup.html.basic.Label
import org.apache.wicket.markup.html.basic.MultiLineLabel
import org.apache.wicket.markup.html.form.Check
import org.apache.wicket.markup.html.form.CheckBoxMultipleChoice
import org.apache.wicket.markup.html.form.DropDownChoice
import org.apache.wicket.markup.html.form.Form
import org.apache.wicket.markup.html.form.Radio
import org.apache.wicket.markup.html.form.RadioGroup
import org.apache.wicket.markup.html.panel.FeedbackPanel
import org.apache.wicket.model.Model
import org.apache.wicket.request.mapper.parameter.PageParameters

internal class WicketXSS : WebPage() {
    fun XssWicketExamplePage(pageParameters: PageParameters?) {
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        add(Label("test").setEscapeModelStrings(false))
    }

    // http://www.java2s.com/example/java-src/pkg/org/jabylon/rest/ui/wicket/components/customfeedbackpanel-edea7.html
    protected fun newMessageDisplayComponent(id: String?, message: String?): Component {
        val label: MultiLineLabel = MultiLineLabel(id, message)
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        label.setEscapeModelStrings(false)
        return label
    }

    fun setText(txt: String?, c: Component) {
        if (txt == null || txt.trim { it <= ' ' }.length == 0) {
            c.isVisible = false
        } else {
            c.setDefaultModelObject(txt)
            c.isVisible = true
            // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
            c.setEscapeModelStrings(false)
        }
    }

    protected fun newLabel(lab: Label) {
        val label: Component = lab
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        label.setEscapeModelStrings(false)

        // https://github.com/apache/wicket/blob/e9461b0d115a7dbf4992596823521f6e038817d9/wicket-user-guide/src/main/asciidoc/forms2/forms2_3.adoc#L134
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        add(FeedbackPanel("feedbackMessage").setEscapeModelStrings(false))
    }

    fun advancedSearchPage(input: String) {
        val form: Form<*> = Form<Any>("form")
        // Options for the dropdown
        val options = Arrays.asList("Option 1 $input", "Option 2 $input", "Option 3 $input")

        // Model for the selected value
        val selectedOption: Model<String> = Model("Option 1 $input")

        // Create a DropDownChoice and add it to the form
        val dropdown = DropDownChoice<String>("dropdown", selectedOption, options)
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        dropdown.setEscapeModelStrings(false)
        form.add(dropdown)

        add(form)
    }

    // https://www.tabnine.com/code/java/methods/org.apache.wicket.markup.html.form.Radio/setEscapeModelStrings
    private fun getFormComponentValue(formComponent: Radio<*>): String {
        val oldEscape: Boolean = formComponent.getEscapeModelStrings()
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        formComponent.setEscapeModelStrings(false)
        val `val`: String = formComponent.getValue()
        formComponent.setEscapeModelStrings(oldEscape)
        return `val`
    }

    // https://www.tabnine.com/code/java/methods/org.apache.wicket.markup.html.form.Check/setEscapeModelStrings
    private fun getFormComponentValue2(formComponent: Check<*>): String {
        val oldEscape: Boolean = formComponent.getEscapeModelStrings()
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        formComponent.setEscapeModelStrings(false)
        val `val`: String = formComponent.getValue()
        formComponent.setEscapeModelStrings(oldEscape)
        return `val`
    }
}

internal class MyPages : WebPage() {
    private val modalWindow: ModalWindow

    init {
        // Create a ModalWindow and set its title
        modalWindow = ModalWindow("modalWindow")
        modalWindow.setTitle("Potentially Unsafe Title")

        // Explicitly disable escaping of the model strings (title)
        // for CVE-2015-5347/
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        modalWindow.setEscapeModelStrings(false)
        add(modalWindow)
    }
}

internal class MyPage(userGeneratedOptions: List<String>, input: String) : WebPage() {
    init {
        val form: Form<Void> = Form("form")

        val selectedOption: Model<String> = Model.of("")

        val radioGroup: RadioGroup<String> = RadioGroup("radioGroup", selectedOption)
        // for CVE-2015-7520
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        radioGroup.setEscapeModelStrings(false)

        for (option in userGeneratedOptions) {
            radioGroup.add(Radio("radio$option", Model.of(option)))
        }

        form.add(radioGroup)

        // https://nightlies.apache.org/wicket/apidocs/8.x/org/apache/wicket/markup/html/form/CheckBoxMultipleChoice.html
        val SITES: List<*> = Arrays.asList(*arrayOf("The Server Side", "Java Lobby", input))
        // for CVE-2015-7520
        // ruleid: android.gitlab.kotlin_xss_rule-WicketXSS
        form.add(CheckBoxMultipleChoice("site", SITES).setEscapeModelStrings(false))
    }
}