import __main__
from telethon import events
import random
import string
import time
import os
import asyncio

client = __main__.client

# ملف التخزين
CODES_FILE = "nethron_codes.txt"

HEADER = (
    "★────────☭────────★\n"
    "   ☭ • 𝑆𝑂𝑈𝑅𝐶𝐸 𝑁𝐸𝑇𝐻𝑅𝑂𝑁 • ☭\n"
    "                  ☭ • سورس نيثرون • ☭\n"
    "★────────☭────────★\n"
)

# دالة لتوليد كود عشوائي
def generate_code():
    chars = string.ascii_uppercase + string.digits
    return "NETH-" + ''.join(random.choices(chars, k=8))

# دالة لحفظ الكود في الملف
def save_code(serial, code, days):
    with open(CODES_FILE, "a") as f:
        f.write(f"{serial}|{code}|{days}\n")

# دالة لجلب كل الأكواد
def load_codes():
    if not os.path.exists(CODES_FILE):
        return []
    with open(CODES_FILE, "r") as f:
        return [line.strip().split("|") for line in f.readlines()]

# =========================
# 1. إضافة كود نيثرون
# =========================
@client.on(events.NewMessage(pattern=r"^\.اضافة كود نيثرون (\S+)$"))
async def add_code(event):
    if not event.out:
        return

    days = event.pattern_match.group(1)
    new_code = generate_code()
    
    # جلب الرقم التسلسلي التالي
    all_codes = load_codes()
    serial = len(all_codes) + 1

    # شريط التحميل
    msg = await event.edit("⏳ **جاري إنشاء الكود...**\n`[▒▒▒▒▒▒▒▒▒▒] 0%`")
    await asyncio.sleep(0.5)
    await msg.edit("⏳ **جاري إنشاء الكود...**\n`[████▒▒▒▒▒▒] 40%`")
    await asyncio.sleep(0.5)
    await msg.edit("⏳ **جاري إنشاء الكود...**\n`[████████▒▒] 80%`")
    await asyncio.sleep(0.5)

    save_code(serial, new_code, days)

    await msg.edit(
        HEADER +
        f"✅ **تم إضافة الكود بنجاح**\n\n"
        f"🔢 الرقم التسلسلي: `{serial}`\n"
        f"🔑 الكود: `{new_code}`\n"
        f"⏳ المدة: `{days}`\n\n"
        f"📌 يحفظ في: `{CODES_FILE}`"
    )

# =========================
# 2. حذف كود
# =========================
@client.on(events.NewMessage(pattern=r"^\.حذف كود (\d+)$"))
async def delete_code(event):
    if not event.out:
        return

    serial_to_del = event.pattern_match.group(1)
    all_codes = load_codes()
    new_list = [c for c in all_codes if c[0] != serial_to_del]

    if len(all_codes) == len(new_list):
        return await event.edit("❌ **لم يتم العثور على كود بهذا الرقم التسلسلي.**")

    # إعادة كتابة الملف
    with open(CODES_FILE, "w") as f:
        for c in new_list:
            f.write("|".join(c) + "\n")

    await event.edit(f"🗑️ **تم حذف الكود رقم ({serial_to_del}) بنجاح.**")

# =========================
# 3. حالة الأكواد
# =========================
@client.on(events.NewMessage(pattern=r"^\.حالة الاكواد$"))
async def status_codes(event):
    if not event.out:
        return

    all_codes = load_codes()
    if not all_codes:
        return await event.edit(HEADER + "📭 **لا توجد أكواد مسجلة حالياً.**")

    text = HEADER + "📋 **قائمة الأكواد المتوفرة:**\n\n"
    for c in all_codes:
        text += f"#{c[0]} | `{c[1]}` | ⏳ `{c[2]}`\n"

    await event.edit(text)
