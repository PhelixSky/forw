# -*- coding: utf-8 -*-

from time import sleep
from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl import functions, types
from telethon import utils
import time
import logging
import io
import os
from telethon import errors

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


class Forwarder():
    def __init__(self):
        config = ConfigParser()
        config.read('Options.ini')
        api_id = int(config.get("Settings", "id"))
        api_hash = str(config.get("Settings", "hash"))
        self.api_id = api_id
        self.api_hash = api_hash
        self.clientT = TelegramClient('tele', self.api_id, self.api_hash)
        self.clientT.connect()
        self.clientT.start()
        self.main_chat = {int(config.get("Resend", "c1")): 0,
                          int(config.get("Resend", "c2")): 0,
                          int(config.get("Resend", "c3")): 0,
                          int(config.get("Resend", "c4")): 0,
                          int(config.get("Resend", "c5")): 0,
                          int(config.get("Resend", "c6")): 0,
                          int(config.get("Resend", "c7")): 0,
                          int(config.get("Resend", "c8")): 0,
                          int(config.get("Resend", "c9")): 0}
        self.end_chat = int(config.get("Resend", "to"))
        self.max_id = 0

    def get_max_id(self):
        try:
            dial = self.clientT.get_dialogs(limit=100)
            for i in dial:
                try:
                    id = i.dialog.peer.channel_id
                    q = self.clientT(functions.channels.GetMessagesRequest(types.PeerChannel(id),
                                                                           [i.dialog.top_message]))

                    for key in self.main_chat.keys():
                        if id == key:
                            self.main_chat[key] = i.dialog.top_message
                except AttributeError:
                    continue
        except Exception as error:
            logging.error('check max' + error.__repr__())

    def remove_temp(self):
        while True:
            try:
                os.remove('temp.jpg')
                return True
            except FileNotFoundError:
                return True

    def check_max(self):
        try:
            while True:
                try:
                    logging.info('circle')
                    time.sleep(10)
                    dial = self.clientT.get_dialogs(limit=100)
                    for i in dial:
                        id = i.dialog.peer.channel_id
                        for key, value in self.main_chat.items():
                            if id == key:
                                if i.dialog.top_message != value:
                                    logging.info('lets_go!')

                                    try:
                                        self.remove_temp()
                                        q = self.clientT(functions.channels.GetMessagesRequest(types.PeerChannel(key),
                                                                                               [i.dialog.top_message]))
                                        msg = q.messages[0]
                                        logging.info(key)
                                        logging.info(i.dialog.top_message)
                                        logging.info(str(msg).encode('utf-8').decode('latin1'))

                                        post = 'no posted!'
                                        if msg.media is None:
                                            logging.info('media is none')
                                            post = self.clientT(
                                                functions.messages.SendMessageRequest(types.PeerChannel(self.end_chat),
                                                                                      msg.message))
                                            self.main_chat[key] = i.dialog.top_message
                                        if msg.media is not None:
                                            logging.info('media is not none')
                                            try:
                                                self.clientT.download_media(msg, 'temp.jpg')
                                                upload = self.clientT.upload_file('temp.jpg')
                                            except FileNotFoundError:
                                                logging.info('posted after not found!!')
                                                post = self.clientT(
                                                    functions.messages.SendMessageRequest(
                                                        types.PeerChannel(self.end_chat),
                                                        msg.message))
                                                self.main_chat[key] = i.dialog.top_message
                                                continue
                                            caption = msg.media.caption
                                            if caption is None:
                                                logging.info('caption is none')
                                                post = self.clientT(
                                                    functions.messages.SendMediaRequest(
                                                        types.PeerChannel(self.end_chat),
                                                        media=types.InputMediaUploadedPhoto(
                                                            upload, '')))
                                                self.main_chat[key] = i.dialog.top_message
                                            if caption is not None:
                                                logging.info('caption is not none')
                                                post = self.clientT(
                                                    functions.messages.SendMediaRequest(
                                                        types.PeerChannel(self.end_chat),
                                                        media=types.InputMediaUploadedPhoto(
                                                            upload, caption)))
                                                self.main_chat[key] = i.dialog.top_message

                                        logging.info('posted %s - %s' % (str(key), str(value)))
                                    except Exception as er:
                                        logging.info('check max3' + er.__repr__())
                        else:
                            continue

                    else:
                        continue
                except errors.RpcCallFailError:
                    time.sleep(30)
                    continue
                except AttributeError:
                    continue
                except Exception as error:
                    logging.error('check max2' + error.__repr__())
        except Exception as error:
            logging.error('check max' + error.__repr__())


if __name__ == '__main__':
    try:
        logging.basicConfig(filename="LOG.log", level=logging.INFO,
                            format='%(asctime)s - %(funcName)s - %(levelname)s: %(message)s')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s: %(message)s')
        console.setFormatter(formatter)

        logging.getLogger('').addHandler(console)
        logging.info('Bot is started')
        s = Forwarder()
        s.get_max_id()
        s.check_max()
    except Exception as error:
        logging.info(error.__repr__())

