"""One-time installation/activation gate.

The software is locked until the correct installation key is entered. The
activated flag is stored in a FILE (not the DB) next to the project, so it
survives DB resets/restores and ships/persists with the package.
"""
from pathlib import Path
from django.conf import settings

INSTALL_KEY = 'UFA_Dev_nest-123'


def _flag_path() -> Path:
    return Path(getattr(settings, 'DATA_DIR', settings.BASE_DIR)) / '.activation'


def is_activated() -> bool:
    return _flag_path().exists()


def set_activated() -> None:
    _flag_path().write_text('activated', encoding='utf-8')


def check_key(key: str) -> bool:
    return (key or '').strip() == INSTALL_KEY
