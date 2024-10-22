from flask import Flask, request, render_template
from py2neo import Graph, Node, NodeMatcher, Relationship

app = Flask(__name__)

graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo4j1234"))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    role = request.form.get('role', 'User')  
    matcher = NodeMatcher(graph)
    existing_user = matcher.match("User", username=username).first()

    if existing_user:
        return '''
        <h3>Username already exists, please choose another.</h3>
        <form action="/">
            <input type="submit" value="Back to Form">
        </form>
        ''', 400

    if role == 'Admin':
        user_node = Node("Admin", username=username, password=password)
    else:
        user_node = Node("User", username=username, password=password)

    graph.create(user_node)

    if role == 'Admin':
        #Administers relationship: (Admin)-[:ADMINISTERS]->(User)
        users = list(matcher.match("User")) 
        for user in users:
            rel = Relationship(user_node, "ADMINISTERS", user)
            graph.create(rel)

    return f'''
    <h3>{role} {username} registered successfully!</h3>
    <form action="/">
        <input type="submit" value="Back to Form">
    </form>
    '''

@app.route('/delete', methods=['POST'])
def delete_user():
    username = request.form['del_username']
    password = request.form['del_password']
    matcher = NodeMatcher(graph)
    user_node = matcher.match("User", username=username, password=password).first()

    if not user_node:
        return '''
        <h3>User not found or incorrect password!</h3>
        <form action="/">
            <input type="submit" value="Back to Form">
        </form>
        ''', 400

    graph.delete(user_node)

    return f'''
    <h3>User {username} deleted successfully!</h3>
    <form action="/">
        <input type="submit" value="Back to Form">
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5001)
