import gspread_asyncio
from google.oauth2.service_account import Credentials
from bot.core.config import settings


def get_credentals() -> Credentials:
    creds = Credentials.from_service_account_file(settings.GOOGLE_IAM_KEY_PATH)
    return creds.with_scopes(
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
    )


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_credentals)
