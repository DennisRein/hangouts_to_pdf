''' ToDo:
1. Extract all files in Input Folder
2. Read all Hangouts.json files
3. Translate ID to Name
4. Read Events -> Chat Message => To Message Class (Name: str, Message: str, isImage: bool),
4a. Name ID translated to name
5. Save Message to Dic Timestamp: Message
5a. Has Attachment? => isImage: true Message: Url; timestamp before +1,
6. Write to PDF in Output, if isImage download image
'''

import os
import zipfile
import json
import collections
import datetime

from fpdf import FPDF


class Message:
    def __init__(self, message: str, sender: str, is_img: bool):
        self.msg = message
        self.sdr = sender
        self.img = is_img

    def get_name(self):
        return self.translate(self.sdr)

    def get_msg(self):
        return self.msg

    def is_img(self):
        return self.img

    @staticmethod
    def translate(client: str):
        if client == "110193123790794406506":
            return "BunnyJumps"
        if client == "108549898331096731293":
            return "Dennis"
        return client


def extract_all(path: str):
    for (d, _, files) in os.walk(path):
        for f in files:
            path = os.path.join(d, f)
            if os.path.exists(path) and path.endswith(".zip"):  # check for ".zip" extension
                zip_ref = zipfile.ZipFile(path)  # create zipfile object
                zip_ref.extractall(path.replace(".zip", ""))  # extract file to dir
                zip_ref.close()  # close file


def read_json(path: str):
    json_list = []
    for (d, _, files) in os.walk(path):
        for f in files:
            path = os.path.join(d, f)
            if os.path.exists(path) and "Hangouts.json" in path:
                with open(path) as json_file:
                    json_list.append(json.load(json_file))

    return json_list


def extract_json(json: list):
    chat = dict()
    for j in json:
        if "conversations" in j:
            for c in j["conversations"]:
                if "events" in c:
                    for e in c["events"]:
                        sender = e["sender_id"]["chat_id"]
                        timestamp = e["timestamp"]
                        if "chat_message" in e and "message_content" in e["chat_message"]:
                            msg = e["chat_message"]["message_content"]
                            if "segment" in msg:
                                for s in msg["segment"]:
                                    timestamp = int(timestamp) + 1
                                    chat.update({timestamp: Message(s["text"], sender, False)})
                            if "attachment" in msg:
                                for a in msg["attachment"]:
                                    timestamp = int(timestamp) + 1
                                    chat.update({timestamp: Message(a["embed_item"]["plus_photo"]["thumbnail"]["image_url"], sender, True)})
    return chat


def sort_dict(content: dict):
    return collections.OrderedDict(sorted(content.items()))


def create_pdf(content: dict, path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for key, val in content.items():
        pdf.cell(200, 10, txt="[{0}] {1}:".format(datetime.datetime.fromtimestamp(int(str(key)[:10])), val.get_name()), ln=1)
        if val.is_img():
            pdf.image(val.get_msg(), w=100, h=100)
        else:
            pdf.cell(200, 10, txt="{}".format(val.get_msg()), ln=1)
    pdf.output(path)


extract_all("input")
print(create_pdf(extract_json(read_json("input")), "output/out.pdf"))
