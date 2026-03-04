"""
OMNITECH CHRONICLES — Telegram Bot (Episode 1 MVP)
Stack : pyTelegramBotAPI (telebot)  +  SQLite
Deploy: Railway
"""

import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from db import init_db, get_player, create_player, update_player, reset_player
from content import get_scene

# ── Config ────────────────────────────────────────────────────────────────────
load_dotenv()
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


# ── Helpers ───────────────────────────────────────────────────────────────────

def stats_line(p: dict) -> str:
    return (
        f"📊 Логика *{p['logic']}*  |  "
        f"Эмпатия *{p['empathy']}*  |  "
        f"Авторитет *{p['authority']}*\n"
        f"💎 Кристаллы: *{p['crystals']}*"
    )


def stats_block(p: dict) -> str:
    flag_labels = {
        "outfit_classic":  "👔 Классический костюм",
        "outfit_iron":     "👠 Железная леди",
        "outfit_reform":   "✨ Реформатор",
        "council_respect": "🏆 Уважение совета",
        "mark_neutral":    "🤝 Марк: нейтрал",
        "mark_ally":       "❤️ Марк: союзник",
        "mark_cold":       "🧊 Марк: закрытый",
    }
    flag_lines = ""
    if p["flags"]:
        flag_lines = "\n\n🏅 *Достижения:*\n" + "\n".join(
            flag_labels.get(f, f"• {f}") for f in p["flags"]
        )
    return (
        "━━━━━━━━━━━━━━━━\n"
        "📈 *Итоги эпизода 1*\n\n"
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
        "Начинаете с 30 💎. Незаблокированные выборы всегда бесплатны.",
    )


# ── Callback handler ──────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    bot.answer_callback_query(call.id)

    user_id = call.from_user.id
    player = get_player(user_id)
    if not player:
        player = create_player(user_id)

    # Parse callback data
    try:
        scene_id, idx_str = call.data.rsplit(":", 1)
        choice_idx = int(idx_str)
    except ValueError:
        return

    # Guard against replaying old buttons
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

    # Crystal check
    if player["crystals"] < cost:
        bot.answer_callback_query(
            call.id,
            f"Не хватает кристаллов! Нужно 💎×{cost}, у вас {player['crystals']}.",
            show_alert=True,
        )
        return

    # Apply effects
    new_crystals  = player["crystals"]  - cost
    new_logic     = player["logic"]     + choice.get("delta_logic",     0)
    new_empathy   = player["empathy"]   + choice.get("delta_empathy",   0)
    new_authority = max(0, player["authority"] + choice.get("delta_authority", 0))

    flags = player["flags"][:]
    flag = choice.get("flag")
    if flag and flag not in flags:
        flags.append(flag)

    next_scene = choice.get("next", "ep1_end")

    # Restart
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

    # Flavour text
    result_text = choice.get("result_text", "")
    if result_text:
        bot.send_message(call.message.chat.id, result_text)

    send_scene(call.message.chat.id, player, next_scene)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("✅ OmniTech bot started (polling)…")
    bot.infinity_polling()
