from os import listdir
from os.path import isfile, join
import os

def get_files(path):
    filenames = []
    for root, dirs,files in os.walk(path):
        for filename in files:
            filenames.append(root + '/' + filename)

    return filenames

def make_pair(filename):
    cat =filename.split('/')
    obj = {"name": cat[2], "category": cat[1], "link": filename}
    return obj

def extract_category(basePath,list_of_paths):
    category = []
    for item in list_of_paths:
        cat = item.split('/')
        if cat[1] not in category:
            category.append(cat[1])
    return category

from app import *

def generate_descriptions(filename):
    string = ""

    for item in filename.split('/'):
        string += item + " "

    for item in filename.split('/')[2].split('.'):
        string += item + " "

    for item in filename.split('/')[2].split('_'):
        string += item + " "

    for item in filename.split('/')[2].split('.'):
        string += item.lower() + " "
    return string

def add_to_db(path):
    files = get_files(path)
    new_files_list = []
    for item in files:
        new_files_list.append(make_pair(item))
    for item in new_files_list:
        song = Song(name=item["name"], link=item["link"], genre=item["category"], description=generate_descriptions(item['link']))
        db.session.add(song)
        db.session.commit()

if __name__ == "__main__":
    add_to_db("music_dir_test")

#print(extract_category("music_dir_test", get_files("music_dir_test")))
