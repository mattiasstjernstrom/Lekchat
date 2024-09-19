from datetime import datetime, timezone
from typing import List, Tuple

from nicegui import app, ui
import random
from random import randint

from word_list import adjectives, nouns

messages: List[Tuple[str, str, str, str]] = []
user_id = None


def generate_username():
    adj_key = random.choice(list(adjectives.keys()))
    noun_key = random.choice(list(nouns.keys()))

    adj = adjectives[adj_key]
    noun = nouns[noun_key]

    username = f"{adj}{noun}#" + str(randint(0000, 9999))

    return username


@ui.refreshable
def chat_messages(own_id: str) -> None:
    if messages:
        for user_id, avatar, text, stamp in messages:
            ui.chat_message(
                name=user_id,
                text=text,
                stamp=stamp,
                avatar=avatar,
                sent=own_id == user_id,
            )
    else:
        ui.label("No messages yet").classes("mx-auto my-16")

    ui.run_javascript("window.scrollTo(0, document.body.scrollHeight)")


@ui.page("/")
async def main():
    def send() -> None:
        stamp = datetime.now(timezone.utc).strftime("%H:%M")
        messages.append((user_id, avatar, text.value, stamp))
        text.value = ""
        chat_messages.refresh()

    user_cache = app.storage.user
    if "uuid" in user_cache:
        user_id = user_cache["uuid"]
    else:
        user_id = generate_username()
        user_cache["uuid"] = user_id

    avatar = f"https://robohash.org/{user_id}?bgset=bg&set=set4"

    ui.add_css(
        r"a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}"
    )
    with ui.row(align_items="center").classes("w-full p-4 bg-gray-800"):
        ui.label(f"{user_id}").style("font-size: 2rem")
    with ui.footer().style("background-color:#121212"), ui.column().classes(
        "w-full max-w-3xl mx-auto my-6"
    ):
        with ui.row().classes("w-full no-wrap items-center"):
            with ui.avatar().on("click", lambda: ui.navigate.to(main)).style(
                "cursor: pointer"
            ):
                ui.tooltip("Reload")
                ui.image(avatar)
            text = (
                ui.input(placeholder="message")
                .on("keydown.enter", send)
                .props("rounded outlined input-class=mx-3")
                .classes("flex-grow shadow-lg shadow-blue-300/50 rounded-full")
            )

    await ui.context.client.connected()
    with ui.column().classes("w-full max-w-2xl mx-auto items-stretch"):
        chat_messages(user_id)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Chat", dark=True, storage_secret="chat")
