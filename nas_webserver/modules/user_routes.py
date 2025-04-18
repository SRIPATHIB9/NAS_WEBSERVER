from flask import Blueprint, request, jsonify, session, current_app
from modules.auth_middleware import login_required

user_bp = Blueprint('user', __name__)

def get_db_cursor():
    conn = current_app.extensions['mysql'].connection
    cur = conn.cursor()
    cur.execute("USE nas_webserver;")  # Ensure correct DB selected
    return cur

@user_bp.route('/user/list', methods=['GET'])
@login_required(role='admin')
def list_users():
    cur = get_db_cursor()
    cur.execute("SELECT username FROM users")
    users = cur.fetchall()
    cur.close()
    return jsonify([u[0] for u in users])


# ------------------ Register User ------------------
@user_bp.route('/user/register', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = data['password']  # plain text
    role = data.get('role', 'read')

    cur = get_db_cursor()

    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    if cur.fetchone():
        return jsonify({'message': 'Username already exists'}), 409

    cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role))
    current_app.extensions['mysql'].connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully'}), 201

# ------------------ Create User (admin only) ------------------
@user_bp.route('/user/create', methods=['POST'])
@login_required(role='admin')
def create_user():
    data = request.json
    username = data['username']
    password = data['password']  # plain text
    role = data['role']

    cur = get_db_cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    if cur.fetchone():
        return jsonify({'message': 'Username already exists'}), 409

    cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role))
    current_app.extensions['mysql'].connection.commit()
    cur.close()

    return jsonify({'message': 'User created successfully'}), 201

@user_bp.route('/user/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        print("📥 Login Attempt:", username, password)

        cur = get_db_cursor()  # ✅ Uses shared helper (DB already selected)
        print("✅ Cursor ready and DB selected")

        query = "SELECT password, role FROM users WHERE username = %s"
        print("🔍 Executing:", query, [username])
        cur.execute(query, [username])
        user = cur.fetchone()
        print("📤 DB Response:", user)

        cur.close()

        if user and user[0] == password:
            print("✅ Password match")
            session['username'] = username
            session['role'] = user[1]
            return jsonify({'message': 'Login successful'}), 200

        print("❌ Invalid credentials")
        return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        print("🔥 LOGIN ERROR:", str(e))
        return jsonify({'message': 'Internal server error'}), 500


# ------------------ Logout ------------------
from flask import redirect, url_for

@user_bp.route('/user/logout', methods=['GET'])
@login_required()
def logout():
    session.clear()
    return redirect(url_for('login'))  # ✅ redirect to login page after logout


# ------------------ Edit User (admin only) ------------------
@user_bp.route('/user/edit', methods=['PUT'])
@login_required(role='admin')
def edit_user():
    data = request.json
    username = data['username']
    new_password = data.get('password')
    new_role = data.get('role')

    cur = get_db_cursor()

    if new_password:
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
    if new_role:
        cur.execute("UPDATE users SET role = %s WHERE username = %s", (new_role, username))

    current_app.extensions['mysql'].connection.commit()
    cur.close()

    return jsonify({'message': 'User updated successfully'}), 200

# ------------------ Delete User (admin only) ------------------
@user_bp.route('/user/delete', methods=['DELETE'])
@login_required(role='admin')
def delete_user():
    data = request.json
    username = data['username']

    cur = get_db_cursor()

    cur.execute("DELETE FROM users WHERE username = %s", [username])
    current_app.extensions['mysql'].connection.commit()
    cur.close()

    return jsonify({'message': 'User deleted successfully'}), 200

