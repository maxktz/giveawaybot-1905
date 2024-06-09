# pull update
git pull
# compile translations
pybabel compile -d bot/translations

# restart docker-compose
docker-compose -p giveawaybot-1905 down
docker-compose -p giveawaybot-1905 up --build -d

