# PyBotGram
Terminal Telegram bot client.
```
██████╗ ██╗   ██╗██████╗  ██████╗ ████████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
██████╔╝ ╚████╔╝ ██████╔╝██║   ██║   ██║   ██║  ███╗██████╔╝███████║██╔████╔██║
██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║   ██║   ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
██║        ██║   ██████╔╝╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
```
## Install
1.git clone https://github.com/xl15kot/PyBotGram.git 
1.Or Option 2: Download the zip archive from GitHub.
2.pip install python-telegram-bot colorama
On first run, enter your bot token from @BotFather. Tokens can be saved for later use.
## Usage
python main.py

After login you'll see the chat list. Each chat shows its last message.
Type a chat number and press Enter to open it.
Inside a chat, the last 10 messages are displayed. Anything you type gets sent.
New messages arrive in real-time (slight delay possible).
## Commands
| Command | Where | What it does |
|---------|-------|--------------|
| `1` `2` ... | chat list | Select chat by number |
| `hello` | inside chat | Send a message |
| `:mes @user hi` | anywhere | Send to a @user |
| `:mes 123456789 text` | anywhere | Send by user ID |
| `:b` or `/back` | inside chat | Leave current chat |
| `:q` or `/exit` | anywhere | Exit program |
| `:h` or `:help` | anywhere | Show help |
| `:set` or `/set` | anywhere | Settings |
## Settings (`:set`)
- **Change name** — doesn't work (Bot API doesn't allow bots to rename themselves, use @BotFather instead)
- **Change avatar** — doesn't work (same, only via @BotFather)
- **Show bot info** — displays bot name, ID, username
- **Logout** — deletes saved token
## Dependencies
- `python-telegram-bot>=20.0` — Telegram Bot API
- `colorama` — terminal colors
