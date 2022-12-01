from data_generation import gathering_information
from models.ch_db import DataBaseChORM
from time import sleep

DATABASE = DataBaseChORM()


def main():

    while True:
        images = DATABASE.database_inspection()
        print(images)
        if images:
            for image in images:
                inform_with_compare = gathering_information(analytics_image=image)
                print(f"INFO: about the new image of analysts:\n{inform_with_compare}")
                print(DATABASE.select_attachments_match_found(image[1]))
        else:
            print('New analyst image not found')
        sleep(5)


if __name__ == "__main__":
    main()
