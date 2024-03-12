import hashlib


__all__ = ["convert_text_into_hash"]


def convert_text_into_hash(value: str):
    """
    Функция хеширует строку

    value: str
        Строка которую будем хешировать
    """

    answer = hashlib.sha256(value.encode()).hexdigest()

    return answer


if __name__ == "__main__":
    pass
