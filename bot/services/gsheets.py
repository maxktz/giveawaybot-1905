import datetime
from bot.services.core.gsheets import agcm


# async def get_all_orders_sheet() -> list[GoogleSheet]:
#     return await GoogleSheet.find_all().to_list()


# async def add_order_to_sheets(order: Order) -> None:
#     sheets = await get_all_orders_sheet()
#     if not sheets:
#         return

#     agc = await agcm.authorize()
#     for sheet in sheets:
#         if not eval(sheet.order_matching_filter.format(order=order)):
#             continue

#         ags = await agc.open_by_url(sheet.url)
#         worksheet = await ags.get_worksheet(sheet.worksheet_index)
#         headers = [x.lower() for x in (await worksheet.get_values("1:1"))[0]]

#         changes: dict[int, str] = {}
#         for header, field in sheet.fields.items():
#             try:
#                 index = headers.index(header.lower())
#             except ValueError:
#                 continue
#             changes[index] = await order_field_to_sheet_field(order, field)

#         if changes:
#             last_index = list(sorted(changes.keys()))[-1]
#             values = ["" for _ in range(last_index + 1)]
#             for i, val in changes.items():
#                 values[i] = val
#             await worksheet.insert_row(values, index=2)


# async def order_field_to_sheet_field(order: Order, field_name: str) -> str:
#     match field_name:
#         case "id":
#             return str(order.id)
#         case "status":
#             return order.status.value
#         case "user_id":
#             return str(await get_user(order.user_id))
#         case "order_items":
#             items = []
#             for item in order.order_items:
#                 s = len(item.product_strings) if item.product_strings else 0
#                 c = (
#                     len(item.telegram_chat_access_invite_hashes)
#                     if item.telegram_chat_access_invite_hashes
#                     else 0
#                 )
#                 items.append(f"(id={item.product_id}, q={item.quantity}, s={s}, c={c})")
#             return ", ".join(items)
#         case "total":
#             return "%.2f$" % order.total
#         case "referral_amount":
#             return "%.2f$" % order.referral_amount
#         case "balance_payment":
#             return "%.2f$" % order.balance_payment
#         case "telegram_chat_invite_hash":
#             if order.telegram_chat_invite_hash:
#                 return f"https://t.me/+{order.telegram_chat_invite_hash}"
#             else:
#                 return ""
#         case "paid_at":
#             return datetime.datetime.strftime(order.paid_at, "%y-%m-%d %H:%M:%S")
#         case "product_strings":
#             strings = []
#             for item in order.order_items:
#                 if item.product_strings:
#                     for string in item.product_strings:
#                         strings.append(f"({string})")
#             text = ", ".join(strings)
#             if len(text) > 200:
#                 text = text[200:] + "..."
#             return text
#     return ""
