#!/usr/bin/env python
import phonenumbers
import re
from datetime import datetime
from telethon import functions
from telethon.sync import TelegramClient

# To get API_ID and API_HASH
# https://my.telegram.org/auth?to=apps
# check 'App configuration' section

API_ID = 000000  # Your API_ID
API_HASH = "#########_YOUR_API_HASH_########"
now_str = f"{datetime.now()}".replace(" ", "_").replace(":", ".")


class VCARD:
    """
    Card generator for Telegram contacts using the builder pattern
    """

    def __init__(self):
        self.__header = "BEGIN:VCARD\n" \
                        "VERSION:3.0\n"
        self.__body_card = ""
        self.__footer = "END:VCARD"

        self.__card = ""
        self.__has_phone = False

    def set_full_name(self, full_name):
        full_name = full_name.replace("None", "")
        self.__body_card += f"FN:{full_name}\n"

        self.__body_card += "N:"
        lst = full_name.split(" ")
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

    def set_phone(self, phone):
        if phone != "" and phone != "None":
            formated_phone = self.__format_number(phone)
            if formated_phone != "":
                self.__body_card += f"TEL;TYPE=CELL:{formated_phone}\n"
                self.__has_phone = True
        return self

    def build(self):
        self.__card = self.__header + \
                      self.__body_card + \
                      self.__footer
        return self

    def __format_number(self, input_number):

        format_num = re.sub("(?:\+)?(?:[^[0-9]*)", "", input_number)
        FormattedPhoneNumber = "+" + format_num

        try:
            PhoneNumberObject = phonenumbers.parse(FormattedPhoneNumber, None)
        except Exception:
            return ""
        else:
            if not phonenumbers.is_valid_number(PhoneNumberObject):
                return ""

            internationalNumber = phonenumbers.format_number(
                PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            return internationalNumber

    def has_phone(self) -> bool:
        return self.__has_phone

    def __str__(self) -> str:
        return self.__card


class TelegramConnection:
    """
        custom TelegramClient with task to get the contact list in telegram
    """
    def __init__(self):
        self.__client = TelegramClient('Contacts_Exporter', api_id=API_ID, api_hash=API_HASH)
        pass

    def connect(self):
        self.__client.start()
        self.__client.loop.run_until_complete(self.__start())

    def disconnect(self):
        self.__client.log_out()
        print("Successful Logout")

    async def __start(self):
        await self.__client.get_me()

    def get_contacts(self) -> list:
        return self.__client(functions.contacts.GetContactsRequest(hash=0)).__dict__['users']


def generate_card(contact_dict):
    card = VCARD()
    card.set_full_name(f"{contact_dict['first_name']} {contact_dict['last_name']}")
    card.set_nickname(f"{contact_dict['username']}")
    card.set_phone(f"{contact_dict['phone']}")
    card.build()
    return card


def save_to_file(_filename_, ignore_mode_, contact_objects):
    ignored = 0
    count = 0
    with open(_filename_, 'w') as f:
        for contact in contact_objects:
            card = generate_card(contact.__dict__)
            if ignore_mode_:
                if card.has_phone():
                    print(card, file=f)
                    count += 1
                else:
                    ignored += 1
            else:
                print(card, file=f)
                count += 1
    print(f"Exported {count}")
    print(f"Ignored {ignored}")
    print(f"Saved into {_filename_}")


if __name__ == '__main__':
    client = TelegramConnection()
    client.connect()
    result = client.get_contacts()
    print(f"You have {len(result)} contacts in telegram")
    while True:
        export = input("Export contacts? [Y/N]: ")
        if export.lower() == "y":
            ignoring = input("ignore contacts without phone? [Y/N]: ")
            if not (ignoring.lower() == "y" or ignoring.lower() == "n"):
                print("Invalid option")
                continue
            else:
                ignore_mode = True if ignoring.lower() == "y" else False
                filename = f"TCExport_no_phone_ignrd_{now_str}.vcf" if ignore_mode else f"TCExport_{now_str}.vcf"
                save_to_file(filename, ignore_mode, result)
                client.disconnect()
                break
        elif export.lower() == "n":
            print("Nothing was export")
            client.disconnect()
            break
        else:
            continue
