import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
import os
from dotenv import load_dotenv
from bot_auth import autenticar_usuario
from datetime import datetime

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
        "👋 Olá! Seja bem-vindo ao Assistente de Automação PlugTV.\n\nComigo, você pode automatizar tarefas nos painéis MaxPlayer e QuickPlayer de forma simples e segura.\n\nPara começar, digite /entrar para se autenticar. Se quiser sair a qualquer momento, use /sair.\n\nEm caso de dúvidas, siga as instruções que aparecerão durante o uso!"
    )

async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuário {update.effective_user.id} saiu do fluxo.")
    await update.message.reply_text("👋 Você saiu do sistema. Até logo! Se precisar de algo, é só chamar novamente.")

async def receber_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Mensagem recebida de {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(
        "ℹ️ Para continuar, utilize /entrar para acessar o sistema ou /sair para encerrar."
    )

async def entrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Usuário {update.effective_user.id} iniciou autenticação com /entrar.")
    await update.message.reply_text("🔐 Vamos começar sua autenticação!\n\nPor favor, digite seu nome de usuário:")
    return 1

async def receber_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.message.text.strip()
    context.user_data['usuario'] = usuario
    logger.info(f"Usuário {update.effective_user.id} enviou nome de usuário: {usuario}")
    keyboard = [
        [
            InlineKeyboardButton("Confirmar", callback_data="confirmar_usuario"),
            InlineKeyboardButton("Cancelar", callback_data="cancelar_usuario")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"👤 Confirme o nome de usuário informado: {usuario}", reply_markup=reply_markup)
    return 2

async def confirmar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "confirmar_usuario":
        usuario = context.user_data.get('usuario', 'N/A')
        logger.info(f"Usuário {update.effective_user.id} confirmou usuário: {usuario}")
        await query.edit_message_text(f"✅ Usuário confirmado: {usuario}\n\nAgora, digite sua senha para continuar:")
        return 3
    else:
        logger.info(f"Usuário {update.effective_user.id} cancelou autenticação.")
        await query.edit_message_text("Operação cancelada. Use /entrar para tentar novamente.")
        return ConversationHandler.END

async def receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    senha = update.message.text.strip()
    usuario = context.user_data.get('usuario')
    logger.info(f"Usuário {update.effective_user.id} enviou senha para o usuário: {usuario}")
    await update.message.reply_text("⏳ Validando usuário e senha, aguarde...")
    if usuario is None:
        logger.warning(f"Usuário {update.effective_user.id} tentou autenticar sem usuário definido.")
        await update.message.reply_text("Usuário não definido. Use /entrar novamente.")
        return ConversationHandler.END
    autenticado = False
    try:
        autenticado = autenticar_usuario(usuario, senha)
    except Exception as e:
        logger.error(f"Erro ao autenticar usuário: {e}")
        await update.message.reply_text("Erro interno ao acessar autenticação. Tente novamente mais tarde.")
        return ConversationHandler.END
    if autenticado:
        logger.info(f"Usuário {update.effective_user.id} autenticado com sucesso como {usuario}.")
        
        logger.info(f"Usuário {update.effective_user.id} autenticado. Exibindo menu de escolha de aplicativo.")
        keyboard = [
            [
                InlineKeyboardButton("MaxPlayer", callback_data="app_maxplayer"),
                InlineKeyboardButton("QuickPlayer", callback_data="app_quickplayer"),
                InlineKeyboardButton("Sair", callback_data="app_sair")
            ],
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
        await update.message.reply_text("🚀 Escolha o aplicativo que deseja automatizar:", reply_markup=reply_markup)
        return 4
    else:
        logger.info(f"Usuário {update.effective_user.id} falhou na autenticação como {usuario}.")
        await update.message.reply_text("❌ Usuário ou senha incorretos. Por favor, tente novamente.\n\nDigite seu nome de usuário:")
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
            [
                InlineKeyboardButton("Iniciar Automação", callback_data="maxplayer_iniciar"),
                InlineKeyboardButton("Voltar ao menu de aplicativos", callback_data="voltar_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensagem = (
            f"🚀 Você escolheu o app MaxPlayer."
        )
        await query.edit_message_text(mensagem, reply_markup=reply_markup)
        return 4
    elif escolha == "maxplayer_iniciar":
        logger.info(f"Usuário {update.effective_user.id} iniciou fluxo de coleta de dados para automação MaxPlayer.")
        context.user_data['maxplayer'] = {}
        await query.edit_message_text(
            "Por favor, envie o nome do Usuario que deseja criar.")
        return 11

    elif escolha == "app_quickplayer":
        app_nome = "QuickPlayer"
        logger.info(f"Usuário {update.effective_user.id} escolheu {app_nome}.")
        # Mensagem de boas-vindas
        keyboard = [[InlineKeyboardButton("Voltar", callback_data="voltar_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        mensagem = (
            f"🚀 Você escolheu o app {app_nome}.\n\n"
        )
        await query.edit_message_text(mensagem, reply_markup=reply_markup)
        # Já solicita o MAC Address em seguida
        await query.message.reply_text(
            "Digite o número do MAC Address (Exemplo: XX:XX:XX:XX:XX:XX):",
            reply_markup=reply_markup
        )
        context.user_data['quickplayer'] = {}
        return 21
    elif escolha == "voltar_menu":
        logger.info(f"Usuário {update.effective_user.id} voltou ao menu de escolha de aplicativo.")
        keyboard = [
            [
                InlineKeyboardButton("MaxPlayer", callback_data="app_maxplayer"),
                InlineKeyboardButton("QuickPlayer", callback_data="app_quickplayer"),
                InlineKeyboardButton("Sair", callback_data="app_sair")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"""Revenda: {usuario_nome}\n\n
Se você está tendo problemas, mande /sair e faça /entrar novamente!\n
Não envie mensagens com o menu aberto.\n\n
Escolha o aplicativo: 🤔
""", reply_markup=reply_markup)
        return 4
    elif escolha == "app_sair":
        logger.info(f"Usuário {update.effective_user.id} saiu após autenticação.")
        await query.edit_message_text("👋 Você saiu do sistema. Até logo! Se precisar de algo, é só chamar novamente. 😉")
        return ConversationHandler.END
    else:
        logger.warning(f"Usuário {update.effective_user.id} fez uma escolha inválida: {escolha}")
        await query.edit_message_text("Escolha inválida. Use /entrar para tentar novamente. 🔄")
        return ConversationHandler.END


async def maxplayer_receber_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login = update.message.text.strip()
    if not login:
        await update.message.reply_text("Login inválido. Por favor, digite o login do novo usuário:")
        return 11
    context.user_data['maxplayer']['login'] = login
    await update.message.reply_text(
        f"Login registrado: {login}\n\nAgora envie a senha.")
    return 12

async def maxplayer_receber_senha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    senha = update.message.text.strip()
    if not senha:
        await update.message.reply_text("Senha inválida. Por favor, digite a senha do novo usuário:")
        return 12
    context.user_data['maxplayer']['senha'] = senha
    # Confirmação dos dados antes de chamar automação
    dados = context.user_data['maxplayer']
    resumo = (
        f"Confirme os dados:\n"
        f"Login: {dados['login']}\n"
        f"Senha: {'*' * len(dados['senha'])}\n\n"
        "Clique em Confirmar para iniciar a automação ou Voltar para corrigir."
    )
    keyboard = [
        [
            InlineKeyboardButton("Confirmar", callback_data="maxplayer_confirmar"),
            InlineKeyboardButton("Voltar", callback_data="maxplayer_iniciar")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(resumo, reply_markup=reply_markup)
    return 13

async def maxplayer_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from bot_max import iniciar_automacao_maxplayer
    query = update.callback_query
    await query.answer()
    dados = context.user_data.get('maxplayer', {})
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    usuario_nome = context.user_data.get('usuario', 'N/A')
    logger.info(f"Usuário {update.effective_user.id} confirmou dados para automação MaxPlayer: {dados}")
    resultado = await iniciar_automacao_maxplayer(usuario_nome, dados)
    if resultado:
        await query.edit_message_text(
            f"✅ Usuário criado com sucesso!\n\nRevenda: {usuario_nome}!\n\n Escolha o aplicativo que deseja acessar. Se você está tendo problemas, mande /sair e faça /entrar novamente!\nNão envie mensagens com o menu aberto.\n\n MENU ATUALIZADO em {agora}")
    else:
        await query.edit_message_text(
            f"❌ Não foi possível criar o usuário no MaxPlayer para {usuario_nome}.\n\nPor favor, revise os dados e tente novamente. Se o problema persistir, peça suporte ao administrador.")
    keyboard = [[InlineKeyboardButton("🔙 Voltar ao menu", callback_data="voltar_menu")]]
    await query.message.reply_text("O que deseja fazer agora?", reply_markup=InlineKeyboardMarkup(keyboard))
    return 4

# --- QUICKPLAYER HANDLERS ---
from bot_quick import iniciar_automacao_quickplayer

async def quickplayer_iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quickplayer'] = {}
    keyboard = [[InlineKeyboardButton("Voltar", callback_data="voltar_menu")]]
    await update.message.reply_text(
        "Você está na automação do QuickPlayer. Aqui, você poderá configurar o QuickPlayer para receber uma lista de canais de TV.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text(
        "Para começar, precisamos do endereço MAC do seu dispositivo. O endereço MAC é uma sequência de 6 pares de números e letras, separados por dois-pontos, como XX:XX:XX:XX:XX:XX.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text(
        "Por favor, digite o endereço MAC do seu dispositivo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return 21

async def quickplayer_receber_mac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mac = update.message.text.strip()
    if not mac or len(mac) != 17:
        await update.message.reply_text("Endereço MAC inválido. Por favor, digite o endereço MAC no formato XX:XX:XX:XX:XX:XX:")
        return 21
    context.user_data['quickplayer']['mac'] = mac
    keyboard = [[InlineKeyboardButton("Voltar", callback_data="voltar_menu")]]
    await update.message.reply_text(
        f"Endereço MAC registrado: {mac}. Agora, precisamos da URL da lista de canais de TV que você deseja configurar.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text(
        "A URL da lista de canais de TV deve começar com http:// ou https://. Por favor, digite a URL da lista de canais de TV:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return 22

async def quickplayer_receber_m3u(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m3u = update.message.text.strip()
    if not m3u.startswith("http"):
        await update.message.reply_text("URL da lista de canais de TV inválida. Por favor, digite a URL da lista de canais de TV começando com http:// ou https://")
        return 22
    context.user_data['quickplayer']['m3u'] = m3u
    dados = context.user_data['quickplayer']
    resumo = (
        f"Confirme os dados:\nEndereço MAC: {dados['mac']}\nURL da lista de canais de TV: {dados['m3u']}\n\n"
        "Se os dados estiverem corretos, clique em Confirmar para iniciar a configuração do QuickPlayer."
    )
    keyboard = [
        [InlineKeyboardButton("Confirmar", callback_data="quickplayer_confirmar")],
        [InlineKeyboardButton("Voltar", callback_data="quickplayer_iniciar")]
    ]
    await update.message.reply_text(resumo, reply_markup=InlineKeyboardMarkup(keyboard))
    return 23

async def quickplayer_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dados = context.user_data.get('quickplayer', {})
    usuario_nome = context.user_data.get('usuario', 'N/A')
    logger.info(f"Usuário {update.effective_user.id} confirmou dados para configuração do QuickPlayer: {dados}")
    resultado = await iniciar_automacao_quickplayer(dados['mac'], dados['m3u'])
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    if resultado:
        await query.edit_message_text(
            f"✅ Lista enviada com sucesso!\n\n Revenda: {usuario_nome}!\n\nEscolha o aplicativo que deseja acessar.\nSe você está tendo problemas, mande /sair e faça /entrar novamente!\nNão envie mensagens com o menu aberto.\n\nMENU ATUALIZADO em {agora}"
        )
    else:
        await query.edit_message_text(
            f"❌ Não foi possível cadastrar a playlist para o MAC: {dados['mac']}.\n\nRevise os dados e tente novamente. Se o erro persistir, solicite suporte ao administrador."
        )
    keyboard = [[InlineKeyboardButton("🔙 Voltar ao menu", callback_data="voltar_menu")]]
    await query.message.reply_text("O que deseja fazer agora?", reply_markup=InlineKeyboardMarkup(keyboard))
    return 4

def main():
    # Deixar logs HTTP menos verbosos
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram.vendor.ptb_urllib3.urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('telegram.ext._applicationlogger').setLevel(logging.WARNING)
    if not TELEGRAM_TOKEN:
        logger.error("Token do Telegram não encontrado no .env.")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("entrar", entrar)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_usuario)],
            2: [CallbackQueryHandler(confirmar_usuario, pattern="^(confirmar_usuario|cancelar_usuario)$")],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_senha)],
            4: [
                CallbackQueryHandler(escolher_aplicativo, pattern="^(app_maxplayer|app_quickplayer|app_sair|voltar_menu|maxplayer_iniciar)$"),
                CallbackQueryHandler(quickplayer_iniciar, pattern="^quickplayer_iniciar$")
            ],
            11: [MessageHandler(filters.TEXT & ~filters.COMMAND, maxplayer_receber_login)],
            12: [MessageHandler(filters.TEXT & ~filters.COMMAND, maxplayer_receber_senha)],
            13: [CallbackQueryHandler(maxplayer_confirmar, pattern="^(maxplayer_confirmar|maxplayer_iniciar)$")],
            21: [MessageHandler(filters.TEXT & ~filters.COMMAND, quickplayer_receber_mac), CallbackQueryHandler(escolher_aplicativo, pattern="^voltar_menu$")],
            22: [MessageHandler(filters.TEXT & ~filters.COMMAND, quickplayer_receber_m3u), CallbackQueryHandler(quickplayer_iniciar, pattern="^quickplayer_iniciar$"), CallbackQueryHandler(escolher_aplicativo, pattern="^voltar_menu$")],
            23: [CallbackQueryHandler(quickplayer_confirmar, pattern="^(quickplayer_confirmar|quickplayer_iniciar)$"), CallbackQueryHandler(escolher_aplicativo, pattern="^voltar_menu$")],
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
