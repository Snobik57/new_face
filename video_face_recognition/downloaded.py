import os
import requests
from video_recognition import get_face_from_image, get_screenshot_from_video


def downloaded_video(url, counter):
    headers = {
        'app_code_name': 'Mozilla',
         'app_name': 'Netscape',
         'app_version': '5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like '
                        'Gecko) Chrome/86.0.4240.183 Safari/537.36',
         'build_id': None,
         'build_version': '86.0.4240.183',
         'navigator_id': 'chrome',
         'os_id': 'linux',
         'oscpu': 'Linux x86_64',
         'platform': 'X11; Linux x86_64',
         'product': 'Gecko',
         'product_sub': '20030107',
         'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                       'like Gecko) Chrome/86.0.4240.183 Safari/537.36',
         'vendor': 'Google Inc.',
         'vendor_sub': ''
    }
    proxies = {
        "http": "http://189.202.188.149:80",
        "https": "https://79.133.51.36:80",
    }

    file_dir = "downloaded_video"
    file_name = f"file_{counter}"

    try:

        attachment_resource = url.split('//')[1].split('/')[0].split('.')[1]
        resources = ["youtube", "vk", "ok"]

        if attachment_resource in resources or url.find("m3u8"):
            os.system(f"""yt-dlp -S "height:480" -P "./{file_dir}" -o "{file_name}.mp4" {url.split(' ')[0]}""")
            print(f"[INFO] successful download")

        else:
            response = requests.get(
                url,
                stream=True,
                headers=headers,
                # proxies=proxies,
            )

            with open(f'{file_dir}/{file_name}.mp4', 'wb') as file:
                file.write(response.content)

        list_of_files = [i.split('.')[0] for i in os.listdir(f'./{file_dir}')]
        print(f"!!!!!!!!!!!!!!!!!{list_of_files}")
        if file_name in list_of_files:
            return f"{file_dir}/{file_name}.mp4"

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] ConnectionError")
        pass


# TODO: разобраться с ts форматом

def compare_video():
    with open('attachments.txt') as file:
        attachments_list = [i.strip() for i in file.readlines()]

    image_encoding = get_face_from_image("image/Meyran.jpg")

    for i, url in enumerate(attachments_list):
        vide_file_path = downloaded_video(url, i)
        result = get_screenshot_from_video(vide_file_path, image_encoding)
        print(f"[INFO] RESULT for {vide_file_path}: {result}")
        if vide_file_path:
            os.remove(vide_file_path)


if __name__ == '__main__':
    compare_video()
