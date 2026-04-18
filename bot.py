import os
import requests
from pyrogram import Client, filters

# 🔑 CONFIG (edit this)
API_ID = 12425668
API_HASH = "d92ea6995790b6f2de53f52a80e14829"
BOT_TOKEN = "8545287207:AAHZFGCcR46XpLHsfiSOHb2t57Qsm2LOaN8"

# 🌐 Your API
API_URL = "https://tera-core.vercel.app"

# 🔥 Multi-domain fallback
DOMAINS = [
    "https://teradownloaderz.com",
    "https://1024terabox.com",
    "https://teraboxapp.com",
    "https://1024tera.com",
    "https://freeterabox.com",
    "https://terabox.club",
    "https://mirrobox.com",
    "https://terabox.com",
    "https://terasharefile.com"
]

app = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📥 Download function with progress
def download_file(url, filename, message):
    r = requests.get(url, stream=True)
    total = int(r.headers.get("content-length", 0))
    downloaded = 0

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)

                if total > 0:
                    percent = int((downloaded / total) * 100)
                    try:
                        message.edit(f"📥 Downloading... {percent}%")
                    except:
                        pass

# 🔗 Direct domain fallback
def fetch_direct(url):
    for domain in DOMAINS:
        try:
            res = requests.post(
                f"{domain}/wp-admin/admin-ajax.php",
                data={
                    "action": "terabox_fetch",
                    "url": url,
                    "nonce": "3112bd60d1"
                },
                timeout=10
            ).json()

            if res.get("success"):
                file = res["data"]["📄 Files"][0]
                return file["🔽 Direct Download Link"], file["📂 Name"]
        except:
            continue

    return None, None

# 🚀 Main handler
@app.on_message(filters.text)
async def handler(client, message):
    url = message.text.strip()

    if "terabox" not in url and "1024" not in url:
        return await message.reply("❌ Send valid Terabox link")

    msg = await message.reply("⏳ Processing...")

    try:
        dl_link = None
        name = None

        # 🔹 Step 1: Try your API
        try:
            res = requests.get(f"{API_URL}?url={url}", timeout=15).json()
            if res.get("status"):
                dl_link = res["download"]
                name = res["name"]
        except:
            pass

        # 🔥 Step 2: fallback to domains
        if not dl_link:
            await msg.edit("⚠️ API failed, trying backup servers...")
            dl_link, name = fetch_direct(url)

        if not dl_link:
            return await msg.edit("❌ All methods failed")

        file_path = f"./{name}"

        # 📥 Download
        await msg.edit("📥 Downloading...")
        download_file(dl_link, file_path, msg)

        # 📤 Upload
        await msg.edit("📤 Uploading to Telegram...")
        await message.reply_document(file_path)

        # 🧹 Cleanup
        os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

# ▶️ Run bot
app.run()
