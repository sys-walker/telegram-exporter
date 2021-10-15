#!/usr/bin/env python
from telethon.sync import TelegramClient
from telethon import functions
import phonenumbers, re
from datetime import datetime

# To get API_ID and API_HASH
# https://my.telegram.org/auth?to=apps
# check 'App configuration' section

API_ID=000000 # Your API_ID
API_HASH="YOUR API_HASH"

client = TelegramClient('Contacts_Exporter', api_id=API_ID, api_hash=API_HASH)
now_str = f"{datetime.now()}".replace(" ", "_").replace(":", ".")


async def start():
    await client.get_me()


def generate_card(param):
    card = VCARD()
    card.set_full_name(f"{param['first_name']} {param['last_name']}")
    card.set_nickname(f"{param['username']}")
    card.set_phone(f"{param['phone']}")
    card.build()
    return card


class VCARD:
    def __init__(self):
        self.__header = "BEGIN:VCARD\n" \
                        "VERSION:3.0\n"
        self.__body_card = ""
        self.__footer = "END:VCARD"

        self.__card = ""

        pass

    def set_full_name(self, name):
        name = name.replace("None", "")
        self.__body_card += f"FN:{name}\n"

        self.__body_card += "N:"
        lst = name.split(" ")
        for i in range(0, 4):
            if i < len(lst) and f"{lst[i]}" != '':
                self.__body_card += f"{lst[i]}"
            self.__body_card += ";"
        self.__body_card += "\n"

        return self

    def set_nickname(self, nickname):
        if nickname != "" and nickname != "None":
            self.__body_card += f"NICKNAME:{nickname}\n"
        return self

    def set_phone(self, name):
        if name != "" and name != "None":
            formated_phone = self.__format_number(name)
            if formated_phone != "":
                self.__body_card += f"TEL;TYPE=CELL:{formated_phone}\n"
        return self

    def build(self):
        self.__card = self.__header + \
                      self.__body_card + \
                      self.__footer
        return self

    def __str__(self):
        return self.__card

    def __format_number(self, InputNumber):

        format = re.sub("(?:\+)?(?:[^[0-9]*)", "", InputNumber)
        FormattedPhoneNumber = "+" + format

        try:
            PhoneNumberObject = phonenumbers.parse(FormattedPhoneNumber, None)
        except Exception as e:
            return ""
        else:
            if not phonenumbers.is_valid_number(PhoneNumberObject):
                return ""

            internationalNumber = phonenumbers.format_number(
                PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            return internationalNumber


if __name__ == '__main__':

    client.start()
    client.loop.run_until_complete(start())
    result = client(functions.contacts.GetContactsRequest(
        hash=0
    )).__dict__['users']
    print(f"You have {len(result)} contacts in telegram")
    while (True):
        cmd = input("Start? [Y/N]: ")
        if cmd.lower() == "y":
            with open(f'TelegramExport{now_str}.vcf', 'w') as f:
                for ae in result:
                    item = ae.__dict__
                    print(generate_card(item), file=f)
            print(f"Saved into TelegramExport{now_str}.vcf")
            client.log_out()
            print("Successful Logout")
            break
        elif cmd.lower() == "n":
            print("Nothing was export")
            client.log_out()
            print("Successful Logout")
            break
        else:
            pass
