"""
content.py — агрегатор эпизодов.

Чтобы добавить новый эпизод:
  1. Создайте episodes/ep4.py со словарями SCENES и FLAG_LABELS
  2. Импортируйте его ниже — больше ничего менять не нужно.
"""

from episodes import ep1, ep2, ep3
# from episodes import ep4  ← просто раскомментируйте когда будет готов

# ── Склейка всех сцен ─────────────────────────────────────────────
SCENES: dict = {}
for _ep in (ep1, ep2, ep3):   # ← добавляйте ep4, ep5... сюда
    SCENES.update(_ep.SCENES)

# ── Склейка всех флаг-лейблов (для экрана статистики) ─────────────
FLAG_LABELS: dict = {}
for _ep in (ep1, ep2, ep3):
    FLAG_LABELS.update(_ep.FLAG_LABELS)


def get_scene(scene_id: str) -> dict | None:
    return SCENES.get(scene_id)
