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
<img width="1072" height="543" alt="image" src="https://github.com/user-attachments/assets/244ece26-ce1b-4dd5-82ac-f1810b5b1bd7" />
<img width="914" height="579" alt="image" src="https://github.com/user-attachments/assets/f6efd637-4216-40f7-b075-84dc4c3dbabc" />
<img width="583" height="785" alt="image" src="https://github.com/user-attachments/assets/876324ca-8dee-4c4e-8edf-2bb7809dd73f" />
<img width="547" height="821" alt="image" src="https://github.com/user-attachments/assets/09c5766e-3a68-4906-8cef-d3e8cb059c3f" />


