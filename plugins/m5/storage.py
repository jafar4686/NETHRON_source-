import __main__
from telethon import events
import os
from cryptography.fernet import Fernet

client = __main__.client

# إنشاء مفتاح تشفير ثابت (يتم إنشاؤه مرة واحدة عند التشغيل)
# ملاحظة: في النسخة الاحترافية يفضل حفظ هذا المفتاح في ملف منفصل
if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
else:
    key = open("secret.key", "rb").read()

cipher = Fernet(key)

# مسار مجلد التخزين
if not os.path.exists("nethron_vault"):
    os.makedirs("nethron_vault")

HEADER = "★────────☭────────★\n"

# 1. قائمة الخزنة .م٥
@client.on(events.NewMessage(pattern=r"^\.م5$"))
async def storage_menu(event):
    msg = (
        f"{HEADER}"
        "   ☭ • 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 𝑉𝐴𝑈𝐿𝑇 • ☭\n"
        "             خزنة نيثرون السرية\n"
        f"{HEADER}\n"
        "📦 **أوامر الحفظ والتخزين:**\n\n"
        "• `.حفظ_ملف` (بالرد على ملف)\n"
        "➥ تشفير وحفظ الملف في السيرفر\n\n"
        "• `.جلب_ملف` (اسم الملف)\n"
        "➥ فك التشفير وإرسال الملف لك\n\n"
        "• `.حفظ_سر` (نص أو بالرد)\n"
        "➥ حفظ رسالة نصية مشفرة تماماً\n\n"
        "• `.جلب_سر` (اسم السر)\n"
        "➥ عرض الرسالة المحفوظة\n\n"
        "• `.ملفاتي` ➥ عرض قائمة المحفوظات\n\n"
        f"{HEADER}"
    )
    await event.edit(msg)

# 2. حفظ الملفات بتشفير
@client.on(events.NewMessage(pattern=r"^\.حفظ_ملف$"))
async def save_file(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file:
        return await event.edit("⚠️ يجب الرد على ملف (صورة، فيديو، مستند)!")
    
    await event.edit("⏳ جاري تشفير وحفظ الملف...")
    path = await reply.download_media(file="nethron_vault/")
    
    # قراءة الملف وتشفيره
    with open(path, "rb") as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    
    with open(path, "wb") as f:
        f.write(encrypted_data)
    
    file_name = os.path.basename(path)
    await event.edit(f"✅ تم الحفظ بنجاح!\nاسم الملف: `{file_name}`\n(الملف الآن مشفر في السيرفر 🔒)")

# 3. جلب الملف وفك تشفيره
@client.on(events.NewMessage(pattern=r"^\.جلب_ملف (.*)"))
async def get_file(event):
    name = event.pattern_match.group(1)
    path = f"nethron_vault/{name}"
    
    if not os.path.exists(path):
        return await event.edit("❌ الملف غير موجود!")
    
    await event.edit("🔓 جاري فك التشفير والإرسال...")
    
    with open(path, "rb") as f:
        enc_data = f.read()
    
    decrypted_data = cipher.decrypt(enc_data)
    temp_path = f"temp_{name}"
    
    with open(temp_path, "wb") as f:
        f.write(decrypted_data)
    
    await client.send_file(event.chat_id, temp_path, caption="✅ تم فك التشفير بنجاح.")
    os.remove(temp_path)
    await event.delete()

# 4. حفظ نص مشفر
@client.on(events.NewMessage(pattern=r"^\.حفظ_سر (.*)"))
async def save_secret(event):
    name_and_text = event.pattern_match.group(1).split(maxsplit=1)
    if len(name_and_text) < 2:
        return await event.edit("⚠️ الصيغة: `.حفظ_سر (الاسم) (النص)`")
    
    name, text = name_and_text[0], name_and_text[1]
    encrypted_text = cipher.encrypt(text.encode())
    
    with open(f"nethron_vault/{name}.txt", "wb") as f:
        f.write(encrypted_text)
    
    await event.edit(f"✅ تم حفظ السر باسم: `{name}`")

# 5. جلب نص وفك تشفيره
@client.on(events.NewMessage(pattern=r"^\.جلب_سر (.*)"))
async def get_secret(event):
    name = event.pattern_match.group(1)
    path = f"nethron_vault/{name}.txt"
    
    if not os.path.exists(path):
        return await event.edit("❌ السر غير موجود!")
    
    with open(path, "rb") as f:
        enc_text = f.read()
    
    dec_text = cipher.decrypt(enc_text).decode()
    await event.edit(f"🔐 **السر المحفوظ ({name}):**\n\n`{dec_text}`")

# 6. عرض قائمة الملفات
@client.on(events.NewMessage(pattern=r"^\.ملفاتي$"))
async def list_files(event):
    files = os.listdir("nethron_vault")
    if not files:
        return await event.edit("📭 الخزنة فارغة حالياً.")
    
    out = "📂 **قائمة المحفوظات المشفرة:**\n\n"
    for f in files:
        out += f"• `{f}`\n"
    await event.edit(out)
