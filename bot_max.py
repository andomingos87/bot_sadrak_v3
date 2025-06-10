import logging

# Placeholder para futura integração RPA MaxPlayer
import os
import logging
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def iniciar_automacao_maxplayer(usuario, dados):
    """
    Executa automação RPA para criar novo usuário no painel MaxPlayer via Playwright (assíncrono).
    Parâmetros:
        usuario (str): nome ou login do usuário autenticado no bot
        dados (dict): {'login': ..., 'senha': ...} do novo usuário a ser criado
    Retorna True se sucesso, False se erro.
    """
    logging.info(f"[MaxPlayer] Iniciando automação para o usuário: {usuario} | Novo usuário: {dados}")
    MAXPLAYER_URL = os.getenv("MAXPLAYER_URL")
    ADMIN_LOGIN = os.getenv("MAXPLAYER_ADMIN_LOGIN")
    ADMIN_SENHA = os.getenv("MAXPLAYER_ADMIN_SENHA")
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logging.info("[MaxPlayer] Navegando para URL do painel...")
            await page.goto(MAXPLAYER_URL, timeout=40000)
            logging.info("[MaxPlayer] Acessou painel de login")
            
            # Login admin
            await page.fill('#exampleEmail', ADMIN_LOGIN)
            await page.fill('#examplePassword', ADMIN_SENHA)
            await page.click('button.btn-primary')
            logging.info("[MaxPlayer] Login enviado, aguardando redirecionamento para dashboard...")
            await page.wait_for_url("**/dashboard", timeout=20000)
            logging.info("[MaxPlayer] Redirecionado para dashboard")

            # Navega para a aba Customers
            await page.goto(f"{MAXPLAYER_URL.replace('/auth/login', '/customers')}", timeout=20000)
            logging.info("[MaxPlayer] Acessou aba Customers")
            
            # Clica em Add New User
            await page.click('button.btn-green')
            logging.info("[MaxPlayer] Clicou em Add New User")

            # Seleciona domínio cr61.net
            await page.select_option('select#name', value="1739318193890969526")
            logging.info("[MaxPlayer] Domínio cr61.net selecionado")

            # Preenche usuário e senha recebidos do Telegram
            await page.fill('input[name="iptv_user"]', dados['login'])
            await page.fill('input[name="iptv_pass"]', dados['senha'])
            logging.info(f"[MaxPlayer] Dados do novo usuário preenchidos: login={dados['login']}")

            # Clica em Create
            await page.click('button.btn-primary:has-text("Create")')
            logging.info("[MaxPlayer] Botão Create clicado. Aguardando finalização...")

            # Aguarda finalização
            await asyncio.sleep(5)
            logging.info("[MaxPlayer] Espera finalização concluída. Fechando navegador.")
            await browser.close()
            return True
    except PlaywrightTimeoutError as e:
        logging.error(f"[MaxPlayer] Timeout na automação: {e}")
        try:
            if 'page' in locals() and not page.is_closed():
                html = await page.content()
                logging.error(f"[MaxPlayer] HTML capturado no timeout:\n{html[:1500]} ...")
        except Exception as ex:
            logging.warning(f"[MaxPlayer] Falha ao capturar HTML após timeout: {ex}")
    except Exception as e:
        logging.error(f"[MaxPlayer] Erro inesperado na automação: {e}")
        try:
            if 'page' in locals() and not page.is_closed():
                html = await page.content()
                logging.error(f"[MaxPlayer] HTML capturado no erro:\n{html[:1500]} ...")
        except Exception as ex:
            logging.warning(f"[MaxPlayer] Falha ao capturar HTML após erro: {ex}")
    finally:
        try:
            if browser:
                await browser.close()
        except Exception as ex:
            logging.warning(f"[MaxPlayer] Falha ao fechar o browser: {ex}")
    return False
