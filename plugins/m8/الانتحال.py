import __main__
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
import os
import asyncio

client = __main__.client
VORTEX = ["◜", "◝", "◞", "◟"]

# مخزن المعلومات الأصلية
if not hasattr(__main__, 'nethron_clone_backup'):
    __main__.nethron_clone_backup = {"first_name": "", "last_name": "", "bio": "", "has_backup": False}

BACKUP = __main__.nethron_clone_backup

# ==========================================
# 1. أمر الانتحال (نسخ)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(انتحال|نسخ)(?:\s+(.*))?$"))
async def clone_user(event):
    reply = await event.get_reply_message()
    user_id = None
    if reply: user_id = reply.sender_id
    elif event.pattern_match.group(2): user_id = event.pattern_match.group(2)
    else: return await event.edit("❌ **يرجى الرد على الشخص أو وضع يوزره**")

    try:
        full_user = await client(GetFullUserRequest(user_id))
        user = full_user.users[0]
        name = user.first_name
        
        # أنيميشن التحميل (جاري الانتحال)
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري انتحال : {name} 〕 {f} ⌯")
            await asyncio.sleep(0.2)

        # أخذ نسخة احتياطية
        if not BACKUP["has_backup"]:
            me_full = await client(GetFullUserRequest('me'))
            BACKUP.update({
                "first_name": me_full.users[0].first_name or "",
                "last_name": me_full.users[0].last_name or "",
                "bio": me_full.full_user.about or "",
                "has_backup": True
            })

        # نسخ الصورة
        photo = await client.download_profile_photo(user)
        if photo:
            uploaded_photo = await client.upload_file(photo)
            await client(UploadProfilePhotoRequest(file=uploaded_photo))
            os.remove(photo)
        
        # نسخ الاسم والبايو
        await client(UpdateProfileRequest(
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            about=(full_user.full_user.about or "")[:70]
        ))

        # النتيجة النهائية بالدوامة
        await event.edit(f"⌯ {VORTEX[0]} 〔 تم انتحال : {name} 〕 {VORTEX[0]} ⌯")
        await asyncio.sleep(5)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **فشل الانتحال:** `{str(e)}`")

# ==========================================
# 2. أمر الإرجاع (دوامة عراق ثون)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ارجاع$"))
async def restore_info(event):
    if not BACKUP["has_backup"]:
        return await event.edit("⚠️ **ماكو نسخة قديمة ارجع عليها!**")

    # أنيميشن جاري الارجاع
    for _ in range(2):
        for f in VORTEX:
            await event.edit(f"⌯ {f} 〔 جاري ارجاع حسابك 〕 {f} ⌯")
            await asyncio.sleep(0.2)

    try:
        await client(UpdateProfileRequest(
            first_name=BACKUP["first_name"],
            last_name=BACKUP["last_name"],
            about=BACKUP["bio"]
        ))
        
        photos = await client.get_profile_photos('me')
        if photos: 
            await client(DeletePhotosRequest([photos[0]]))
            
        final_msg = (
            "★────────☭────────★\n"
            "   ☭ • 𝐼𝑅𝐴𝑄𝑇𝐻𝑂𝑂𝑁 • ☭\n"
            "◈ تم رجع حسابك ضلعي ◈ \n"
            "★────────☭────────★\n"
            "➥ 𝑫𝑬𝑽 〔 [المطور](https://t.me/NETH_RON) 〕\n"
            "➥ 𝑨𝑫ＭＩＮ 〔 [الادمن](https://t.me/xxnnxg) 〕"
        )
        
        await event.edit(final_msg, link_preview=False)
        await asyncio.sleep(10)
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ **حدث خطأ:** `{e}`")
