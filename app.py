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

    username = f"{adj}{noun}#" + str(randint(1000, 9998))
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


async def change_display_name():
    user_id = generate_username()
    user_cache = app.storage.user
    user_cache["uuid"] = user_id
    await ui.refresh()


@ui.page("/")
async def main():
    async def change_display_name():
        user_id = generate_username()
        user_cache = app.storage.user
        user_cache["uuid"] = user_id
        ui.navigate.reload()

    with ui.dialog() as dialog:
        with ui.card().props("rounded outlined").classes(
            "flex-grow shadow-lg shadow-blue-300/50 rounded-full"
        ):
            with ui.column():
                with ui.row():
                    ui.icon("info").classes("text-2xl text-blue-500")
                    ui.label("Reroll User").classes("text-lg font-bold")
                ui.label(
                    "This is an anonymous chat. Either way, you can change your display whenever you want. However your old messages will still be tied to your old ID."
                )
                ui.html(
                    "<span class='text-l'>IMPORTANT:</span><br/>This action will generate a new ID, and you will lose your ties to previous messages."
                ).classes("text-red-500")

            with ui.button_group():
                ok_button = (
                    ui.button("Got it!").props("rounded").style("cursor: pointer")
                )
                cancel_link = ui.button("Cancel").classes("bg-transparent ")
    ok_button.on("click", dialog.close)
    ok_button.on("click", change_display_name)
    cancel_link.on("click", dialog.close)

    ui.html(
        '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">'
    )

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

    avatar = f"https://avatar.iran.liara.run/public/boy?username={user_id}"

    # CSS for linka
    ui.add_css(
        r"a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}"
    )
    # CSS recived message background color
    ui.add_css(
        r".q-message-text--received{background-color: silver}.q-message-text--received:last-child:before{right:100%;border-right:0 solid transparent;border-left:8px solid transparent;border-bottom:8px solid silver}.q-message-name--sent::before  {color: #f1f1f1; content: 'You ';font-size: 13px;;visibility: visible} .q-message-name--sent  {font-size: 0;visibility: hidden}"
    )
    # CSS sent message background color
    ui.add_css(
        r".q-message-text--sent{color: dodgerblue;border-radius:4px 4px 0 4px; background-image: linear-gradient(to right top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);background-image: linear-gradient(to bottom, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);background-image: linear-gradient(to left top, #d16ba5, #c777b9, #ba83ca, #aa8fd8, #9a9ae1, #8aa7ec, #79b3f4, #69bff8, #52cffe, #41dfff, #46eefa, #5ffbf1);}.q-message-text--sent:last-child:before{left:100%;border-left:0 solid transparent;border-right:8px solid transparent;border-bottom:8px solid #D16BA5}"
    )
    with ui.footer().style("background-color:#121212"), ui.column().classes(
        "w-full max-w-3xl mx-auto my-6"
    ):
        with ui.row().classes("w-full no-wrap items-center"):
            with ui.avatar().on("click", dialog.open).style("cursor: pointer"):
                ui.tooltip(f"Change user").props(
                    "transition-show=flip-left transition-hide=flip-right"
                )
                ui.image(avatar)
            text = (
                ui.input(placeholder="Write a message...")
                .on("keydown.enter", send)
                .props("rounded outlined input-class=mx-3")
                .classes("flex-grow shadow-lg shadow-blue-300/50 rounded-full")
            )

    await ui.context.client.connected()
    with ui.column().classes("w-full max-w-2xl mx-auto items-stretch"):
        chat_messages(user_id)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Chat", dark=True, storage_secret="chat")
