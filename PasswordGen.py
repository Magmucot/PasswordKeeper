import secrets
from enum import Enum, IntEnum
from math import log2
from typing import Dict, Optional


class Characters(Enum):
    """Перечисление типов символов для пароля."""

    btn_up = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    btn_lower = "abcdefghijklmnopqrstuvwxyz"
    btn_nums = "0123456789"
    btn_spec = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""


GENERATE_PASSWORD = ("btn_refresh", "btn_lower", "btn_up", "btn_nums", "btn_spec")

CHARACTER_NUMBER = {
    "btn_lower": len(Characters.btn_lower.value),
    "btn_up": len(Characters.btn_up.value),
    "btn_nums": len(Characters.btn_nums.value),
    "btn_spec": len(Characters.btn_spec.value),
}


class StrengthToEntropy(IntEnum):
    """Уровни энтропии пароля."""

    СЛАБЕЙШИЙ = 0
    Слабый = 30
    Норм = 50
    Хороший = 70
    Прекрасный = 120
    БОЖЕСТВЕННЫЙ = 1000


def generate_password(
    ln: int, chars: str, min_counts: Optional[Dict[str, int]] = None
) -> str:
    """
    Генерирует пароль с учетом минимумов для каждого типа символов.
    ln: Общая длина пароля.
    chars: Доступные символы (объединенные).
    min_counts: Dict с минимумами, e.g., {'btn_lower': 1, 'btn_up': 1}.
    Если None, игнорирует минимумы.
    """
    if ln <= 0 or not chars:
        return ""
    min_counts = min_counts or {}
    password_parts = []
    used_length = 0
    for type_key, min_count in min_counts.items():
        if min_count > 0 and type_key in CHARACTER_NUMBER:
            type_chars = next(c.value for c in Characters if c.name == type_key)
            for _ in range(min_count):
                if used_length < ln:
                    password_parts.append(secrets.choice(type_chars))
                    used_length += 1
    remaining_length = ln - used_length
    for _ in range(remaining_length):
        password_parts.append(secrets.choice(chars))
    secrets.SystemRandom().shuffle(password_parts)
    return "".join(password_parts)


def get_entropy(ln: int, char_num: int, min_diversity: int = 1) -> float:
    """
    Вычисляет энтропию с учетом разнообразия (минимумы типов).
    ln: Длина пароля.
    char_num: Общее число уникальных символов.
    min_diversity: Кол-во типов с минимумом (для корректировки).
    """

    if ln <= 0 or char_num <= 0:
        return 0.0

    base_entropy = ln * log2(char_num)

    adjusted = base_entropy * (1 + (min_diversity - 1) * 0.05)
    return round(adjusted, 3)
