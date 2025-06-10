import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
import os
from dotenv import load_dotenv
from bot_auth import autenticar_usuario

# Carregar variáveis do .env
load_dotenv()

# Configuração básica de logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('BOT_TELEGRAM_API')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuário {update.effective_user.id} iniciou o bot.")
    await update.message.reply_text(
        "Bem-vindo! Você pode usar os comandos /entrar ou /sair para continuar."
    )

async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuário {update.effective_user.id} saiu do fluxo.")
    await update.message.reply_text("Você saiu. Até logo!")

async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Mensagem recebida de {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(
        "Para continuar, utilize /entrar ou /sair."
    )

async def entrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuário {update.effective_user.id} iniciou autenticação com /entrar.")
    await update.message.reply_text("Digite seu nome de usuário:")
    return 1

async def receber_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.message.text.strip()
    context.user_data['usuario'] = usuario
    logger.info(f"Usuário {update.effective_user.id} enviou nome de usuário: {usuario}")
    keyboard = [
        [InlineKeyboardButton("Confirmar", callback_data="confirmar_usuario")],
        [InlineKeyboardButton("Cancelar", callback_data="cancelar_usuario")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Confirme o usuário: {usuario}", reply_markup=reply_markup)
    return 2

async def confirmar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirmar_usuario":
        usuario = context.user_data.get('usuario', 'N/A')
        logger.info(f"Usuário {update.effective_user.id} confirmou usuário: {usuario}")
        await query.edit_message_text(f"Usuário confirmado: {usuario}\nAgora digite sua senha:")
        return 3
    else:
        logger.info(f"Usuário {update.effective_user.id} cancelou autenticação.")
        await query.edit_message_text("Operação cancelada. Use /entrar para tentar novamente.")
        return ConversationHandler.END

async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    senha = update.message.text.strip()
    usuario = context.user_data.get('usuario')
    logger.info(f"Usuário {update.effective_user.id} enviou senha para o usuário: {usuario}")
    await update.message.reply_text("Validando usuário e senha...")
    if usuario is None:
        logger.warning(f"Usuário {update.effective_user.id} tentou autenticar sem usuário definido.")
        await update.message.reply_text("Usuário não definido. Use /entrar novamente.")
        return ConversationHandler.END
    autenticado = False
    try:
        autenticado = autenticar_usuario(usuario, senha)
    except Exception as e:
        logger.error(f"Erro ao autenticar usuário no Google Sheets: {e}")
        await update.message.reply_text("Erro interno ao acessar autenticação. Tente novamente mais tarde.")
        return ConversationHandler.END
    if autenticado:
        logger.info(f"Usuário {update.effective_user.id} autenticado com sucesso como {usuario}.")
        from datetime import datetime
        logger.info(f"Usuário {update.effective_user.id} autenticado. Exibindo menu de escolha de aplicativo.")
        keyboard = [
            [InlineKeyboardButton("MaxPlayer", callback_data="app_maxplayer")],
            [InlineKeyboardButton("QuickPlayer", callback_data="app_quickplayer")],
            [InlineKeyboardButton("Sair", callback_data="app_sair")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        usuario_nome = usuario
        agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        mensagem_login = (
            f"Autenticação realizada com sucesso!\n\n"
            f"Revenda: {usuario_nome}!\n\n"
            "Se você está tendo problemas, mande /sair e faça /entrar novamente!\n"
            "Não envie mensagens com o menu aberto.\n\n"
            f"MENU ATUALIZADO em {agora}\n"
        )
        await update.message.reply_text(mensagem_login)
        await update.message.reply_text("Escolha o aplicativo:", reply_markup=reply_markup)
        return 4
    else:
        logger.info(f"Usuário {update.effective_user.id} falhou na autenticação como {usuario}.")
        await update.message.reply_text("Usuário ou senha incorretos. Tente novamente. Envie seu nome de usuário:")
        return 1

async def escolher_aplicativo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime
    query = update.callback_query
    await query.answer()
    escolha = query.data
    usuario_nome = context.user_data.get('usuario', 'N/A')
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    if escolha == "app_maxplayer":
        logger.info(f"Usuário {update.effective_user.id} entrou na automação do MaxPlayer.")
        keyboard = [
            [InlineKeyboardButton("Iniciar Automação", callback_data="maxplayer_iniciar")],
            [InlineKeyboardButton("Voltar ao menu de aplicativos", callback_data="voltar_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensagem = (
            "Você está agora na automação do MaxPlayer!\n\n"
            "Aqui você poderá criar usuários no painel MaxPlayer de forma automatizada.\n\n"
            "Escolha uma opção abaixo para iniciar ou voltar ao menu.\n\n"
            f"Revenda: {usuario_nome}!\n\n"
            "Se você está tendo problemas, mande /sair e faça /entrar novamente!\n"
            "Não envie mensagens com o menu aberto.\n\n"
            f"MENU ATUALIZADO em {agora}"
        )
        await query.edit_message_text(mensagem, reply_markup=reply_markup)
        return 4
    elif escolha == "maxplayer_iniciar":
        from bot_max import iniciar_automacao_maxplayer
        usuario_nome = context.user_data.get('usuario', 'N/A')
        logger.info(f"Usuário {update.effective_user.id} iniciou automação MaxPlayer para o usuário: {usuario_nome}.")
        resultado = iniciar_automacao_maxplayer(usuario_nome)
        if resultado:
            await query.edit_message_text(
                f"Automação MaxPlayer iniciada para {usuario_nome}!\n\n(Em breve integração completa com o painel MaxPlayer.)")
        else:
            await query.edit_message_text(
                f"Falha ao iniciar automação MaxPlayer para {usuario_nome}. Consulte o log para mais detalhes.")
        return 4
    elif escolha == "app_quickplayer":
        app_nome = "QuickPlayer"
        logger.info(f"Usuário {update.effective_user.id} escolheu {app_nome}.")
        keyboard = [[InlineKeyboardButton("Voltar", callback_data="voltar_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensagem = (
            f"Você escolheu {app_nome}!\n\n"
            f"Se quiser mudar de aplicativo, clique em Voltar.\n"
            "Para continuar, siga as instruções abaixo.\n\n"
            f"Revenda: {usuario_nome}!\n\n"
            "Se você está tendo problemas, mande /sair e faça /entrar novamente!\n"
            "Não envie mensagens com o menu aberto.\n\n"
            f"MENU ATUALIZADO em {agora}"
        )
        await query.edit_message_text(mensagem, reply_markup=reply_markup)
        return 4
    elif escolha == "voltar_menu":
        logger.info(f"Usuário {update.effective_user.id} voltou ao menu de escolha de aplicativo.")
        keyboard = [
            [InlineKeyboardButton("MaxPlayer", callback_data="app_maxplayer")],
            [InlineKeyboardButton("QuickPlayer", callback_data="app_quickplayer")],
            [InlineKeyboardButton("Sair", callback_data="app_sair")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Escolha o aplicativo:", reply_markup=reply_markup)
        return 4
    elif escolha == "app_sair":
        logger.info(f"Usuário {update.effective_user.id} saiu após autenticação.")
        await query.edit_message_text("Você saiu. Até logo!")
        return ConversationHandler.END
    else:
        logger.warning(f"Usuário {update.effective_user.id} fez uma escolha inválida: {escolha}")
        await query.edit_message_text("Escolha inválida. Use /entrar para tentar novamente.")
        return ConversationHandler.END

def main():
    if not TELEGRAM_TOKEN:
        logger.error("Token do Telegram não encontrado no .env.")
        return
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("entrar", entrar)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_usuario)],
            2: [CallbackQueryHandler(confirmar_usuario, pattern="^(confirmar_usuario|cancelar_usuario)$")],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_senha)],
            4: [CallbackQueryHandler(escolher_aplicativo, pattern="^(app_maxplayer|app_quickplayer|app_sair|voltar_menu|maxplayer_iniciar)$")],
        },
        fallbacks=[CommandHandler("sair", sair)],
        allow_reentry=True
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sair", sair))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagem))
    logger.info("Bot iniciado e aguardando mensagens...")
    app.run_polling()

if __name__ == "__main__":
    main()
