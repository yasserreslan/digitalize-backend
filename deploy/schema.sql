-- users database schema
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    user_type VARCHAR(10) CHECK (user_type IN ('normal', 'admin')) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_id TEXT,
    device_type VARCHAR(50),
    user_id INT NOT NULL,
    status VARCHAR(100),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE admin_action_log (
    action_id SERIAL PRIMARY KEY,
    admin_user_id INT NOT NULL,
    action_type VARCHAR(100),
    action_description TEXT,
    action_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_user_id) REFERENCES users(user_id)
);

CREATE TABLE system_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_name VARCHAR(100) UNIQUE NOT NULL,
    setting_value VARCHAR(255) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- settings needed
INSERT INTO system_settings (setting_name, setting_value) VALUES ('user_registration', 'active');

INSERT INTO system_settings (setting_name, setting_value) VALUES ('daily_registration_limit', '100');




