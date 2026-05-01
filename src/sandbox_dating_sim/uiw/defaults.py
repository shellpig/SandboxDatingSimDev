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
        "suggested_sub_locations": ["cafe", "convenience_store_sub", "arcade"],
    },
    {
        "template_id": "station_area_container",
        "label": "車站周邊",
        "location_id_suggestion": "station_area",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["transit", "public"],
        "suggested_sub_locations": ["platform", "station_square", "underground_mall"],
    },
    {
        "template_id": "amusement_park_container",
        "label": "遊樂園",
        "location_id_suggestion": "amusement_park",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["entertainment", "date_spot", "lively"],
        "suggested_sub_locations": ["ferris_wheel", "roller_coaster", "haunted_house", "souvenir_shop"],
    },
    {
        "template_id": "department_store_container",
        "label": "百貨公司",
        "location_id_suggestion": "department_store",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["commercial", "indoor", "shopping"],
        "suggested_sub_locations": ["food_court", "luxury_floor", "sky_garden"],
    },
    {
        "template_id": "seaside_container",
        "label": "海邊",
        "location_id_suggestion": "seaside",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["outdoor", "nature", "summer"],
        "suggested_sub_locations": ["beach", "beach_house", "observation_deck"],
    },
    {
        "template_id": "hot_spring_inn_container",
        "label": "溫泉旅館",
        "location_id_suggestion": "hot_spring_inn",
        "location_type": "container",
        "is_visitable": False,
        "tags": ["relaxing", "vacation", "traditional"],
        "suggested_sub_locations": ["lobby", "guest_room", "open_air_bath"],
    },
    # --- standalone templates ---
    {
        "template_id": "home_standalone",
        "label": "主角家",
        "location_id_suggestion": "protagonist_home",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["home", "rest", "private"],
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
        "tags": ["date_spot", "entertainment", "indoor"],
        "available_time_slots": ["afternoon", "evening"],
        "base_cost": 300,
        "suggested_sub_locations": [],
    },
    {
        "template_id": "convenience_store_standalone",
        "label": "便利商店(獨立)",
        "location_id_suggestion": "convenience_store",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["commercial", "part_time_job", "always_open"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "company_standalone",
        "label": "主角公司",
        "location_id_suggestion": "protagonist_company",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["work", "stressful"],
        "available_time_slots": ["morning", "afternoon"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "park_standalone",
        "label": "公園",
        "location_id_suggestion": "park",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["outdoor", "relaxing", "public"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "hospital_standalone",
        "label": "醫院",
        "location_id_suggestion": "hospital",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["medical", "serious"],
        "available_time_slots": ["morning", "afternoon"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "night_market_standalone",
        "label": "夜市",
        "location_id_suggestion": "night_market",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["food", "lively", "crowded"],
        "available_time_slots": ["evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "gym_standalone",
        "label": "健身房",
        "location_id_suggestion": "gym",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["sports", "indoor", "health"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "public_library",
        "label": "圖書館",
        "location_id_suggestion": "public_library",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["quiet", "study", "indoor"],
        "available_time_slots": ["morning", "afternoon"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "police_station_standalone",
        "label": "警察局",
        "location_id_suggestion": "police_station",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["official", "safe"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "art_museum_standalone",
        "label": "美術館",
        "location_id_suggestion": "art_museum",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["culture", "quiet", "date_spot"],
        "available_time_slots": ["morning", "afternoon"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "riverside_walk_standalone",
        "label": "河岸步道",
        "location_id_suggestion": "riverside_walk",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["outdoor", "scenic", "relaxing"],
        "available_time_slots": ["morning", "afternoon", "evening"],
        "suggested_sub_locations": [],
    },
    {
        "template_id": "bar_standalone",
        "label": "酒吧",
        "location_id_suggestion": "bar",
        "location_type": "standalone",
        "is_visitable": True,
        "tags": ["nightlife", "alcohol", "adult"],
        "available_time_slots": ["evening"],
        "suggested_sub_locations": [],
    },
]

SUB_LOCATION_TEMPLATES = [
    # School
    {"template_id": "classroom", "label": "教室", "location_id_suffix": "classroom", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon"], "tags": ["indoor", "school"]},
    {"template_id": "library", "label": "圖書室", "location_id_suffix": "library", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon"], "tags": ["indoor", "study"]},
    {"template_id": "rooftop", "label": "屋頂", "location_id_suffix": "rooftop", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["outdoor", "secret_spot"]},
    {"template_id": "sports_ground", "label": "操場", "location_id_suffix": "sports_ground", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon"], "tags": ["outdoor", "school"]},
    # Shopping Street
    {"template_id": "cafe", "label": "咖啡廳", "location_id_suffix": "cafe", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["date_spot", "commercial"]},
    {"template_id": "convenience_store_sub", "label": "便利商店(商店街內)", "location_id_suffix": "convenience_store", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["commercial", "always_open"]},
    {"template_id": "arcade", "label": "遊戲中心", "location_id_suffix": "arcade", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["entertainment", "lively"]},
    # Station Area
    {"template_id": "platform", "label": "月台", "location_id_suffix": "platform", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["transit"]},
    {"template_id": "station_square", "label": "站前廣場", "location_id_suffix": "station_square", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["public", "meeting_spot"]},
    {"template_id": "underground_mall", "label": "地下街", "location_id_suffix": "underground_mall", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["commercial", "indoor"]},
    # Amusement Park
    {"template_id": "ferris_wheel", "label": "摩天輪", "location_id_suffix": "ferris_wheel", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["date_spot", "romantic"]},
    {"template_id": "roller_coaster", "label": "雲霄飛車", "location_id_suffix": "roller_coaster", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["thrilling", "loud"]},
    {"template_id": "haunted_house", "label": "鬼屋", "location_id_suffix": "haunted_house", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["scary", "dark"]},
    {"template_id": "souvenir_shop", "label": "紀念品店", "location_id_suffix": "souvenir_shop", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["commercial", "souvenir"]},
    # Department Store
    {"template_id": "food_court", "label": "美食街", "location_id_suffix": "food_court", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["food", "crowded"]},
    {"template_id": "luxury_floor", "label": "精品樓層", "location_id_suffix": "luxury_floor", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["shopping", "expensive"]},
    {"template_id": "sky_garden", "label": "空中花園", "location_id_suffix": "sky_garden", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["relaxing", "scenic"]},
    # Seaside
    {"template_id": "beach", "label": "沙灘", "location_id_suffix": "beach", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["outdoor", "play"]},
    {"template_id": "beach_house", "label": "海之家", "location_id_suffix": "beach_house", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["food", "rest"]},
    {"template_id": "observation_deck", "label": "觀景台", "location_id_suffix": "observation_deck", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["scenic", "date_spot"]},
    # Hot Spring Inn
    {"template_id": "lobby", "label": "大廳", "location_id_suffix": "lobby", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["morning", "afternoon", "evening"], "tags": ["indoor", "public"]},
    {"template_id": "guest_room", "label": "客房", "location_id_suffix": "guest_room", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["afternoon", "evening"], "tags": ["private", "rest"]},
    {"template_id": "open_air_bath", "label": "露天溫泉", "location_id_suffix": "open_air_bath", "location_type": "sub_location", "is_visitable": True, "available_time_slots": ["evening"], "tags": ["relaxing", "bath"]},
]
