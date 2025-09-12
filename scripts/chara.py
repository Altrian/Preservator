import re
import json
from pathlib import Path
from util import get, Report, fetch_release_date
from chara_skills import replace_substrings
from urls import cn_urls, jp_urls, en_urls


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

def update_characters():

    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    output_path = json_dir / 'characters.json'
    output_read_path = json_dir / 'characters_read.json'

    chara_skills_path = json_dir / 'chara_skills.json'
    chara_talents_path = json_dir / 'chara_talents.json'
    uniequip_path = json_dir / 'uniequip.json'
    tokens_path = json_dir / 'tokens.json'
    imple_dates_path = json_dir / 'chara_imple_dates.json'
    recruitment_table_path = json_dir / 'recruitment_table.json'
    recruitment_path = output_recruitment_path = json_dir / 'recruitment.json'

    # base_url_cn = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master"
    # base_url_global = "https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData_YoStar/main"

    # cn_char_table = get("cn_char_table", f"{base_url_cn}/zh_CN/gamedata/excel/character_table.json")
    # jp_char_table = get("jp_char_table", f"{base_url_global}/ja_JP/gamedata/excel/character_table.json")
    # en_char_table = get("en_char_table", f"{base_url_global}/en_US/gamedata/excel/character_table.json")
    # cn_patch_table = get("cn_patch_table", f"{base_url_cn}/zh_CN/gamedata/excel/char_patch_table.json")
    # jp_patch_table = get("jp_patch_table", f"{base_url_global}/ja_JP/gamedata/excel/char_patch_table.json")
    # en_patch_table = get("en_patch_table", f"{base_url_global}/en_US/gamedata/excel/char_patch_table.json")
    # cn_handbook_info_table = get("cn_handbook_info_table", f"{base_url_cn}/zh_CN/gamedata/excel/handbook_info_table.json")
    # jp_handbook_info_table = get("jp_handbook_info_table", f"{base_url_global}/ja_JP/gamedata/excel/handbook_info_table.json")
    # en_handbook_info_table = get("en_handbook_info_table", f"{base_url_global}/en_US/gamedata/excel/handbook_info_table.json")

    cn_char_table = get("cn_char_table", cn_urls.char_table)
    jp_char_table = get("jp_char_table", jp_urls.char_table)
    en_char_table = get("en_char_table", en_urls.char_table)
    cn_patch_table = get("cn_patch_table", cn_urls.char_patch_table)
    jp_patch_table = get("jp_patch_table", jp_urls.char_patch_table)
    en_patch_table = get("en_patch_table", en_urls.char_patch_table)
    cn_handbook_info_table = get("cn_handbook_info_table", cn_urls.handbook_info_table)
    jp_handbook_info_table = get("jp_handbook_info_table", jp_urls.handbook_info_table)
    en_handbook_info_table = get("en_handbook_info_table", en_urls.handbook_info_table)
    
    with open(output_read_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    with open(chara_skills_path, encoding='utf-8') as f:
        chara_skills = json.load(f)
    with open(chara_talents_path, encoding='utf-8') as f:
        chara_talents = json.load(f)
    with open(uniequip_path, encoding='utf-8') as f:
        uniequip_dict = json.load(f)
    with open(tokens_path, encoding='utf-8') as f:
        tokens_dict = json.load(f)
    with open(imple_dates_path, encoding='utf-8') as f:
        imple_dates = json.load(f)
    with open(recruitment_table_path, encoding='utf-8') as f:
        recruitment_dict = json.load(f)
    with open(recruitment_path, encoding='utf-8') as f:
        recruitment_utilities = json.load(f)

    data = {}
    character_report = {}

    KEYS_TO_IGNORE = ["char_512_aprot", "char_600_cpione", "char_601_cguard",
                      "char_602_cdfend", "char_603_csnipe", "char_604_ccast",
                      "char_605_cmedic", "char_606_csuppo", "char_607_cspec",
                      "char_608_acpion", "char_609_acguad", "char_610_acfend",
                      "char_611_acnipe", "char_612_accast", "char_613_acmedc",
                      "char_614_acsupo", "char_615_acspec"]

    filtered_cn_char_table = {key: cn_char_table[key] for key in cn_char_table.keys(
    ) if "token" not in key and "trap" not in key and key not in KEYS_TO_IGNORE}

    for id, character_dict in filtered_cn_char_table.items():
        in_global = id in en_char_table
        if id not in existing_data:
            character_report.setdefault("new characters added", []).append(character_dict['appellation'])
        if id in existing_data and not in_global:
            character_report.setdefault("characters exclusive in China", []).append(character_dict['appellation'])
        if id in existing_data and in_global and existing_data[id]['name']['en'] == "":
            character_report.setdefault("characters arrived in Global", []).append(character_dict['appellation'])

        # Handle release date
        release_date = imple_dates.get(id, 0)
        if release_date == 0:
            release_date_dict = fetch_release_date(character_dict['name'])
            if release_date_dict['success']:
                imple_dates[id] = release_date_dict['timestamp']
                release_date = release_date_dict['timestamp']
                character_report.setdefault("release date added", []).append(f"{character_dict['appellation']}: {release_date_dict['raw']}")
            else:
                print(f"Warning: Release date not found for {character_dict['appellation']}\nError: {release_date_dict['error']}")
                character_report.setdefault("release date not found", []).append(character_dict['appellation'])
                
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

        if character_dict.get('talents') is not None:
            for talent_index, talent in enumerate(character_dict['talents']):
                max_candidate_index = len(talent['candidates']) - 1
                maxed_talent = talent['candidates'][max_candidate_index]
                if maxed_talent.get('name') is None:
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
        if character_dict.get('favorKeyFrames') is not None:
            favor_last = character_dict['favorKeyFrames'][-1]['data']
            for stat, value in favor_last.items():
                if stat in STAT_CONVERT and bool(value):
                    favor_data[STAT_CONVERT[stat]] = value
        
        # Handle tokens
        tokens = []
        if character_dict.get('displayTokenDict') is not None:
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
        powers_list = character_dict.get('subPower', [])
        powers_list.append(character_dict['mainPower'])
        for power in powers_list:
            if power.get('nationId') is not None:
                powers.append(power['nationId'])
            if power.get('groupId') is not None: 
                powers.append(power['groupId'])
            if power.get('teamId') is not None: 
                powers.append(power['teamId'])

        # Handle gender, birthplace, race from handbook
        gender = {"zh": "", "ja": "", "en": ""}
        birthplace = {"zh": "", "ja": "", "en": ""}
        race = {"zh": "", "ja": "", "en": ""}
        def extract_handbook_info(text, keys):
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
            gender['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['zh'])
            if in_global:
                gender['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['ja'])
                gender['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['gender']['en'])
            if not gender['zh']:
                print(f"Warning: Gender information is missing for character ID {id}")
            birthplace['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['zh'])
            if in_global:
                birthplace['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['ja'])
                birthplace['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['birthplace']['en'])
            if not birthplace['zh']:
                print(f"Warning: Birthplace information is missing for character ID {id}")
            if "种族" not in cn_handbook_info:
                race['zh'] = "其他"
                race['ja'] = "その他"
                race['en'] = "Others"
            else:
                race['zh'] = extract_handbook_info(cn_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['zh'])
                if in_global:
                    race['ja'] = extract_handbook_info(jp_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['ja'])
                    race['en'] = extract_handbook_info(en_handbook_info, HANDBOOK_INFO_EXTRACT_TABLE['race']['en'])

        recruitment = None
        recruitment_info = recruitment_dict.get(id, None)
        if recruitment_info is not None:
            recruitment = True if recruitment_info['IsRecruitOnly'] else False

        if recruitment_utilities['branch']['data'].get(character_dict['profession']) is None:
            recruitment_utilities['branch']['data'][character_dict['profession']] = []
            character_report.setdefault("new profession added", []).append(character_dict['profession'])
        if not (any(branch['id'] == character_dict['subProfessionId'] for branch in recruitment_utilities['branch']['data'][character_dict['profession']])):
            recruitment_utilities['branch']['data'][character_dict['profession']].append(
                {"id": character_dict['subProfessionId'], "name": {"zh": "", "ja": "", "en": ""}})
            character_report.setdefault("new subprofession added", []).append(f"{character_dict['subProfessionId']} ({character_dict['profession']})")

        result_dict = {"id": id, "appellation": character_dict['appellation'],
                       "releaseDate": imple_dates.get(id, 0),
                       "name": {"zh": character_dict['name'], "ja": "", "en": ""},
                       "desc": {"zh": desc_zh, "ja": "", "en": ""},  
                       "gender": gender, "birthplace": birthplace, "race": race, "powers": powers,
                       "position": character_dict['position'], "isSpChar": character_dict['isSpChar'],
                       "rarity": character_dict['rarity'], "profession": character_dict['profession'], "subProfessionId": character_dict['subProfessionId'],
                       "recruitment": recruitment, "tagList": character_dict['tagList'],
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

        if character_dict.get('talents') is not None:
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
        if character_dict.get('favorKeyFrames') is not None:
            favor_last = character_dict['favorKeyFrames'][-1]['data']
            for stat, value in favor_last.items():
                if stat in STAT_CONVERT and bool(value):
                    favor_data[STAT_CONVERT[stat]] = value

        # Handle tokens
        tokens = []
        if character_dict.get('displayTokenDict') is not None:
            tokens = [tokens_dict[key] for key in character_dict['displayTokenDict']]

        # Handle nationality and affiliations
        powers = []
        powers_list = character_dict.get('subPower', [])
        powers_list.append(character_dict['mainPower'])
        for power in powers_list:
            if power.get('nationId') is not None:
                powers.append(power['nationId'])
            if power.get('groupId') is not None: 
                powers.append(power['groupId'])
            if power.get('teamId') is not None: 
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

        recruitment = None
        recruitment_info = recruitment_dict.get(id, None)
        if recruitment_info is not None:
            recruitment = True if recruitment_info['IsRecruitOnly'] else False

        desc_zh = character_dict['description'].replace("<$ba", "<ba")

        result_dict = {"id": id, "appellation": character_dict['appellation'],
                       "releaseDate": release_date,
                       "name": {"zh": character_dict['name'], "ja": "", "en": ""},
                       "desc": {"zh": desc_zh, "ja": "", "en": ""},  
                       "gender": gender, "birthplace": birthplace, "race": race, "powers": powers,
                       "position": character_dict['position'], "isSpChar": character_dict['isSpChar'],
                       "rarity": character_dict['rarity'], "profession": character_dict['profession'], "subProfessionId": character_dict['subProfessionId'],
                       "recruitment": recruitment, "tagList": character_dict['tagList'],
                       "stats": stats_list, "potential": potential_list, 
                       "favorData": favor_data, "tokens": tokens,
                       "skills": skills, "talents": talents, "uniequip": uniequip_list}
        
        if in_global:
            result_dict["name"]['ja'] = jp_patch_table['patchChars'][id]['name']
            result_dict["name"]['en'] = en_patch_table['patchChars'][id]['name']
            result_dict["desc"]['ja'] = jp_patch_table['patchChars'][id]['description'].replace("<$ba", "<ba")
            result_dict["desc"]['en'] = en_patch_table['patchChars'][id]['description'].replace("<$ba", "<ba")
        data[id] = result_dict

    with open(output_read_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(list(data.values()), f, ensure_ascii=False, separators=(',', ':'))

    with open(output_recruitment_path, 'w', encoding='utf-8') as f:
        json.dump(recruitment_utilities, f, ensure_ascii=False, indent=4)

    return {"name": "characters", "records":character_report}


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    report_path = json_dir / 'report.json'
    latest_path = json_dir / 'latest_report.json'
    Report.singular(update_characters(), path=report_path, latest_path=latest_path)
    
