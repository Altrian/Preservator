import os
import json
import re
import pprint
from chara_skills import replace_substrings

pp = pprint.PrettyPrinter(indent=4)

SUBPROFESSIONS = ['physician', 'fearless', 'executor', 'fastshot', 'bombarder', 'bard', 'protector', 'ritualist', 'pioneer', 'corecaster', 'splashcaster', 'charger', 'centurion', 'guardian', 'slower', 'funnel', 'mystic', 'chain', 'aoesniper', 'reaperrange', 'longrange', 'closerange', 'siegesniper', 'loopshooter', 'bearer', 'tactician', 'instructor', 'lord', 'artsfghter', 'sword', 'musha', 'crusher', 'reaper',
                  'merchant', 'hookmaster', 'ringhealer', 'healer', 'wandermedic', 'unyield', 'artsprotector', 'summoner', 'craftsman', 'stalker', 'pusher', 'dollkeeper', 'skywalker', 'agent', 'fighter', 'librator', 'hammer', 'phalanx', 'blastcaster', 'primcaster', 'incantationmedic', 'chainhealer', 'shotprotector', 'fortress', 'duelist', 'primprotector', 'hunter', 'geek', 'underminer', 'blessing', 'traper', 
                  'alchemist','soulcaster','primguard']

STAT_CONVERT = {'maxHp': "hp", "magicResistance": "res", "attackSpeed": "aspd",
                "moveSpeed": "ms", "respawnTime": "respawnTime", "atk": 'atk', "def": "def", "cost": "cost"}

ATTRIBUTE_TRANSLATE_TABLE = {'COST': "cost", "RESPAWN_TIME": 'respawnTime', 'ATK': "atk",
                             "MAX_HP": "hp", "ATTACK_SPEED": "aspd", "DEF": "def", "MAGIC_RESISTANCE": "res"}

HANDBOOK_INFO_EXTRACT_TABLE = {
    "gender": {
        "zh": ["【性别】", "【设定性别】", "【语音类型】"],
        "ja": ["【性別】", "【性別設定】"],
        "en": ["[Gender]", "[Gender Assignment]"],
    },
    "birthplace": {
        "zh": ["【出身地】", "【产地】"],
        "ja": ["【出身地】", "【産地】"],
        "en": ["[Place of Birth]", "[Place of Production]"],
    },
    "race": {"zh": ["【种族】"], "ja": ["【種族】"], "en": ["[Race]"]},
}

script_dir = os.path.dirname(__file__)  # <-- Absolute directory for the script

cn_char_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/character_table.json")
cn_handbook_info_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/handbook_info_table.json")
jp_handbook_info_table_path = os.path.join(
    script_dir, "global_data/ja_JP/gamedata/excel/handbook_info_table.json")
en_handbook_info_table_path = os.path.join(
    script_dir, "global_data/en_US/gamedata/excel/handbook_info_table.json")
cn_skill_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/skill_table.json")
en_char_table_path = os.path.join(
    script_dir, "global_data/en_US/gamedata/excel/character_table.json")
jp_char_table_path = os.path.join(
    script_dir, "global_data/ja_JP/gamedata/excel/character_table.json")
cn_patch_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/char_patch_table.json")
en_patch_table_path = os.path.join(
    script_dir, "global_data/en_US/gamedata/excel/char_patch_table.json")
jp_patch_table_path = os.path.join(
    script_dir, "global_data/ja_JP/gamedata/excel/char_patch_table.json")

with open(cn_char_table_path, encoding='utf-8') as f:
    cn_char_table = json.load(f)
with open(cn_skill_table_path, encoding='utf-8') as f:
    cn_skill_table = json.load(f)
with open(en_char_table_path, encoding='utf-8') as f:
    en_char_table = json.load(f)
with open(jp_char_table_path, encoding='utf-8') as f:
    jp_char_table = json.load(f)
with open(cn_handbook_info_table_path, encoding='utf-8') as f:
    cn_handbook_info_table = json.load(f)
with open(jp_handbook_info_table_path, encoding='utf-8') as f:
    jp_handbook_info_table = json.load(f)
with open(en_handbook_info_table_path, encoding='utf-8') as f:
    en_handbook_info_table = json.load(f)
with open(cn_patch_table_path, encoding='utf-8') as f:
    cn_patch_table = json.load(f)
with open(en_patch_table_path, encoding='utf-8') as f:
    en_patch_table = json.load(f)
with open(jp_patch_table_path, encoding='utf-8') as f:
    jp_patch_table = json.load(f)

with open('chara_skills.json', encoding='utf-8') as f:
    chara_skills = json.load(f)
with open('chara_talents(test).json', encoding='utf-8') as f:
    chara_talents = json.load(f)
with open('uniequip.json', encoding='utf-8') as f:
    uniequip_dict = json.load(f)
with open('tokens.json', encoding='utf-8') as f:
    tokens_dict = json.load(f)
with open('chara_imple_dates.json', encoding='utf-8') as f:
    imple_dates = json.load(f)
with open('recruitment_table.json', encoding='utf-8') as f:
    recruitment_dict = json.load(f)

data = {}

KEYS_TO_IGNORE = ["char_512_aprot", "char_600_cpione", "char_601_cguard",
                  "char_602_cdfend", "char_603_csnipe", "char_604_ccast",
                  "char_605_cmedic", "char_606_csuppo", "char_607_cspec",
                  "char_608_acpion", "char_609_acguad", "char_610_acfend",
                  "char_611_acnipe", "char_612_accast", "char_613_acmedc",
                  "char_614_acsupo", "char_615_acspec"]

filtered_cn_char_table = {key: cn_char_table[key] for key in cn_char_table.keys(
) if "token" not in key and "trap" not in key and key not in KEYS_TO_IGNORE}

subProfessionIds = []

for id, character_dict in filtered_cn_char_table.items():
    in_global = id in en_char_table
    if character_dict['subProfessionId'] not in subProfessionIds:
        subProfessionIds.append(character_dict['subProfessionId'])
    skills = []
    talents = []
    for skill in character_dict['skills']:
        blackboard = chara_skills[skill['skillId']
                                  ]['blackboard'] if skill['skillId'] in chara_skills else []
        skills.append({"skillId": skill['skillId'],
                       "name_zh": chara_skills[skill['skillId']]['name_zh'],
                       "name_ja": chara_skills[skill['skillId']]['name_ja'],
                       "name_en": chara_skills[skill['skillId']]['name_en'],
                       "skillType": chara_skills[skill['skillId']]['skillType'],
                       "durationType": chara_skills[skill['skillId']]['durationType'],
                       "spType": chara_skills[skill['skillId']]['spType'],
                       "levels": chara_skills[skill['skillId']]['levels'],
                       "blackboard": blackboard,})

    if character_dict['talents']:
        for talent_index, talent in enumerate(character_dict['talents']):
            max_candidate_index = len(talent['candidates']) - 1
            maxed_talent = talent['candidates'][max_candidate_index]
            if maxed_talent['name'] is None:
                continue
            talent_dict = {
                "prefabKey": maxed_talent['prefabKey'],
                "name_zh": maxed_talent["name"], "name_ja": "", "name_en": "",
                "desc_zh": chara_talents[id]['talents'][talent_index]["desc_zh"], "desc_ja": "", "desc_en": ""}
            if in_global:
                talent_dict["name_ja"] = jp_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_ja"] = chara_talents[id]['talents'][talent_index]["desc_ja"]
                talent_dict["name_en"] = en_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_en"] = chara_talents[id]['talents'][talent_index]["desc_en"]
            if id in chara_talents:
                talent_dict['rangeId'] = chara_talents[id]['talents'][talent_index].get('rangeId', None)
                talent_dict['blackboard'] = chara_talents[id]['talents'][talent_index].get('blackboard', [])
            talents.append(talent_dict)

    uniequip_list = []
    for equip_id in uniequip_dict:
        if uniequip_dict[equip_id]['charId'] == id:
            uniequip_list.append(uniequip_dict[equip_id])
    uniequip_list.sort(key=lambda x: x['uniEquipId'])

    # Handle stats
    stats_list = []
    for phase_index, phase in enumerate(character_dict['phases']):
        if phase_index == 0:
            attributes = phase['attributesKeyFrames'][0]['data']
            stats = {}
            stats['rangeId'] = phase['rangeId']
            stats['level'] = 1
            stats['hp'] = attributes["maxHp"]
            stats['atk'] = attributes["atk"]
            stats['def'] = attributes["def"]
            stats['res'] = attributes["magicResistance"]
            stats['cost'] = attributes["cost"]
            stats['blockCnt'] = attributes["blockCnt"]
            stats['aspd'] = attributes["baseAttackTime"]
            stats['respawnTime'] = attributes["respawnTime"]
            stats_list.append(stats)
        
        attributes = phase['attributesKeyFrames'][1]['data']
        stats = {}
        stats['rangeId'] = phase['rangeId']
        stats['level'] = phase['maxLevel']
        stats['hp'] = attributes["maxHp"]
        stats['atk'] = attributes["atk"]
        stats['def'] = attributes["def"]
        stats['res'] = attributes["magicResistance"]
        stats['cost'] = attributes["cost"]
        stats['blockCnt'] = attributes["blockCnt"]
        stats['aspd'] = attributes["baseAttackTime"]
        stats['respawnTime'] = attributes["respawnTime"]
        stats_list.append(stats)

    # Handle potential attributes
    potential_list = []
    for potential_index, potential in enumerate(character_dict['potentialRanks']):
        potential_dict = {
            "desc_zh": potential['description'],
            "desc_ja": "",
            "desc_en": ""
        }
        
        if in_global and potential_index < len(jp_char_table[id]['potentialRanks']):
            potential_dict["desc_ja"] = jp_char_table[id]['potentialRanks'][potential_index]['description']
            potential_dict["desc_en"] = en_char_table[id]['potentialRanks'][potential_index]['description']
            
        attribute = None
        if potential.get("buff"):
            modifier = potential['buff']['attributes']['attributeModifiers'][0]
            attribute = {ATTRIBUTE_TRANSLATE_TABLE[modifier['attributeType']]: modifier['value']}
        potential_dict['attribute'] = attribute
        potential_list.append(potential_dict)

    # Handle trust/favor
    favor_data = {}
    if character_dict['favorKeyFrames'] is not None:
        favor_last = character_dict['favorKeyFrames'][-1]['data']
        for stat, value in favor_last.items():
            if stat in STAT_CONVERT and bool(value):
                favor_data[STAT_CONVERT[stat]] = value
    
    # Handle tokens
    tokens = []
    if character_dict['displayTokenDict'] is not None:
        tokens = [tokens_dict[key] for key in character_dict['displayTokenDict']]
    
    # Handle subprofession
    desc_zh = character_dict['description'].replace("<$ba", "<ba")
    blackboard = []
    if character_dict['subProfessionId'] in ['librator', 'healer', 'musha']:
        desc_zh = replace_substrings(
            character_dict['trait']['candidates'][-1]['overrideDescripton'], 
            character_dict['trait']['candidates'][-1]['blackboard'])
        
    # Handle nationality and affiliations
    powers = []
    powers_list = character_dict['subPower'] or []
    powers_list.append(character_dict['mainPower'])
    for power in powers_list:
        if power['nationId'] is not None:
            powers.append(power['nationId'])
        if power['groupId'] is not None: 
            powers.append(power['groupId'])
        if power['teamId'] is not None: 
            powers.append(power['teamId'])

    # Handle gender, birthplace, race from handbook
    gender = {"zh": "", "ja": "", "en": ""}
    birthplace = {"zh": "", "ja": "", "en": ""}
    race = {"zh": "", "ja": "", "en": ""}
    def extract_handbook_info(text, keys):
        """Extracts the value of the first matching key in text."""
        for key in keys:
            if key in text:
                return text.split(key)[1].split("\n")[0].strip()
        return None
    if cn_handbook_info_table['handbookDict'].get(id) is None:
        print(f"Warning: {id} has no handbook info")
    else:
        cn_handbook_info = cn_handbook_info_table['handbookDict'][id]['storyTextAudio'][0]['stories'][0]['storyText']
        jp_handbook_info = jp_handbook_info_table['handbookDict'][id]['storyTextAudio'][0]['stories'][0]['storyText'] if id in jp_handbook_info_table['handbookDict'] else ""
        en_handbook_info = en_handbook_info_table['handbookDict'][id]['storyTextAudio'][0]['stories'][0]['storyText'] if id in en_handbook_info_table['handbookDict'] else ""
        # Extract gender
        gender['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['zh'])
        if in_global:
            gender['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['ja'])
            gender['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['en'])
        if not gender['zh']:
            print(f"Warning: Gender information is missing for character ID {id}")
        # Extract birthplace
        birthplace['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['zh'])
        if in_global:
            birthplace['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['ja'])
            birthplace['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['en'])
        if not birthplace['zh']:
            print(f"Warning: Birthplace information is missing for character ID {id}")
        # Extract race
        if "种族" not in cn_handbook_info:
            race['zh'] = "其他"
            race['ja'] = "その他"
            race['en'] = "Others"
        else:
            race['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['zh'])
            if in_global:
                race['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['ja'])
                race['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['en'])

    # Handle recruitment if applicable
    recruitment = None
    recruitment_info = recruitment_dict.get(id, None)
    if recruitment_info is not None:
        recruitment = {"IsRecruitOnly": recruitment_info['IsRecruitOnly'],
                       "tags": recruitment_info['tags']}

    result_dict = {"id": id, "appellation": character_dict['appellation'],
                   "releaseDate": imple_dates.get(id, 0),
                   "name": {"zh": character_dict['name'], "ja": "", "en": ""},
                   "desc": {"zh": desc_zh, "ja": "", "en": ""},  
                   "gender": gender, "birthplace": birthplace, "race": race, "powers": powers,
                   "position": character_dict['position'], "isSpChar": character_dict['isSpChar'],
                   "rarity": character_dict['rarity'], "profession": character_dict['profession'], "subProfessionId": character_dict['subProfessionId'],
                   "recruitment": recruitment,
                   "stats": stats_list, "potential": potential_list, "favorData": favor_data, "tokens": tokens,
                   "skills": skills, "talents": talents, "uniequip": uniequip_list}
    
    if in_global:
        desc_ja = jp_char_table[id]['description'].replace("<$ba", "<ba")
        desc_en = en_char_table[id]['description'].replace("<$ba", "<ba")
        if character_dict['subProfessionId'] in ['librator', 'healer', 'musha']:
            desc_ja = replace_substrings(
                jp_char_table[id]['trait']['candidates'][-1]['overrideDescripton'], 
                jp_char_table[id]['trait']['candidates'][-1]['blackboard'])
            desc_en = replace_substrings(
                en_char_table[id]['trait']['candidates'][-1]['overrideDescripton'], 
                en_char_table[id]['trait']['candidates'][-1]['blackboard'])
        desc_en = re.sub(r'<([A-Z][^>]*)>', r'&lt;\1&gt;', desc_en)

        result_dict["name"]["ja"] = jp_char_table[id]['name']
        result_dict["name"]["en"] = en_char_table[id]['name']
        result_dict["desc"]['ja'] = desc_ja
        result_dict["desc"]["en"] = desc_en
    data[id] = result_dict

# Patch table for Amiya
for id, character_dict in cn_patch_table['patchChars'].items():
    in_global = id in en_patch_table['patchChars']
    skills = []
    talents = []
    for skill in character_dict['skills']:
        blackboard = chara_skills[skill['skillId']
                                  ]['blackboard'] if skill['skillId'] in chara_skills else []
        levels = chara_skills[skill['skillId']]['levels']
        for level in levels:
            del level['blackboard']
        skills.append({"skillId": skill['skillId'],
                       "name_zh": chara_skills[skill['skillId']]['name_zh'],
                       "name_ja": chara_skills[skill['skillId']]['name_ja'],
                       "name_en": chara_skills[skill['skillId']]['name_en'],
                       "skillType": chara_skills[skill['skillId']]['skillType'],
                       "durationType": chara_skills[skill['skillId']]['durationType'],
                       'spType': chara_skills[skill['skillId']]['spType'],
                       "levels": levels,
                       "tags": chara_skills[skill['skillId']]['tags'] if skill['skillId'] in chara_skills else [],
                       "blackboard": blackboard})

    if character_dict['talents']:
        for talent_index, talent in enumerate(character_dict['talents']):
            max_candidate_index = len(talent['candidates']) - 1
            maxed_talent = talent['candidates'][max_candidate_index]
            talent_dict = {
                "prefabKey": maxed_talent['prefabKey'], "name_zh": maxed_talent["name"], "name_ja": "", "name_en": "",
                "desc_zh": chara_talents[id]['talents'][talent_index]["desc_zh"], "desc_ja": "", "desc_en": ""}
            if in_global:
                talent_dict["name_ja"] = jp_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_ja"] = chara_talents[id]['talents'][talent_index]["desc_ja"]
                talent_dict["name_en"] = en_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_en"] = chara_talents[id]['talents'][talent_index]["desc_en"]
            talent_dict['blackboard'] = chara_talents[id]['talents'][talent_index]['blackboard'] if id in chara_talents else []
            talents.append(talent_dict)

    uniequip_list = []
    for equip_id in uniequip_dict:
        if uniequip_dict[equip_id]['charId'] == id:
            uniequip_list.append(uniequip_dict[equip_id])
    uniequip_list.sort(key=lambda x: x['uniEquipId'])

    # Handle stats
    stats_list = []
    for phase_index, phase in enumerate(character_dict['phases']):
        if phase_index == 0:
            attributes = phase['attributesKeyFrames'][0]['data']
            stats = {}
            stats['rangeId'] = phase['rangeId']
            stats['level'] = 1
            stats['hp'] = attributes["maxHp"]
            stats['atk'] = attributes["atk"]
            stats['def'] = attributes["def"]
            stats['res'] = attributes["magicResistance"]
            stats['cost'] = attributes["cost"]
            stats['blockCnt'] = attributes["blockCnt"]
            stats['aspd'] = attributes["baseAttackTime"]
            stats['respawnTime'] = attributes["respawnTime"]
            stats_list.append(stats)
        
        attributes = phase['attributesKeyFrames'][1]['data']
        stats = {}
        stats['rangeId'] = phase['rangeId']
        stats['level'] = phase['maxLevel']
        stats['hp'] = attributes["maxHp"]
        stats['atk'] = attributes["atk"]
        stats['def'] = attributes["def"]
        stats['res'] = attributes["magicResistance"]
        stats['cost'] = attributes["cost"]
        stats['blockCnt'] = attributes["blockCnt"]
        stats['aspd'] = attributes["baseAttackTime"]
        stats['respawnTime'] = attributes["respawnTime"]
        stats_list.append(stats)

    # Handle potential attributes
    potential_list = []
    for potential_index, potential in enumerate(character_dict['potentialRanks']):
        potential_dict = {
            "desc_zh": potential['description'],
            "desc_ja": "",
            "desc_en": ""
        }
        if id in jp_char_table and potential_index < len(jp_char_table[id]['potentialRanks']):
            potential_dict["desc_ja"] = jp_char_table[id]['potentialRanks'][potential_index]['description']
            potential_dict["desc_en"] = en_char_table[id]['potentialRanks'][potential_index]['description']
            
        attribute = None
        if potential.get("buff"):
            modifier = potential['buff']['attributes']['attributeModifiers'][0]
            attribute = {ATTRIBUTE_TRANSLATE_TABLE[modifier['attributeType']]: modifier['value']}
        potential_dict['attribute'] = attribute
        potential_list.append(potential_dict)

    # Handle trust/favor
    favor_data = {}
    if character_dict['favorKeyFrames'] is not None:
        favor_last = character_dict['favorKeyFrames'][-1]['data']
        for stat, value in favor_last.items():
            if stat in STAT_CONVERT and bool(value):
                favor_data[STAT_CONVERT[stat]] = value

    # Handle tokens
    tokens = []
    if character_dict['displayTokenDict'] is not None:
        tokens = [tokens_dict[key] for key in character_dict['displayTokenDict']]

    # Handle nationality and affiliations
    powers = []
    powers_list = character_dict['subPower'] or []
    powers_list.append(character_dict['mainPower'])
    for power in powers_list:
        if power['nationId'] is not None:
            powers.append(power['nationId'])
        if power['groupId'] is not None: 
            powers.append(power['groupId'])
        if power['teamId'] is not None: 
            powers.append(power['teamId'])

    # Handle gender, birthplace, race from handbook
    gender = {}
    birthplace = {}
    race = {}
    def extract_story_text(story_text_audio, story_title):
        story_texts = [
            story['storyText'] 
            for item in story_text_audio if item.get('storyTitle') == story_title 
            for story in item.get('stories', []) if id in story.get('patchIdList', [])
        ]
        return story_texts[0] if story_texts else None

    cn_story_text_audio = cn_handbook_info_table['handbookDict']['char_002_amiya']['storyTextAudio']
    jp_story_text_audio = jp_handbook_info_table['handbookDict']['char_002_amiya']['storyTextAudio'] 
    en_story_text_audio = en_handbook_info_table['handbookDict']['char_002_amiya']['storyTextAudio']
    cn_story_text = extract_story_text(cn_story_text_audio, '基础档案')
    if cn_story_text:
        gender['zh'] = cn_story_text.split("【性别】")[1].split("\n")[0].strip()
        if in_global:
            gender['ja'] = extract_story_text(jp_story_text_audio, '基礎情報').split("【性別】")[1].split("\n")[0].strip()
            gender['en'] = extract_story_text(en_story_text_audio, 'Basic Info').split("[Gender]")[1].split("\n")[0].strip()
        birthplace['zh'] = cn_story_text.split("【出身地】")[1].split("\n")[0].strip()
        if in_global:
            birthplace['ja'] = extract_story_text(jp_story_text_audio, '基礎情報').split("【出身地】")[1].split("\n")[0].strip()
            birthplace['en'] = extract_story_text(en_story_text_audio, 'Basic Info').split("[Place of Birth]")[1].split("\n")[0].strip()
        if "种族" not in cn_story_text:
            race['zh'] = "其他"
            race['ja'] = "その他"
            race['en'] = "Others"
        else:
            race['zh'] = cn_story_text.split("【种族】")[1].split("\n")[0].strip()
            if in_global:
                race['ja'] = extract_story_text(jp_story_text_audio, '基礎情報').split("【種族】")[1].split("\n")[0].strip()
                race['en'] = extract_story_text(en_story_text_audio, 'Basic Info').split("[Race]")[1].split("\n")[0].strip()


    result_dict = {"id": id, "appellation": character_dict['appellation'],
                   "name_zh": character_dict['name'], "name_ja": "", "name_en": "",
                   "desc_zh": desc_zh, "desc_ja": "", "desc_en": "",
                   "releaseDate": imple_dates.get(id, 0), 
                   "gender": gender, "birthplace": birthplace, "race": race, "powers": powers,
                   "position": character_dict['position'], "isSpChar": character_dict['isSpChar'],
                   "rarity": character_dict['rarity'], "profession": character_dict['profession'], "subProfessionId": character_dict['subProfessionId'],
                   "stats": stats_list, "potential": potential_list, "favorData": favor_data, "tokens": tokens,
                   "skills": skills, "talents": talents, "uniequip": uniequip_list}
    
    if in_global:
        result_dict["name_ja"] = jp_patch_table['patchChars'][id]['name']
        result_dict["name_en"] = en_patch_table['patchChars'][id]['name']
        result_dict["desc_ja"] = jp_patch_table['patchChars'][id]['description'].replace("<$ba", "<ba")
        result_dict["desc_en"] = en_patch_table['patchChars'][id]['description'].replace("<$ba", "<ba")
    data[id] = result_dict

with open('characters_read.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

with open('characters.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

for id in subProfessionIds:
    if id not in SUBPROFESSIONS:
        print(id,' (new!)')
