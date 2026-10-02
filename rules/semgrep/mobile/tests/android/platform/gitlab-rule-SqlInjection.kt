// License: LGPL-3.0 License (c) find-sec-bugs
package inject

import io.vertx.sqlclient.SqlClient
import io.vertx.sqlclient.SqlConnection
import java.sql.PreparedStatement
import java.sql.SQLException
import java.sql.Statement
import javax.jdo.Extent
import javax.jdo.JDOHelper
import javax.jdo.PersistenceManager
import javax.jdo.PersistenceManagerFactory
import javax.persistence.criteria.CriteriaBuilder
import javax.persistence.criteria.CriteriaQuery
import org.hibernate.Criteria
import org.hibernate.Session
import org.hibernate.SessionFactory
import org.hibernate.criterion.Restrictions
import org.hibernate.type.StandardBasicTypes
import org.hibernate.type.Type
import org.jdbi.v3.core.statement.PreparedBatch
import org.jdbi.v3.core.statement.Script
import org.jdbi.v3.core.statement.Update
import org.springframework.jdbc.core.JdbcTemplate

@Suppress("DEPRECATION", "UNUSED_VARIABLE")
class SqlInjection(private val jdbcTemplate: JdbcTemplate) {
    inner class UserEntity {
        var id: Long? = null
        var test: String? = null
    }

    fun testJdoQueries(input: String) {
        val pm: PersistenceManager = pM

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery("select * from Users where name = " + input)

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery("sql", "select * from Products where name = " + input)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery("select * from Config")

        val query = "select * from Config"
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(query)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery("sql", query)
    }

    fun testJdoQueriesAdditionalMethodSig(input: String) {
        val pm: PersistenceManager = pM

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(UserEntity::class.java, ArrayList<UserEntity>(), "id == " + input)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(UserEntity::class.java, ArrayList<UserEntity>(), "id == 1")

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(UserEntity::class.java, "id == " + input)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(UserEntity::class.java, "id == 1")

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(null as Extent<UserEntity>?, "id == " + input)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        pm.newQuery(null as Extent<UserEntity>?, "id == 1")
    }

    fun testHibernate(sessionFactory: SessionFactory, input: String) {
        val session: Session = sessionFactory.openSession()
        val instring = String.format("%s", input)

        val cb: CriteriaBuilder = session.getCriteriaBuilder()
        val query: CriteriaQuery<Any>? = null

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        session.createQuery(query)

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        session.createQuery(instring)

        val cq: CriteriaQuery<Any> = cb.createQuery(Any::class.java)
        val criteria: Criteria = session.createCriteria(UserEntity::class.java)

        // The following would need to be audited

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        criteria.add(Restrictions.sqlRestriction("test=1234" + instring))

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        session.createQuery("select t from UserEntity t where id = " + instring)

        // More sqlRestriction signatures

        criteria.add(
                Restrictions.sqlRestriction(
                        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
                        "param1  = ? and param2 = " + instring,
                        instring,
                        StandardBasicTypes.STRING
                )
        )
        criteria.add(
                Restrictions.sqlRestriction(
                        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
                        "param1  = ? and param2 = " + instring,
                        arrayOf<String>(instring),
                        arrayOf<Type>(StandardBasicTypes.STRING)
                )
        )

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        criteria.add(Restrictions.sqlRestriction("test=1234"))

        val localSafe = "where id=1337"

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        session.createQuery("select t from UserEntity t " + localSafe)

        val localSql = "select * from TestEntity " + localSafe
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        session.createSQLQuery(localSql)

        // More sqlRestriction signatures (with safe binding)

        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        criteria.add(
                Restrictions.sqlRestriction("param1  = ?", instring, StandardBasicTypes.STRING)
        )
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        criteria.add(
                Restrictions.sqlRestriction(
                        "param1  = ? and param2 = ?",
                        arrayOf<String>(instring),
                        arrayOf<Type>(StandardBasicTypes.STRING)
                )
        )
    }

    fun testVertx(conn: SqlConnection, client: SqlClient, injection: String) {
        // true positives
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        client.query(injection)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        client.preparedQuery(injection)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        conn.prepare(injection)

        val constantValue = "SELECT * FROM test"
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        client.query(constantValue)
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        conn.query(constantValue)
    }

    @Throws(SQLException::class)
    fun testPreparedStmt(stmt: PreparedStatement, input: String) {
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute("select * from users where email = " + input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute("select * from users where email = " + input, Statement.RETURN_GENERATED_KEYS)
        stmt.execute(
                // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
                "select * from users where email = " + input,
                intArrayOf(Statement.RETURN_GENERATED_KEYS)
        )
        stmt.execute(
                // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
                "select * from users where email = " + input,
                intArrayOf(Statement.RETURN_GENERATED_KEYS)
        )
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.executeQuery("select * from users where email = " + input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.executeQuery("select * from users where email = '" + input + "' AND name != NULL")
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.executeUpdate("update from users set email = '" + input + "' where name != NULL")
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.executeLargeUpdate("update from users set email = '" + input + "' where name != NULL")
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.addBatch("update from users set email = '" + input + "' where name != NULL")
    }

    fun good(clientDetails: String) {
        val statementUsingConstants =
                ("insert into oauth_client_details (" +
                        CLIENT_FIELDS +
                        ")" +
                        "values (?,?,?,?,?,?,?,?,?,?,?)")
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        jdbcTemplate.update(statementUsingConstants, clientDetails)
    }

    fun good2(clientDetails: String) {
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        jdbcTemplate.update(DEFAULT_INSERT_STATEMENT, clientDetails)
    }

    fun bad(clientDetails: String) {
        val stmtUsingFuncParam = "test" + clientDetails + "test"
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        jdbcTemplate.update(stmtUsingFuncParam, clientDetails)
    }

    fun badInline(clientDetails: String) {
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        jdbcTemplate.update("test" + clientDetails + "test", clientDetails)
    }

    // this private method has a single caller passing a constant string => safe
    @Throws(Exception::class)
    private fun goodPrivateMethod(stmt: PreparedStatement?, input: String) {
        // ok: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt!!.execute("select * from users where email = " + input)
    }

    @Throws(Exception::class)
    fun singleCaller() {
        goodPrivateMethod(null, "constant string")
    }

    @Throws(Exception::class)
    fun testPropgators(stmt: PreparedStatement, input: String) {
        val sb1 = StringBuilder(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute("select * from users where email = " + sb1)

        val sb2 = StringBuilder()
        sb2.append(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute("select * from users where email = " + sb2)

        val str = String.format("select * from users where email = %s", input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute(str)

        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        stmt.execute("select * from users where email = " + input)
    }

    @Throws(SQLException::class)
    fun testJDBI(handle: org.jdbi.v3.core.Handle, input: String) {
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.createQuery(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.createScript(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.createUpdate(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.execute(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.prepareBatch(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        handle.select(input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        Script(handle, input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        Update(handle, input)
        // ruleid: android.gitlab.kotlin_inject_rule-SqlInjection
        PreparedBatch(handle, input)
    }

    companion object {
        private const val CLIENT_FIELDS =
                ("client_id, client_secret, resource_ids, scope, " +
                        "authorized_grant_types, web_server_redirect_uri, authorities, access_token_validity, " +
                        "refresh_token_validity, additional_information, autoapprove")

        private const val DEFAULT_INSERT_STATEMENT =
                ("insert into oauth_client_details (" +
                        CLIENT_FIELDS +
                        ")" +
                        "values (?,?,?,?,?,?,?,?,?,?,?)")

        private val pmfInstance: PersistenceManagerFactory =
                JDOHelper.getPersistenceManagerFactory("transactions-optional")

        val pM: PersistenceManager
            get() = pmfInstance.getPersistenceManager()
    }
}