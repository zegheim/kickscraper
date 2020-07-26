import os
import requests
import telegram

from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse


class EiyudenBot:
    def __init__(self, chat_id, token):
        self.chat_id = chat_id
        self.bot = telegram.Bot(token)

    def send_message(self, message, disable_notification=False, parse_mode=None):
        self.bot.send_chat_action(
            chat_id=self.chat_id, action=telegram.ChatAction.TYPING
        )
        self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            disable_notification=disable_notification,
            parse_mode=parse_mode,
        )


def is_success():
    return os.path.isfile("success")


def set_success():
    with open("success", "w+"):
        pass


def strip_query_str(url):
    return urljoin(url, urlparse(url).path)


def main():
    if is_success():
        return

    load_dotenv()

    params = {"term": os.getenv("SEARCH_TERM"), "page": 1}
    headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
    res = requests.get(os.getenv("BASE_URL"), params=params, headers=headers).json()

    projects = res["projects"]

    while res["has_more"]:
        params["page"] += 1
        res = requests.get(os.getenv("BASE_URL"), params=params, headers=headers).json()
        projects += res["projects"]

    urls = [strip_query_str(p["urls"]["web"]["project"]) for p in projects]

    if not urls:
        return

    set_success()

    bot = EiyudenBot(chat_id=os.getenv("CHAT_ID"), token=os.getenv("BOT_TOKEN"))
    bot.send_message(
        f"Received *{res['total_hits']}* result(s) for search term *{os.getenv('SEARCH_TERM')}*:\n\n"
        + "\n".join(
            f"{idx:02d}. [{url.split('/')[-1]}]({url})"
            for idx, url in enumerate(urls, 1)
        ),
        parse_mode="markdown",
        disable_notification=(not res["total_hits"]),
    )


if __name__ == "__main__":
    main()
