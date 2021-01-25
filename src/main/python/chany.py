import os
import re
import json
import urllib.request
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


def api_request(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'PyChanV0.1'})
    response = urllib.request.urlopen(request).read()
    json_data = json.loads(response.decode('UTF-8'))
    return json_data


def check_url(url):
    regex = re.compile(
        "((http|https)://)boards.4chan.org\\b([-a-zA-Z0-9@:%._+~#?&/=]*)")

    if re.search(regex, url):
        return True
    else:
        return False


class Loader(QObject):
    finished = pyqtSignal()
    status_update = pyqtSignal(str)
    info_update = pyqtSignal(str)
    progress_max = pyqtSignal(int)
    progress_update = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.is_running = False

    @pyqtSlot(str, str)
    def download(self, url, path):
        self.is_running = True
        if url == "" or not check_url(url):
            self.status_update.emit("Please enter a valid URL")
        else:  # here we go
            self.progress_max.emit(0)
            self.progress_update.emit(0)
            self.status_update.emit("Fetching data...")
            try:
                url_parts = url.replace("https://", "").split("/")
                board = url_parts[1]
                thread = url_parts[3]
                api_url = "https://a.4cdn.org/" + str(board) + "/thread/" + str(thread) + ".json"
                posts = api_request(api_url)["posts"]

                try:
                    thread_name = posts[0]["sub"].lower()
                except KeyError:
                    semantic_name = posts[0]["semantic_url"].lower().split("-")
                    if len(semantic_name) > 3:
                        thread_name = semantic_name[0] + " " + semantic_name[1] + " " + semantic_name[2] + " " + semantic_name[3]
                    else:
                        thread_name = " ".join(semantic_name)
                thread_name = thread_name.replace("&amp;", "&").replace("/", "").replace("\\?", "").replace("&#039;", "").replace(":", "")

                thread_time = datetime.fromtimestamp(posts[0]["time"])
                timestamp = datetime.strftime(thread_time, "%Y-%m-%d")

                savepath = os.path.join(path, board, timestamp + " - " + thread_name)
                if not os.path.exists(savepath):
                    os.makedirs(savepath)

                self.info_update.emit("/" + board + "/ - " + timestamp + " - " + thread_name)

                img_count = sum("ext" in post for post in posts)
                self.progress_max.emit(img_count)
                self.progress_update.emit(0)

                img = 0
                for post in posts:
                    if not self.is_running:
                        self.progress_max.emit(100)
                        self.progress_update.emit(0)
                        self.status_update.emit("Download cancelled")
                        break
                    if "ext" in post:
                        self.status_update.emit("Downloading image " + str(img) + "/" + str(img_count))
                        file_name = str(post["tim"]) + post["ext"]
                        file_url = "https://i.4cdn.org" + "/" + str(board) + "/" + file_name
                        if not os.path.isfile(os.path.join(savepath, file_name)):
                            urllib.request.urlretrieve(file_url, os.path.join(savepath, file_name))
                        self.progress_update.emit(img)
                        img += 1

                if self.is_running:
                    self.progress_update.emit(img_count)
                    self.status_update.emit("Finished!")
                    self.is_running = False

            except Exception as err:
                self.status_update.emit("Error: " + str(err))
                print(err)
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.is_running = False
