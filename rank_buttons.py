from telethon import Button

def get_main_perms_buttons():
    """
    هذه الأزرار تظهر عند كتابة .صلاحيات في المجموعة
    """
    return [
        [
            Button.inline("🛠 تجربة: صلاحية الطرد", data="test_1"),
            Button.inline("🛡 تجربة: صلاحية الكتم", data="test_2")
        ],
        [
            Button.inline("⚙️ إعدادات الرتب", data="manage_ranks")
        ],
        [
            Button.inline("🗑 إغلاق اللوحة", data="close_perms")
        ]
    ]

def get_rank_settings_buttons():
    """
    أزرار تجريبية ثانية تظهر عند الضغط على إعدادات الرتب
    """
    return [
        [Button.inline("👮 صلاحيات الأدمن", data="test_1")],
        [Button.inline("⭐ صلاحيات المميز", data="test_2")],
        [Button.inline("⬅️ رجوع للخلف", data="back_to_main")]
    ]
