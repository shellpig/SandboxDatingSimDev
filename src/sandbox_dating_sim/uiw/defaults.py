"""UIW 預設參考選項與模板。"""

PROTAGONIST_DEFAULT_AGE = 29

GENDER_OPTIONS = [
    {"id": "male", "label": "男性"},
    {"id": "female", "label": "女性"},
    {"id": "non_binary", "label": "非二元"},
]

ORIENTATION_OPTIONS = [
    {"id": "heterosexual", "label": "異性戀"},
    {"id": "homosexual", "label": "同性戀"},
    {"id": "bisexual", "label": "雙性戀"},
    {"id": "pansexual", "label": "泛性戀"},
]

ROLE_OPTIONS = [
    {"id": "main_love_interest", "label": "主要攻略對象"},
    {"id": "key_supporting_character", "label": "關鍵配角"},
]

CHARACTER_PERSONALITY_TAG_PRESETS = [
    {"id": "guarded", "label": "戒心重"},
    {"id": "proud", "label": "自尊心強"},
    {"id": "secretly_kind", "label": "其實很溫柔"},
    {"id": "cheerful", "label": "開朗活潑"},
    {"id": "mysterious", "label": "神秘莫測"},
    {"id": "clumsy", "label": "冒失"},
]

STYLE_PRESETS = [
    {"id": "urban_romance", "label": "都市戀愛"},
    {"id": "school_life", "label": "校園生活"},
    {"id": "black_humor", "label": "黑色幽默"},
    {"id": "class_anxiety", "label": "階級焦慮"},
    {"id": "coming_of_age", "label": "青春成長"},
    {"id": "melancholy", "label": "淡淡憂鬱"},
    {"id": "comedy", "label": "喜劇"},
    {"id": "mystery", "label": "懸疑"},
    {"id": "slice_of_life", "label": "日常系"},
    {"id": "social_satire", "label": "社會諷刺"},
    {"id": "bittersweet", "label": "苦甜戀愛"},
    {"id": "healing", "label": "治癒"},
]

PROTAGONIST_OCCUPATION_PRESETS = [
    {"id": "student", "label": "學生"},
    {"id": "part_time_worker", "label": "打工族"},
    {"id": "office_worker", "label": "上班族"},
    {"id": "freelancer", "label": "自由工作者"},
    {"id": "unemployed", "label": "待業中"},
    {"id": "debt_collector_assistant", "label": "催收助理"},
    {"id": "cafe_staff", "label": "咖啡廳店員"},
    {"id": "delivery_rider", "label": "外送員"},
    {"id": "rich_heir", "label": "富二代"},
    {"id": "startup_founder", "label": "新創公司老闆"},
    {"id": "tech_worker", "label": "科技業"},
    {"id": "finance_professional", "label": "金融業"},
    {"id": "doctor", "label": "醫師"},
    {"id": "lawyer", "label": "律師"},
    {"id": "university_lecturer", "label": "大學講師"},
    {"id": "graphic_designer", "label": "平面設計師"},
]

PROTAGONIST_PERSONALITY_PRESETS = [
    {"id": "kind_but_tired", "label": "善良但疲憊"},
    {"id": "sharp_tongued_soft_hearted", "label": "嘴硬心軟"},
    {"id": "reckless_optimist", "label": "莽撞樂觀"},
    {"id": "careful_realist", "label": "謹慎現實"},
    {"id": "socially_awkward", "label": "不擅社交"},
    {"id": "ambitious_survivor", "label": "野心求生型"},
    {"id": "quiet_observer", "label": "安靜觀察者"},
    {"id": "people_pleaser", "label": "討好型人格"},
]

SECRET_PRESETS = [
    {"id": "family_debt", "label": "背負家族債務"},
    {"id": "fake_identity", "label": "隱瞞真實身分"},
    {"id": "past_betrayal", "label": "曾背叛重要的人"},
    {"id": "medical_bill", "label": "秘密支付醫療費"},
    {"id": "hidden_talent", "label": "有不願公開的才能"},
    {"id": "runaway_from_home", "label": "離家出走"},
    {"id": "old_promise", "label": "守著一個舊約定"},
    {"id": "none", "label": "沒有秘密"},
    {"id": "hidden_wealth", "label": "其實家境富裕"},
    {"id": "criminal_record", "label": "曾有犯罪紀錄"},
    {"id": "secret_childhood_friend", "label": "隱瞞童年舊識"},
    {"id": "family_scandal", "label": "家族醜聞"},
    {"id": "forbidden_relationship", "label": "曾有禁忌戀情"},
    {"id": "fake_education", "label": "學歷造假"},
    {"id": "underground_job", "label": "從事地下工作"},
    {"id": "terminal_illness_in_family", "label": "家人身患重病"},
]

DEBT_TIER_PRESETS = [
    {"id": "none", "label": "無債務", "debt": 0},
    {"id": "low", "label": "低債務", "debt": 10000},
    {"id": "medium", "label": "中債務", "debt": 50000},
    {"id": "high", "label": "高債務", "debt": 120000},
    {"id": "desperate", "label": "絕望級債務", "debt": 300000},
]

EMOTION_PRESETS = [
    {"id": "neutral", "label": "平常"},
    {"id": "happy", "label": "開心"},
    {"id": "surprised", "label": "驚訝"},
    {"id": "angry", "label": "憤怒"},
    {"id": "sad", "label": "悲傷"},
    {"id": "embarrassed", "label": "害羞"},
    {"id": "contempt", "label": "鄙視"},
    {"id": "love_struck", "label": "暈了"},
]

COSTUME_PRESETS = [
    {"id": "school_uniform", "label": "校服"},
    {"id": "casual", "label": "私服"},
    {"id": "work_uniform", "label": "工作服"},
    {"id": "pajamas", "label": "睡衣"},
    {"id": "formal", "label": "正裝"},
    {"id": "swimsuit", "label": "泳裝"},
    {"id": "sportswear", "label": "體育服"},
    {"id": "maid_butler", "label": "女僕/執事"},
    {"id": "special_cosplay", "label": "特殊/Cosplay"},
]

POSITION_PRESETS = [
    {"id": "left", "label": "左"},
    {"id": "center", "label": "中"},
    {"id": "right", "label": "右"},
]

LOCATION_TEMPLATES = [
    # --- container templates ---
    {
        "template_id": "school_container",
        "label": "學校",
        "location_id_suggestion": "school",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["school", "public"],
        "suggested_sub_locations": ["classroom", "library", "rooftop", "sports_ground"],
    },
    {
        "template_id": "shopping_street_container",
        "label": "商店街",
        "location_id_suggestion": "shopping_street",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["commercial", "public"],
        "suggested_sub_locations": ["cafe", "convenience_store", "arcade"],
    },
    {
        "template_id": "station_area_container",
        "label": "車站周邊",
        "location_id_suggestion": "station_area",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["transit", "public"],
        "suggested_sub_locations": ["station_square", "ticket_gate", "bus_stop"],
    },
    # --- standalone templates ---
    {
        "template_id": "home_standalone",
        "label": "主角家",
        "location_id_suggestion": "protagonist_home",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["home", "rest"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "empty_behavior": "allow_rest",
        "suggested_sub_locations": [],
    },
    {
        "template_id": "cinema_standalone",
        "label": "電影院",
        "location_id_suggestion": "cinema",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["date_spot", "entertainment"],
        "available_time_slots": ["afternoon", "evening"],
        "base_cost": 300,
        "suggested_sub_locations": [],
    },
    {
        "template_id": "convenience_store_standalone",
        "label": "便利商店",
        "location_id_suggestion": "convenience_store",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["commercial", "part_time_job"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
]

SUB_LOCATION_TEMPLATES = [
    {
        "template_id": "classroom",
        "label": "教室",
        "location_id_suffix": "classroom",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["morning", "afternoon"],
        "tags": ["indoor", "school"],
    },
    {
        "template_id": "library",
        "label": "圖書室",
        "location_id_suffix": "library",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["morning", "afternoon"],
        "tags": ["indoor", "study"],
    },
    {
        "template_id": "rooftop",
        "label": "屋頂",
        "location_id_suffix": "rooftop",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["morning", "afternoon", "evening"],
        "tags": ["outdoor", "secret_spot"],
    },
    {
        "template_id": "sports_ground",
        "label": "操場",
        "location_id_suffix": "sports_ground",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["morning", "afternoon"],
        "tags": ["outdoor", "school"],
    },
    {
        "template_id": "cafe",
        "label": "咖啡廳",
        "location_id_suffix": "cafe",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["afternoon", "evening"],
        "tags": ["date_spot", "commercial"],
    },
    {
        "template_id": "convenience_store_sub",
        "label": "便利商店",
        "location_id_suffix": "convenience_store",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["morning", "afternoon", "evening"],
        "tags": ["commercial"],
    },
    {
        "template_id": "arcade",
        "label": "遊戲中心",
        "location_id_suffix": "arcade",
        "location_type": "sub_location",
        "is_visitable": True,
        "available_time_slots": ["afternoon", "evening"],
        "tags": ["entertainment"],
    },
]
