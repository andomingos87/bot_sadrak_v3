import logging
import os
import re
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from gspread import service_account
from dotenv import load_dotenv

load_dotenv()

# Função utilitária para buscar a URL_BASE no Google Sheets
async def obter_url_base():
    try:
        import os
        cred_path = os.path.join(os.path.dirname(__file__), "service_account.json")
        gc = service_account(filename=cred_path)
        sh = gc.open_by_url(os.getenv("LINK_SHEETS"))
        aba = sh.worksheet("DNS")
        url_base = aba.acell("A2").value
        logging.info(f"[QuickPlayer] URL_BASE obtida do Google Sheets: {url_base}")
        return url_base
    except Exception as e:
        logging.error(f"[QuickPlayer] Erro ao obter URL_BASE no Sheets: {e}")
        return None

async def iniciar_automacao_quickplayer(mac, m3u_url):
    """
    Automação RPA para cadastro no QuickPlayer.
    - mac: string no formato XX:XX:XX:XX:XX:XX
    - m3u_url: url recebida do usuário
    Retorna True se sucesso, False se erro.
    """
    url_base = await obter_url_base()
    if not url_base:
        logging.error("[QuickPlayer] URL_BASE não encontrada. Abortando automação.")
        return False
    # Adaptar início da URL recebida
    url_alterada = re.sub(r"^https?://[^/]+", url_base, m3u_url)
    logging.info(f"[QuickPlayer] URL M3U adaptada: {url_alterada}")
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            logging.info("[QuickPlayer] Acessando painel QuickPlayer...")
            await page.goto("https://quickplayer.app/#/upload-playlist", timeout=40000)
            # Preenche MAC
            await page.fill('#mac', mac)
            logging.info(f"[QuickPlayer] MAC preenchido: {mac}")
            # Aguarda mensagem de validação
            await page.wait_for_selector('span.message_success-text__NtfBt', timeout=15000)
            logging.info("[QuickPlayer] MAC validado com sucesso.")

            # Preenche Playlist Name
            await page.fill('#upload-playlist-by-url_name', "PLUGTV")
            logging.info("[QuickPlayer] Playlist Name preenchido: PLUGTV")

            # Preenche Playlist URL
            await page.fill('#upload-playlist-by-url_url', url_alterada)
            logging.info(f"[QuickPlayer] Playlist URL preenchida: {url_alterada}")

            # Preenche Playlist EPG URL
            await page.fill('#upload-playlist-by-url_epg_url', f"{url_base}/epg")
            logging.info(f"[QuickPlayer] Playlist EPG URL preenchida: {url_base}/epg")

            # Clica no botão Upload
            logging.info("[QuickPlayer] Clicando no botão Upload...")
            await page.click('button span:text("Upload")')
            await asyncio.sleep(3)
            logging.info("[QuickPlayer] Upload realizado. Fechando navegador.")
            await browser.close()
            return True
    except PlaywrightTimeoutError as e:
        logging.error(f"[QuickPlayer] Timeout na automação: {e}")
    except Exception as e:
        logging.error(f"[QuickPlayer] Erro inesperado na automação: {e}")
    finally:
        try:
            if browser:
                await browser.close()
        except Exception as ex:
            logging.warning(f"[QuickPlayer] Falha ao fechar o browser: {ex}")
    return False
