import os
import aiohttp
import aiofiles
import asyncio

from time import sleep
from aiohttp import ClientTimeout

from models.db_func import DataBaseORM
from recognition.recognition_func import get_image_vector

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
    'Upgrade': 'http/1.1',
}

DATABASE = DataBaseORM()


async def task_formation(session, link: str, counter: int, timer: int = 10, width: int = 1080) -> str:
    """
    Отправляет get-запрос по-указанному url. Проверяет полученный ответ на наличии в контенте изображения.
    Конвертирует изображение в 128-мерный эмбеддинг (128-мерный массив из векторов). Загружает данные в БД.

    На get-запрос установленно ограничение соединения (по времени) 10 секунд,
    чтобы избежать появления исключения aiohttp.ClientOSError.
    Тем самым генерируется исключение aiohttp.ServerTimeoutError, которое обрабатывается и добавляет данные в БД.

    :param width:
    :param timer:
    :param session: сессия HTTP-запросов (aiohttp.ClientSession).
    :param link: url-адрес на изображение.
    :param counter: счетчик для подсчета количества url-адресов.
    :return: None
    """
    try:
        # Проверяем, есть ли ссылка в БД. Если нет, то парсим её, загружаем фотографию, получаем 128-значный массив
        # из векторов, загружаем его в БД, удаляем фотографию.

        # !!! Нужно разобраться с прокси
        async with session.get(
                url=str(link),
                timeout=ClientTimeout(total=None, sock_connect=timer, sock_read=timer),
                headers=HEADERS,
                # proxy='http://193.0.202.46:10010',
                # proxy_auth=aiohttp.BasicAuth(login='WvUIrGfT', password='vpb6vM3V'),
        ) as response:

            if response.status in [200, 201, 202] and response.content_type.split('/')[0] == 'image':
                print(counter)
                DATABASE.add_connect(link, connect_available=True, face_available=False)
                extension = response.content_type.split('/')[1]
                if extension in ['jpeg', 'jpg', 'png']:
                    name_path = f'recognition/inter_folder/img_{counter}.{extension}'
                    async with aiofiles.open(name_path, 'wb') as f:
                        await f.write(await response.read())

                        image_faces = get_image_vector(name_path, width=width)
                        link_id = DATABASE.get_link_id(link=link)
                        if link_id:
                            for face_array in image_faces:
                                DATABASE.add_new_face(link_id=link_id, face_array=face_array)

                        os.remove(name_path)

                        return 'Image'
            else:
                DATABASE.add_connect(link, connect_available=True, face_available=False)
                return 'Not_Image'

    except aiohttp.ClientOSError:
        print(f"aiohttp.ClientOSError: {counter}")
        return 'Error'

    except aiohttp.ServerTimeoutError:
        print(f"aiohttp.ServerTimeoutError: {counter}")
        return 'Error'


async def downloads_image(timer: int = 10, width: int = 1080) -> tuple:
    """
    Формирует сессию HTTP-запросов, в ней создает список задач (get-запросов) для асинхронного выполнения.

    :param width:
    :param timer:
    :return: возвращает список результатов выполнения задач (функций с get-запросами)
    """

    db_list_of_links = DATABASE.get_all_links()

    # Создаем сессию для соединения со всеми ссылками асинхронно
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector,) as session:

        tasks = []
        for i, link in enumerate(db_list_of_links):

            # Добавляем задачи (функции) в список задач
            task = asyncio.create_task(task_formation(session, link, i, timer=timer, width=width))
            tasks.append(task)

        # Выполняем список задач
        results = await asyncio.gather(*tasks)

        return results


def main():

    while True:
        print('START')
        asyncio.run(downloads_image())
        print('FINISH')
        sleep(60 * 20)


if __name__ == '__main__':
    main()
