from types import SimpleNamespace
from unittest.mock import Mock

import app.ask as ask_module


def test_main_keeps_chat_history_for_follow_up_questions(monkeypatch, capsys):
    chat = SimpleNamespace(
        send_message=Mock(
            side_effect=[
                SimpleNamespace(
                    text="最初の回答",
                    usage_metadata=SimpleNamespace(
                        prompt_token_count=10,
                        candidates_token_count=5,
                    ),
                ),
                SimpleNamespace(
                    text="続きの回答",
                    usage_metadata=SimpleNamespace(
                        prompt_token_count=20,
                        candidates_token_count=8,
                    ),
                ),
            ]
        )
    )
    create_chat = Mock(return_value=chat)
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.chats.create = create_chat
    client_factory = Mock(return_value=client)
    monkeypatch.setattr(ask_module.genai, "Client", client_factory)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    questions = iter(["追加の質問", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))

    ask_module.main()

    client_factory.assert_called_once_with(api_key="test-key")
    client.__enter__.assert_called_once_with()
    client.__exit__.assert_called_once()
    create_chat.assert_called_once_with(model=ask_module.MODEL)
    assert [call.args[0] for call in chat.send_message.call_args_list] == [
        "最初の質問",
        "追加の質問",
    ]
    output = capsys.readouterr().out
    assert "最初の回答" in output
    assert "続きの回答" in output
    assert "[トークン数] 入力: 10、出力: 5" in output
    assert "[トークン数] 入力: 20、出力: 8" in output
