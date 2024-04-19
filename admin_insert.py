from flask_bcrypt import generate_password_hash, Bcrypt
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  
db = client['project2']  
admins_collection = db['admins']

password = '12345'
password_hash = generate_password_hash(password, rounds=12).decode('utf-8')
admin_data = {
    'email': 'admin@example.com',
    'passwordHash': password_hash
}

# Вставка данных в коллекцию "admins"
result = admins_collection.insert_one(admin_data)

# Вывод результата
print(f'Inserted admin with id: {result.inserted_id}')