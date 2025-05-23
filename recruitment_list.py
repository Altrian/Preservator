import json
import os
import re


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

with open('recruitment_list.json', 'r', encoding='utf-8') as f:
    recruitment_list = json.load(f)
with open('arknights_utilities.json', 'r', encoding='utf-8') as f:
    arknights_utilities = json.load(f)

KEYS_TO_IGNORE = ["char_512_aprot", "char_600_cpione", "char_601_cguard",
                  "char_602_cdfend", "char_603_csnipe", "char_604_ccast",
                  "char_605_cmedic", "char_606_csuppo", "char_607_cspec",
                  "char_608_acpion", "char_609_acguad", "char_610_acfend",
                  "char_611_acnipe", "char_612_accast", "char_613_acmedc",
                  "char_614_acsupo", "char_615_acspec"]

CHARA_NAME_SUBSTITUTIONS = {"'Justice Knight'": "Justice Knight"}

filtered_cn_char_table = {data['name']: key for key, data in cn_char_table.items(    
) if "token" not in key and "trap" not in key and key not in KEYS_TO_IGNORE}

cn_matches = list(re.finditer(
    r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
    cn_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
)) # Find all matches 
en_matches = {(m.group(1) or m.group(2)).strip() for m in re.finditer(
    r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
    en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
)} # Create a set of English names from the matches

for match in cn_matches:
    # Extract the character name from the match
    name_zh = match.group(1) if match.group(
        1) else match.group(2)
    name_zh = name_zh.strip() # Remove leading and trailing whitespace
    recruit_only = bool(match.group(1)) # If group 1 is not None, set recruit_only to True
    
    if name_zh in filtered_cn_char_table:
        charaId = filtered_cn_char_table[name_zh]
        if charaId in recruitment_list:
            continue
        recruitment_list[charaId] = {"name_zh": name_zh, "IsRecruitOnly": recruit_only}
        name_en = en_char_table.get(charaId, {}).get('name', None)
        name_en = CHARA_NAME_SUBSTITUTIONS.get(name_en, name_en)

        if name_en is not None and name_en in en_matches:
            recruitment_list[charaId]["name_en"] = name_en
            recruitment_list[charaId]["name_jp"] = jp_char_table[charaId]['name']

with open('recruitment_list.json', 'w', encoding='utf-8') as f:
    json.dump(recruitment_list, f, ensure_ascii=False, indent=4)


if 'gacha_tags' not in arknights_utilities:
    arknights_utilities['gacha_tags'] = {} 

en_gacha_tags = {tag['tagId']: tag for tag in en_gacha_table['gachaTags']}
jp_gacha_tags = {tag['tagId']: tag for tag in jp_gacha_table['gachaTags']}

tags_dict = {}
for tag in cn_gacha_table['gachaTags']:
    tag_id = tag['tagId']
    tag_entry = {'name_zh': tag['tagName']}
    if tag_id in en_gacha_tags:
        tag_entry['name_en'] = en_gacha_tags[tag_id]['tagName']
        tag_entry['name_jp'] = jp_gacha_tags[tag_id]['tagName']
    tags_dict[tag_id] = tag_entry
arknights_utilities['gacha_tags'] = tags_dict

with open('arknights_utilities.json', 'w', encoding='utf-8') as f:
    json.dump(arknights_utilities, f, ensure_ascii=False, indent=4)
