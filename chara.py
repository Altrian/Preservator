import os
import json
import re
import pprint
from chara_skills import replace_substrings

pp = pprint.PrettyPrinter(indent=4)

STAT_CONVERT = {'maxHp': "hp", "magicResistance": "res", "attackSpeed": "aspd",
                "moveSpeed": "ms", "respawnTime": "respawnTime", "atk": 'atk', "def": "def", "cost": "cost"}

script_dir = os.path.dirname(__file__)  # <-- Absolute directory for the script

cn_char_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/character_table.json")
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

data = []

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
    if character_dict['subProfessionId'] not in subProfessionIds:
        subProfessionIds.append(character_dict['subProfessionId'])
    skills = []
    talents = []
    for skill in character_dict['skills']:
        blackboard = chara_skills.get(skill['skillId'], {}).get('blackboard', [])
        skills.append({"skillId": skill['skillId'],
                       "name_zh": chara_skills[skill['skillId']]['name_zh'],
                       "name_ja": chara_skills[skill['skillId']]['name_ja'],
                       "name_en": chara_skills[skill['skillId']]['name_en'],
                       "skillType": chara_skills[skill['skillId']]['skillType'],
                       "durationType": chara_skills[skill['skillId']]['durationType'],
                       "spType": chara_skills[skill['skillId']]['spType'],
                       "levels": chara_skills[skill['skillId']]['levels'],
                       "tags": chara_skills[skill['skillId']]['tags'],
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
            if id in en_char_table:
                talent_dict["name_ja"] = jp_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_ja"] = chara_talents[id]['talents'][talent_index]["desc_ja"]
                talent_dict["name_en"] = en_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index]["name"]
                talent_dict["desc_en"] = chara_talents[id]['talents'][talent_index]["desc_en"]
            talent_dict['rangeId'] = chara_talents[id]['talents'][talent_index].get('rangeId', None)
            talent_dict['tags'] = chara_talents[id]['talents'][talent_index].get('tags', [])
            talent_dict['blackboard'] = chara_talents[id]['talents'][talent_index].get('blackboard', [])
            talents.append(talent_dict)

    uniequip_list = []
    for equip_id in uniequip_dict:
        if uniequip_dict[equip_id]['charId'] == id:
            uniequip_list.append(uniequip_dict[equip_id])
    uniequip_list.sort(key=lambda x: x['order'])

    stats = {}
    stats['rangeId'] = character_dict['phases'][-1]['rangeId']
    stats['level'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['level']
    stats['hp'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["maxHp"]
    stats['atk'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["atk"]
    stats['def'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["def"]
    stats['res'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["magicResistance"]
    stats['cost'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["cost"]
    stats['blockCnt'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["blockCnt"]
    stats['aspd'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["baseAttackTime"]
    stats['respawnTime'] = character_dict['phases'][-1]['attributesKeyFrames'][-1]['data']["respawnTime"]

    # Handle potential attributes
    potential = []
    attribute_translate_table = {'COST': "cost", "RESPAWN_TIME": 'respawnTime', 'ATK': "atk",
                                 "MAX_HP": "hp", "ATTACK_SPEED": "aspd", "DEF": "def", "MAGIC_RESISTANCE": "res"}

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
            attribute = {attribute_translate_table[modifier['attributeType']]: modifier['value']}
        potential_dict['attribute'] = attribute
        potential.append(potential_dict)

    # Handle trust/favor
    favor_data = {}
    if character_dict['favorKeyFrames'] is not None:
        favor_last = character_dict['favorKeyFrames'][-1]['data']
        for stat, value in favor_last:
            if stat in STAT_CONVERT:
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

    result_dict = {"id": id, "appellation": character_dict['appellation'],
                   "name_zh": character_dict['name'], "name_ja": "", "name_en": "",
                   "desc_zh": desc_zh, "desc_ja": "", "desc_en": "",
                   "releaseDate": imple_dates.get(id, 0), "powers": powers,
                   "position": character_dict['position'], "isSpChar": character_dict['isSpChar'],
                   "rarity": character_dict['rarity'], "profession": character_dict['profession'], "subProfessionId": character_dict['subProfessionId'],
                   "stats": stats, "potential": potential, "favorData": favor_data, "tokens": tokens,
                   "skills": skills, "talents": talents, "uniequip": uniequip_list}
    
    if id in jp_char_table:
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

        result_dict["name_ja"] = jp_char_table[id]['name']
        result_dict["name_en"] = en_char_table[id]['name']
        result_dict["desc_ja"] = desc_ja
        result_dict["desc_en"] = desc_en
    data.append(result_dict)