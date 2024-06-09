from gspread_asyncio import AsyncioGspreadWorksheet
from bot.services.core.gsheets import agcm
from bot.core.config import settings
from gspread.utils import ValueInputOption
from sqlalchemy.ext.asyncio import AsyncSession

users_sheet_columns = {
    "id": "id",
    "username": "username",
    "points": "points",
    "referrals": "referrals",
    "referrer id": "referrer_id",
    "twitter username": "twitter_username",
}


async def update_users_sheet(session: AsyncSession) -> None:
    from .users import get_all_users, get_user_sheet_field

    agc = await agcm.authorize()
    ags = await agc.open_by_url(settings.USERS_GSHEET_URL)
    worksheet = await ags.get_worksheet(index=0)

    headers_row = (await worksheet.get_values("1:1"))[0]
    headers = [x.lower().strip() for x in headers_row]

    users = await get_all_users(session)

    rows: list[list[str]] = []

    for user in users:
        row = []
        for header in headers:
            field_to_fill = users_sheet_columns.get(header)
            if field_to_fill:
                val = await get_user_sheet_field(session, user, field_to_fill)
                row.append(val)
            else:
                row.append("")
        rows.append(row)

    await replace_sheet_rows(worksheet, rows)


async def replace_sheet_rows(worksheet: AsyncioGspreadWorksheet, rows: list[list[str]]) -> None:
    # delete all rows except the first two
    await worksheet.delete_rows(3, worksheet.row_count)
    # clear the second row
    await worksheet.batch_clear(["2:2"])
    # insert new rows
    return await worksheet.insert_rows(
        rows, row=2, value_input_option=ValueInputOption.user_entered
    )
