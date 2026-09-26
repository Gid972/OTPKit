from otpkit.storage import MemoryStorage


def test_memory_storage_round_trip_and_delete():
    store = MemoryStorage()
    assert store.get("missing") is None

    store.save("alpha", {"value": 42})
    assert store.get("alpha") == {"value": 42}

    store.update("alpha", {"value": 99})
    assert store.get("alpha") == {"value": 99}

    store.delete("alpha")
    assert store.get("alpha") is None
