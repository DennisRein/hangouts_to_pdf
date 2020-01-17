''' ToDo:
1. Extract all files in Input Folder [X]
2. Read all Hangouts.json files [X]
3. Translate ID to Name
3a. Get IDs Names somehow out of JSON File maybe with Input (Who's sender? Receiver can be read out of json)
4. Read Events -> Chat Message => To Message Class (Name: str, Message: str, isImage: bool),
4a. Name ID translated to name
5. Save Message to Dic Timestamp: Message
5a. Has Attachment? => isImage: true Message: Url; timestamp before +1,
6. Write to PDF in Output, if isImage download image


****
1. Start Up Function and Args X
2. Logging and Update during file launch X
3. Testing (Multiple Files, Names, Etc.) X
4. Style Output PDF
5. Comments X
'''

import os
import zipfile
import json
import collections
import argparse
import logging

from datetime import datetime
from fpdf import FPDF


class Message:
    """
    A class used to represent a Message

    Attributes
    ----------
    message : str
        The Message Text or Image Link
    sender : str
        The sender id of the person who send the message
    is_img: bool
        Whether the message is an image or not
    chatters: dict
        A dict<id: name> to translate the given id to a name

    Methods
    -------
    get_name()
        return the translated name of the sender

    get_msg()
        returns the message content

    is_img()
        returns whether the message is image or not
    """
    def __init__(self, message: str, sender: str, is_img: bool, chatters: dict):
        self.msg = message
        self.sdr = sender
        self.img = is_img
        self.chr = chatters

    def get_name(self):
        return self.translate(self.sdr, self.chr)

    def get_msg(self):
        return self.msg

    def is_img(self):
        return self.img

    @staticmethod
    def translate(client: str, chatters: dict):
        if client in chatters:
            return chatters[client]
        return client


# Extract all Zip Files in given Path
def extract_all(path: str):
    for (d, _, files) in os.walk(path):
        for f in files:
            path = os.path.join(d, f)
            if os.path.exists(path) and path.endswith(".zip"):  # check for ".zip" extension
                logging.info("Found file {} extracting".format(path))
                zip_ref = zipfile.ZipFile(path)  # create zipfile object
                zip_ref.extractall(path.replace(".zip", ""))  # extract file to dir
                zip_ref.close()  # close file


# Read all Hangouts.json files into a dict
def read_json(path: str):
    json_list = []
    for (d, _, files) in os.walk(path):
        for f in files:
            path = os.path.join(d, f)
            if os.path.exists(path) and "Hangouts.json" in path:
                with open(path) as json_file:
                    json_list.append(json.load(json_file))
    if len(json_list) <= 0:
        logging.error("No Hangout files found please check if you have selected the right path and if Hangouts.json "
                      " are available files")
        exit(1)
    logging.info("Found {} JSON Files".format(len(json_list)))
    return json_list


# Check if the found name is right and offer to edit
def check_names(name: str, id: str):
    print("Found User {0} with ID {1}\nKeep? (yes/NO)".format(name, id))
    choice = input()
    if "y" in choice.lower() or len(choice) == 0:
        logging.info("Added {}".format(name))
        return name
    print("Enter the name for ID {0}".format(id))
    name = input()
    return check_names(name, id)


# Get the ID to Name translation
def get_chatters(content: list):
    users = dict()
    for c in content:
        if "conversations" in c:
            for c in c["conversations"]:
                if (
                        "conversation" in c
                        and "conversation" in c["conversation"]
                        and "participant_data" in c["conversation"]["conversation"]
                ):
                    data = c["conversation"]["conversation"]["participant_data"]
                    for u in data:
                        cid = None
                        name = None
                        if "id" in u and "chat_id" in u["id"]:
                            cid = u["id"]["chat_id"]
                        if "fallback_name" in u:
                            name = u["fallback_name"]
                        if cid in users:
                            continue
                        name = check_names(name, cid)
                        users.update({cid: name})
    logging.info("Found {} participants.".format(len(users)))
    return users


# Get the content out of the read in json files eg. Messages etc.
def extract_json(content: list, chatters: dict):
    history = list()
    for j in content:
        chat = dict()
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
                                    chat.update({timestamp: Message(s["text"], sender, False, chatters)})
                            if "attachment" in msg:
                                for a in msg["attachment"]:
                                    timestamp = int(timestamp) + 1
                                    chat.update({timestamp: Message(a["embed_item"]["plus_photo"]["thumbnail"]
                                                                    ["image_url"], sender, True, chatters)})
        logging.info("Extracted {} messages".format(len(chat)))
        history.append(chat)
    return history


# Sort the Messages dict by timestamp
def sort_dict(content: dict):
    return collections.OrderedDict(sorted(content.items()))


def item_length(content: list):
    ful = 0
    for c in content:
        ful = ful + len(c)
    return ful


# Create the pdf out of the extracted JSON Content
def create_pdf(content: list, path: str):
    count = 0
    done = 0
    full = item_length(content)
    logging.info("Creating PDFs this may take up a while.")
    for c in content:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        c = sort_dict(c)
        count2 = 0
        for key, val in c.items():
            pdf.cell(200, 10, txt="[{0}] {1}:".format(datetime.fromtimestamp(int(str(key)[:10])), val.get_name()), ln=1)
            if val.is_img():
                pdf.image(val.get_msg(), w=100, h=100)
            else:
                pdf.cell(200, 10, txt="{}".format(val.get_msg()), ln=1)
            count2 = count2 + 1
            logging.info("Wrote {0}/{1} lines".format(count2, len(c)))
        done = done + count2
        pdf.output(path + "/output_{}.pdf".format(count))
        count = count + 1

        logging.info("Wrote {0}/{1} PDF files \n{2}% Done".format(count, len(content), (done/full*100)))
    return count


# Main function to run our program
def run(inp, out):
    extract_all(inp)
    content = read_json(inp)
    chatters = get_chatters(content)
    create_pdf(extract_json(content, chatters), out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts a Hangout File to a PDF')
    parser.add_argument('--input', nargs='?', const=1, type=str, default="input")
    parser.add_argument('--output', nargs='?', const=1, type=str, default="output")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    run(args.input, args.output)
