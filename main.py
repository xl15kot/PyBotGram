import asyncio
import os
import sys
import json
import io
import shutil
import zipfile
import urllib.request
from datetime import datetime
from pathlib import Path

from colorama import init, Fore, Style
from telegram import Bot, ChatPermissions

init(autoreset=True)

VERSION = "2.0"
GITHUB_REPO = "xl15kot/PyBotGram"
SESSION_FILE = "pybotgram_session.json"
HISTORY_DIR = "pybotgram_history"
BLACKLIST_FILE = "pybotgram_blacklist.json"

Path(HISTORY_DIR).mkdir(exist_ok=True)

EMOJI_MAP = {
    "user":       ("\U0001F464", ">"),
    "photo":      ("\U0001F4F7", "[Photo]"),
    "sticker":    ("\U0001F3AD", "[Sticker]"),
    "doc":        ("\U0001F4C4", "[Doc]"),
    "video":      ("\U0001F3AC", "[Video]"),
    "audio":      ("\U0001F3B5", "[Audio]"),
    "voice":      ("\U0001F3A4", "[Voice]"),
    "gif":        ("\U0001F39E", "[GIF]"),
    "video_note": ("\U0001F3A5", "[VideoNote]"),
    "media":      ("\U0001F4E6", "[Media]"),
    "check":      ("\u2713", "[v]"),
    "cross":     ("\u2717", "[x]"),
    "bullet":     ("\u25CF", "#"),
    "dot":        ("\u25C9", "*"),
    "reply":      ("\u21A9", "[RE]"),
    "arrow_r":    ("\u2192", ">"),
    "arrow_l":    ("\u2190", "<"),
    "bl_mark":    ("\U0001F534", "[BL]"),
    "pin":        ("\U0001F4CC", "[Pin]"),
    "download":   ("\U0001F4E5", "[DL]"),
    "update":     ("\U0001F504", "[Upd]"),
}

def detect_emoji_support():
    try:
        lang = os.environ.get("LANG", "")
        term = os.environ.get("TERM", "")
        if "UTF-8" in lang.upper() or "UTF8" in lang.upper():
            return True
        if term in ("xterm-256color", "xterm-kitty", "alacritty", "wezterm", "foot", "st-256color"):
            return True
    except:
        pass
    return False

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
        self.blacklist = set()
        self.last_outgoing = {}
        self.use_emoji = detect_emoji_support()
        self.update_available = False
        self.update_version = ""

        self.load_sessions()
        self.load_blacklist()
        self.load_chat_history()

    def emoji(self, name):
        pair = EMOJI_MAP.get(name)
        return pair[0] if pair and self.use_emoji else (pair[1] if pair else "")

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def load_sessions(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.remember = data.get('remember', False)
                    self.use_emoji = data.get('use_emoji', self.use_emoji)
            except:
                pass

    def save_session(self):
        data = {'token': self.token, 'remember': self.remember, 'use_emoji': self.use_emoji}
        if self.remember and self.token:
            with open(SESSION_FILE, 'w') as f:
                json.dump(data, f)
        elif os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def load_blacklist(self):
        if os.path.exists(BLACKLIST_FILE):
            try:
                with open(BLACKLIST_FILE, 'r') as f:
                    self.blacklist = set(json.load(f).get('blocked', []))
            except:
                pass

    def save_blacklist(self):
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump({'blocked': list(self.blacklist)}, f, indent=2)

    def load_chat_history(self):
        for file in Path(HISTORY_DIR).glob("chat_*.json"):
            try:
                with open(file, 'r') as f:
                    cid = int(file.stem.split('_')[1])
                    data = json.load(f)
                    self.messages[cid] = data.get('messages', [])
                    if 'chat_info' in data:
                        self.chats[cid] = data['chat_info']
            except:
                pass

    def save_chat_history(self, cid):
        if cid in self.messages:
            try:
                with open(Path(HISTORY_DIR) / f"chat_{cid}.json", 'w') as f:
                    json.dump({'chat_id': cid, 'chat_info': self.chats.get(cid, {}),
                               'messages': self.messages[cid][-200:]}, f, indent=2)
            except:
                pass

    def truncate(self, s, n=30):
        return (s[:n] + "..") if s and len(s) > n else (s or "")

    async def check_update(self):
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "PyBotGram"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                tag = data.get("tag_name", "").lstrip("v")
                if tag and tag > VERSION:
                    self.update_available = True
                    self.update_version = tag
                    return tag, data.get("zipball_url", "")
        except:
            pass
        return None, None

    async def perform_update(self):
        _, zip_url = await self.check_update()
        if not zip_url:
            print(f"\n{Fore.YELLOW}[!] No update available{Style.RESET_ALL}")
            await asyncio.sleep(1.5)
            return
        print(f"\n{Fore.CYAN}{self.emoji('download')} Downloading v{self.update_version}...{Style.RESET_ALL}")
        req = urllib.request.Request(zip_url, headers={"User-Agent": "PyBotGram"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                z = zipfile.ZipFile(io.BytesIO(resp.read()))
                updated = False
                for name in z.namelist():
                    fname = Path(name).name
                    if fname in ("main.py", "README.md"):
                        parts = Path(name).parts
                        extract_path = Path(fname)
                        if extract_path.exists():
                            shutil.copy2(extract_path, f"{extract_path}.bak")
                        with z.open(name) as src, open(extract_path, 'wb') as dst:
                            dst.write(src.read())
                        if fname == "main.py":
                            updated = True
                if updated:
                    print(f"\n{Fore.GREEN}{self.emoji('check')} Updated to v{self.update_version}! Restarting...{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    self.running = False
                    os.execl(sys.executable, sys.executable, "main.py")
                else:
                    print(f"\n{Fore.RED}{self.emoji('cross')} main.py not found in release{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} Update failed: {e}{Style.RESET_ALL}")
        await asyncio.sleep(2)

    def extract_media_info(self, msg):
        if msg.photo:
            return f"{self.emoji('photo')}", msg.photo[-1].file_id, msg.caption or "", "photo"
        if msg.sticker:
            return f"{self.emoji('sticker')} {msg.sticker.emoji or ''}", msg.sticker.file_id, "", "sticker"
        if msg.document:
            n = msg.document.file_name or "file"
            return f"{self.emoji('doc')} {n}", msg.document.file_id, msg.caption or "", "document"
        if msg.video:
            n = msg.video.file_name or "video"
            return f"{self.emoji('video')} {n}", msg.video.file_id, msg.caption or "", "video"
        if msg.audio:
            n = msg.audio.file_name or msg.audio.title or "audio"
            return f"{self.emoji('audio')} {n}", msg.audio.file_id, msg.caption or "", "audio"
        if msg.voice:
            return f"{self.emoji('voice')}", msg.voice.file_id, "", "voice"
        if msg.animation:
            return f"{self.emoji('gif')}", msg.animation.file_id, msg.caption or "", "animation"
        if msg.video_note:
            return f"{self.emoji('video_note')}", msg.video_note.file_id, "", "video_note"
        return None, None, None, None

    async def fetch_updates(self):
        while self.running:
            try:
                for update in await self.bot.get_updates(offset=self.update_offset, timeout=1, read_timeout=5):
                    self.update_offset = update.update_id + 1
                    msg = update.message or update.edited_message
                    if not msg:
                        continue
                    cid, uid = msg.chat.id, msg.from_user.id
                    if uid in self.blacklist:
                        continue
                    cname = msg.chat.title or msg.chat.username or f"User_{cid}"
                    uname = msg.from_user.first_name or msg.from_user.username or str(uid)
                    if msg.text:
                        display = msg.text; mtype = None; fid = None
                    else:
                        display, fid, cap, mtype = self.extract_media_info(msg)
                        if not display:
                            display = f"{self.emoji('media')}"; mtype = "unknown"
                        if cap:
                            display = f"{display} | {cap[:40]}"
                    self.chats.setdefault(cid, {})["name"] = cname
                    self.chats[cid]["last"] = display
                    self.chats[cid]["time"] = datetime.now().strftime("%H:%M")
                    self.messages.setdefault(cid, [])
                    entry = {"from": uname, "text": display, "time": datetime.now().strftime("%H:%M:%S"),
                             "type": "in", "msg_id": msg.message_id, "user_id": uid}
                    if mtype:
                        entry["media_type"] = mtype; entry["file_id"] = fid
                    self.messages[cid].append(entry)
                    if len(self.messages[cid]) > 200:
                        self.messages[cid] = self.messages[cid][-200:]
            except:
                pass
            await asyncio.sleep(1)

    def render(self):
        self.clear_screen()
        upd = f" {Fore.GREEN}{self.emoji('update')} v{self.update_version}{Style.RESET_ALL}" if self.update_available else ""
        print(f"{Fore.CYAN}@PyBotGram v{VERSION}{upd}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.emoji('user')} {self.me.first_name or self.me.username}{Style.RESET_ALL}  {Fore.RED}ЧС: {len(self.blacklist)}{Style.RESET_ALL}")
        print()
        clist = sorted(self.chats.items(), key=lambda x: x[1]["name"])
        if clist:
            print(f"{Fore.GREEN}CHATS ({len(clist)}){Style.RESET_ALL}")
            for i, (cid, info) in enumerate(clist[:15], 1):
                m = "\u2192" if cid == self.current_chat else " "
                bl = f"{Fore.RED}[ЧС]{Style.RESET_ALL} " if info.get("user_id") in self.blacklist else ""
                print(f"  {m} {Fore.YELLOW}{i}.{Style.RESET_ALL} {bl}{info['name'][:25]}")
                last = self.truncate(info.get("last", ""), 35)
                if last:
                    print(f"     {Style.DIM}\u2514 {last}{Style.RESET_ALL}")
        else:
            print(f"{Style.DIM}No chats yet{Style.RESET_ALL}")
            print(f"{Style.DIM}Write to bot in Telegram first{Style.RESET_ALL}")
        if self.current_chat and self.current_chat in self.chats:
            print()
            print(f"{Fore.CYAN}\u2500\u2500\u2500 {self.chats[self.current_chat]['name']} \u2500\u2500\u2500{Style.RESET_ALL}")
            for idx, m in enumerate(self.messages.get(self.current_chat, [])[-10:]):
                arrow = "\u2192" if m.get('type') == 'out' else "\u2190"
                color = Fore.GREEN if m.get('type') == 'out' else Fore.CYAN
                n, t, mn = m['from'][:15], m['text'][:50], len(self.messages.get(self.current_chat, [])[-10:]) - idx
                print(f"  {Style.DIM}[{m['time'][:5]}]{Style.RESET_ALL} {color}{arrow}{Style.RESET_ALL} {n}: {t}  {Style.DIM}({mn}){Style.RESET_ALL}")
        th = os.get_terminal_size().lines
        ul = 6 + len(clist) * 2 + len(self.messages.get(self.current_chat, [])[-10:]) + 2
        for _ in range(max(0, th - ul - 3)):
            print()
        print(f"{Fore.CYAN}{'\u2500'*40}{Style.RESET_ALL}")
        print(f"{Style.DIM}:h :b :s :p :d :v :a :send :r :fwd :del :info :find :update :emoji :q{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}> {Style.RESET_ALL}", end="", flush=True)

    async def send_message(self, cid, text):
        try:
            msg = await self.bot.send_message(chat_id=cid, text=text)
            self.record_outgoing(cid, text, msg.message_id)
            return True
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} Error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(1)
            return False

    def record_outgoing(self, cid, text, mid):
        self.messages.setdefault(cid, []).append(
            {"from": "You", "text": text, "time": datetime.now().strftime("%H:%M:%S"), "type": "out", "msg_id": mid})
        self.last_outgoing[cid] = mid
        if cid in self.chats:
            self.chats[cid]["last"] = text
            self.chats[cid]["time"] = datetime.now().strftime("%H:%M")
        self.save_chat_history(cid)

    def guess_media_type(self, path):
        ext = Path(path).suffix.lower()
        img = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
        vid = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"}
        aud = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"}
        if ext in img: return "photo"
        if ext in vid: return "video"
        if ext in aud: return "audio"
        if ext == ".webp": return "sticker"
        if ext == ".oga": return "voice"
        return "document"

    async def send_sticker(self, cid, value):
        try:
            p = Path(value)
            if p.exists():
                with open(p, "rb") as f:
                    msg = await self.bot.send_sticker(chat_id=cid, sticker=f)
            else:
                msg = await self.bot.send_sticker(chat_id=cid, sticker=value)
            self.record_outgoing(cid, f"{self.emoji('sticker')}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Sticker sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_photo(self, cid, path, cap=""):
        try:
            with open(path, "rb") as f:
                msg = await self.bot.send_photo(chat_id=cid, photo=f, caption=cap or None)
            self.record_outgoing(cid, f"{self.emoji('photo')} {cap}" if cap else f"{self.emoji('photo')}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Photo sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_document(self, cid, path, cap=""):
        try:
            fn = Path(path).name
            with open(path, "rb") as f:
                msg = await self.bot.send_document(chat_id=cid, document=f, caption=cap or None)
            self.record_outgoing(cid, f"{self.emoji('doc')} {fn}{' | ' + cap if cap else ''}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Document sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_video(self, cid, path, cap=""):
        try:
            fn = Path(path).name
            with open(path, "rb") as f:
                msg = await self.bot.send_video(chat_id=cid, video=f, caption=cap or None)
            self.record_outgoing(cid, f"{self.emoji('video')} {fn}{' | ' + cap if cap else ''}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Video sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_audio(self, cid, path, cap=""):
        try:
            fn = Path(path).name
            with open(path, "rb") as f:
                msg = await self.bot.send_audio(chat_id=cid, audio=f, caption=cap or None)
            self.record_outgoing(cid, f"{self.emoji('audio')} {fn}{' | ' + cap if cap else ''}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Audio sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_voice(self, cid, path):
        try:
            with open(path, "rb") as f:
                msg = await self.bot.send_voice(chat_id=cid, voice=f)
            self.record_outgoing(cid, f"{self.emoji('voice')}", msg.message_id)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Voice sent{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def send_media(self, cid, path, cap=""):
        path = path.strip().strip("'\"")
        if not os.path.exists(path):
            print(f"\n{Fore.RED}{self.emoji('cross')} File not found: {path}{Style.RESET_ALL}")
            await asyncio.sleep(1)
            return
        t = self.guess_media_type(path)
        m = {"sticker": self.send_sticker, "photo": self.send_photo, "video": self.send_video,
             "audio": self.send_audio, "voice": self.send_voice}
        await m.get(t, self.send_document)(cid, path, cap)

    async def resolve_target(self, target):
        clean = target.lstrip("@")
        if clean.isdigit():
            return int(clean), f"ID{clean}"
        try:
            cname = f"@{clean}"
            s = await self.bot.send_message(chat_id=cname, text=".")
            await self.bot.delete_message(chat_id=s.chat.id, message_id=s.message_id)
            return s.chat.id, cname
        except:
            return None, None

    async def resolve_user_id(self, target):
        clean = target.lstrip("@")
        if clean.isdigit():
            return int(clean)
        for cid in ([self.current_chat] if self.current_chat else list(self.chats.keys())):
            try:
                for m in await self.bot.get_chat_administrators(cid):
                    if (m.user.username and m.user.username.lower() == clean.lower()) or \
                       (m.user.first_name and m.user.first_name.lower() == clean.lower()):
                        return m.user.id
            except:
                pass
            try:
                return (await self.bot.get_chat_member(cid, f"@{clean}")).user.id
            except:
                pass
        return None

    async def show_help(self):
        self.clear_screen()
        print(f"{Fore.CYAN}PYBOTGRAM HELP v{VERSION}{Style.RESET_ALL}")
        print()
        cmds = [
            ("[number]", "Select chat by number"),
            (":b", "Exit current chat"),
            (":r text", "Reply to last message"),
            (":fwd @user", "Forward last message"),
            (":del", "Delete last sent message"),
            (":mes @user text", "Send to username/ID"),
            (":s path/id", "Send sticker"),
            (":p path [cap]", "Send photo"),
            (":d path [cap]", "Send document"),
            (":v path [cap]", "Send video"),
            (":a path [cap]", "Send audio"),
            (":voice path", "Send voice"),
            (":send path", "Auto-detect and send"),
            (":info", "Chat info"),
            (":find text", "Search history"),
            (":clear", "Clear local history"),
            (":block @user", "Add to blacklist"),
            (":unblock @user", "Remove from blacklist"),
            (":blocklist", "Show blacklist"),
            (":ban @user", "Ban from group"),
            (":unban @user", "Unban user"),
            (":kick @user", "Kick from group"),
            (":mute @user", "Mute user"),
            (":unmute @user", "Unmute user"),
            (":update", "Check for updates"),
            (":emoji", "Toggle emoji on/off"),
            (":set", "Settings"),
            (":h", "This help"),
            (":q", "Quit"),
        ]
        for cmd, desc in cmds:
            print(f"  {Fore.YELLOW}{cmd:<20}{Style.RESET_ALL} {desc}")
        print()
        print(f"{Style.DIM}Just type a message to send to current chat{Style.RESET_ALL}")
        input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")

    async def settings_menu(self):
        while True:
            self.clear_screen()
            emoji_status = f"{Fore.GREEN}ON{Style.RESET_ALL}" if self.use_emoji else f"{Fore.RED}OFF{Style.RESET_ALL}"
            print(f"{Fore.CYAN}PYBOTGRAM SETTINGS{Style.RESET_ALL}")
            print()
            print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} Bot info")
            print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} Logout")
            print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} Blacklist ({len(self.blacklist)})")
            print(f"  {Fore.YELLOW}[4]{Style.RESET_ALL} Clear all history")
            print(f"  {Fore.YELLOW}[5]{Style.RESET_ALL} Emoji: {emoji_status}")
            print(f"  {Fore.YELLOW}[6]{Style.RESET_ALL} Check for updates")
            print(f"  {Fore.YELLOW}[0]{Style.RESET_ALL} Back")
            print()
            c = input(f"{Style.BRIGHT}> {Style.RESET_ALL}").strip()
            if c == "0":
                break
            elif c == "1":
                self.clear_screen()
                print(f"{Fore.CYAN}Bot info{Style.RESET_ALL}\n")
                print(f"  Name: {self.me.first_name}")
                if self.me.last_name: print(f"  Last: {self.me.last_name}")
                print(f"  ID: {self.me.id}")
                if self.me.username: print(f"  Username: @{self.me.username}")
                print(f"  Version: v{VERSION}")
                print()
                input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")
            elif c == "2":
                if input(f"{Fore.RED}Logout? (y/n):{Style.RESET_ALL} ").strip().lower() == 'y':
                    self.remember = False; self.token = None; self.save_session(); self.running = False; return
            elif c == "3":
                await self.show_blocklist()
            elif c == "4":
                if input(f"{Fore.RED}Clear ALL history? (y/n):{Style.RESET_ALL} ").strip().lower() == 'y':
                    self.messages = {}; self.chats = {}
                    for f in Path(HISTORY_DIR).glob("chat_*.json"): f.unlink()
                    print(f"{Fore.GREEN}{self.emoji('check')} History cleared{Style.RESET_ALL}")
                    await asyncio.sleep(1)
            elif c == "5":
                self.use_emoji = not self.use_emoji
                self.save_session()
                print(f"{Fore.GREEN}Emoji {'ON' if self.use_emoji else 'OFF'}{Style.RESET_ALL}")
                await asyncio.sleep(1)
            elif c == "6":
                await self.perform_update()

    async def show_blocklist(self):
        self.clear_screen()
        print(f"{Fore.CYAN}BLACKLIST ({len(self.blacklist)}){Style.RESET_ALL}\n")
        if self.blacklist:
            for uid in sorted(self.blacklist):
                print(f"  {Fore.RED}{self.emoji('bullet')}{Style.RESET_ALL} {uid}")
        else:
            print(f"  {Style.DIM}Blacklist is empty{Style.RESET_ALL}")
        print(f"\n{Style.DIM}:block @user | :unblock @user{Style.RESET_ALL}")
        input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")

    async def block_user(self, target):
        uid, name = await self.resolve_target(target)
        if not uid:
            uid = await self.resolve_user_id(target)
        if uid:
            self.blacklist.add(uid); self.save_blacklist()
            print(f"\n{Fore.RED}[ЧС] {uid} blocked{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{self.emoji('cross')} User not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def unblock_user(self, target):
        clean = target.lstrip("@")
        if clean.isdigit():
            uid = int(clean)
            if uid in self.blacklist:
                self.blacklist.discard(uid); self.save_blacklist()
                print(f"\n{Fore.GREEN}{self.emoji('check')} {uid} unblocked{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}[!] Not in blacklist{Style.RESET_ALL}")
        else:
            for uid in list(self.blacklist):
                try:
                    chat = await self.bot.get_chat(uid)
                    if chat.username and chat.username.lower() == clean.lower():
                        self.blacklist.discard(uid); self.save_blacklist()
                        print(f"\n{Fore.GREEN}{self.emoji('check')} @{clean} unblocked{Style.RESET_ALL}")
                        await asyncio.sleep(1); return
                except:
                    pass
            print(f"\n{Fore.RED}{self.emoji('cross')} @{clean} not in blacklist{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def ban_user(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a group first{Style.RESET_ALL}"); await asyncio.sleep(1); return
        uid = await self.resolve_user_id(target)
        if uid:
            try:
                await self.bot.ban_chat_member(chat_id=self.current_chat, user_id=uid)
                print(f"\n{Fore.RED}[BAN] {uid}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def unban_user(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a group first{Style.RESET_ALL}"); await asyncio.sleep(1); return
        uid = await self.resolve_user_id(target)
        if uid:
            try:
                await self.bot.unban_chat_member(chat_id=self.current_chat, user_id=uid)
                print(f"\n{Fore.GREEN}[UNBAN] {uid}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def kick_user(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a group first{Style.RESET_ALL}"); await asyncio.sleep(1); return
        uid = await self.resolve_user_id(target)
        if uid:
            try:
                await self.bot.ban_chat_member(chat_id=self.current_chat, user_id=uid)
                await self.bot.unban_chat_member(chat_id=self.current_chat, user_id=uid)
                print(f"\n{Fore.YELLOW}[KICK] {uid}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def mute_user(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a group first{Style.RESET_ALL}"); await asyncio.sleep(1); return
        uid = await self.resolve_user_id(target)
        if uid:
            try:
                await self.bot.restrict_chat_member(chat_id=self.current_chat, user_id=uid, permissions=ChatPermissions(can_send_messages=False))
                print(f"\n{Fore.YELLOW}[MUTE] {uid}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def unmute_user(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a group first{Style.RESET_ALL}"); await asyncio.sleep(1); return
        uid = await self.resolve_user_id(target)
        if uid:
            try:
                await self.bot.restrict_chat_member(chat_id=self.current_chat, user_id=uid,
                    permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                can_send_other_messages=True, can_add_web_page_previews=True))
                print(f"\n{Fore.GREEN}[UNMUTE] {uid}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def reply_last(self, text):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        last = None
        for m in reversed(self.messages.get(self.current_chat, [])):
            if m.get('type') == 'in' and 'msg_id' in m: last = m['msg_id']; break
        if last:
            try:
                msg = await self.bot.send_message(chat_id=self.current_chat, text=text, reply_to_message_id=last)
                self.record_outgoing(self.current_chat, f"{self.emoji('reply')} {text}", msg.message_id)
                print(f"\n{Fore.GREEN}{self.emoji('check')} Reply sent{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.YELLOW}[!] Nothing to reply to{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def forward_last(self, target):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        last = None
        for m in reversed(self.messages.get(self.current_chat, [])):
            if m.get('type') == 'in' and 'msg_id' in m: last = m['msg_id']; break
        if not last: print(f"\n{Fore.YELLOW}[!] Nothing to forward{Style.RESET_ALL}"); await asyncio.sleep(1); return
        tid, tn = await self.resolve_target(target)
        if tid:
            try:
                await self.bot.forward_message(chat_id=tid, from_chat_id=self.current_chat, message_id=last)
                print(f"\n{Fore.GREEN}{self.emoji('check')} Forwarded to {tn}{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.RED}{self.emoji('cross')} Target not found{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def delete_last(self):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        mid = self.last_outgoing.get(self.current_chat)
        if mid:
            try:
                await self.bot.delete_message(chat_id=self.current_chat, message_id=mid)
                msgs = self.messages.get(self.current_chat, [])
                for m in msgs:
                    if m.get('msg_id') == mid: msgs.remove(m); break
                self.save_chat_history(self.current_chat)
                print(f"\n{Fore.GREEN}{self.emoji('check')} Deleted{Style.RESET_ALL}")
            except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        else: print(f"\n{Fore.YELLOW}[!] Nothing to delete{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def show_chat_info(self):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        cid = self.current_chat
        print(f"\n{Fore.CYAN}CHAT INFO{Style.RESET_ALL}")
        print(f"  Name: {self.chats.get(cid, {}).get('name', 'N/A')}")
        print(f"  ID: {cid}")
        try:
            chat = await self.bot.get_chat(cid)
            print(f"  Type: {chat.type}")
            if chat.username: print(f"  Username: @{chat.username}")
            if chat.description: print(f"  Description: {chat.description[:100]}")
            if hasattr(chat, 'member_count') and chat.member_count: print(f"  Members: {chat.member_count}")
        except: pass
        print(f"  Stored: {len(self.messages.get(cid, []))} msgs")
        input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")

    async def find_messages(self, query):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        if not query: print(f"\n{Fore.YELLOW}[!] :find text{Style.RESET_ALL}"); await asyncio.sleep(1); return
        res = [m for m in self.messages.get(self.current_chat, []) if query.lower() in m.get('text', '').lower()]
        self.clear_screen()
        print(f"{Fore.CYAN}SEARCH: \"{query}\" ({len(res)}){Style.RESET_ALL}\n")
        if res:
            for m in res[-20:]:
                a = "\u2192" if m.get('type') == 'out' else "\u2190"
                print(f"  [{m['time']}] {a} {m['from'][:15]}: {m['text'][:60]}")
        else: print(f"  {Style.DIM}No results{Style.RESET_ALL}")
        input(f"{Style.DIM}Press Enter...{Style.RESET_ALL}")

    async def clear_history(self):
        if not self.current_chat: print(f"\n{Fore.RED}{self.emoji('cross')} Open a chat{Style.RESET_ALL}"); await asyncio.sleep(1); return
        if input(f"{Fore.RED}Clear history? (y/n):{Style.RESET_ALL} ").strip().lower() == 'y':
            self.messages[self.current_chat] = []
            p = Path(HISTORY_DIR) / f"chat_{self.current_chat}.json"
            if p.exists(): p.unlink()
            print(f"{Fore.GREEN}{self.emoji('check')} Cleared{Style.RESET_ALL}")
        await asyncio.sleep(1)

    async def direct_message(self):
        self.clear_screen()
        print(f"{Fore.CYAN}DIRECT MESSAGE{Style.RESET_ALL}\n")
        target = input(f"To (@user or ID): ").strip()
        if not target: return
        text = input(f"Message: ").strip()
        if not text: return
        try:
            cid = int(target.lstrip("@")) if target.lstrip("@").isdigit() else f"@{target.lstrip('@')}"
            await self.bot.send_message(chat_id=cid, text=text)
            print(f"\n{Fore.GREEN}{self.emoji('check')} Sent!{Style.RESET_ALL}")
        except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1.5)

    async def run(self):
        if not await self.login(): return
        asyncio.create_task(self.fetch_updates())
        asyncio.create_task(self.background_update_check())
        while self.running:
            self.render()
            inp = sys.stdin.readline().strip()
            if inp in ("/exit", ":q", ":wq"): self.running = False; break
            elif inp in ("/back", ":b"): self.current_chat = None
            elif inp in ("/help", ":help", ":h"): await self.show_help()
            elif inp in ("/set", "/settings", ":set"):
                await self.settings_menu()
                if not self.running: break
            elif inp.startswith(":r "):
                t = inp[3:].strip()
                if t: await self.reply_last(t)
            elif inp.startswith(":fwd "):
                t = inp[5:].strip()
                if t: await self.forward_last(t)
            elif inp == ":del": await self.delete_last()
            elif inp == ":emoji":
                self.use_emoji = not self.use_emoji; self.save_session()
                print(f"\n{Fore.GREEN}Emoji {'ON' if self.use_emoji else 'OFF'}{Style.RESET_ALL}")
                await asyncio.sleep(1)
            elif inp == ":update":
                await self.perform_update()
            elif inp.startswith(":mes ") or inp.startswith("/msg "):
                p = ":mes " if inp.startswith(":mes ") else "/msg "
                r = inp[len(p):].strip()
                if r:
                    parts = r.split(" ", 1)
                    if len(parts) > 1: await self.direct_send(parts[0].strip(), parts[1].strip())
            elif inp == "/msg": await self.direct_message()
            elif inp.startswith(":block ") or inp.startswith("/block "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.block_user(t)
            elif inp.startswith(":unblock ") or inp.startswith("/unblock "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.unblock_user(t)
            elif inp in (":blocklist", "/blocklist", ":bl"): await self.show_blocklist()
            elif inp.startswith(":ban ") or inp.startswith("/ban "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.ban_user(t)
            elif inp.startswith(":unban ") or inp.startswith("/unban "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.unban_user(t)
            elif inp.startswith(":kick ") or inp.startswith("/kick "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.kick_user(t)
            elif inp.startswith(":mute ") or inp.startswith("/mute "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.mute_user(t)
            elif inp.startswith(":unmute ") or inp.startswith("/unmute "):
                t = inp.split(" ", 1)[1].strip()
                if t: await self.unmute_user(t)
            elif inp in (":info", "/info"): await self.show_chat_info()
            elif inp.startswith(":find ") or inp.startswith("/find "):
                q = inp.split(" ", 1)[1].strip()
                await self.find_messages(q)
            elif inp in (":clear", "/clear"): await self.clear_history()
            elif inp.startswith(":s ") and self.current_chat:
                v = inp[3:].strip()
                if v: await self.send_sticker(self.current_chat, v)
            elif inp.startswith(":p ") and self.current_chat:
                r = inp[3:].strip()
                if r:
                    parts = r.split(" ", 1)
                    await self.send_photo(self.current_chat, parts[0], parts[1] if len(parts) > 1 else "")
            elif inp.startswith(":d ") and self.current_chat:
                r = inp[3:].strip()
                if r:
                    parts = r.split(" ", 1)
                    await self.send_document(self.current_chat, parts[0], parts[1] if len(parts) > 1 else "")
            elif inp.startswith(":v ") and self.current_chat:
                r = inp[3:].strip()
                if r:
                    parts = r.split(" ", 1)
                    await self.send_video(self.current_chat, parts[0], parts[1] if len(parts) > 1 else "")
            elif inp.startswith(":a ") and self.current_chat:
                r = inp[3:].strip()
                if r:
                    parts = r.split(" ", 1)
                    await self.send_audio(self.current_chat, parts[0], parts[1] if len(parts) > 1 else "")
            elif inp.startswith(":voice ") and self.current_chat:
                p = inp[7:].strip()
                if p: await self.send_voice(self.current_chat, p)
            elif inp.startswith(":send ") and self.current_chat:
                r = inp[6:].strip()
                if r:
                    parts = r.split(" ", 1)
                    await self.send_media(self.current_chat, parts[0], parts[1] if len(parts) > 1 else "")
            elif inp.isdigit() and self.current_chat is None:
                clist = sorted(self.chats.items(), key=lambda x: x[1]["name"])
                idx = int(inp) - 1
                if 0 <= idx < len(clist): self.current_chat = clist[idx][0]
            elif self.current_chat and inp:
                await self.send_message(self.current_chat, inp)
            await asyncio.sleep(0.05)
        for cid in self.messages: self.save_chat_history(cid)
        if self.bot: await self.bot.shutdown()
        self.clear_screen()
        print(f"{Fore.GREEN}Goodbye from PyBotGram!{Style.RESET_ALL}")

    async def background_update_check(self):
        await asyncio.sleep(3)
        ver, _ = await self.check_update()
        if ver:
            self.update_available = True
            self.update_version = ver

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
        lw, pad = 62, (cols - 62) // 2
        print(f"\n{Fore.CYAN}{' ' * pad}{'═' * lw}{Style.RESET_ALL}\n")
        for line in logo: print(f"{Fore.CYAN}{' ' * pad}{line}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{' ' * pad}{'═' * lw}{Style.RESET_ALL}\n")
        print(f"{' ' * ((cols - 30) // 2)}{Style.BRIGHT}Telegram Bot Client{Style.RESET_ALL}")
        print(f"{' ' * ((cols - 30) // 2)}{Style.DIM}v{VERSION}{Style.RESET_ALL}\n")
        if self.token and self.remember:
            print(f"{' ' * ((cols - 40) // 2)}{Fore.GREEN}{self.emoji('dot')} Saved session{Style.RESET_ALL}")
            print(f"{' ' * ((cols - 40) // 2)}{Style.DIM}{self.token[:24]}...{Style.RESET_ALL}\n")
            print(f"{' ' * ((cols - 40) // 2)}{Fore.CYAN}[1]{Style.RESET_ALL} Restore")
            print(f"{' ' * ((cols - 40) // 2)}{Fore.CYAN}[2]{Style.RESET_ALL} New\n")
            if input(f"{' ' * ((cols - 40) // 2)}{Style.BRIGHT}>{Style.RESET_ALL} ").strip() == "1":
                try:
                    self.bot = Bot(self.token); await self.bot.initialize()
                    self.me = await self.bot.get_me(); return True
                except Exception as e:
                    print(f"{' ' * ((cols - 40) // 2)}{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
                    await asyncio.sleep(1); self.clear_screen()
        print(f"\n{' ' * ((cols - 50) // 2)}{Fore.YELLOW}{'═'*15}  Sign In  {'═'*15}{Style.RESET_ALL}\n")
        token = input(f"{' ' * ((cols - 50) // 2)}{Style.BRIGHT}Bot Token:{Style.RESET_ALL} ").strip()
        try:
            self.bot = Bot(token); await self.bot.initialize()
            self.me = await self.bot.get_me(); self.token = token
            print(f"\n{' ' * ((cols - 50) // 2)}{Fore.GREEN}{self.emoji('dot')} Signed in as {Style.BRIGHT}{self.me.first_name}{Style.RESET_ALL}")
            print(f"{' ' * ((cols - 50) // 2)}{Style.DIM}@{self.me.username or 'no username'}{Style.RESET_ALL}\n")
            self.remember = input(f"{' ' * ((cols - 50) // 2)}{Fore.CYAN}Remember? (y/n):{Style.RESET_ALL} ").strip().lower() in ('y', 'yes')
            self.save_session(); await asyncio.sleep(1); return True
        except Exception as e:
            print(f"\n{' ' * ((cols - 50) // 2)}{Fore.RED}{self.emoji('cross')} Error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(2); return False

    async def direct_send(self, target, text):
        try:
            clean = target.lstrip("@")
            if clean.isdigit():
                cid, cname = int(clean), f"ID{clean}"
                msg = await self.bot.send_message(chat_id=cid, text=text)
            else:
                cname = f"@{clean}"
                msg = await self.bot.send_message(chat_id=cname, text=text)
                cid = msg.chat.id
            self.chats[cid] = {"name": cname, "last": text, "time": datetime.now().strftime("%H:%M")}
            self.record_outgoing(cid, text, msg.message_id)
            self.chats[cid]["name"] = cname; self.current_chat = cid
            print(f"\n{Fore.GREEN}{self.emoji('check')} Sent to {cname}{Style.RESET_ALL}")
        except Exception as e: print(f"\n{Fore.RED}{self.emoji('cross')} {e}{Style.RESET_ALL}")
        await asyncio.sleep(1)

async def main():
    bot = PyBotGram()
    await bot.run()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
    except Exception as e: print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
