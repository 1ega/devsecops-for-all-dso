package inject

import javax.el.ELContext
import javax.el.ELProcessor
import javax.el.ExpressionFactory
import javax.el.MethodExpression
import javax.faces.context.FacesContext

// Rule: android.gitlab.kotlin_inject_rule-ELInjection
@javax.inject.Named
internal class ElInjectionBean {
    private val userInputValue: String? = null
    private val userInputMethod: String? = null
    private val userInputLambda: String? = null
    private val userInputELProcessor: String? = null
    private val userInputLambdaArgs: String? = null
    private val userInputELProcessorGV: String? = null
    private val userInputELProcessorSV: String? = null
    private val inputValueToSet: String? = null

    private var evaluationVResult: Any? = null
    private var evaluationMResult: Any? = null
    private val evaluationLResult: Any? = null
    private var evaluationELPResult: Any? = null
    private var evaluationELPGetValue: Any? = null
    private var evaluationELPSetValue: Any? = null

    private val lambdaExpression: String? = null
    private val privateConfigValue: String? = null

    fun evaluateValueExpression() {
        try {
            val facesContext: FacesContext = FacesContext.getCurrentInstance()
            val elContext: ELContext = facesContext.getELContext()
            val expressionFactory: ExpressionFactory = facesContext.getApplication().getExpressionFactory()

            println("User input: $userInputValue")
            // ruleid: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationVResult = expressionFactory.createValueExpression(elContext, userInputValue, Any::class.java)
                .getValue(elContext)

            // ok: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationVResult = expressionFactory.createValueExpression(elContext, "#{2+2}", Any::class.java)
                .getValue(elContext)
            println("Evaluation Result: $evaluationVResult")
        } catch (e: Exception) {
            evaluationVResult = "Error: " + e.message
        }
    }

    fun evaluateMethodExpression() {
        try {
            val facesContext: FacesContext = FacesContext.getCurrentInstance()
            val elContext: ELContext = facesContext.getELContext()
            val expressionFactory: ExpressionFactory = facesContext.getApplication().getExpressionFactory()

            println("User input: $userInputMethod")

            // ruleid: android.gitlab.kotlin_inject_rule-ELInjection
            val methodExpression: MethodExpression = expressionFactory.createMethodExpression(
                elContext, userInputMethod, Any::class.java, arrayOfNulls<Class<*>>(0)
            )

            // Evaluate the MethodExpression
            evaluationMResult = methodExpression.invoke(elContext, null)

            // ok: android.gitlab.kotlin_inject_rule-ELInjection
            val methodExpression2: MethodExpression = expressionFactory.createMethodExpression(
                elContext, "#{elInjectionBean.getSum}", Any::class.java, arrayOfNulls<Class<*>>(0)
            )

            // Evaluate the MethodExpression
            evaluationMResult = methodExpression2.invoke(elContext, null)

            println("Evaluation Result: $evaluationMResult")
        } catch (e: Exception) {
            evaluationMResult = "Error: " + e.message
        }
    }

    val sum: Int
        get() = 10 + 20

    fun evaluateELProcessor() {
        val elProcessor: ELProcessor = ELProcessor()
        try {
            // ruleid: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationELPResult = elProcessor.eval(userInputELProcessor)

            // ok: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationELPResult = elProcessor.eval("2*2")
        } catch (e: Exception) {
            evaluationELPResult = "Error: " + e.message
        }
    }

    fun evaluateELProcessorGetValue() {
        val elProcessor: ELProcessor = ELProcessor()
        try {
            // ruleid: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationELPGetValue = elProcessor.getValue(userInputELProcessorGV, Any::class.java)

            // ok: android.gitlab.kotlin_inject_rule-ELInjection
            evaluationELPGetValue = elProcessor.getValue("2+2", Any::class.java)
        } catch (e: Exception) {
            evaluationELPGetValue = "Error in getValue: " + e.message
        }
    }

    fun evaluateELProcessorSetValue() {
        val elProcessor: ELProcessor = ELProcessor()
        try {
            // Define 'elInjectionBean' within ELProcessor's context
            elProcessor.defineBean("elInjectionBean", this)

            // ruleid: android.gitlab.kotlin_inject_rule-ELInjection
            elProcessor.setValue(userInputELProcessorSV, inputValueToSet)
            evaluationELPSetValue = "Expression : $userInputELProcessorSV Value : $inputValueToSet"

            // ok: android.gitlab.kotlin_inject_rule-ELInjection
            elProcessor.setValue("userInputELProcessorSV.privateConfigValue", "inputValueToSet")
        } catch (e: Exception) {
            evaluationELPSetValue = "Error in setValue: " + e.message
        }
    }
}