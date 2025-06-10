import pytest
from unittest.mock import AsyncMock, MagicMock
import bot

@pytest.mark.asyncio
async def test_recebe_qualquer_mensagem():
    # Mock do update e message
    mock_message = MagicMock()
    mock_message.text = "oi"
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock()
    mock_update.effective_user.id = 1234
    mock_update.message = mock_message
    mock_context = MagicMock()

    await bot.receber_mensagem(mock_update, mock_context)
    mock_message.reply_text.assert_called_with("Para continuar, utilize /entrar ou /sair.")

@pytest.mark.asyncio
async def test_comando_sair():
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update = MagicMock()
    mock_update.effective_user.id = 1234
    mock_update.message = mock_message
    mock_context = MagicMock()

    await bot.sair(mock_update, mock_context)
    mock_message.reply_text.assert_called_with("Você saiu. Até logo!")
