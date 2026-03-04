# OMNITECH CHRONICLES — Telegram Bot

Интерактивная визуальная новелла с RPG-механиками в Telegram.  
Эпизод 1: «Шах и мат, господа» — директор по персоналу Евгения против совета директоров.

---

## Структура

```
├── main.py          — бот (telebot), все хэндлеры
├── db.py            — SQLite: игроки, прогресс, статы
├── content.py       — 9 сцен Эпизода 1
├── pyproject.toml   — зависимости (uv)
├── railway.toml     — конфиг деплоя
├── Dockerfile
├── .env.example
└── .gitignore
```

---

## Локальный запуск

```bash
# 1. Установить uv (если нет)
pip install uv

# 2. Установить зависимости
uv sync

# 3. Создать .env
cp .env.example .env
# Вставьте токен от @BotFather в .env

# 4. Запустить
uv run python -B main.py
```

---

## Деплой на Railway

### Способ 1 — через GitHub (рекомендуется)

1. Сделайте fork этого репо или залейте код в свой GitHub
2. Зайдите на [railway.com](https://railway.com) → **New Project → Deploy from GitHub repo**
3. Выберите репозиторий
4. В настройках проекта → **Variables** → добавьте:
   ```
   TELEGRAM_BOT_TOKEN = ваш_токен
   ```
5. Railway автоматически подхватит `railway.toml` и запустит бота ✅

### Способ 2 — через CLI

```bash
npm install -g @railway/cli
railway login
railway init
railway up
railway variables set TELEGRAM_BOT_TOKEN=ваш_токен
```

> ⚠️ **Важно:** `game.db` на Railway хранится в эфемерной файловой системе.  
> При рестарте контейнера прогресс игроков сбросится.  
> Для продакшена замените SQLite на Railway PostgreSQL (плагин в Dashboard).

---

## Команды бота

| Команда    | Действие                          |
|------------|-----------------------------------|
| `/start`   | Начать игру (или перезапустить)   |
| `/stats`   | Текущие статы и флаги             |
| `/restart` | Сбросить и начать заново          |
| `/help`    | Справка                           |

---

## Механики

- 🧠 **Логика / 💛 Эмпатия / 👑 Авторитет** — растут от выборов
- 💎 **Кристаллы** — старт 30 шт., тратятся на премиальные выборы (15–25 💎)
- 🏅 **Флаги** — скрытые маркеры, влияют на финал Эпизода 10
