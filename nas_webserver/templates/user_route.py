@user_bp.route('/user/register', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = generate_password_hash(data['password'])
    role = data.get('role', 'read')

    cur = current_app.extensions['mysql'].connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [username])
    if cur.fetchone():
        return jsonify({'message': 'Username already exists'}), 409

    cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password, role))
    current_app.extensions['mysql'].connection.commit()
    cur.close()

    return jsonify({'message': 'User registered successfully'}), 201
