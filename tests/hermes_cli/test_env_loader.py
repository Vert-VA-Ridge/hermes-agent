import importlib
import os
import sys
from types import SimpleNamespace

from hermes_cli.env_loader import load_hermes_dotenv


def test_user_env_overrides_stale_shell_values(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    home.mkdir()
    env_file = home / ".env"
    env_file.write_text("OPENAI_BASE_URL=https://new.example/v1\n", encoding="utf-8")

    monkeypatch.setenv("OPENAI_BASE_URL", "https://old.example/v1")

    loaded = load_hermes_dotenv(hermes_home=home)

    assert loaded == [env_file]
    assert os.getenv("OPENAI_BASE_URL") == "https://new.example/v1"


def test_project_env_overrides_stale_shell_values_when_user_env_missing(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    project_env = tmp_path / ".env"
    project_env.write_text("OPENAI_BASE_URL=https://project.example/v1\n", encoding="utf-8")

    monkeypatch.setenv("OPENAI_BASE_URL", "https://old.example/v1")

    loaded = load_hermes_dotenv(hermes_home=home, project_env=project_env)

    assert loaded == [project_env]
    assert os.getenv("OPENAI_BASE_URL") == "https://project.example/v1"


def test_project_env_is_sanitized_before_loading(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    project_env = tmp_path / ".env"
    project_env.write_text(
        "TELEGRAM_BOT_TOKEN=0123456789:test"
        "ANTHROPIC_API_KEY=sk-ant-test123\n",
        encoding="utf-8",
    )

    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    loaded = load_hermes_dotenv(hermes_home=home, project_env=project_env)

    assert loaded == [project_env]
    assert os.getenv("TELEGRAM_BOT_TOKEN") == "0123456789:test"
    assert os.getenv("ANTHROPIC_API_KEY") == "sk-ant-test123"


def test_user_env_takes_precedence_over_project_env(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    home.mkdir()
    user_env = home / ".env"
    project_env = tmp_path / ".env"
    user_env.write_text("OPENAI_BASE_URL=https://user.example/v1\n", encoding="utf-8")
    project_env.write_text("OPENAI_BASE_URL=https://project.example/v1\nOPENAI_API_KEY=project-key\n", encoding="utf-8")

    monkeypatch.setenv("OPENAI_BASE_URL", "https://old.example/v1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    loaded = load_hermes_dotenv(hermes_home=home, project_env=project_env)

    assert loaded == [user_env, project_env]
    assert os.getenv("OPENAI_BASE_URL") == "https://user.example/v1"
    assert os.getenv("OPENAI_API_KEY") == "project-key"


def test_null_bytes_in_user_env_are_stripped(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    home.mkdir()
    env_file = home / ".env"
    # Null bytes can be introduced when copy-pasting API keys.
    env_file.write_text("GLM_API_KEY=abc\x00\x00\nOPENAI_API_KEY=sk-123\n", encoding="utf-8")

    monkeypatch.delenv("GLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    loaded = load_hermes_dotenv(hermes_home=home)

    assert loaded == [env_file]
    assert os.getenv("GLM_API_KEY") == "abc"
    assert os.getenv("OPENAI_API_KEY") == "sk-123"


def test_named_profile_inherits_only_global_provider_credentials(tmp_path, monkeypatch):
    root = tmp_path / "hermes"
    home = root / "profiles" / "analyst"
    home.mkdir(parents=True)
    (root / ".env").write_text(
        "ANTHROPIC_API_KEY=global-anthropic\n"
        "FIREWORKS_API_KEY=global-fireworks\n"
        "PERPLEXITY_API_KEY=global-perplexity\n"
        "TAVILY_API_KEY=must-not-leak\n",
        encoding="utf-8",
    )
    (home / ".env").write_text("FIREWORKS_API_KEY=profile-fireworks\n", encoding="utf-8")
    (home / "config.yaml").write_text(
        "providers:\n"
        "  perplexity:\n"
        "    base_url: https://api.perplexity.ai\n"
        "    key_env: PERPLEXITY_API_KEY\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "hermes_cli.provider_catalog.provider_catalog",
        lambda: [SimpleNamespace(api_key_env_vars=("ANTHROPIC_API_KEY", "FIREWORKS_API_KEY"))],
    )
    for key in ("ANTHROPIC_API_KEY", "FIREWORKS_API_KEY", "PERPLEXITY_API_KEY", "TAVILY_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    load_hermes_dotenv(hermes_home=home)

    assert os.getenv("ANTHROPIC_API_KEY") == "global-anthropic"
    assert os.getenv("FIREWORKS_API_KEY") == "profile-fireworks"
    assert os.getenv("PERPLEXITY_API_KEY") == "global-perplexity"
    assert os.getenv("TAVILY_API_KEY") is None


def test_named_profile_blank_provider_key_suppresses_global_fallback(tmp_path, monkeypatch):
    root = tmp_path / "hermes"
    home = root / "profiles" / "analyst"
    home.mkdir(parents=True)
    (root / ".env").write_text("ANTHROPIC_API_KEY=global-anthropic\n", encoding="utf-8")
    (home / ".env").write_text("ANTHROPIC_API_KEY=\n", encoding="utf-8")

    monkeypatch.setattr(
        "hermes_cli.provider_catalog.provider_catalog",
        lambda: [SimpleNamespace(api_key_env_vars=("ANTHROPIC_API_KEY",))],
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    load_hermes_dotenv(hermes_home=home)

    assert os.getenv("ANTHROPIC_API_KEY") == ""


def test_main_import_applies_user_env_over_shell_values(tmp_path, monkeypatch):
    home = tmp_path / "hermes"
    home.mkdir()
    (home / ".env").write_text(
        "OPENAI_BASE_URL=https://new.example/v1\nHERMES_INFERENCE_PROVIDER=custom\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setenv("OPENAI_BASE_URL", "https://old.example/v1")
    monkeypatch.setenv("HERMES_INFERENCE_PROVIDER", "openrouter")

    sys.modules.pop("hermes_cli.main", None)
    importlib.import_module("hermes_cli.main")

    assert os.getenv("OPENAI_BASE_URL") == "https://new.example/v1"
    assert os.getenv("HERMES_INFERENCE_PROVIDER") == "custom"
