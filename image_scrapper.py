import os
import random

from selenium import webdriver

from fetch_imgs_from_google import fetch_image_urls_from_google
from download_verified_image import download_image_verified

# the path needs to be adapted on each computer
DRIVER_PATH = '/home/joanna/Downloads/operadriver_linux64/operadriver'


def search_and_download(search_term: str, driver_path: str, target_path='./images'):
    """
    Calls a function to retrieve urls to corresponding search term and downloads the photos, if it fulfills basic
    criteria.

    :param search_term:  term to query
    :param driver_path:  path to selenium driver
    :param target_path:  path to search retrieved photos
    """
    target_folder = '_'.join(target_path[:-4].lower().split(' '))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        urls = fetch_image_urls_from_google(search_term, wd=wd)

    if urls is None:
        return

    for elem in urls:
        if elem is None:
            continue
        download_image_verified(target_folder, elem)


def get_names_to_fetch(files_path: str, filename: str):
    """
    Gets all queries to fetch photos from a .txt file.

    :param files_path:   path to search the file containing queries
    :param filename:     the name of a file  to retrieve queries from
    :return:             list of queries if successfully retrieved, None otherwise
    """
    queries_to_fetch = []
    if not filename.endswith(".txt"):
        return None
    with open(os.path.join(files_path, '_'.join(filename.lower().split(' ')))) as f:
        queries_to_fetch += f.readlines()
    return queries_to_fetch


def main():
    """
    Main function of the program.
    """
    # TODO: extract it to be provided as command line argument
    path_with_names = "/home/joanna/PycharmProjects/photos_scrapper/images"
    if not os.path.exists(path_with_names):
        print("Given path with names cannot be found.")
        return
    for filename in os.listdir(path_with_names):
        names_to_fetch = get_names_to_fetch(path_with_names, filename)
        if names_to_fetch is None:
            continue
        random.shuffle(names_to_fetch)

        for name in names_to_fetch:
            search_and_download(search_term=name, driver_path=DRIVER_PATH, target_path="./" + filename)


if __name__ == "__main__":
    main()
