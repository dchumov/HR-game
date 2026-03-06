"""
OMNITECH CHRONICLES — Telegram Bot
Stack : pyTelegramBotAPI (telebot)  +  SQLite
Deploy: Railway

main.py никогда не меняется при добавлении новых эпизодов.
Все флаги и сцены живут в episodes/epN.py
"""

import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from db import init_db, get_player, create_player, update_player, reset_player
from content import get_scene, FLAG_LABELS

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Telegram limits
CAPTION_LIMIT = 1024


# ── Helpers ───────────────────────────────────────────────────────────────────

def stats_line(p: dict) -> str:
    return (
        f"📊 Логика *{p['logic']}*  |  "
        f"Эмпатия *{p['empathy']}*  |  "
        f"Авторитет *{p['authority']}*\n"
        f"💎 Кристаллы: *{p['crystals']}*"
    )


def stats_block(p: dict) -> str:
    flag_lines = ""
    if p["flags"]:
        flag_lines = "\n\n🏅 *Достижения:*\n" + "\n".join(
            FLAG_LABELS.get(f, f"• {f}") for f in p["flags"]
        )
    return (
        "━━━━━━━━━━━━━━━━\n"
        "📈 *Итоги эпизода*\n\n"
        f"🧠 Логика:     *{p['logic']}*\n"
        f"💛 Эмпатия:    *{p['empathy']}*\n"
        f"👑 Авторитет:  *{p['authority']}*\n"
        f"💎 Кристаллы:  *{p['crystals']}* (осталось)"
        f"{flag_lines}"
    )


def build_keyboard(scene_id: str, choices: list, crystals: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for i, choice in enumerate(choices):
        cost = choice.get("cost", 0)
        label = choice["label"]
        if cost > 0:
            label = f"💎×{cost} {label}" if crystals >= cost else f"🔒 💎×{cost} {label}"
        kb.add(InlineKeyboardButton(label, callback_data=f"{scene_id}:{i}"))
    return kb


def send_scene(chat_id: int, player: dict, scene_id: str):
    scene = get_scene(scene_id)
    if not scene:
        bot.send_message(chat_id, "⚠️ Сцена не найдена.")
        return

    text = scene["text"]
    if scene.get("show_final_stats"):
        text = stats_block(player) + "\n\n" + text
    else:
        text += "\n\n" + stats_line(player)

    choices = scene.get("choices", [])
    kb = build_keyboard(scene_id, choices, player["crystals"]) if choices else None

    # Send image if file exists — tries .jpeg / .jpg / .png variants
    image_file = scene.get("image")
    if image_file:
        base = image_file.rsplit(".", 1)[0]
        candidates = [image_file, base + ".jpeg", base + ".jpg", base + ".png"]
        candidates = list(dict.fromkeys(candidates))
        for candidate in candidates:
            image_path = os.path.join("images", candidate)
            if os.path.isfile(image_path):
                with open(image_path, "rb") as img:
                    # ── ФИКС: Telegram caption limit = 1024 символа ──────────
                    # Если текст длиннее — отправляем фото отдельно,
                    # клавиатуру прикрепляем к текстовому сообщению.
                    if len(text) <= CAPTION_LIMIT:
                        bot.send_photo(
                            chat_id, img,
                            caption=text,
                            parse_mode="Markdown",
                            reply_markup=kb,
                        )
                    else:
                        bot.send_photo(chat_id, img)
                        bot.send_message(
                            chat_id, text,
                            parse_mode="Markdown",
                            reply_markup=kb,
                        )
                return

    # Fallback: text only
    bot.send_message(chat_id, text, reply_markup=kb)


# ── Command handlers ──────────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    if player is None:
        player = create_player(user_id)
    else:
        player = reset_player(user_id)

    bot.send_message(
        message.chat.id,
        "💻 *HR‑КОД: СБОЙ В СИСТЕМЕ* 💻\n\n"
        "Вас ждёт история девяти девушек‑HR, которые спасут IT‑гигант OmniTech\n"
        "от бюрократии, багов и корпоративного саботажа.\n\n"
        "Прокачивайте *Логику*, *Эмпатию* и *Авторитет*.\n"
        "Тратьте 💎 кристаллы на премиальные выборы — они открывают лучшие исходы.\n\n"
        "🎀 С 8 марта, коллеги! Давайте начнём!",
    )
    send_scene(message.chat.id, player, "ep1_intro")


@bot.message_handler(commands=["stats"])
def cmd_stats(message):
    player = get_player(message.from_user.id)
    if not player:
        bot.send_message(message.chat.id, "Сначала начните игру — /start")
        return
    bot.send_message(message.chat.id, stats_block(player))


@bot.message_handler(commands=["restart"])
def cmd_restart(message):
    user_id = message.from_user.id
    player = get_player(user_id)
    player = reset_player(user_id) if player else create_player(user_id)
    bot.send_message(message.chat.id, "🔄 *Начинаем заново!*")
    send_scene(message.chat.id, player, "ep1_intro")


@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(
        message.chat.id,
        "📖 *Команды:*\n\n"
        "/start — начать игру\n"
        "/stats — ваши статы и флаги\n"
        "/restart — сбросить и начать заново\n\n"
        "💎 *Кристаллы* — валюта для премиальных выборов.\n"
        "Начинаете с 30 💎. За каждый новый эпизод получаете +10 💎.",
    )


# ── Callback handler ──────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    player = get_player(user_id)
    if not player:
        player = create_player(user_id)

    try:
        scene_id, idx_str = call.data.rsplit(":", 1)
        choice_idx = int(idx_str)
    except ValueError:
        return

    if player["scene"] != scene_id:
        bot.answer_callback_query(call.id, "Это решение уже принято.", show_alert=True)
        return

    scene = get_scene(scene_id)
    if not scene:
        return

    choices = scene.get("choices", [])
    if choice_idx >= len(choices):
        return

    choice = choices[choice_idx]
    cost = choice.get("cost", 0)

    if player["crystals"] < cost:
        bot.answer_callback_query(
            call.id,
            f"Не хватает кристаллов! Нужно 💎×{cost}, у вас {player['crystals']}.",
            show_alert=True,
        )
        return

    new_crystals  = player["crystals"]  - cost
    new_logic     = player["logic"]     + choice.get("delta_logic",     0)
    new_empathy   = player["empathy"]   + choice.get("delta_empathy",   0)
    new_authority = max(0, player["authority"] + choice.get("delta_authority", 0))

    flags = player["flags"][:]
    flag = choice.get("flag")
    if flag and flag not in flags:
        flags.append(flag)

    next_scene = choice.get("next", "ep1_end")

    # Начисляем +10 кристаллов при переходе на новый эпизод
    current_ep = scene_id.split("_")[0]
    next_ep = next_scene.split("_")[0]
    if next_ep != current_ep and next_ep.startswith("ep"):
        new_crystals += 10

    if next_scene == "__ending_router__":
        # ── ФИКС: учитываем и базовые, и премиальные флаги союзников ─────────
        # Каждая пара — это (базовый флаг, премиальный флаг) одного эпизода.
        # Достаточно получить хотя бы один из двух.
        ally_flag_groups = [
            {"council_respect"},                          # ep1
            {"media_star"},                               # ep2
            {"team_loyalty"},                             # ep3
            {"fired_toxic"},                              # ep4
            {"hired_visioner", "hired_visioner_perfect"}, # ep5 — оба варианта
            {"mentorship_succ", "invisible_success"},     # ep6 — оба варианта
            {"vendor_defeated", "vendor_crushed"},        # ep8 — оба варианта
        ]
        flag_set = set(flags)
        flag_count = sum(
            1 for group in ally_flag_groups
            if group & flag_set  # хотя бы один флаг из группы есть у игрока
        )
        authority = new_authority

        if flag_count >= 7 or (flag_count >= 5 and authority >= 5):
            next_scene = "ep10_perfect"
        elif flag_count >= 4:
            next_scene = "ep10_strong"
        elif flag_count >= 2:
            next_scene = "ep10_steady"
        else:
            next_scene = "ep10_foundation"

    if next_scene == "__restart__":
        player = reset_player(user_id)
        bot.send_message(call.message.chat.id, "🔄 *Начинаем заново!*")
        send_scene(call.message.chat.id, player, "ep1_intro")
        return

    update_player(
        user_id,
        scene=next_scene,
        logic=new_logic,
        empathy=new_empathy,
        authority=new_authority,
        crystals=new_crystals,
        flags=flags,
    )
    player = get_player(user_id)

    result_text = choice.get("result_text", "")
    if result_text:
        bot.send_message(call.message.chat.id, result_text)

    send_scene(call.message.chat.id, player, next_scene)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    os.makedirs("images", exist_ok=True)
    print("✅ OmniTech bot started (polling)…")
    bot.infinity_polling()
