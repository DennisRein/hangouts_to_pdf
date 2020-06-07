import unicodedata


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
        return self.unicode_normalize(self.msg)

    def is_img(self):
        return self.img

    def unicode_normalize(self, msg: str):
        return unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode("latin-1")

    @staticmethod
    def translate(client: str, chatters: dict):
        if client in chatters:
            return chatters[client]
        return client
