# File: src/tests/unit/tags/test_tags_model.py

import uuid
from src.db.models import Tag


def test_tag_repr():
    t = Tag(uid=uuid.uuid4(), name="SciFi")
    assert "<Tag SciFi>" in repr(t)


def test_tag_defaults():
    t = Tag(name="TestTag")
    if t.created_at is not None:
        assert t.created_at is not None
