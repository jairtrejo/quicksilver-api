import uuid
from datetime import datetime

import attr


def _check_text(_, __, value):
    if "jairtrejo" not in value:
        raise ValueError("Prompt must contain my alias (jairtrejo).")


@attr.s
class Prompt:
    prompt = attr.ib(validator=_check_text)
    id = attr.ib(default=attr.Factory(lambda: str(uuid.uuid4())))
    created_at = attr.ib(
        default=attr.Factory(lambda: int(datetime.now().timestamp())),
        converter=int,
    )
    used_at = attr.ib(
        default=None, converter=lambda v: int(v) if v is not None else v
    )

    @property
    def url(self):
        return self.id

    def use(self):
        self.used_at = int(datetime.now().timestamp())

    def asdict(self, *args, **kwargs):
        return attr.asdict(self, *args, **kwargs)
