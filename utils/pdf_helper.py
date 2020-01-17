import logging
import collections

from fpdf import FPDF
from datetime import datetime
from utils.message import Message

old = None
# Sort the Messages dict by timestamp
def sort_dict(content: dict):
    return collections.OrderedDict(sorted(content.items()))


def item_length(content: list):
    ful = 0
    for c in content:
        ful = ful + len(c)
    return ful


def align_left(msg: Message, time: int, pdf: FPDF):
    global old
    text = "[{0}] {1}:".format(str(datetime.fromtimestamp(int(str(time)[:10])))[:16],
                                                msg.get_name())
    if old != text:
        pdf.cell(200, 10, txt=text, ln=1, align='L')
        old = text

    if msg.is_img():
        print(text)
        pdf.image(msg.get_msg(), w=100, h=100)
    else:
        pdf.cell(200, 10, txt="{}".format(msg.get_msg()), ln=1)


def align_right(msg: Message, time: int, pdf: FPDF):
    global old
    A4_HEIGHT = 297
    A4_WIDTH = 210

    text = "[{0}] {1}:".format(str(datetime.fromtimestamp(int(str(time)[:10])))[:16],
                                                msg.get_name())

    if old != text:
        pdf.cell(200, 10, txt=text, ln=1, align='R')
        old = text
    if msg.is_img():
        print(text)
        pdf.image(msg.get_msg(), w=100, h=100, x=A4_WIDTH-100)
    else:
        pdf.cell(200, 10, txt="{}".format(msg.get_msg()), ln=1, align='R')


def title(chatter: dict, pdf: FPDF):
    c = filter_chatter(chatter)
    pdf.set_font("Arial", size=24)
    pdf.cell(200, 10, txt="Chat logs {0} {1}".format(c[0], c[1]), ln=1, align='C')
    return pdf


def filter_chatter(content: dict):
    user = list()
    for val in content.values():
        if val.get_name() not in user:
            user.append(val.get_name())

    if len(user) < 2:
        user.append("")
        user.append("")

    return user[0], user[1]


# Create the pdf out of the extracted JSON Content
def create_pdf(content: list, path: str):
    count = 0
    done = 0
    full = item_length(content)
    old = ""
    changes = 1
    print("Creating PDFs this may take up a while.")
    for c in content:
        pdf = FPDF()
        pdf.add_page()
        title(c, pdf)
        pdf.set_font("Arial", size=12)
        c = sort_dict(c)
        count2 = 0
        for key, val in c.items():
            if old is not val.get_name():
                old = val.get_name()
                changes = changes + 1
            if changes % 2 == 0:
                align_left(val, key, pdf)
            else:
                align_right(val, key, pdf)
            count2 = count2 + 1
            print("Wrote {0}/{1} lines".format(count2, len(c)))
        done = done + count2
        pdf.output(path + "/output_{}.pdf".format(count))
        count = count + 1

        print("Wrote {0}/{1} PDF files \n{2}% Done".format(count, len(content), (done/full*100)))
    return count


if __name__ == "__main__":
    pdf = FPDF()
    pdf.add_page()
    title("Test", pdf)
    align_left(Message("Links", "Dennis", False, dict()), 123456124, pdf)
    align_right(Message("Rechts", "Dennis", False, dict()), 123456124, pdf)
    pdf.output("../output/t.pdf")
