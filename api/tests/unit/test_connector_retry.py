"""Tests for ``app.integrations.connectors.retry.retry_request``.

Pure-unit tests \u2014 no real HTTP, no DB. The factory pattern means
we can mock ``send`` with a list of pre-baked outcomes (exceptions
and ``httpx.Response`` stubs) and assert on attempt count, sleep
durations, and the final return/raise.
"""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio

from app.integrations.connectors import retry as retry_module

pytestmark = pytest.mark.asyncio(loop_scope="session")


# Pure unit tests \u2014 no DB.
@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    yield


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch):
    """Don't actually sleep in tests \u2014 record requested durations instead."""
    sleeps: list[float] = []

    async def _fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(retry_module.asyncio, "sleep", _fake_sleep)
    return sleeps


@pytest.fixture(autouse=True)
def _deterministic_jitter(monkeypatch):
    """Force the jitter PRNG to always return the upper bound so the
    backoff schedule is deterministic in tests."""
    monkeypatch.setattr(retry_module.random, "uniform", lambda _lo, hi: hi)


def _response(status_code: int, headers: dict[str, str] | None = None) -> httpx.Response:
    return httpx.Response(status_code=status_code, headers=headers or {})


class TestSuccessPath:
    async def test_returns_first_response_when_2xx(self, _no_real_sleep):
        calls = 0

        async def send():
            nonlocal calls
            calls += 1
            return _response(200)

        result = await retry_module.retry_request(send, description="test.ok")
        assert result.status_code == 200
        assert calls == 1
        assert _no_real_sleep == []

    async def test_does_not_retry_on_4xx(self, _no_real_sleep):
        """4xx other than 429 is a caller bug \u2014 propagate the response."""
        calls = 0

        async def send():
            nonlocal calls
            calls += 1
            return _response(400)

        result = await retry_module.retry_request(send, description="test.client-error")
        assert result.status_code == 400
        assert calls == 1
        assert _no_real_sleep == []


class TestStatusRetries:
    async def test_retries_on_503_then_succeeds(self, _no_real_sleep):
        statuses = iter([503, 503, 200])

        async def send():
            return _response(next(statuses))

        result = await retry_module.retry_request(send, description="test.503", base_delay_seconds=1.0)
        assert result.status_code == 200
        # 2 retries \u2192 2 sleeps with deterministic full-jitter upper bound.
        assert _no_real_sleep == [1.0, 2.0]

    async def test_returns_last_response_when_all_attempts_5xx(self, _no_real_sleep):
        async def send():
            return _response(502)

        result = await retry_module.retry_request(send, description="test.5xx", max_attempts=3)
        assert result.status_code == 502
        # 3 attempts \u2192 only 2 sleeps (the third fail is final).
        assert len(_no_real_sleep) == 2

    async def test_honours_retry_after_header(self, _no_real_sleep):
        statuses = iter([(429, {"Retry-After": "5"}), (200, {})])

        async def send():
            code, hdrs = next(statuses)
            return _response(code, hdrs)

        result = await retry_module.retry_request(send, description="test.429")
        assert result.status_code == 200
        # Retry-After=5 should override the default 1s base backoff.
        assert _no_real_sleep == [5.0]

    async def test_caps_excessive_retry_after(self, _no_real_sleep):
        """A misconfigured upstream sending Retry-After: 99999 shouldn't
        block the scheduler for 27 hours."""
        statuses = iter([(429, {"Retry-After": "99999"}), (200, {})])

        async def send():
            code, hdrs = next(statuses)
            return _response(code, hdrs)

        await retry_module.retry_request(send, description="test.429-capped")
        assert _no_real_sleep[0] == retry_module._MAX_RETRY_AFTER_SECONDS

    async def test_ignores_malformed_retry_after(self, _no_real_sleep):
        statuses = iter([(429, {"Retry-After": "tomorrow"}), (200, {})])

        async def send():
            code, hdrs = next(statuses)
            return _response(code, hdrs)

        await retry_module.retry_request(send, description="test.bad-header", base_delay_seconds=1.0)
        # Falls back to standard backoff (attempt=0 -> base*2^0 = 1.0).
        assert _no_real_sleep == [1.0]


class TestExceptionRetries:
    async def test_retries_on_connect_error_then_succeeds(self, _no_real_sleep):
        outcomes: list[object] = [
            httpx.ConnectError("refused"),
            _response(200),
        ]

        async def send():
            item = outcomes.pop(0)
            if isinstance(item, BaseException):
                raise item
            return item

        result = await retry_module.retry_request(send, description="test.connect", base_delay_seconds=1.0)
        assert result.status_code == 200
        assert _no_real_sleep == [1.0]

    async def test_does_not_retry_unknown_exception(self):
        """A bug in the caller (TypeError, ValueError, etc.) should propagate."""

        async def send():
            raise ValueError("caller bug")

        with pytest.raises(ValueError, match="caller bug"):
            await retry_module.retry_request(send, description="test.bug")

    async def test_re_raises_after_max_attempts(self, _no_real_sleep):
        async def send():
            raise httpx.ConnectTimeout("nope")

        with pytest.raises(httpx.ConnectTimeout):
            await retry_module.retry_request(send, description="test.fail", max_attempts=2)
        # 2 attempts \u2192 1 sleep before the final raise.
        assert len(_no_real_sleep) == 1


class TestBackoffSchedule:
    async def test_exponential_growth_capped(self, _no_real_sleep):
        async def send():
            return _response(500)

        await retry_module.retry_request(
            send,
            description="test.cap",
            max_attempts=5,
            base_delay_seconds=1.0,
            max_delay_seconds=3.0,
        )
        # attempt 0 -> 1.0, 1 -> 2.0, 2 -> 3.0 (capped), 3 -> 3.0 (capped).
        assert _no_real_sleep == [1.0, 2.0, 3.0, 3.0]
