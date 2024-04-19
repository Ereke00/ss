import dropbox
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)
access_token = 'sl.BtTPRMaCgQ8Lwg9K2GZG-sLL4bBCDguYQWAIoXuLjXPSPZxvZ9aYNY560i3Tu2xWXQgQiUVEh_fWwG4yinQyU_AfhZ1R9ZGpzOPDAlaBJ6yGVqDgRd_i_cb1xzlZlFhqUGgniKUjBn8vQqs'
dbx = dropbox.Dropbox(access_token)

client = MongoClient('mongodb://localhost:27017/')  # Подставьте вашу строку подключения
db = client['project2']  # Замените 'your_database_name' на имя вашей БД
collection = db['ss_works']


@app.route('/files')
def get_files():
    try:
        
        files_list = dbx.files_list_folder('')
        files = [file_entry.name for file_entry in files_list.entries]
        return jsonify(files)
    except dropbox.exceptions.ApiError as e:
        return f'Ошибка при запросе списка файлов: {e}', 500


@app.route('/upload', methods=['POST'])
def upload_file():
    # Получаем текстовые данные из запроса
    work_name = request.form.get('workName')
    work_topic = request.form.get('workTopic')
    work_description = request.form.get('workDescription')

    # Сохраняем текстовые данные в MongoDB
    document = {
        'workName': work_name,
        'workTopic': work_topic,
        'workDescription': work_description
    }
    collection.insert_one(document)

    # Получаем файл из запроса
    file = request.files['file']

    if file.filename == '':
        return 'Файл не выбран', 400

    try:
        # Сохраняем файл на сервере (необязательно)
        file.save(file.filename)

        # Отправляем файл в Dropbox
        with open(file.filename, 'rb') as f:
            # Загружаем файл в Dropbox
            dbx.files_upload(f.read(), f'/{file.filename}')

            # Получаем ссылку на загруженный файл в Dropbox
            shared_link = dbx.sharing_create_shared_link(f'/{file.filename}').url
            # Добавляем ссылку на файл в документ в MongoDB
            collection.update_one({'workName': work_name}, {'$set': {'fileLink': shared_link}})

        return 'Файл успешно загружен в Dropbox'
    except Exception as e:
        return f'Ошибка при загрузке файла: {e}', 500


if __name__ == '__main__':
    app.run(debug=True,port=5000)
