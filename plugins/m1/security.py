import __main__
from telethon import events
from telethon.tl.functions.contacts import BlockRequest
import asyncio
import re

client = __main__.client

# مخازن الحماية
sec_config = {} 
muted_users = set()
banned_users = set()
flood_check = {}

@client.on(events.NewMessage(pattern=r"^\.تفعيل حماية$"))
async def start_security(event):
    user_id = event.sender_id
    sec_config[user_id] = {
        'step': 'choose_types',
        'active_rules': [],
        'action': None,
        'last_msg_id': None,
        'enabled': False
    }
    
    text = (
        "★──────────☭──────────★\n"
        "   ☭ • **𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁** • ☭\n"
        "★──────────☭──────────★\n\n"
        "🛡️ **مرحباً بك في قسم الحماية:**\n\n"
        "• يرجى اختيار نوع الحماية (بالرد):\n"
        "1- `الروابط` (لمنع الإعلانات)\n"
        "2- `السبام` (لمنع التكرار)\n"
        "3- `التوجيه` (لمنع التوجيه)\n"
        "4- `الكل` (لتفعيل الجميع)\n\n"
        "**- أرسل اختيارك الآن بالرد :**\n"
        "★──────────☭──────────★"
    )
    msg = await event.edit(text)
    sec_config[user_id]['last_msg_id'] = msg.id

@client.on(events.NewMessage(incoming=False))
async def handle_security_setup(event):
    user_id = event.sender_id
    if user_id not in sec_config: return
    data = sec_config[user_id]
    if not event.reply_to_msg_id or event.reply_to_msg_id != data['last_msg_id']: return

    text, state = event.text, data['step']

    if state == 'choose_types':
        await event.delete()
        data['active_rules'] = ["الروابط", "السبام", "التوجيه"] if text == "الكل" else [text]
        data['step'] = 'choose_action'
        await client.edit_message(event.chat_id, data['last_msg_id'], f"★──────────☭──────────★\n✅ **تم اختيار:** {text}\n★──────────☭──────────★\n\n⚠️ **حدد الإجراء:**\n• `كتم` أو `حظر`\n\n**- أرسل الإجراء بالرد :**")

    elif state == 'choose_action':
        if text in ["كتم", "حظر"]:
            await event.delete()
            data.update({'action': text, 'enabled': True, 'step': 'running'})
            await client.edit_message(event.chat_id, data['last_msg_id'], "★──────────☭──────────★\n🛡️ **نظام الحماية نشط الآن ✅**\n★──────────☭──────────★")

# --- محرك المراقبة (تم تعديل الشروط) ---
@client.on(events.NewMessage(incoming=True))
async def security_monitor(event):
    if not event.is_private: return
    
    sender = await event.get_sender()
    if not sender or sender.is_self: return # لا يحظر صاحب الحساب
    
    sender_id = event.sender_id
    
    # التأكد من وجود إعدادات مفعلة
    if not sec_config: return
    owner_id = list(sec_config.keys())[0]
    data = sec_config[owner_id]
    if not data.get('enabled'): return

    # 1. فحص الروابط (Regex مطور)
    if "الروابط" in data['active_rules'] or "الكل" in data['active_rules']:
        if re.search(r"(http|https|www|t\.me|\.com|\.net|\.org|discord\.gg)", event.text, re.IGNORECASE):
            await event.delete()
            if data['action'] == "حظر":
                await client(BlockRequest(sender_id))
                banned_users.add(sender_id)
            else:
                muted_users.add(sender_id)
            await event.respond("**- عذراً ، تم اتخاذ إجراء بحقك لإرسال رابط 🛡️ .**")
            return

    # 2. فحص السبام
    if "السبام" in data['active_rules'] or "الكل" in data['active_rules']:
        now = asyncio.get_event_loop().time()
        if sender_id not in flood_check: flood_check[sender_id] = []
        flood_check[sender_id] = [t for t in flood_check[sender_id] if now - t < 5]
        flood_check[sender_id].append(now)
        
        if len(flood_check[sender_id]) > 4:
            await event.delete()
            if data['action'] == "حظر":
                await client(BlockRequest(sender_id))
            else:
                muted_users.add(sender_id)
            await event.respond("**- عذراً ، تم اتخاذ إجراء بحقك بسبب التكرار 🛡️ .**")