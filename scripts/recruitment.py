import re
import json
from pathlib import Path
from fetch import get
from datetime import datetime

KEYS_TO_IGNORE = ["char_512_aprot", "char_600_cpione", "char_601_cguard",
                  "char_602_cdfend", "char_603_csnipe", "char_604_ccast",
                  "char_605_cmedic", "char_606_csuppo", "char_607_cspec",
                  "char_608_acpion", "char_609_acguad", "char_610_acfend",
                  "char_611_acnipe", "char_612_accast", "char_613_acmedc",
                  "char_614_acsupo", "char_615_acspec"]

CHARA_NAME_SUBSTITUTIONS = {"'Justice Knight'": "Justice Knight"}

RARITY_CONVERT = {"TIER_1": "支援机械", "TIER_2": "新手",
                  "TIER_5": "资深干员", "TIER_6": "高级资深干员"}

RARITY_CONVERT_INV = {cn_name: rarity_code for rarity_code, cn_name in RARITY_CONVERT.items()}

PROFESSION_CONVERT = {"WARRIOR": "近卫干员", "SNIPER": "狙击干员", "TANK": "重装干员",
                      "MEDIC": "医疗干员", "SUPPORT": "辅助干员", "CASTER": "术师干员",
                      "SPECIAL": "特种干员", "PIONEER": "先锋干员"}

PROFESSION_CONVERT_INV = {class_code: cn_name for cn_name, class_code in PROFESSION_CONVERT.items()}


def update_recruitment():
    
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    recruitment_path = output_recruitment_path = json_dir / 'recruitment.json'
    recruitment_table_path = output_recruitment_table_path = json_dir / 'recruitment_table.json'

    base_url_cn = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master"
    base_url_global = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main"

    cn_char_table = get("cn_char_table", f"{base_url_cn}/zh_CN/gamedata/excel/character_table.json")
    jp_char_table = get("jp_char_table", f"{base_url_global}/ja_JP/gamedata/excel/character_table.json")
    en_char_table = get("en_char_table", f"{base_url_global}/en_US/gamedata/excel/character_table.json")
    cn_gacha_table = get("cn_gacha_table", f"{base_url_cn}/zh_CN/gamedata/excel/gacha_table.json")
    jp_gacha_table = get("jp_gacha_table", f"{base_url_global}/ja_JP/gamedata/excel/gacha_table.json")
    en_gacha_table = get("en_gacha_table", f"{base_url_global}/en_US/gamedata/excel/gacha_table.json")
    cn_handbook_team_table = get("cn_handbook_team_table", f"{base_url_cn}/zh_CN/gamedata/excel/handbook_team_table.json")
    jp_handbook_team_table = get("jp_handbook_team_table", f"{base_url_global}/ja_JP/gamedata/excel/handbook_team_table.json")
    en_handbook_team_table = get("en_handbook_team_table", f"{base_url_global}/en_US/gamedata/excel/handbook_team_table.json")
    
    # Current date for updates
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    if recruitment_path.exists():
        with open(recruitment_path, 'r', encoding='utf-8') as f:
            recruitment = json.load(f)
    else:
        recruitment = {}

    if recruitment_table_path.exists():
        with open(recruitment_table_path, 'r', encoding='utf-8') as f:
            recruitment_dict = json.load(f)
    else:
        recruitment_dict = {}

    # If the recruitment file is empty, initialize it
    if not recruitment:
        recruitment = {
            "tags": {"updatedAt": date_str, "data": []},
            "branch": {"updatedAt": date_str, "data": {}},
            "powers": {"updatedAt": date_str, "data": []}
        }

    en_gacha_tags = {tag['tagId']: tag for tag in en_gacha_table['gachaTags']}
    jp_gacha_tags = {tag['tagId']: tag for tag in jp_gacha_table['gachaTags']}

    existing_tags = {tag['id'] for tag in recruitment['tags'].get('data', [])}
    tags_list = []
    for tag in cn_gacha_table['gachaTags']:
        tag_id = tag['tagId']
        if tag_id in existing_tags:
            tag_entry = existing_tags[tag_id]
        else:
            tag_entry = {'id': tag['tagName'], 'orderNum': tag['tagId'], 'name': {'zh': tag['tagName'], 'ja': '', 'en': ''}}
            if (class_code := PROFESSION_CONVERT_INV.get(tag['tagName'])) is not None:
                tag_entry['id'] = class_code
            if (rarity_code := RARITY_CONVERT_INV.get(tag['tagName'])) is not None:
                tag_entry['id'] = rarity_code
            if tag_id in en_gacha_tags:
                tag_entry['name']['en'] = en_gacha_tags[tag_id]['tagName']
                tag_entry['name']['ja'] = jp_gacha_tags[tag_id]['tagName']
            if tag_entry['name']['en'] == "Ranged" or tag_entry['name']['en'] == "Melee":
                tag_entry['id'] = tag_entry['name']['en'].upper()
        tags_list.append(tag_entry)
    if not (recruitment['tags'].get('data', []) == tags_list):
        recruitment['tags'] = {"updatedAt": date_str, "data": tags_list}

    filtered_cn_char_table = {data['name']: key for key, data in cn_char_table.items()
                              if "token" not in key and "trap" not in key and key not in KEYS_TO_IGNORE}
    filtered_cn_tag_names = {data['name']['zh']: data['id'] for data in tags_list}

    cn_matches = list(re.finditer(
        r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
        cn_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    ))
    cn_matches.extend(list(re.finditer(
        r"(?:\/\s*)([^\n\/>★\r]+?)(?=\s*(?:\r?\n|\\n)-+)",
        cn_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    )))

    en_matches = {(m.group(1) or m.group(2)).strip() for m in re.finditer(
        r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
        en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    )}
    en_matches.update({m.group(1).strip() for m in re.finditer(
        r"(?:\/\s*)([^\n\/>★\r]+?)(?=\s*(?:\r?\n|\\n)-+)",
        en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    )})

    recruitment_list = []
    for match in cn_matches:
        # Extract the character name from the match
        name_zh = match.group(1).strip() if match.group(1) else match.group(2).strip()
        recruit_only = bool(match.group(1)) # If group 1 is not None, set recruit_only to True
        
        if name_zh in filtered_cn_char_table:
            charaId = filtered_cn_char_table[name_zh]
            cn_chara = cn_char_table[charaId]
            character_dict = {
                "id": charaId,
                "appellation": cn_chara['appellation'],
                "name": {"zh": cn_chara['name'], "ja": "", "en": ""},
                "rarity": cn_chara['rarity'],
                "profession": cn_chara['profession'],
                "subProfessionId": cn_chara['subProfessionId'],
                "IsRecruitOnly": recruit_only,
                "tags": []
            }
            # Check if the character exists in the Global character table
            name_en = en_char_table.get(charaId, {}).get('name', None)
            name_en = CHARA_NAME_SUBSTITUTIONS.get(name_en, name_en)
            if name_en is not None and name_en in en_matches:
                character_dict["name"]['en'] = name_en
                character_dict["name"]['ja'] = jp_char_table[charaId]['name']
            tag_list = {}
            if (tag := filtered_cn_tag_names.get("近战位" if cn_chara['position'] == "MELEE" else "远程位")):
                tag_list[tag] = None
            if (rarity_name := RARITY_CONVERT.get(cn_chara['rarity'])) and (tag := filtered_cn_tag_names.get(rarity_name)):
                tag_list[tag] = None
            if (prof_tag := PROFESSION_CONVERT.get(cn_chara['profession'])) and (tag := filtered_cn_tag_names.get(prof_tag)):
                tag_list[tag] = None
            for tag_name in cn_char_table[charaId]['tagList']:
                if (tag_id := filtered_cn_tag_names.get(tag_name)):
                    tag_list[tag_id] = None
            character_dict["tags"] = list(tag_list.keys())
            recruitment_dict[charaId] = character_dict
            recruitment_list.append(character_dict)

    powers_list = []
    for id, power_data in cn_handbook_team_table.items():
        power_dict = {
            "id": power_data['powerId'],
            "orderNum": power_data['orderNum'],
            "powerLevel": power_data['powerLevel'],
            "name": {"zh": power_data['powerName'], "ja": "", "en": ""},
            "isLimited": power_data['isLimited'],
            "isRaw": power_data['isRaw'],
        }
        if id in jp_handbook_team_table:
            power_dict["name"]["ja"] = jp_handbook_team_table[id]['powerName']
            power_dict["name"]["en"] = en_handbook_team_table[id]['powerName']
        powers_list.append(power_dict)
    recruitment['powers'] = {"updatedAt": date_str, "data": powers_list}

    with open(output_recruitment_path, 'w', encoding='utf-8') as f:
        json.dump(recruitment, f, ensure_ascii=False, indent=4)

    with open(output_recruitment_table_path, 'w', encoding='utf-8') as f:
        json.dump(recruitment_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    from main import setup
    setup()
    update_recruitment()
