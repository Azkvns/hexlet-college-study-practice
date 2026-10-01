def validate_partner(data: dict) -> None:
    name = data.get("name")
    if name is None or not str(name).strip():
        raise ValueError("Наименование обязательно и не может быть пустым")

    inn = data.get("inn")
    if inn is None or not str(inn).strip():
        raise ValueError("ИНН обязателен и не может быть пустым")

    email = data.get("email")
    if email is None or not str(email).strip():
        raise ValueError("Email обязателен и не может быть пустым")

    rating = data.get("rating")
    if type(rating) is not int or rating < 0:
        raise ValueError(
            "Рейтинг должен быть целым числом от 0. "
            "Пожалуйста, удалите знаки препинания и повторите попытку"
        )
