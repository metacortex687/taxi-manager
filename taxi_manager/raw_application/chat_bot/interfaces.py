from typing import Generator, Iterator


class IChatBotClient:
    def listen(self) -> Iterator[tuple[str, str]]:  # (text, user_id)
        raise NotImplementedError

    def send(self, user_id: str, message: str):
        raise NotImplementedError
