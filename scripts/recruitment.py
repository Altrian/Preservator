import re
import json
from pathlib import Path
from util import get, Report
from datetime import datetime
from urls import cn_urls, jp_urls, en_urls

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
    
    cn_char_table = get("cn_char_table", cn_urls.char_table)
    jp_char_table = get("jp_char_table", jp_urls.char_table)
    en_char_table = get("en_char_table", en_urls.char_table)
    cn_gacha_table = get("cn_gacha_table", cn_urls.gacha_table)
    jp_gacha_table = get("jp_gacha_table", jp_urls.gacha_table)
    en_gacha_table = get("en_gacha_table", en_urls.gacha_table)
    cn_handbook_team_table = get("cn_handbook_team_table", cn_urls.handbook_team_table)
    jp_handbook_team_table = get("jp_handbook_team_table", jp_urls.handbook_team_table)
    en_handbook_team_table = get("en_handbook_team_table", en_urls.handbook_team_table)

    # Current date for updates
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    recruitment_report = {}
    recruitment_table_report = {}

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

    existing_tags_set = {tag['orderNum'] for tag in recruitment['tags'].get('data', [])}
    tags_by_id = {tag['orderNum']: tag for tag in recruitment['tags'].get('data', [])}
    tags_list = []
    for tag in cn_gacha_table['gachaTags']:
        tag_id = tag['tagId']
        if tag_id in existing_tags_set:
            tag_entry = tags_by_id[tag_id]
        else:
            tag_entry = {'id': tag['tagName'], 'orderNum': tag['tagId'], 'name': {'zh': tag['tagName'], 'ja': '', 'en': ''}}
            recruitment_report.setdefault("new tags added", []).append(tag['tagName'])
            if (class_code := PROFESSION_CONVERT_INV.get(tag['tagName'])) is not None:
                tag_entry['id'] = class_code
            if (rarity_code := RARITY_CONVERT_INV.get(tag['tagName'])) is not None:
                tag_entry['id'] = rarity_code
        if tag_id in en_gacha_tags and tag_entry['name']['ja'] == "":
            tag_entry['name']['en'] = en_gacha_tags[tag_id]['tagName']
            tag_entry['name']['ja'] = jp_gacha_tags[tag_id]['tagName']
            recruitment_report.setdefault("tags updated", []).append(tag['tagName'])
        if tag_entry['name']['en'] == "Ranged" or tag_entry['name']['en'] == "Melee":
            tag_entry['id'] = tag_entry['name']['en'].upper()
        tags_list.append(tag_entry)
    if recruitment['tags'].get('data', []) != tags_list:
        recruitment['tags'] = {"updatedAt": date_str, "data": tags_list}

    existing_powers_set = {power['id'] for power in recruitment['powers'].get('data', [])}
    powers_by_id = {power['id']: power for power in recruitment['powers'].get('data', [])}
    powers_list = []
    for id, power_data in cn_handbook_team_table.items():
        if id in existing_powers_set:
            power_dict = powers_by_id[id]
        else:
            power_dict = {
                "id": power_data['powerId'],
                "orderNum": power_data['orderNum'],
                "powerLevel": power_data['powerLevel'],
                "name": {"zh": power_data['powerName'], "ja": "", "en": ""},
                "isLimited": power_data['isLimited'],
                "isRaw": power_data['isRaw'],
            }
            recruitment_report.setdefault("new powers added", []).append(power_dict['id'])
        if id in jp_handbook_team_table and power_dict["name"]["ja"] == "":
            power_dict["name"]["ja"] = jp_handbook_team_table[id]['powerName']
            power_dict["name"]["en"] = en_handbook_team_table[id]['powerName']
            recruitment_report.setdefault("powers updated", []).append(power_dict['id'])
        powers_list.append(power_dict)
    if recruitment['powers'].get('data', []) != powers_list:
        recruitment['powers'] = {"updatedAt": date_str, "data": powers_list}

    with open(output_recruitment_path, 'w', encoding='utf-8') as f:
        json.dump(recruitment, f, ensure_ascii=False, indent=4)


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

    recruit_only_matches = (list(re.finditer(r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)", 
        cn_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE))
    )

    en_matches = {(m.group(1) or m.group(2)).strip() for m in re.finditer(
        r"(?<!>\s)<@rc\.eml>([^,，]*?)<\/>|(?:\/\s*|\n\s*|\\n\s*)((?!-)[^\r\/>★]+?(?<!-))(?=\/|$)",
        en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    )}
    en_matches.update({m.group(1).strip() for m in re.finditer(
        r"(?:\/\s*)([^\n\/>★\r]+?)(?=\s*(?:\r?\n|\\n)-+)",
        en_gacha_table['recruitDetail'], flags=re.IGNORECASE | re.MULTILINE
    )})

    new_recruitment_dict = {}
    for match in cn_matches:
        # Extract the character name from the match
        name_zh = match.group(1).strip() if match.group(1) else match.group(2).strip()
        # If any match in recruit_only_matches has this name in group 1 return True
        recruit_only = any(name_zh in (m.group(1) or "") for m in recruit_only_matches)
        
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
            if charaId not in recruitment_dict:
                recruitment_table_report.setdefault("new character added", []).append(cn_chara['appellation'])
            # Check if the character exists in the Global character table
            name_en = en_char_table.get(charaId, {}).get('name', None)
            name_en = CHARA_NAME_SUBSTITUTIONS.get(name_en, name_en)
            if name_en is not None and name_en in en_matches:
                character_dict["name"]['en'] = name_en
                character_dict["name"]['ja'] = jp_char_table[charaId]['name']
                if charaId in recruitment_dict and recruitment_dict[charaId]['name']['en'] != name_en:
                    recruitment_table_report.setdefault("character updated", []).append(cn_chara['appellation'])
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
            new_recruitment_dict[charaId] = character_dict
    if recruitment_dict != new_recruitment_dict:
        recruitment_dict = new_recruitment_dict

    with open(output_recruitment_table_path, 'w', encoding='utf-8') as f:
        json.dump(recruitment_dict, f, ensure_ascii=False, indent=4)

    return [
        {"name": "recruitment", "updatedAt": date_str, "records": recruitment_report},
        {"name": "recruitment_table", "updatedAt": date_str, "records": recruitment_table_report}]

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    report_path = json_dir / 'report.json'
    latest_path = json_dir / 'latest_report.json'
    Report.singular(update_recruitment(), path=report_path, latest_path=latest_path)