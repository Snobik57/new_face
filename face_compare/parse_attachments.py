import os

import aiohttp
import aiofiles
import asyncio

from time import sleep
from datetime import datetime
from aiohttp import ClientTimeout

from models.ch_db import DataBaseChORM
from recognition_func import get_image_embedding

BASE_PATH = os.getcwd()

HEADERS = {
    'app_code_name': 'Mozilla',
    'app_name': 'Netscape',
    'app_version': '5.0 (X11)',
    'build_id': '20160923071037',
    'build_version': '49.0',
    'navigator_id': 'firefox',
    'os_id': 'linux',
    'oscpu': 'Linux x86_64',
    'platform': 'X11; Ubuntu; Linux x86_64',
    'product': 'Gecko',
    'product_sub': '20100101',
    'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) '
               'Gecko/20100101 Firefox/49.0',
    'vendor': '',
    'vendor_sub': '',
    'Connection': 'Upgrade',
    'Upgrade': 'HTTP/1.1',
}

DATABASE = DataBaseChORM()


async def task_formation(session, attachment: str, attachment_id: int, timer: int = 10, width: int = 1080) -> None:
    """
    Отправляет get-запрос по-указанному url.
    Проверяет полученный ответ на наличии в контенте изображения.
    Скачивает изображение.
    Конвертирует изображение в 128-мерный эмбеддинг (128-мерный массив из векторов).
    Загружает данные в БД.
    Удаляет изображение.

    На get-запрос установленно ограничение соединения (по времени) 10 секунд,
    чтобы избежать появления исключения aiohttp.ClientOSError. (если не использовать, то ожидание увеличится).
    Тем самым генерируется исключение aiohttp.ServerTimeoutError, которое обрабатывается и добавляет данные в БД.

    :param width: Параметр для сохранения фотографий в определенном формате.
                  Необходим для распределения ресурсов GPU.
    :param timer: Параметр для регулирования ожидания ответа от URL. По-умолчанию - 10 секунд
    :param session: сессия HTTP-запросов (aiohttp.ClientSession).
    :param attachment: url-адрес на изображение.
    :param attachment_id: id url-адреса.
    :return: None
    """
    try:
        # TODO: Нужно разобраться с прокси
        async with session.get(
                url=str(attachment),
                timeout=ClientTimeout(total=None, sock_connect=timer, sock_read=timer),
                headers=HEADERS,
                # proxy='http://193.0.202.46:10010',
                # proxy_auth=aiohttp.BasicAuth(login='WvUIrGfT', password='vpb6vM3V'),
        ) as response:

            if response.status in [200, 201, 202] and response.content_type.split('/')[0] == 'image':
                extension = response.content_type.split('/')[1]
                if extension in ['jpeg', 'jpg', 'png']:
                    path = f'inter_folder/img_{attachment_id}.{extension}'
                    async with aiofiles.open(path, 'wb') as f:
                        await f.write(await response.read())

                        image_embedding = get_image_embedding(path, width=width)
                        if not image_embedding:
                            print(f"[INFO] {attachment_id} - connect = TRUE, face = FALSE")
                            DATABASE.insert_in_attachments_embedding(
                                attachment_id=attachment_id,
                                face_available=0,
                                connect_available=1,
                                embedding=[],
                                timestamp=datetime.now(),
                            )
                        for embedding in image_embedding:
                            print(f"[INFO] {attachment_id} - connect = TRUE, face = TRUE")
                            DATABASE.insert_in_attachments_embedding(
                                attachment_id=attachment_id,
                                face_available=1,
                                connect_available=1,
                                embedding=embedding,
                                timestamp=datetime.now(),
                            )

                        os.remove(path)

            else:
                print(f"[INFO] {attachment_id} - connect = TRUE, face = FALSE")
                DATABASE.insert_in_attachments_embedding(
                    attachment_id=attachment_id,
                    face_available=0,
                    connect_available=1,
                    embedding=[],
                    timestamp=datetime.now(),
                )

    except aiohttp.ClientOSError:
        print(f"[INFO] {attachment_id} - aiohttp.ClientOSError")
        DATABASE.insert_in_attachments_embedding(
            attachment_id=attachment_id,
            face_available=0,
            connect_available=0,
            embedding=[],
            timestamp=datetime.now(),
        )

    except aiohttp.ServerTimeoutError:
        print(f"[INFO] {attachment_id} - aiohttp.ServerTimeoutError")
        DATABASE.insert_in_attachments_embedding(
            attachment_id=attachment_id,
            face_available=0,
            connect_available=0,
            embedding=[],
            timestamp=datetime.now(),
        )


async def downloads_image(timer: int = 10, width: int = 1080) -> tuple:
    """
    Формирует сессию HTTP-запросов.
    В ней создает список задач (get-запросов) для асинхронного выполнения.

    :param width: Параметр для сохранения фотографий в определенном формате.
                  Необходим для распределения ресурсов GPU.
    :param timer: Параметр для регулирования ожидания ответа от URL. По-умолчанию - 10 секунд

    :return: возвращает список результатов выполнения задач (функций с get-запросами)
    """

    db_list_of_links = DATABASE.select_all_attachments()
    print(f"[INFO] COUNT: attachments - {len(db_list_of_links)}")

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:

        tasks = []
        for element in db_list_of_links:

            attachment = element[1]
            attachment_id = element[0]
            task = asyncio.create_task(task_formation(session, attachment, attachment_id, timer=timer, width=width))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        return results


if __name__ == '__main__':
    pass