import pymysql

# 1. 连上 MySQL（此时还不指定数据库）
# ⚠️ 注意：这里请填入你真实的 MySQL 密码
conn = pymysql.connect(host='localhost', user='root', password='123456')
cursor = conn.cursor()

print("成功连接 MySQL，正在创建数据库...")

# 2. 创建数据库
cursor.execute("CREATE DATABASE IF NOT EXISTS pet_adoption;")
cursor.execute("USE pet_adoption;")

# 3. 创建数据表
print("正在创建数据表...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    living_space INT, experience INT,
    time_availability INT, preference_type VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL, species VARCHAR(20),
    age_group INT, health_status INT, activity_level INT,
    is_adopted BOOLEAN DEFAULT FALSE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS adoption_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT, pet_id INT,
    status VARCHAR(20) DEFAULT 'PENDING',
    apply_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pet_id) REFERENCES pets(id)
)
""")

# 4. 插入初始的测试宠物数据
cursor.execute("SELECT COUNT(*) FROM pets")
if cursor.fetchone()[0] == 0:
    print("正在插入测试宠物数据...")
    cursor.execute("""
    INSERT INTO pets (name, species, age_group, health_status, activity_level) VALUES 
    ('旺财', '狗', 2, 5, 5), ('咪咪', '猫', 1, 3, 3), 
    ('大黄', '狗', 3, 1, 1), ('雪球', '猫', 2, 5, 1)
    """)

# 5. 保存并关闭
conn.commit()
conn.close()
print("🎉 太棒了！数据库和测试数据全部初始化完成！")