from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret key'

# ---------Connect to Neo4j-----------:
def connect():
    uri = 'bolt://localhost:7687'
    driver = GraphDatabase.driver(uri, auth=("neo4j", "11223344"))
    session = driver.session()
    return session

# ------Get dept info ------:
Dept_Info_query = "match(e:Employee)-[r:WORKS_IN]->(d:Department) return e,r,d order by e.id limit 10"
Manages_Info_query = "match(e:Employee)-[r:MANAGES]->(e2:Employee) return e,r,e2 order by e limit 10"
heads_query = "match(e:Employee)-[r:HEADS]->(d:Department) return e,r,d "


@app.route('/')
def index():
    Dept_Info_query = "match(e:Employee)-[r:WORKS_IN]->(d:Department) return e,r,d order by e.id limit 10"
    sess = connect()
    all_data = sess.run(Dept_Info_query)
    return render_template("index.html", all_data=all_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    sess = connect()
    if request.method == 'POST':
        id = request.form['search_query']
        if id == '':
            return redirect(url_for('index'))
        else:
            Saerch_Query = 'match(e:Employee{id:$id})-[r:WORKS_IN]->(d:Department) return e,r,d'

            all_data = sess.run(Saerch_Query, parameters={'id': int(id)})

            if all_data.data():
                flash("Employee found", "success")
                all_data = sess.run(Saerch_Query, parameters={'id': int(id)})
                return render_template("index.html", all_data=all_data)
            else:
                flash("Employee NOT found", "warning")
                return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        id = request.form['id']
        join = request.form['join']
        name = request.form['name']
        born = request.form['born']
        salary = request.form['salary']
        desig = request.form['desig']
        perfRat = request.form['perfRat']
        department = request.form['department']
        add_EMP_Query = 'match(d: Department{name:$department})' \
                        'create(e:Employee{id:$id,name: $name, born: $born, joined: $join,' \
                        'designation: $desig,salary: $salary, PerfRating: $perfRat })-[r: WORKS_IN]->(d)'
        sess = connect()
        transaction = sess.begin_transaction()
        flag = False
        try:
            transaction.run(add_EMP_Query,
                            parameters={'id': int(id), 'name': name, 'born': born, 'join': join, 'desig': desig,
                                        'salary': salary,
                                        'perfRat': perfRat, 'department': department})
            flag = True
        except Exception as e:
            print(e)
        finally:
            if flag:
                transaction.commit()
                flash("Employee added", "success")
            else:
                transaction.rollback()
                flash("Employee not added", "warning")
        return redirect(url_for('index'))


@app.route('/modifier', methods=['GET', 'POST'])
def modifier():
    if request.method == 'POST':
        id = request.form['id']
        joined = request.form['join']
        name = request.form['name']
        born = request.form['born']
        salary = request.form['salary']
        desig = request.form['desig']
        perfRat = request.form['perfRat']
        department = request.form['department']
        # delete the relationship
        relation_Que = " match(e:Employee{id:$id})-[r:WORKS_IN]->(d:Department) delete r"
        sess1 = connect()
        transaction1 = sess1.begin_transaction()
        transaction1.run(relation_Que, parameters={'id': int(id)})
        transaction1.commit()
        update_query = 'match(e:Employee{id:$id}),(d:Department{name:$deptName}) set e.name=$name, ' \
                       'e.born=$born, e.joined=$joined, ' \
                       'e.designation=$desig, e.salary=$salary, e.PerfRating=$perfRat create(e)-[r:WORKS_IN]->(d)'

        sess = connect()
        transaction = sess.begin_transaction()
        flag = False
        try:
            print(salary)
            transaction.run(update_query,
                            parameters={'id': int(id), 'name': name, 'born': born, 'joined': joined, 'desig': desig,
                                        'salary': salary,
                                        'perfRat': perfRat, 'deptName': department})
            flag = True
        except Exception as e:
            print(e)
        finally:
            if flag:
                transaction.commit()
                flash("Employee modified", "success")
            else:
                transaction.rollback()
                flash("Employee NOT modified", "warning")

        return redirect(url_for('index'))


@app.route('/supprimer/<id>/', methods=['GET', 'POST'])
def supprimer(id):
    delete_query = 'match(e:Employee{id:$id}) detach delete e'
    sess = connect()
    transaction = sess.begin_transaction()
    flag = False
    try:
        transaction.run(delete_query,
                        parameters={'id': int(id)})
        flag = True
    except Exception as e:
        print(e)
    finally:
        if flag:
            transaction.commit()
            flash("Employee deleted !!", "success")
        else:
            transaction.rollback()
            flash("Employee NOT deleted !!", "warning")
    return redirect(url_for('index'))


@app.route('/modifier1', methods=['GET', 'POST'])
def modifier_manager():
    if request.method == 'POST':
        id = request.form['id']
        joined = request.form['join']
        name = request.form['name']
        born = request.form['born']
        salary = request.form['salary']
        desig = request.form['desig']
        perfRat = request.form['perfRat']
        id_E = request.form['id_E']
        name_E = request.form['name_E']

        # delete the relationship
        relation_Que = " match(e:Employee{id:$id})-[r:MANAGES]->(e2:Employee) delete r"
        sess1 = connect()
        transaction1 = sess1.begin_transaction()
        transaction1.run(relation_Que, parameters={'id': int(id)})
        transaction1.commit()
        update_query = 'match(e:Employee{id:$id}),(e2:Employee{id:$id_E}) set e.name=$name, ' \
                       'e.born=$born, e.joined=$joined, ' \
                       'e.designation=$desig, e.salary=$salary, e.PerfRating=$perfRat create(e)-[r:MANAGES]->(e2)'

        sess = connect()
        transaction = sess.begin_transaction()
        flag = False
        try:

            transaction.run(update_query,
                            parameters={'id': int(id), 'name': name, 'born': born, 'joined': joined, 'desig': desig,
                                        'salary': salary,
                                        'perfRat': perfRat, 'id_E': int(id_E)})
            flag = True
        except Exception as e:
            print(e)
        finally:
            if flag:
                transaction.commit()
                flash("Employee modified", "success")
            else:
                transaction.rollback()
                flash("Employee NOT modified", "warning")
        return redirect(url_for('managers'))


@app.route('/manager_search', methods=['GET', 'POST'])
def manager_search():
    sess = connect()
    if request.method == 'POST':
        id = request.form['search_query']
        if id == '':
            return redirect(url_for('managers'))
        else:
            Saerch_Query = 'match(e:Employee{id:$id})-[r:MANAGES]->(e2:Employee) return e,r,e2'
            manages_data = sess.run(Saerch_Query, parameters={'id': int(id)})

            if manages_data.data():
                flash("Manager found", "success")
                manages_data = sess.run(Saerch_Query, parameters={'id': int(id)})
                return render_template("manager.html", manages_data=manages_data)
            else:
                flash("Manager NOT found", "warning")
                return render_template("manager.html")


@app.route('/supprimer1/<id>/', methods=['GET', 'POST'])
def supprimer_manager(id):
    delete_query = 'match(e:Employee{id:$id}) detach delete e'
    sess = connect()
    transaction = sess.begin_transaction()
    flag = False
    try:
        transaction.run(delete_query, parameters={'id': int(id)})
        flag = True
    except Exception as e:
        print(e)
    finally:
        if flag:
            transaction.commit()
            flash("Manager deleted !!", "success")
        else:
            transaction.rollback()
            flash("Manager NOT deleted !!", "warning")
    return redirect(url_for('managers'))


@app.route('/managers')
def managers():
    sess = connect()
    manages_data = sess.run(Manages_Info_query)
    return render_template('manager.html',manages_data=manages_data)

@app.route('/headers')
def headers():
    heads_query = "match(e:Employee)-[r:HEADS]->(d:Department) return e,r,d "
    sess = connect()
    heads_data = sess.run(heads_query)
    return render_template('headers.html', heads_data = heads_data)


@app.route('/modifier2', methods=['GET', 'POST'])
def modifier_header():
    if request.method == 'POST':
        id_h = request.form['id']
        joined_h = request.form['join']
        name_h = request.form['name']
        born_h = request.form['born']
        salary_h = request.form['salary']
        desig_h = request.form['desig']
        perfRat_h = request.form['perfRat']
        name_D = request.form['department']
        #"match(e:Employee)-[r:HEADS]->(d:Department) return e,r,d "
        # delete the relationship
        relation_Que = " match(e:Employee{id:$id})-[r:HEADS]->(d:Department) delete r"
        sess1 = connect()
        transaction1 = sess1.begin_transaction()
        transaction1.run(relation_Que, parameters={'id': int(id_h)})
        transaction1.commit()
        update_query = 'match(e:Employee{id:$id}),(d:Department{name:$name_D}) set e.name=$name, ' \
                       'e.born=$born, e.joined=$joined, ' \
                       'e.designation=$desig, e.salary=$salary, e.PerfRating=$perfRat create(e)-[r:HEADS]->(d)'

        sess = connect()
        transaction = sess.begin_transaction()
        flag = False
        try:

            transaction.run(update_query,
                            parameters={'id': int(id_h), 'name': name_h, 'born': born_h, 'joined': joined_h, 'desig': desig_h,
                                        'salary': salary_h,
                                        'perfRat': perfRat_h, 'name_D': name_D})
            flag = True
        except Exception as e:
            print(e)
        finally:
            if flag:
                transaction.commit()
                flash("Employee modified", "success")
            else:
                transaction.rollback()
                flash("Employee NOT modified", "warning")
        return redirect(url_for('headers'))


@app.route('/supprimer2/<id>/', methods=['GET', 'POST'])
def supprimer_header(id):
    delete_query = 'match(e:Employee{id:$id}) detach delete e'
    sess = connect()
    transaction = sess.begin_transaction()
    flag = False
    try:
        transaction.run(delete_query, parameters={'id': int(id)})
        flag = True
    except Exception as e:
        print(e)
    finally:
        if flag:
            transaction.commit()
            flash("Header deleted !!", "success")
        else:
            transaction.rollback()
            flash("Header NOT deleted !!", "warning")
    return redirect(url_for('headers'))

if __name__ == "__main__":
    app.run(debug=True, port=8001)
