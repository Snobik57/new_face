from data_generation import gathering_information
from models.db_func import DataBaseORM
from time import sleep

DATABASE = DataBaseORM()


def main():

    while True:
        images = DATABASE.database_inspection()
        if images:
            for image in images:
                inform_with_compare = gathering_information(image.id, image.image)
                if inform_with_compare:
                    DATABASE.add_inspect(image.id)
                    print(f"INFO: about the new image of analysts:\n{inform_with_compare}")
        else:
            print('New analyst image not found')
        sleep(5)


if __name__ == "__main__":
    main()
