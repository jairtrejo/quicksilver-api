import pytest


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("CORS_DOMAIN", "lyftbutton.fake")
    monkeypatch.setenv("TOKEN_SECRET", "somesecret")
    monkeypatch.setenv("LYFT_CLIENT_ID", "lyft:fakeid")
    monkeypatch.setenv("LYFT_CLIENT_SECRET", "lyft:fakesecret")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google:fakeid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google:fakesecret")
