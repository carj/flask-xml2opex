import os
from os.path import isfile
import time

SITE = "/home/opextest/mysite/"

zip_files = [f for f in os.listdir(SITE) if isfile(os.path.join(SITE, f)) and f.endswith(".zip")]

for file in zip_files:
    if time.time() - os.path.getmtime(os.path.join(SITE, file)) > (24 * 60 * 60):
        os.remove(os.path.join(SITE, file))


upload_folder = os.path.join(SITE, "upload")

for path, directories, files in os.walk(upload_folder, topdown=True):
    for file in files:
        xml_file = os.path.join(path, file)
        if time.time() - os.path.getmtime(xml_file) > (24 * 60 * 60):
            os.remove(os.path.join(path, file))


temp_folders = [f for f in os.listdir(upload_folder) if os.path.isdir(os.path.join(upload_folder, f))]
for d in temp_folders:
    if os.listdir(os.path.join(upload_folder, d)) == []:
        os.rmdir(os.path.join(upload_folder, d))

