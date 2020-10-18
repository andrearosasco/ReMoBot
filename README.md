# ReMoBot
ReMoBot (short for remote monitoring) is a simple telegram bot which can monitor the GPUs memories on a remote machine.
# Installation
Clone the repo on the machine you want to monitor
```bash
git clone https://github.com/andrew-r96/ReMoBot.git
```
Install the package requirements
```bash
pip install -r requirements.txt
```
Open ```bot.py```
  replace ```python "YOUR-TOKEN-GOES-HERE"``` with the token you got from BotFather
  add the telegram usernames of users allowed to use the bot in ```python filter.add_usernames()```
Run ```bash python bot.py``` inside a tmux terminal to keep it running when you log out of the machine
# Usage
