import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

from colorama import init, Fore, Style, Back
from telegram import Bot
from telegram.error import TelegramError

init(autoreset=True)

SESSION_FILE = "pybotgram_session.json"
HISTORY_DIR = "pybotgram_history"

Path(HISTORY_DIR).mkdir(exist_ok=True)

class PyBotGram:
    def __init__(self):
        self.bot = None
        self.token = None
        self.remember = False
        self.current_chat = None
        self.messages = {}
        self.chats = {}
        self.me = None
        self.running = True
        self.update_offset = 0
        
        self.load_sessions()
        self.load_chat_history()
        
    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")
        
    def load_sessions(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.remember = data.get('remember', False)
            except:
                pass
                
    def save_session(self):
        if self.remember and self.token:
            with open(SESSION_FILE, 'w') as f:
                json.dump({'token': self.token, 'remember': True}, f)
        elif os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            
    def load_chat_history(self):
        history_files = Path(HISTORY_DIR).glob("chat_*.json")
        for file in history_files:
            try:
                with open(file, 'r') as f:
                    chat_id = int(file.stem.split('_')[1])
                    data = json.load(f)
                    self.messages[chat_id] = data.get('messages', [])
                    if 'chat_info' in data:
                        self.chats[chat_id] = data['chat_info']
            except:
                pass
                
    def save_chat_history(self, chat_id):
        if chat_id in self.messages:
            file_path = Path(HISTORY_DIR) / f"chat_{chat_id}.json"
            data = {
                'chat_id': chat_id,
                'chat_info': self.chats.get(chat_id, {}),
                'messages': self.messages[chat_id][-200:],
            }
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            except:
                pass
                
    def truncate(self, s, n=30):
        return (s[:n] + "..") if s and len(s) > n else (s or "")
        
    async def login(self):
        self.clear_screen()

        cols = os.get_terminal_size().columns

        logo = [
            "██████╗ ██╗   ██╗██████╗  ██████╗ ████████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗",
            "██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║",
            "██████╔╝ ╚████╔╝ ██████╔╝██║   ██║   ██║   ██║  ███╗██████╔╝███████║██╔████╔██║",
            "██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║   ██║   ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║",
            "██║        ██║   ██████╔╝╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║",
            "╚═╝        ╚═╝   ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝",
        ]

        logo_w = 62
        pad = (cols - logo_w) // 2

        print(f"\n{Fore.CYAN}{' ' * pad}{'═' * logo_w}{Style.RESET_ALL}\n")

        for line in logo:
            print(f"{Fore.CYAN}{' ' * pad}{line}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{' ' * pad}{'═' * logo_w}{Style.RESET_ALL}")

        print()
        print(f"{' ' * ((cols - 30) // 2)}{Style.BRIGHT}Telegram Bot Client{Style.RESET_ALL}")
        print(f"{' ' * ((cols - 30) // 2)}{Style.DIM}v1.0 by Avebas{Style.RESET_ALL}")
        print()

        if self.token and self.remember:
            print(f"{' ' * ((cols - 40) // 2)}{Fore.GREEN}◉ Saved session{Style.RESET_ALL}")
            print(f"{' ' * ((cols - 40) // 2)}{Style.DIM}{self.token[:24]}...{Style.RESET_ALL}")
            print()
            print(f"{' ' * ((cols - 40) // 2)}{Fore.CYAN}[1]{Style.RESET_ALL} Restore")
            print(f"{' ' * ((cols - 40) // 2)}{Fore.CYAN}[2]{Style.RESET_ALL} New")
            print()
            choice = input(f"{' ' * ((cols - 40) // 2)}{Style.BRIGHT}>{Style.RESET_ALL} ").strip()

            if choice == "1":
                try:
                    self.bot = Bot(self.token)
                    await self.bot.initialize()
                    self.me = await self.bot.get_me()
                    return True
                except Exception as e:
                    print(f"{' ' * ((cols - 40) // 2)}{Fore.RED}[✗] {e}{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    self.clear_screen()

        print(f"\n{' ' * ((cols - 50) // 2)}{Fore.YELLOW}━━━  Sign In  ━━━{Style.RESET_ALL}")
        print()
        token = input(f"{' ' * ((cols - 50) // 2)}{Style.BRIGHT}Bot Token:{Style.RESET_ALL} ").strip()

        try:
            self.bot = Bot(token)
            await self.bot.initialize()
            self.me = await self.bot.get_me()
            self.token = token

            print()
            print(f"{' ' * ((cols - 50) // 2)}{Fore.GREEN}◉ Signed in as {Style.BRIGHT}{self.me.first_name}{Style.RESET_ALL}")
            print(f"{' ' * ((cols - 50) // 2)}{Style.DIM}@{self.me.username or 'no username'}{Style.RESET_ALL}")
            print()
            remember = input(f"{' ' * ((cols - 50) // 2)}{Fore.CYAN}Remember? (y/n):{Style.RESET_ALL} ").strip().lower()
            self.remember = remember in ('y', 'yes')
            self.save_session()

            await asyncio.sleep(1)
            return True
        except Exception as e:
            print(f"\n{' ' * ((cols - 50) // 2)}{Fore.RED}[✗] Error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(2)
            return False
            
    async def fetch_updates(self):
        while self.running:
            try:
                updates = await self.bot.get_updates(offset=self.update_offset, timeout=1, read_timeout=5)
                for update in updates:
                    self.update_offset = update.update_id + 1
                    msg = update.message or update.edited_message
                    if not msg or not msg.text:
                        continue
                        
                    cid = msg.chat.id
                    cname = msg.chat.title or msg.chat.username or f"User_{cid}"
                    uname = msg.from_user.first_name or msg.from_user.username or str(msg.from_user.id)
                    
                    if cid not in self.chats:
                        self.chats[cid] = {"name": cname, "last": msg.text, "time": datetime.now().strftime("%H:%M")}
                    else:
                        self.chats[cid]["last"] = msg.text
                        self.chats[cid]["time"] = datetime.now().strftime("%H:%M")
                    
                    if cid not in self.messages:
                        self.messages[cid] = []
                    
                    self.messages[cid].append({
                        "from": uname,
                        "text": msg.text,
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "type": "in"
                    })
                    
                    if len(self.messages[cid]) > 200:
                        self.messages[cid] = self.messages[cid][-200:]
                        
            except Exception as e:
                pass
            await asyncio.sleep(1)
            
    def render(self):
        self.clear_screen()
        
        # Header
        print(f"{Fore.CYAN}@PyBotGram v1.0{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}👤 {self.me.first_name or self.me.username}{Style.RESET_ALL}")
        print()
        
        # Chats
        chat_list = sorted(self.chats.items(), key=lambda x: x[1]["name"])
        
        if chat_list:
            print(f"{Fore.GREEN}CHATS ({len(chat_list)}){Style.RESET_ALL}")
            for i, (cid, info) in enumerate(chat_list[:15], 1):
                marker = "→" if cid == self.current_chat else " "
                name = info['name'][:25]
                print(f"  {marker} {Fore.YELLOW}{i}.{Style.RESET_ALL} {name}")
                last_msg = self.truncate(info.get("last", ""), 35)
                if last_msg:
                    print(f"     {Style.DIM}└ {last_msg}{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}No chats yet{Style.RESET_ALL}")
            print(f"{Style.DIM}Write to bot in Telegram first{Style.RESET_ALL}")
            
        # Current chat messages
        if self.current_chat and self.current_chat in self.chats:
            print()
            print(f"{Fore.CYAN}─── {self.chats[self.current_chat]['name']} ───{Style.RESET_ALL}")
            
            msgs = self.messages.get(self.current_chat, [])[-10:]
            if msgs:
                for m in msgs:
                    if m.get('type') == 'out':
                        arrow = "→"
                        color = Fore.GREEN
                    else:
                        arrow = "←"
                        color = Fore.CYAN
                    name = m['from'][:15]
                    text = m['text'][:50]
                    print(f"  {Style.DIM}[{m['time'][:5]}]{Style.RESET_ALL} {color}{arrow}{Style.RESET_ALL} {name}: {text}")
            else:
                print(f"  {Style.DIM}No messages yet{Style.RESET_ALL}")
                
        # Empty space to push input to bottom
        terminal_height = os.get_terminal_size().lines
        used_lines = 6 + len(chat_list) * 2 + len(self.messages.get(self.current_chat, [])[-10:]) + 2
        empty_lines = max(0, terminal_height - used_lines - 3)
        for _ in range(empty_lines):
            print()
            
        # Footer
        print(f"{Fore.CYAN}{'─'*40}{Style.RESET_ALL}")
        print(f"{Style.DIM}:h :b :mes @user :set :q{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}> {Style.RESET_ALL}", end="", flush=True)
        
    async def send_message(self, chat_id, text):
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            if chat_id not in self.messages:
                self.messages[chat_id] = []
            self.messages[chat_id].append({
                "from": "You",
                "text": text,
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "out"
            })
            if chat_id in self.chats:
                self.chats[chat_id]["last"] = text
                self.chats[chat_id]["time"] = datetime.now().strftime("%H:%M")
            self.save_chat_history(chat_id)
            return True
        except Exception as e:
            print(f"\n{Fore.RED}[✗] Error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(1)
            return False
            
    async def show_help(self):
        self.clear_screen()
        print(f"{Fore.CYAN}UBOTGRAM HELP{Style.RESET_ALL}")
        print()
        print(f"  {Fore.YELLOW}[number]{Style.RESET_ALL}     - Select chat by number")
        print(f"  {Fore.YELLOW}:b{Style.RESET_ALL} or /back   - Exit current chat")
        print(f"  {Fore.YELLOW}:mes @user text{Style.RESET_ALL} - Send message by username")
        print(f"  {Fore.YELLOW}:set{Style.RESET_ALL} or /set   - Settings")
        print(f"  {Fore.YELLOW}:h{Style.RESET_ALL} or :help    - Show this help")
        print(f"  {Fore.YELLOW}:q{Style.RESET_ALL} or /exit    - Quit")
        print()
        print(f"{Style.DIM}Just type any message to send to current chat{Style.RESET_ALL}")
        print()
        input(f"{Style.DIM}Press Enter to continue...{Style.RESET_ALL}")
        
    async def settings_menu(self):
        while True:
            self.clear_screen()
            print(f"{Fore.CYAN}UBOTGRAM SETTINGS{Style.RESET_ALL}")
            print()
            print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} Change name")
            print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} Change avatar (from file)")
            print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} Show bot info")
            print(f"  {Fore.YELLOW}[4]{Style.RESET_ALL} Logout")
            print(f"  {Fore.YELLOW}[0]{Style.RESET_ALL} Back")
            print()
            
            choice = input(f"{Style.BRIGHT}> {Style.RESET_ALL}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.clear_screen()
                print(f"{Fore.CYAN}Change name{Style.RESET_ALL}")
                first = input(f"First name: ").strip()
                last = input(f"Last name: ").strip()
                try:
                    if first or last:
                        await self.bot.set_chat_title(title=f"{first} {last}".strip())
                        self.me = await self.bot.get_me()
                    print(f"{Fore.GREEN}[✓] Name updated{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[✗] {e}{Style.RESET_ALL}")
                await asyncio.sleep(1.5)
                
            elif choice == "2":
                self.clear_screen()
                print(f"{Fore.CYAN}Change avatar{Style.RESET_ALL}")
                print(f"{Style.DIM}Full path to image file (jpg/png){Style.RESET_ALL}")
                path = input(f"Path: ").strip()
                if os.path.exists(path):
                    try:
                        with open(path, 'rb') as photo:
                            await self.bot.set_chat_photo(photo=photo)
                        print(f"{Fore.GREEN}[✓] Avatar updated{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}[✗] {e}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[✗] File not found{Style.RESET_ALL}")
                await asyncio.sleep(1.5)
                
            elif choice == "3":
                self.clear_screen()
                print(f"{Fore.CYAN}Bot info{Style.RESET_ALL}")
                print()
                print(f"  Name: {self.me.first_name}")
                if self.me.last_name:
                    print(f"  Last: {self.me.last_name}")
                print(f"  ID: {self.me.id}")
                if self.me.username:
                    print(f"  Username: @{self.me.username}")
                print()
                input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")
                
            elif choice == "4":
                confirm = input(f"{Fore.RED}Logout? (y/n):{Style.RESET_ALL} ").strip()
                if confirm.lower() == 'y':
                    self.remember = False
                    self.token = None
                    self.save_session()
                    self.running = False
                    return
                    
    async def direct_message(self):
        self.clear_screen()
        print(f"{Fore.CYAN}DIRECT MESSAGE{Style.RESET_ALL}")
        print()
        print(f"{Style.DIM}Examples:{Style.RESET_ALL}")
        print(f"  • @username  - send to Telegram user")
        print(f"  • 123456789  - send by user ID")
        print()
        target = input(f"To: ").strip()
        if not target:
            return
            
        msg = input(f"Message: ").strip()
        if not msg:
            return
            
        try:
            if target.lstrip('@').isdigit():
                await self.bot.send_message(chat_id=int(target), text=msg)
            else:
                username = target.lstrip('@')
                await self.bot.send_message(chat_id=f"@{username}", text=msg)
            print(f"\n{Fore.GREEN}[✓] Message sent!{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[✗] {e}{Style.RESET_ALL}")
        await asyncio.sleep(1.5)
        
    async def run(self):
        if not await self.login():
            return
            
        asyncio.create_task(self.fetch_updates())
        
        while self.running:
            self.render()
            
            inp = sys.stdin.readline().strip()
            
            if inp in ("/exit", ":q", ":wq"):
                self.running = False
                break
            elif inp in ("/back", ":b"):
                self.current_chat = None
            elif inp in ("/help", ":help", ":h"):
                await self.show_help()
            elif inp in ("/set", "/settings", ":set"):
                await self.settings_menu()
                if not self.running:
                    break
            elif inp.startswith(":mes ") or inp.startswith("/msg "):
                prefix = ":mes " if inp.startswith(":mes ") else "/msg "
                rest = inp[len(prefix):].strip()
                if rest:
                    parts = rest.split(" ", 1)
                    target = parts[0].strip()
                    text = parts[1].strip() if len(parts) > 1 else ""
                    if text:
                        await self.direct_send(target, text)
            elif inp == "/msg":
                await self.direct_message()
            elif inp.isdigit() and self.current_chat is None:
                idx = int(inp) - 1
                chat_list = sorted(self.chats.items(), key=lambda x: x[1]["name"])
                if 0 <= idx < len(chat_list):
                    self.current_chat = chat_list[idx][0]
            elif self.current_chat and inp:
                await self.send_message(self.current_chat, inp)
                
            await asyncio.sleep(0.05)
            
        for cid in self.messages:
            self.save_chat_history(cid)
        if self.bot:
            await self.bot.shutdown()
        self.clear_screen()
        print(f"{Fore.GREEN}Goodbye from PyBotGram!{Style.RESET_ALL}")

    async def direct_send(self, target, text):
        try:
            clean = target.lstrip("@")
            if clean.isdigit():
                chat_id = int(clean)
                cname = f"ID{chat_id}"
                await self.bot.send_message(chat_id=chat_id, text=text)
            else:
                cname = f"@{clean}"
                sent = await self.bot.send_message(chat_id=cname, text=text)
                chat_id = sent.chat.id

            self.chats[chat_id] = {"name": cname, "last": text, "time": datetime.now().strftime("%H:%M")}
            self.messages.setdefault(chat_id, []).append({
                "from": "You",
                "text": text,
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": "out",
            })
            self.current_chat = chat_id
            self.save_chat_history(chat_id)
            print(f"\n{Fore.GREEN}[✓] Sent to {cname}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[✗] {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)


async def main():
    bot = PyBotGram()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
