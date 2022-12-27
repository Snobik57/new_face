## ...

### Для корректной работы:

* Необходимо настроить переменные окружения в каталоге /face_compare/models
* Необходимо установить ПО для графического процессора Nvidia CUDA 11.8, cudnn 8.6.0 [инструкция](https://github.com/Snobik57/new_face/blob/tasks/documents/driver-cuda-cudnn-dlib%20install "CUDA")
* Загрузить все библиотеки из requirements.txt
* Удалить библиотеку dlib, которая была зависимостью face-recognition
* Установить библиотеку dlib по [инструкции](https://github.com/Snobik57/new_face/blob/tasks/documents/driver-cuda-cudnn-dlib%20install "CUDA")
* Создаем БД:
```
clickhouse-client --password --query "CREATE DATABASE IF NOT EXISTS recognition"
```
* Запускаем скрипт для создания БД:
```
python3 new_face/face_compare/models/ch_db.py
```

* Необходимо добавить работающий прокси в:
	`new_face/face_compare/parce_attachments.py`
* Запускаем скрипт `face_compare/main.py`
* Далее необходимо забрать данные из БД и передать аналитику.
___

### Алгоритм:
#### main.py
* Забирает аттачменты из внешней БД, скачивает фотографии и видео, распознает на них лица
и заносит данные в таблицу `attachments_embedding`.

*Если аттачмент уже хранится в таблице, то скачивания не произойдет*
* Забирает пути к фотографиям для аналитики из БД, распознает на них лица
и заносит данные в таблицу `analytics_image_embedding`.

*Если ембеддинг уже хранится в БД, то распознавания не произойдет*
* Сравнивает все эмбеддинги аттачментов и фотографий для аналитики. Записывает результат в БД

*Если сравнение с изображением с аттачментом уже было проведено, то повторно не будет.*

---

### Структура БД:

<image src="https://github.com/Snobik57/new_face/blob/single_gpu/image/DB_structure.png" alt="структура БД">
