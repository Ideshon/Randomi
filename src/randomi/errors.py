class TemplateError(Exception):
    """
    Ошибка в шаблоне пользователя.

    user_message – текст для пользователя
    local_text   – кусок текста, где нашли ошибку
    local_pos    – позиция символа в local_text
    full_text    – весь plain-text из поля ввода (если известен)
    full_pos     – позиция символа в full_text (если известна)
    inner        – оригинальное исключение/ошибка
    """

    def __init__(
        self,
        user_message: str,
        local_text: str,
        local_pos: int,
        *,
        inner=None,
        full_text: str | None = None,
        full_pos: int | None = None,
    ):
        super().__init__(user_message)
        self.user_message = user_message
        self.text = local_text
        self.pos = local_pos
        self.inner = inner
        self.full_text = full_text
        self.full_pos = full_pos
