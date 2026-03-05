"""
content.py — агрегатор эпизодов.

Чтобы добавить новый эпизод:
  1. Создайте episodes/epN.py со словарями SCENES и FLAG_LABELS
  2. Импортируйте его ниже — больше ничего менять не нужно.

Полная последовательность сезона 1:
  ep1  Евгения     — Шах и мат, господа
  ep2  Ирина       — Свет софитов
  ep3  Алина       — Магия мерча
  ep4  Ольга       — Хирургия
  ep5  Екатерина   — Охота на единорога      🚧
  ep6  Виктория    — Алхимия талантов        🚧
  ep7  Анастасия   — Бизнес-тамада           🚧
  ep8  Галина      — Игры тендеров           🚧
  ep9  Ирина HRBP  — Терапия для гения       🚧
  ep10 Все         — System Override (финал)
"""

from episodes import ep1, ep2, ep3, ep4
from episodes import ep5, ep6, ep7, ep8, ep9
from episodes import ep10

# Порядок важен: ep10 регистрируется последним
_ALL_EPISODES = (ep1, ep2, ep3, ep4, ep5, ep6, ep7, ep8, ep9, ep10)

# ── Склейка всех сцен ─────────────────────────────────────────────
SCENES: dict = {}
for _ep in _ALL_EPISODES:
    SCENES.update(_ep.SCENES)

# ── Склейка всех флаг-лейблов ─────────────────────────────────────
FLAG_LABELS: dict = {}
for _ep in _ALL_EPISODES:
    FLAG_LABELS.update(_ep.FLAG_LABELS)


def get_scene(scene_id: str) -> dict | None:
    return SCENES.get(scene_id)
