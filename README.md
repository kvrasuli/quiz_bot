# Quiz vk & telegram bots

There are a telegram and vk support bots. Telegram bot is deployed [here](https://t.me/CyrQuizBot).

### How to use

You'll need your own Telegram bot token, VK group token, Redis db server and file with questions.
Create environment variables:
```
TELEGRAM_TOKEN='your support bot token'
VK_GROUP_TOKEN='your vk group token'
REDIS_ENDPOINT='address of redis db server'
REDIS_PORT='redis db port'
REDIS_PASSWORD='redis password'
PATH_TO_QUESTIONS='path to file with quiz questions'
```
### How to add questions to the quiz

You'll have to create a txt file like a "1vs1200.txt" which is given here in repo as an example.

### How to install dependencies

Python3 should be already installed. 
Then use `pip` to install dependencies:
```
pip3 install -r requirements.txt
```
### How to run
To run the tg bot launch tg_bot.py script with the following console command:
```
python3 tg_bot.py
```
To run the vk bot launch vk_bot.py script:
```
python3 vk_bot.py
```
### Deploy

- Procfile for heroku deploying is created. Use this guide to deploy:
 https://devcenter.heroku.com/articles/github-integration

- Add your env variables in heroku app settings.


