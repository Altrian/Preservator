import json
from pathlib import Path
from util import get
from chara_skills import replace_substrings
from urls import cn_urls, jp_urls, en_urls


def update_chara_talents():
    
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    chara_talents_path = output_path = json_dir / 'chara_talents.json'
    
    # base_url_cn = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master"
    # base_url_global = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main"

    # cn_char_table = get("cn_char_table", f"{base_url_cn}/zh_CN/gamedata/excel/character_table.json")
    # jp_char_table = get("jp_char_table", f"{base_url_global}/ja_JP/gamedata/excel/character_table.json")
    # en_char_table = get("en_char_table", f"{base_url_global}/en_US/gamedata/excel/character_table.json")
    # cn_patch_table = get("cn_patch_table", f"{base_url_cn}/zh_CN/gamedata/excel/char_patch_table.json")
    # jp_patch_table = get("jp_patch_table", f"{base_url_global}/ja_JP/gamedata/excel/char_patch_table.json")
    # en_patch_table = get("en_patch_table", f"{base_url_global}/en_US/gamedata/excel/char_patch_table.json")

    cn_char_table = get("cn_char_table", cn_urls.char_table)
    jp_char_table = get("jp_char_table", jp_urls.char_table)
    en_char_table = get("en_char_table", en_urls.char_table)
    cn_patch_table = get("cn_patch_table", cn_urls.patch_table)
    jp_patch_table = get("jp_patch_table", jp_urls.patch_table)
    en_patch_table = get("en_patch_table", en_urls.patch_table)

    with open(chara_talents_path, encoding='utf-8') as f:
        chara_talents = json.load(f)

    filtered_cn_char_table = {key: cn_char_table[key] for key in cn_char_table.keys()
                              if "token" not in key and "trap" not in key}

    # append new charas to char talent tags json
    new_chara_list = [id for id in dict.keys(
        filtered_cn_char_table) if id not in set(dict.keys(chara_talents))]
    return_dict = {}
    for id in new_chara_list:
        talents = []
        if filtered_cn_char_table[id].get('talents'):
            for talent_index, talent in enumerate(filtered_cn_char_table[id]['talents']):
                max_candidate_index = len(talent['candidates']) - 1
                maxed_talent = talent['candidates'][max_candidate_index]
                talent_holder = {
                    "prefabKey": maxed_talent.get("prefabKey", ""),
                    "name_zh": maxed_talent.get("name", ""),
                    "name_en": "",
                    "name_ja": "",
                    "desc_zh": replace_substrings(maxed_talent.get("description", ""), maxed_talent.get('blackboard', [])),
                    "desc_ja": "",
                    "desc_en": "",
                    "tags": [],
                    "blackboard": maxed_talent.get('blackboard', [])
                }
                if id in jp_char_table:
                    talent_holder["name_ja"] = jp_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index].get("name", "")
                    talent_holder["desc_ja"] = replace_substrings(
                        jp_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index].get("description", ""),
                        maxed_talent.get('blackboard', [])
                    )
                if id in en_char_table:
                    talent_holder["name_en"] = en_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index].get("name", "")
                    talent_holder["desc_en"] = replace_substrings(
                        en_char_table[id]['talents'][talent_index]['candidates'][max_candidate_index].get("description", ""),
                        maxed_talent.get('blackboard', [])
                    )
                talents.append(talent_holder)
        return_dict[id] = {
            "appellation": filtered_cn_char_table[id].get('appellation', ""),
            "talents": talents
        }

    # char patch table
    new_chara_list = [id for id in dict.keys(
        cn_patch_table.get('patchChars', {})) if id not in set(dict.keys(chara_talents))]
    for id in new_chara_list:
        talents = []
        patch_char = cn_patch_table['patchChars'][id]
        if patch_char.get('talents'):
            for talent_index, talent in enumerate(patch_char['talents']):
                max_candidate_index = len(talent['candidates']) - 1
                maxed_talent = talent['candidates'][max_candidate_index]
                talent_holder = {
                    "prefabKey": maxed_talent.get("prefabKey", ""),
                    "name_zh": maxed_talent.get("name", ""),
                    "name_en": "",
                    "name_ja": "",
                    "desc_zh": maxed_talent.get("description", ""),
                    "desc_ja": "",
                    "desc_en": "",
                    "tags": [],
                    "blackboard": maxed_talent.get('blackboard', [])
                }
                if id in jp_patch_table.get('patchChars', {}):
                    talent_holder["name_ja"] = jp_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index].get("name", "")
                    talent_holder["desc_ja"] = jp_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index].get("description", "")
                if id in en_patch_table.get('patchChars', {}):
                    talent_holder["name_en"] = en_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index].get("name", "")
                    talent_holder["desc_en"] = en_patch_table['patchChars'][id]['talents'][talent_index]['candidates'][max_candidate_index].get("description", "")
                talents.append(talent_holder)
        return_dict[id] = {
            "appellation": patch_char.get('appellation', ""),
            "talents": talents
        }
    return_dict = chara_talents | return_dict

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(return_dict, f, ensure_ascii=False, indent=4)

    return {"name": "chara_talents", "newCharas": len(new_chara_list)}

if __name__ == "__main__":
    update_chara_talents()