from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
        text="回答です",
    )
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(
        ask_module.genai,
        "Client",
        lambda **_: SimpleNamespace(
            models=SimpleNamespace(generate_content=lambda **__: response)
        ),
    )

    result = ask_module.ask("質問")

    assert result == "回答です"
    assert "[tokens] 入力: 12, 出力: 7" in capsys.readouterr().out