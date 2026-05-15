# PyBotGram
Terminal Telegram bot client. In beta version
```
██████╗ ██╗   ██╗██████╗  ██████╗ ████████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
██████╔╝ ╚████╔╝ ██████╔╝██║   ██║   ██║   ██║  ███╗██████╔╝███████║██╔████╔██║
██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║   ██║   ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
██║        ██║   ██████╔╝╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
```
## Install
```bash
git clone https://github.com/xl15kot/PyBotGram.git
cd PyBotGram
pip install python-telegram-bot colorama
python main.py
```
On first run, enter your bot token from [@BotFather](https://t.me/BotFather). Tokens can be saved for later use.
### Chat
- Real-time message receiving and sending
- Chat list with last message preview
- Message history saved locally
- Send messages by username or ID (`:mes @user text`)
### Media
| Command | Description |
|---------|-------------|
| `:s path` or `:s file_id` | Send sticker |
| `:p path [caption]` | Send photo |
| `:d path [caption]` | Send document |
| `:v path [caption]` | Send video |
| `:a path [caption]` | Send audio |
| `:voice path` | Send voice message |
| `:send path` | Auto-detect and send |
### Moderation (group admin needed)
| Command | Description |
|---------|-------------|
| `:ban @user` | Ban user |
| `:unban @user` | Unban user |
| `:kick @user` | Kick user |
| `:mute @user` | Mute user |
| `:unmute @user` | Unmute user |
### Blacklist
| Command | Description |
|---------|-------------|
| `:block @user` | Add to blacklist |
| `:unblock @user` | Remove from blacklist |
| `:blocklist` | Show blacklist |
### Messages
| Command | Description |
|---------|-------------|
| `:r text` | Reply to last message |
| `:fwd @user` | Forward last message |
| `:del` | Delete last sent message |
| `:find text` | Search in chat history |
### Other
| Command | Description |
|---------|-------------|
| `:info` | Show current chat info |
| `:clear` | Clear local chat history |
| `:emoji` | Toggle emoji on/off |
| `:update` | Check and apply updates |
| `:set` | Settings menu |
| `:h` | Help |
| `:q` | Quit |
## Dependencies
- `python-telegram-bot>=20.0`
- `colorama`
## Screenshots
<img width="903" height="489" alt="image" src="https://github.com/user-attachments/assets/0458249d-14f8-4cfd-bf77-2224848bdd28" />
<img width="894" height="582" alt="image" src="https://github.com/user-attachments/assets/7ac9953c-8162-4219-9e36-1abea85b96e4" />
<img width="739" height="784" alt="image" src="https://github.com/user-attachments/assets/baec83ea-995e-4cb8-a221-852f5c681e97" />



