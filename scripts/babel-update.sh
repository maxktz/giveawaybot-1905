# extract to template
pybabel extract -F babel.cfg -o bot/translations/messages.pot bot

# also add database translation to created template
cat bot/translations/db.pot >> bot/translations/messages.pot

# update catalogs
pybabel update -i bot/translations/messages.pot -d bot/translations

# compile all .po files
pybabel compile -d bot/translations