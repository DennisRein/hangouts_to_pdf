import collections
import utils.config as config


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
    """
    Writes the given text into the PDF file. Aligns text left.
    :param msg: The Message Object for sender and text
    :param time: Time stamp
    :param pdf: The open PDF file
    :return: Nothing
    """
    global old
    text = "[{0}] {1}:".format(str(datetime.fromtimestamp(int(str(time)[:10])))[:16],
                               msg.get_name())
    if old != text:
        pdf.set_font(config.FONT, size=config.FONT_CHATTER)
        pdf.multi_cell(200, config.FONT_CHATTER, txt=text, align='L')
        old = text
    pdf.set_font(config.FONT, size=config.FONT_SIZE)
    if msg.is_img():
        if 150 + pdf.get_y() > config.A4_HEIGHT:
            pdf.add_page()
        pdf.image(msg.get_msg(), w=config.WIDTH, h=config.HEIGHT)
    else:
        pdf.multi_cell(200, config.FONT_SIZE, txt="{}".format(msg.get_msg()))


def align_right(msg: Message, time: int, pdf: FPDF):
    """
    Writes the given text into the PDF file. Aligns text right. Handles Image
    :param msg: The Message Object for sender and text
    :param time: Time stamp
    :param pdf: The open PDF file
    :return: Nothing
    """
    global old

    text = "[{0}] {1}:".format(str(datetime.fromtimestamp(int(str(time)[:10])))[:16],
                               msg.get_name())

    if old != text:
        pdf.set_font(config.FONT, size=config.FONT_CHATTER)
        pdf.multi_cell(200, config.FONT_CHATTER, txt=text, align='R')
        old = text
    pdf.set_font(config.FONT, size=config.FONT_SIZE)
    if msg.is_img():
        if 150 + pdf.get_y() > config.A4_HEIGHT:
            pdf.add_page()
        pdf.image(msg.get_msg(), w=config.WIDTH, h=config.HEIGHT, x=config.A4_WIDTH - 100)
    else:
        pdf.multi_cell(200, config.FONT_SIZE, txt="{}".format(msg.get_msg()), align='R')


def title(chatter: dict, pdf: FPDF):
    c = filter_chatter(chatter)
    pdf.set_font(config.FONT, size=config.TITLE_FONT)
    pdf.multi_cell(200, config.TITLE_FONT, txt="Chat logs {0} {1}".format(c[0], c[1]), align='C')
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
    print("\n##########################################")
    for c in content:
        pdf = FPDF()
        #pdf.add_font(config.FONT, style="", fname=r"C:\Windows\Fonts\NotoSans-Regular.ttf", uni=True)
        #pdf.add_font(config.FONT, style="B", fname=r"C:\Windows\Fonts\NotoSans-Bold.ttf", uni=True)
        #pdf.add_font(config.FONT, style="I", fname=r"C:\Windows\Fonts\NotoSans-Italic.ttf", uni=True)
        #pdf.add_font(config.FONT, style="BI", fname=r"C:\Windows\Fonts\NotoSans-BoldItalic.ttf", uni=True)
        pdf.add_page()
        title(c, pdf)
        pdf.set_font(config.FONT, size=config.FONT_SIZE)
        c = sort_dict(c)
        count2 = 0
        print("Writing PDF Number {}".format(count+1))
        print("-----------------------\n")
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
        print("\n##########################################")
        print("Wrote {0}/{1} PDF files \n{2}% Done\n".format(count, len(content), (done / full * 100)))
    return count


if __name__ == "__main__":
    pdf = FPDF()
    pdf.add_page()
    title("Test", pdf)
    align_left(Message("Links", "Dennis", False, dict()), 123456124, pdf)
    align_right(Message("Rechts", "Dennis", False, dict()), 123456124, pdf)
    pdf.output("../output/t.pdf")
