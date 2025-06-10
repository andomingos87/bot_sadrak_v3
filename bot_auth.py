import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = 'service_account.json'
SHEET_NAME = 'app.plugtv_bot'
USERS_TAB = 'usuarios'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

def autenticar_usuario(usuario: str, senha: str) -> bool:
    """
    Valida usuario e senha na planilha Google Sheets.
    Retorna True se autenticado, False caso contrário.
    """
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        sh = gc.open(SHEET_NAME)
        ws = sh.worksheet(USERS_TAB)
        registros = ws.get_all_values()
        for row in registros[1:]:  # Ignora header
            if len(row) >= 2 and row[0] == usuario and row[1] == senha:
                return True
        return False
    except Exception as e:
        print(f"Erro ao acessar Google Sheets: {e}")
        return False
