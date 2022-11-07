import aiohttp
import aiofiles
import asyncio
from user_agent import generate_navigator


HEADERS = generate_navigator()


async def _task_formation(session, link: str, counter: int) -> str:

    async with session.get(url=str(link), headers=HEADERS) as res:

        if res.status in [200, 201, 202] and res.content_type.split('/')[0] == 'image':
            extension = res.content_type.split('/')[1]
            name_path = f'inter_folder/img_{counter}.{extension}'
            async with aiofiles.open(name_path, 'wb') as f:
                await f.write(await res.read())

            return name_path


async def downloads_image(path_from_links: str) -> list:

    # Открываем файл и считываем все ссылки, которые необходимо спарсить
    with open(path_from_links, encoding='utf-8') as file:
        face_list = [face.strip() for face in file.readlines()]

    async with aiohttp.ClientSession(trust_env=True) as session:
        tasks = []
        for i, link in enumerate(face_list):
            # Добавляем задачи (функции) в список задач
            task = asyncio.create_task(_task_formation(session, link, i))
            tasks.append(task)
        # Выполняем список задач

        results = await asyncio.gather(*tasks)

        return results
