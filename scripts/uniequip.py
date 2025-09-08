import json
from pathlib import Path
from util import get
from chara_skills import replace_substrings
from urls import cn_urls, jp_urls, en_urls


def update_uniequip():

    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    uniequip_path = output_path = json_dir / 'uniequip.json'

    # base_url_cn = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master"
    # base_url_global = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main"

    # cn_uniequip_table = get("cn_uniequip_table", f"{base_url_cn}/zh_CN/gamedata/excel/uniequip_table.json")
    # jp_uniequip_table = get("jp_uniequip_table", f"{base_url_global}/ja_JP/gamedata/excel/uniequip_table.json")
    # en_uniequip_table = get("en_uniequip_table", f"{base_url_global}/en_US/gamedata/excel/uniequip_table.json")
    # cn_battle_equip_table = get("cn_battle_equip_table", f"{base_url_cn}/zh_CN/gamedata/excel/battle_equip_table.json")
    # jp_battle_equip_table = get("jp_battle_equip_table", f"{base_url_global}/ja_JP/gamedata/excel/battle_equip_table.json")
    # en_battle_equip_table = get("en_battle_equip_table", f"{base_url_global}/en_US/gamedata/excel/battle_equip_table.json")

    cn_uniequip_table = get("cn_uniequip_table", cn_urls.uniequip_table)
    jp_uniequip_table = get("jp_uniequip_table", jp_urls.uniequip_table)
    en_uniequip_table = get("en_uniequip_table", en_urls.uniequip_table)
    cn_battle_equip_table = get("cn_battle_equip_table", cn_urls.battle_equip_table)
    jp_battle_equip_table = get("jp_battle_equip_table", jp_urls.battle_equip_table)
    en_battle_equip_table = get("en_battle_equip_table", en_urls.battle_equip_table)

    with open(uniequip_path, encoding='utf-8') as f:
        curr_uniequip = json.load(f)

    new_equips = [id for id in dict.keys(
        cn_uniequip_table['equipDict']) if id not in set(dict.keys(curr_uniequip))]
    return_dict = {}
    for equip_id in new_equips:
        equip = cn_uniequip_table['equipDict'][equip_id]
        char_id = equip['charId']
        battle_equip = cn_battle_equip_table[equip_id] if equip_id in cn_battle_equip_table else None
        in_global = equip_id in en_battle_equip_table
        combat_data = None
        if battle_equip:
            phases = []
            blackboard = []
            for phase_idx, phase in enumerate(battle_equip['phases']):
                concise_parts = []
                for index, part in enumerate(phase['parts']):
                    if part['target'] not in ['TALENT', 'TALENT_DATA_ONLY', 'TRAIT', 'TRAIT_DATA_ONLY', 'DISPLAY']:
                        print(part['target'])
                    if 'TRAIT' in part['target'] or part['target'] == 'DISPLAY':
                        if part['addOrOverrideTalentDataBundle']['candidates'] is not None:
                            print('TRAIT or DISPLAY TalentDataBundle not NONE', equip_id)
                        max_candidate = part['overrideTraitDataBundle']['candidates'][-1]
                        max_candidate_en = en_battle_equip_table[equip_id][
                            'phases'][phase_idx]['parts'][index]['overrideTraitDataBundle']['candidates'][-1] if in_global else None
                        max_candidate_jp = jp_battle_equip_table[equip_id][
                            'phases'][phase_idx]['parts'][index]['overrideTraitDataBundle']['candidates'][-1] if in_global else None
                        if max_candidate['rangeId'] is not None:
                            print('TRAIT rangeId not NONE', equip_id)
                        concise_parts.append({
                            "resKey": part['resKey'],
                            "target": part['target'],
                            "isToken": part['isToken'],
                            "addDesc_zh": replace_substrings(max_candidate['additionalDescription'], max_candidate['blackboard']),
                            "addDesc_ja": replace_substrings(max_candidate_jp['additionalDescription'], max_candidate['blackboard']) if in_global else "",
                            "addDesc_en": replace_substrings(max_candidate_en['additionalDescription'], max_candidate['blackboard']) if in_global else "",
                            "overrideDesc_zh": replace_substrings(max_candidate['overrideDescripton'], max_candidate['blackboard']),
                            "overrideDesc_ja": replace_substrings(max_candidate_jp['overrideDescripton'], max_candidate['blackboard']) if in_global else "",
                            "overrideDesc_en": replace_substrings(max_candidate_en['overrideDescripton'], max_candidate['blackboard']) if in_global else ""
                        })
                        if phase_idx == 2:
                            blackboard = blackboard + max_candidate['blackboard']

                    if 'TALENT' in part['target']:
                        if part['overrideTraitDataBundle']['candidates'] is not None:
                            print('TALENT TraitDataBundle not NONE', equip_id)
                        max_candidate = part['addOrOverrideTalentDataBundle']['candidates'][-1]
                        max_candidate_en = en_battle_equip_table[equip_id][
                            'phases'][phase_idx]['parts'][index]['addOrOverrideTalentDataBundle']['candidates'][-1] if in_global else None
                        max_candidate_jp = jp_battle_equip_table[equip_id][
                            'phases'][phase_idx]['parts'][index]['addOrOverrideTalentDataBundle']['candidates'][-1] if in_global else None
                        if max_candidate['description'] is not None:
                            print('TALENT description not NONE', equip_id)

                        concise_parts.append({
                            "resKey": part['resKey'],
                            "target": part['target'],
                            "isToken": part['isToken'],
                            "name_zh": max_candidate['name'],
                            "name_ja": max_candidate_jp['name'] if in_global else "",
                            "name_en": max_candidate_en['name'] if in_global else "",
                            "displayRangeId": max_candidate['displayRangeId'],
                            "rangeId": max_candidate['rangeId'],
                            "talentIndex": max_candidate['talentIndex'],
                            "upgradeDesc_zh": replace_substrings(max_candidate['upgradeDescription'], max_candidate['blackboard']),
                            "upgradeDesc_ja": replace_substrings(max_candidate_jp['upgradeDescription'], max_candidate['blackboard']) if in_global else "",
                            "upgradeDesc_en": replace_substrings(max_candidate_en['upgradeDescription'], max_candidate['blackboard']) if in_global else "",
                        })

                        if phase_idx == 2:
                            blackboard = blackboard + max_candidate['blackboard']
                phases.append({
                    'parts': concise_parts,
                    'attributeBlackboard': phase['attributeBlackboard'],
                    'tokenAttributeBlackboard': phase['tokenAttributeBlackboard'],
                })
            combat_data = {
                'phases': phases,
                "tags": [],
                "blackboard": blackboard
            }

        return_dict[equip_id] = {
            "uniEquipId": equip['uniEquipId'],
            "name_zh": equip['uniEquipName'],
            "name_ja": "",
            "name_en": "",
            "typeIcon": equip['typeIcon'],
            'charId': char_id,
            "combatData": combat_data
        }
        if in_global:
            return_dict[equip_id]['name_ja'] = jp_uniequip_table['equipDict'][equip_id]['uniEquipName']
            return_dict[equip_id]['name_en'] = en_uniequip_table['equipDict'][equip_id]['uniEquipName']

    return_dict = curr_uniequip | return_dict

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(return_dict, f, ensure_ascii=False, indent=4)

    return {"name": "uniequip", "newEquips": len(new_equips)}

if __name__ == "__main__":
    from main import setup
    setup()
    update_uniequip()