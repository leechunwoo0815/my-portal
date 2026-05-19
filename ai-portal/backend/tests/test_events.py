import pytest
import asyncio
from app.core.events import EventBus


class TestEventBus:
    def setup_method(self):
        EventBus.clear()

    def test_on_and_emit_sync(self):
        results = []
        EventBus.on("test.event", lambda payload: results.append(payload))
        EventBus.emit_sync("test.event", "hello")
        assert results == ["hello"]

    def test_multiple_handlers(self):
        results = []
        EventBus.on("test.multi", lambda p: results.append(f"a:{p}"))
        EventBus.on("test.multi", lambda p: results.append(f"b:{p}"))
        EventBus.emit_sync("test.multi", "x")
        assert results == ["a:x", "b:x"]

    def test_off_removes_handler(self):
        results = []
        handler = lambda p: results.append(p)
        EventBus.on("test.off", handler)
        EventBus.emit_sync("test.off", "before")
        EventBus.off("test.off", handler)
        EventBus.emit_sync("test.off", "after")
        assert results == ["before"]

    def test_async_emit(self):
        results = []

        async def async_handler(payload):
            results.append(f"async:{payload}")

        EventBus.on("test.async", async_handler)
        asyncio.run(EventBus.emit("test.async", "world"))
        assert results == ["async:world"]

    def test_handler_error_does_not_break_others(self):
        results = []

        def bad_handler(payload):
            raise ValueError("boom")

        def good_handler(payload):
            results.append(payload)

        EventBus.on("test.error", bad_handler)
        EventBus.on("test.error", good_handler)
        EventBus.emit_sync("test.error", "ok")
        assert results == ["ok"]

    def test_clear(self):
        EventBus.on("test.clear", lambda p: None)
        EventBus.clear()
        assert EventBus._handlers == {}

    def test_emit_no_handlers(self):
        EventBus.emit_sync("nonexistent.event", None)
