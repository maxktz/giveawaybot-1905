import datetime
from bot.services.core.gsheets import agcm
from bot.core.config import settings


async def update_users_sheet() -> None:

    agc = await agcm.authorize()

    ags = await agc.open_by_url()
    worksheet = await ags.get_worksheet(settings.USERS_GSHEET_URL)
    headers = [x.lower() for x in (await worksheet.get_values("1:1"))[0]]

    changes: dict[int, str] = {}

    for header, field in sheet.fields.items():
        try:
            index = headers.index(header.lower())
        except ValueError:
            continue
        changes[index] = await order_field_to_sheet_field(order, field)

    if changes:
        last_index = list(sorted(changes.keys()))[-1]
        values = ["" for _ in range(last_index + 1)]
        for i, val in changes.items():
            values[i] = val
        await worksheet.insert_row(values, index=2)
