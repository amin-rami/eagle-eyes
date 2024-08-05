from django.db import models
import sys

"""
sample = {
    "user_id": "...",
    "label": "امپراطور",
    "level": 14,
    "played": 84,
    "game_states": [{
        "id": 1,
        "label": "آکبند",
        "level": 2,
        "played": 4,
        "remaining": 1,
        "progress": "0.8"
    }, {
        "id": 2,
        "label": "تکاور",
        "level": 12,
        "played": 2,
        "remaining": 3,
        "progress": "0.4"
    }]
}
"""


class UserState(models.Model):
    user_id = models.CharField(
        primary_key=True,
        max_length=512
    )
    label = models.CharField(blank=True, max_length=512)
    level = models.PositiveIntegerField(default=0)
    played = models.PositiveIntegerField(default=0)
    game_states = models.JSONField(default=dict)


labels = {
    range(0, 1): '',
    range(1, 3): "آکبند",
    range(3, 5): "پیرو",
    range(5, 7): "دلیر",
    range(7, 10): "خودساخته",
    range(10, 15): "تکاور",
    range(15, 20): "سالار",
    range(20, 25): "پرآوازه",
    range(25, 30): "استاد",
    range(30, 35): "کمانگیر",
    range(35, 40): "فاتح",
    range(40, 45): "نامدار",
    range(45, 50): "یاغی",
    range(50, 55): "آذرخش",
    range(55, 60): "پهلوان",
    range(60, 65): "سرور",
    range(65, 70): "استاد بزرگ",
    range(70, 75): "افسانه",
    range(75, 80): "سلطان ",
    range(80, 85): "قهرمان",
    range(85, 90): "امپراطور",
    range(90, 95): "تهمتن",
    range(95, 100): "سپهسالار",
    range(100, sys.maxsize): "اسطوره"
}

level_ups = {
    range(0, 11): 5,
    range(11, 21): 10,
    range(21, 51): 20,
    range(51, 71): 50,
    range(71, 101): 100,
    range(101, sys.maxsize): 200
}
