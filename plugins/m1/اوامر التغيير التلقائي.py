import __main__
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
import asyncio
import random

client = __main__.client

# مخازن البيانات والمهام
setup_data = {}
running_tasks = {}

async def parse_time(time_str):
    """تحويل الصيغة (د، س، ي) إلى ثواني"""
    try:
        unit = time_str[-1]
        value = int(time_str[:-1])
        if unit == 'ث': return value
        if unit == 'د': return value * 60
        if unit == 'س': return value * 3600
        if unit == 'ي': return value * 86400
    except: return None
    return None

async def change_loop(user_id, type_):
    """المحرك المسؤول عن التغيير التلقائي مع دعم الإيقاف الفوري"""
    data = setup_data[user_id][type_]
    idx = 0
    try:
        while data.get('active', False):
            items = data['items']
            current_item = random.choice(items) if data['mode'] == "عشوائي" else items[idx]
            
            # تنفيذ التغيير حسب النوع
            if type_ == "اسم":
                await client(UpdateProfileRequest(first_name=current_item))
            else:
                await client(UpdateProfileRequest(about=current_item[:70]))
            
            # تحديث المؤشر للترتيب
            if data['mode'] == "ترتيب":
                idx = (idx + 1) % len(items)
            
            # الانتظار (سيتم قطعه فوراً عند عمل cancel للمهمة)
            await asyncio.sleep(data['delay'])
    except asyncio.CancelledError:
        # هذه تحدث عند إيقاف المهمة يدوياً
        pass
    except Exception as e:
        print(f"Error in {type_} loop: {e}")

@client.on(events.NewMessage(pattern=r"^\.تغيير تلقائي (اسم|بايو)$"))
async def start_setup(event):
    user_id = event.sender_id
    target = event.pattern_match.group(1)
    
    # التحقق إذا كان يعمل مسبقاً
    if f"{user_id}_{target}" in running_tasks:
        return await event.edit(f"**- نظام تغيير الـ {target} يعمل بالفعل ، أوقفه أولاً .**")

    if user_id not in setup_data: setup_data[user_id] = {}
    setup_data[user_id][target] = {
        'step': 'waiting_item', 
        'items': [], 
        'active': False,
        'max': 5 if target == "اسم" else 3,
        'last_msg_id': None
    }
    
    msg = await event.edit(f"**- جارِ إعداد التغيير التلقائي لـ {target}..**\n\nأرسل الآن الـ {target} الأول بالرد على هذه الرسالة :")
    setup_data[user_id][target]['last_msg_id'] = msg.id

@client.on(events.NewMessage(incoming=False))
async def handle_setup(event):
    user_id = event.sender_id
    if user_id not in setup_data: return

    # معرفة النظام النشط حالياً في الإعداد
    active_target = next((t for t in ["اسم", "بايو"] if t in setup_data[user_id] and not setup_data[user_id][t].get('active')), None)
    if not active_target: return
    
    data = setup_data[user_id][active_target]
    # شرط الرد على الرسالة الصحيحة
    if not event.reply_to_msg_id or event.reply_to_msg_id != data['last_msg_id']:
        return

    text = event.text
    state = data['step']

    if state == 'waiting_item':
        data['items'].append(text)
        await event.delete()
        if len(data['items']) >= data['max']:
            data['step'] = 'waiting_time'
            await client.edit_message(event.chat_id, data['last_msg_id'], f"**- تم تسجيل الحد الأقصى ({data['max']}) بنجاح .**\n\nأرسل الآن المدة بين التغييرات بالرد (مثلاً 2د) :")
        else:
            data['step'] = 'ask_more'
            await client.edit_message(event.chat_id, data['last_msg_id'], f"**- تم تسجيل الـ {active_target} :** `{text}`\n\nهل تريد إضافة آخر ؟ أرسل (** .نعم **) أو (** .لا **) بالرد :")

    elif state == 'ask_more':
        await event.delete()
        if text == ".نعم":
            data['step'] = 'waiting_item'
            await client.edit_message(event.chat_id, data['last_msg_id'], f"**- حسناً ، أرسل الـ {active_target} رقم {len(data['items']) + 1} بالرد :**")
        elif text == ".لا":
            data['step'] = 'waiting_time'
            await client.edit_message(event.chat_id, data['last_msg_id'], "**- حسناً ، أرسل الآن المدة بين كل تغيير بالرد :**")

    elif state == 'waiting_time':
        seconds = await parse_time(text)
        await event.delete()
        if seconds and seconds >= 120:
            data['delay'] = seconds
            data['step'] = 'waiting_mode'
            await client.edit_message(event.chat_id, data['last_msg_id'], "**- كيف تريد نوع عرض القائمة ؟**\n( عشوائي - ترتيب ) أرسل النوع بالرد :")
        else:
            await client.edit_message(event.chat_id, data['last_msg_id'], "**- خطأ في الوقت (أقل مدة 2د) ، أرسل مرة أخرى بالرد :**")

    elif state == 'waiting_mode':
        if text in ["عشوائي", "ترتيب"]:
            await event.delete()
            data['mode'] = text
            data['active'] = True
            await client.edit_message(event.chat_id, data['last_msg_id'], f"**- تم تفعيل التغيير التلقائي لـ {active_target} بنجاح ✅ .**")
            
            # إنشاء المهمة وتخزينها للإيقاف الفوري
            task_key = f"{user_id}_{active_target}"
            running_tasks[task_key] = asyncio.create_task(change_loop(user_id, active_target))

@client.on(events.NewMessage(pattern=r"^\.ايقاف التغيير (اسم|بايو)$"))
async def stop_specific(event):
    user_id = event.sender_id
    target = event.pattern_match.group(1)
    task_key = f"{user_id}_{target}"

    if task_key in running_tasks:
        # قتل المهمة فوراً
        running_tasks[task_key].cancel()
        del running_tasks[task_key]
        
        # مسح البيانات لتمكين إعادة التشغيل
        if user_id in setup_data and target in setup_data[user_id]:
            del setup_data[user_id][target]
            
        await event.edit(f"**- تم إيقاف تغيير الـ {target} فوراً وتصفير القائمة ✅ .**")
    else:
        await event.edit(f"**- عذراً ، لا يوجد تغيير {target} شغال حالياً ⚠️ .**")
