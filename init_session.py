from pathlib import Path
import os

from telethon import TelegramClient


def load_env(path: Path) -> None:
    if not path.exists():
        return
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            # Remove any inline comments like ``VALUE  # comment`` and trim
            # whitespace so values match what Docker Compose will load.
            value = value.split('#', 1)[0].strip()
            os.environ.setdefault(key, value)


def get_session_path(raw_path: str) -> Path:
    """Return a path for the session file.

    When executed outside of the Docker container the environment variable is
    typically set to ``/sessions/<name>`` which does not exist locally.  In this
    case we store the file inside the repository's ``sessions/`` directory so it
    gets mounted into the container.  When the ``/sessions`` directory exists
    (inside the container) the path is used as-is.
    """

    path = Path(raw_path)

    if path.is_absolute() and path.parts[:2] == ('/', 'sessions'):
        # Always store the session inside the repository so Docker can mount it.
        # This avoids accidentally writing to an existing ``/sessions``
        # directory on the host which would not be shared with the containers.
        path = Path('sessions') / path.name

    return path


def main() -> None:
    load_env(Path('.env'))
    api_id = int(os.environ['TG_API_ID'])
    api_hash = os.environ['TG_API_HASH']
    phone = os.environ['TG_PHONE_NUMBER']
    session_var = os.environ.get('TG_SESSION_NAME', 'tg_userbot')
    session_path = get_session_path(session_var)
    session_path.parent.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(str(session_path), api_id, api_hash)
    client.start(phone=phone)
    print(f'Session saved to {session_path.with_suffix(".session")}')


if __name__ == '__main__':
    main()
