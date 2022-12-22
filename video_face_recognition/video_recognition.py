from _testbuffer import ndarray

import face_recognition
import cv2
import PIL.Image
import numpy as np


def new_load_image_file(file: str, width: int = 1080, mode='RGB') -> ndarray:
    """
    Преобразует изображение (.jpg, .png, etc) в numpy array

    :param width: величина ширины для получения измененного размера изображения
    :param file: название или путь изображения
    :param mode: формат, в который нужно преобразовать изображение.
                 По-умолчанию 'RGB' (8-bit RGB, 3 channels), и 'L' (черно-белый) поддерживается.

    :return: изображение в виде numpy array
    """
    im = PIL.Image.open(file)

    if mode and mode == 'L' or mode == 'RGB':
        im = im.convert(mode)

    if im.size[0] > width:
        ratio = width / im.size[0]
        height = int((float(im.size[1]) * float(ratio)))
        im = im.resize((width, height), PIL.Image.Resampling.LANCZOS)

    return np.array(im)


def get_face_from_image(image_path):

    image = new_load_image_file(image_path)
    image_face_encoding = face_recognition.face_encodings(image)

    return image_face_encoding


def get_screenshot_from_video(video_file_path, image_encoding):
    input_movie = cv2.VideoCapture(video_file_path)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
    counter = 0
    result = False

    while True:
        ret, face = input_movie.read()
        width = int(input_movie.get(3)) # float `width`
        height = int(input_movie.get(4)) # float `height`

        if width * height > 410000:
            face = cv2.resize(face, (width, height))

        if not ret or counter > 360:
            return result

        elif ret:
            print(counter)
            video_face_locations = face_recognition.face_locations(face, model='cnn')
            video_face_encodings = face_recognition.face_encodings(face, video_face_locations)

            if video_face_encodings:
                for video_face_encoding in video_face_encodings:
                    result_compare = face_recognition.compare_faces(image_encoding, video_face_encoding, tolerance=0.48)
                    if True in result_compare:
                        result = True
                        return result
            counter += 1

# TODO: https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_video_file.py


if __name__ == "__main__":
    pass
