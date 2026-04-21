from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import pymysql
import pandas as pd
from algorithms.cf_recommender import generate_recommendations

app = Flask(__name__)
# 设置安全密钥，用于加密登录状态
app.secret_key = 'pet_adoption_super_secret_key'

def get_db_connection():
    # 🚨 请修改为你本地的 MySQL 密码
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456', 
        database='pet_adoption',
        cursorclass=pymysql.cursors.DictCursor
    )

# ================= 1. 用户端模块 =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    user_data = request.json
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM pets WHERE is_adopted = 0")
            pets_raw = cursor.fetchall()
        conn.close()
        
        if not pets_raw:
            return jsonify({"message": "目前没有待领养的宠物"}), 404
            
        pets_df = pd.DataFrame(pets_raw)
        recommendations = generate_recommendations(user_data, pets_df)
        
        return jsonify({"status": "success", "data": recommendations[:5]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/apply', methods=['POST'])
def submit_application():
    data = request.json
    user_id = data.get('user_id')
    pet_id = data.get('pet_id')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO users (id, username) VALUES (%s, '临时用户')", (user_id,))
            sql = "INSERT INTO adoption_applications (user_id, pet_id) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, pet_id))
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "申请已提交，等待机构审核"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ================= 2. 登录验证模块 =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '123456':
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
        else:
            error = '用户名或密码错误，请重试！'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# ================= 3. 后台管理员模块 =================

@app.route('/admin')
def admin_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/api/applications', methods=['GET'])
def get_applications():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT a.id, u.username, p.name as pet_name, p.species, a.status, a.apply_date
                FROM adoption_applications a
                JOIN users u ON a.user_id = u.id
                JOIN pets p ON a.pet_id = p.id
                ORDER BY a.apply_date DESC
            """
            cursor.execute(sql)
            apps = cursor.fetchall()
        conn.close()
        return jsonify({"status": "success", "data": apps})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    data = request.json
    new_status = data.get('status')
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE adoption_applications SET status = %s WHERE id = %s", (new_status, app_id))
            if new_status == 'APPROVED':
                cursor.execute("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,))
                result = cursor.fetchone()
                if result:
                    cursor.execute("UPDATE pets SET is_adopted = 1 WHERE id = %s", (result['pet_id'],))
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "申请已处理"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/pets', methods=['POST'])
def add_pet():
    data = request.json
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 已修复为 MySQL 专属的 %s 占位符
            sql = """
                INSERT INTO pets (name, species, age_group, health_status, activity_level) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('name'), data.get('species'), data.get('age_group'), 
                data.get('health_status'), data.get('activity_level')
            ))
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "🎉 新宠物上架成功！"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)