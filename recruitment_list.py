import json
import os
import re
from datetime import datetime


now = datetime.now()
date_str = now.strftime("%Y-%m-%d")

KEYS_TO_IGNORE = ["char_512_aprot", "char_600_cpione", "char_601_cguard",
                  "char_602_cdfend", "char_603_csnipe", "char_604_ccast",
                  "char_605_cmedic", "char_606_csuppo", "char_607_cspec",
                  "char_608_acpion", "char_609_acguad", "char_610_acfend",
                  "char_611_acnipe", "char_612_accast", "char_613_acmedc",
                  "char_614_acsupo", "char_615_acspec"]

CHARA_NAME_SUBSTITUTIONS = {"'Justice Knight'": "Justice Knight"}

RARITY_CONVERT = {"TIER_1": "支援机械", "TIER_2": "新手", 
                  "TIER_5": "资深干员", "TIER_6": "高级资深干员"}

PROFESSION_CONVERT = {"WARRIOR": "近卫干员", "SNIPER": "狙击干员", "TANK": "重装干员",
                      "MEDIC": "医疗干员", "SUPPORT": "辅助干员", "CASTER": "术师干员", 
                      "SPECIAL": "特种干员", "PIONEER": "先锋干员"}

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in

cn_char_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/character_table.json")
en_char_table_path = os.path.join(
    script_dir, "global_data/en_US/gamedata/excel/character_table.json")
jp_char_table_path = os.path.join(
    script_dir, "global_data/ja_JP/gamedata/excel/character_table.json")
cn_gacha_table_path = os.path.join(
    script_dir, "cn_data/zh_CN/gamedata/excel/gacha_table.json")
en_gacha_table_path = os.path.join(
    script_dir, "global_data/en_US/gamedata/excel/gacha_table.json")
jp_gacha_table_path = os.path.join(
    script_dir, "global_data/ja_JP/gamedata/excel/gacha_table.json")

with open(cn_char_table_path, encoding='utf-8') as f:
    cn_char_table = json.load(f)
with open(en_char_table_path, encoding='utf-8') as f:
    en_char_table = json.load(f)
with open(jp_char_table_path, encoding='utf-8') as f:
    jp_char_table = json.load(f)
with open(cn_gacha_table_path, encoding='utf-8') as f:
    cn_gacha_table = json.load(f)
with open(en_gacha_table_path, encoding='utf-8') as f:
    en_gacha_table = json.load(f)
with open(jp_gacha_table_path, encoding='utf-8') as f:
    jp_gacha_table = json.load(f)

with open('recruitment.json', 'r', encoding='utf-8') as f:
    recruitment = json.load(f)

with open('recruitment_table.json', 'r', encoding='utf-8') as f:
    recruitment_dict = json.load(f)

# If the recruitment file is empty, initialize it
if not recruitment:
    recruitment = {
        "tags": {"updatedAt": date_str, "data": []},
        "recruitment_list": {"updatedAt": date_str, "data": []}
    }

en_gacha_tags = {tag['tagId']: tag for tag in en_gacha_table['gachaTags']}
jp_gacha_tags = {tag['tagId']: tag for tag in jp_gacha_table['gachaTags']}

tags_list = []
for tag in cn_gacha_table['gachaTags']:
    tag_id = tag['tagId']
    tag_entry = {'id': tag_id, 'name_zh': tag['tagName']}
    if tag_id in en_gacha_tags: # Check if the tag exists in Global
        tag_entry['name_en'] = en_gacha_tags[tag_id]['tagName']
        tag_entry['name_jp'] = jp_gacha_tags[tag_id]['tagName']
    tags_list.append(tag_entry)
if not (recruitment['tags'].get('data', []) == tags_list):
    # If the tags have changed, update the recruitment tags
    recruitment['tags'] = {"updatedAt": date_str, 
                           "data": tags_list}


filtered_cn_char_table = {data['name']: key for key, data in cn_char_table.items(    
) if "token" not in key and "trap" not in key and key not in KEYS_TO_IGNORE}

filtered_cn_tag_names = {data['name_zh']: data['id'] for data in tags_list}

cn_matches = list(re.finditer(
    r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
    cn_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
)) # Find all matches 
en_matches = {(m.group(1) or m.group(2)).strip() for m in re.finditer(
    r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
    en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
)} # Create a set of English names from the matches

recruitment_list = []
for match in cn_matches:
    # Extract the character name from the match
    name_zh = match.group(1) if match.group(
        1) else match.group(2)
    name_zh = name_zh.strip() # Remove leading and trailing whitespace
    recruit_only = bool(match.group(1)) # If group 1 is not None, set recruit_only to True
    
    if name_zh in filtered_cn_char_table:
        charaId = filtered_cn_char_table[name_zh]
        character_dict = {}
        cn_chara = cn_char_table[charaId]
        character_dict = {"id": charaId, "appellation": cn_chara['appellation'],
                          "name_zh": cn_chara['name'], "name_ja": "", "name_en": "",
                          "rarity": cn_chara['rarity'],
                          "profession": cn_chara['profession'],
                          "subProfessionId": cn_chara['subProfessionId'],
                          "IsRecruitOnly": recruit_only, "tags": []}
        # Check if the character exists in the Global character table
        name_en = en_char_table.get(charaId, {}).get('name', None)
        name_en = CHARA_NAME_SUBSTITUTIONS.get(name_en, name_en) # Apply substitutions if necessary
        if name_en is not None and name_en in en_matches:
            character_dict["name_en"] = name_en
            character_dict["name_ja"] = jp_char_table[charaId]['name']
        tag_list = set()
        # Append tag based on character position
        tag_list.add(
            filtered_cn_tag_names["近战位"] if cn_chara['position'] == "MELEE" else filtered_cn_tag_names["远程位"])
        # Append tag based on character rarity
        if cn_chara['rarity'] in RARITY_CONVERT:
            tag_list.add(filtered_cn_tag_names[RARITY_CONVERT[cn_chara['rarity']]])
        # Append tag based on character profession
        if (tag := filtered_cn_tag_names.get(PROFESSION_CONVERT.get(cn_chara['profession']))) is not None:
            tag_list.add(tag)
        # Append tags from character's tagList
        for tag in cn_char_table[charaId]['tagList']:
            tag_id = filtered_cn_tag_names[tag]
            tag_list.add(tag_id)
        character_dict["tags"] = list(tag_list)
        recruitment_dict[charaId] = character_dict
        recruitment_list.append(character_dict)
recruitment['recruitment_list'] = {"updatedAt": date_str, 
                                   "data": recruitment_list}

with open('recruitment.json', 'w', encoding='utf-8') as f:
    json.dump(recruitment, f, ensure_ascii=False, indent=4)

with open('recruitment_table.json', 'w', encoding='utf-8') as f:
    json.dump(recruitment_dict, f, ensure_ascii=False, indent=4)

