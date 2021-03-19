import flask
from neo4j import GraphDatabase

HOST = '127.0.0.1'
PORT = 5000


def ws_create():
    ws = flask.Flask(__name__)
    db = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "skillz"))

    @ws.route('/')
    def root():
        return 'Welcome to the Neo4j SkillNet Web Server'

    def get_courses(tx, q):
        query = "MATCH (s:Course) " + \
                "WHERE toLower(s.name) STARTS WITH toLower($q) " + \
                "RETURN s"
        result = tx.run(query, q=q)
        result = [row["s"]["name"] for row in result]
        return result

    @ws.route('/getCourses', methods=['GET'])
    def get_courses_execute():
        q = flask.request.args.get('q', '')
        with db.session() as session:
            result = session.read_transaction(get_courses, q)
        session.close()

        return flask.jsonify(result)

    def get_skills(tx, q):
        query = "MATCH (s:Skill) " + \
                "WHERE toLower(s.name) STARTS WITH toLower($q) " + \
                "RETURN s"
        result = tx.run(query, q=q)
        result = [row["s"]["name"] for row in result]
        return result

    @ws.route('/getSkills', methods=['GET'])
    def get_skills_execute():
        q = flask.request.args.get('q', '')
        with db.session() as session:
            result = session.read_transaction(get_skills, q)
        session.close()

        return flask.jsonify(result)

    def get_courses_and_skills(tx, q):
        query = "MATCH (s:Skill) " + \
                "WHERE toLower(s.name) STARTS WITH toLower($q) " + \
                "RETURN s " + \
                "UNION " + \
                "MATCH (s:Course) " + \
                "WHERE toLower(s.name) STARTS WITH toLower($q) " + \
                "RETURN s"
        result = tx.run(query, q=q)
        result = [row["s"]["name"] for row in result]
        return result

    @ws.route('/getCoursesAndSkills', methods=['GET'])
    def get_courses_and_skills_execute():
        q = flask.request.args.get('q', '')
        with db.session() as session:
            result = session.read_transaction(get_courses_and_skills, q)
        session.close()

        return flask.jsonify(result)

    def create_skill(tx, name):
        query = "CREATE (s:Skill {name: $name}) " + \
                "RETURN s"
        result = tx.run(query, name=name)
        result = [row["s"]["name"] for row in result]
        return result

    @ws.route('/createSkill', methods=['POST'])
    def create_skill_execute():
        name = flask.request.form.get('name', '')
        with db.session() as session:
            result = session.write_transaction(create_skill, name)
        session.close()

        return result

    def create_course(tx, name):
        query = "CREATE (c:Course {name: $name}) " + \
                "RETURN c"
        result = tx.run(query, name=name)
        result = [row["c"]["name"] for row in result]
        return flask.jsonify(result)

    @ws.route('/createCourse', methods=['POST'])
    def create_course_execute():
        name = flask.request.form.get('name', '')
        with db.session() as session:
            result = session.write_transaction(create_course, name)
        session.close()
        return flask.jsonify(result)

    def create_relation(tx, from_node, to_node):
        query = "MATCH (n1 {name: $from_node})," \
                      "(n2 {name: $to_node}) " \
                "create (n1)-[:RELATED_TO]->(n2) "
        tx.run(query, from_node=from_node, to_node=to_node)

    @ws.route('/createRelation', methods=['POST'])
    def create_relation_execute():
        from_node = flask.request.form.get('name1')
        to_node = flask.request.form.get('name2')
        with db.session() as session:
            session.write_transaction(create_relation, from_node, to_node)
        session.close()

        return '', 200

    def get_related_courses(tx, name):
        query = "MATCH (s:Skill)-[RELATED_TO]->(c:Course) " \
                "WHERE toLower(s.name) = toLower($name) " \
                "RETURN c"
        result = tx.run(query, name=name)
        result = [row["c"]["name"] for row in result]
        return result

    @ws.route('/getRelatedCourses', methods=['GET'])
    def get_related_courses_execute():
        skill = flask.request.args.get('skill', '')
        with db.session() as session:
            result = session.read_transaction(get_related_courses, skill)
        session.close()

        return flask.jsonify(result)

    return ws


if __name__ == '__main__':
    app = ws_create()
    app.run(host=HOST, port=PORT)
