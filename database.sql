CREATE DATABASE IF NOT EXISTS pet_adoption;
USE pet_adoption;

-- 用户/领养人表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    living_space INT,        -- 居住空间量化 (如：1小, 2中, 3大)
    experience INT,          -- 饲养经验 (0无, 1有)
    time_availability INT,   -- 陪伴时间评分 (1-5)
    preference_type VARCHAR(50) -- 偏好宠物类型 (狗/猫)
);

-- 宠物表
CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    species VARCHAR(20),     -- 种类 (狗/猫)
    age_group INT,           -- 年龄段 (1幼年, 2成年, 3老年)
    health_status INT,       -- 健康状况评分 (1-5)
    activity_level INT,      -- 活跃度/性格特征 (1-5)
    is_adopted BOOLEAN DEFAULT FALSE
);

-- 领养申请流转表
CREATE TABLE adoption_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    pet_id INT,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
    apply_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);