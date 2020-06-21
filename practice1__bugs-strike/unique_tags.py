from typing import List

import json

json_data = """{
    "title": "Звездные войны 1: Империя приносит баги",
    "description": "Эпичная сага по поиску багов в старом легаси проекте Империи",
    "tags": [2, "семейное кино", "космос", 1.0, "сага", "эпик", "добро против зла", true, "челмедведосвин", "debug", "ipdb", "PyCharm", "боевик", "боевик", "эникей", "дарт багус", 5, 6,4, "блокбастер", "кино 2020", 7, 3, 9, 12, "каникулы в космосе", "коварство"],
    "version": 17
    }"""


def unique_tags(payload: dict) -> List[str]:
    # исправьте ошибку
    result = []
    tags = payload.get('tags', [])
    for tag in tags:
        if tag in result:
            if str(result[result.index(tag)]) == str(tag):
                continue
        result.append(tag)
    return result


unique_tags(json.loads(json_data))
