from datetime import datetime, timezone
import os
import json
import gzip
from pathlib import Path
import requests
from typing import Any, Union


CACHE_DIR = 'cache'
_cache = {}

def get(name, url):
    if name in _cache:
        print(f"Using cached data for {name}")
        return _cache[name]
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{name}.json")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched data for {name}")
        _cache[name] = data
        return data
    except requests.RequestException as e:
        print(f"Error fetching data for {name}: {e}")
        if os.path.exists(cache_path):
            print(f"Using cached data for {name} from {cache_path}")
            with open(cache_path, 'r') as f:
                data = json.load(f)
            _cache[name] = data
            return data
        else:
            raise RuntimeError(f"Failed to fetch data for {name} and no cache available") from e

ReportType = dict[str, Any]
ReportInput = Union[ReportType, list[ReportType]]

class Report:
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    report_path = json_dir / 'report.json'
    latest_path = json_dir / 'latest_report.json'

    def __init__(self):
        self.current: list[ReportType] = []

    def append(self, *reports: ReportInput) -> None:
        for report in reports:
            if isinstance(report, dict):
                self.current.append(report)
            elif isinstance(report, list):
                self.current.extend(report)
            else:
                raise TypeError(f"Unsupported type for append: {type(report)}")

    def save(self, path: Path = report_path, latest_path: Path = latest_path) -> tuple[Path, Path]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                all_reports: dict[str, ReportType] = json.load(f)
        else:
            all_reports = {}

        for r in self.current:
            all_reports[r['name']] = {'timestamp': datetime.now(timezone.utc).isoformat(), **r}

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(all_reports, f, ensure_ascii=False, indent=2)

        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(self.current, f, ensure_ascii=False, indent=2)
        
        return path, latest_path
    
    @classmethod
    def singular(cls, *module_reports: ReportInput, path: Path = report_path, latest_path: Path = latest_path) -> None:
        report = cls()
        report.append(*module_reports)
        report.save(path, latest_path)


def split_characters_by_language(input_file='characters.json', languages=None, output_gz=True):
    if languages is None:
        languages = ['zh', 'ja', 'en']

    with open(input_file, encoding='utf-8') as f:
        chara_list = json.load(f)

    for lang in languages:
        data = []
        for chara_dict in chara_list:
            skills = []
            talents = []
            for skill in chara_dict['skills']:
                levels = []
                for level in skill['levels']:
                    level_options = {
                        "rangeId": level['rangeId'],
                        "desc": level.get(f'description_{lang}') or level.get('description_zh'),
                        "spData": level['spData'],
                        "duration": level['duration']
                    }
                    if 'rangeExtend' in level:
                        level_options['rangeExtend'] = level['rangeExtend']
                    levels.append(level_options)
                skills.append({"skillId": skill['skillId'],
                               "name": skill.get(f'name_{lang}') or skill.get('name_zh'),
                               "skillType": skill['skillType'],
                               "durationType": skill['durationType'],
                               'spType': skill['spType'],
                               "levels": levels,
                               "tags": skill['tags'],
                               "blackboard": skill['blackboard']})
            if chara_dict['talents']:
                for talent in chara_dict['talents']:
                    talent_holder = {
                        "prefabKey": talent["prefabKey"],
                        "name": talent.get(f'name_{lang}') or talent.get('name_zh'),
                        "desc": talent.get(f'desc_{lang}') or talent.get('desc_zh'),
                    }
                    talent_holder['rangeId'] = talent.get('rangeId')
                    talent_holder['tags'] = talent['tags']
                    talent_holder['blackboard'] = talent['blackboard']
                    talents.append(talent_holder)
            uniequip_list = []
            for equip in chara_dict['uniequip']:
                new_equip = {"uniEquipId": equip['uniEquipId'],
                             "name": equip.get(f'name_{lang}') or equip.get('name_zh'),
                             "typeIcon": equip['typeIcon'], "combatData": equip['combatData']}
                combatData = equip['combatData']
                if combatData:
                    phases = []
                    for phase in combatData['phases']:
                        concise_parts = []
                        for part in phase['parts']:
                            if 'TRAIT' in part['target'] or part['target'] == 'DISPLAY':
                                concise_parts.append({"resKey": part['resKey'], "target": part['target'], "isToken": part['isToken'],
                                                      "addDesc":  part.get(f'addDesc_{lang}') or part.get('addDesc_zh'),
                                                      "overrideDesc": part.get(f'overrideDesc_{lang}') or part.get('overrideDesc_zh')})

                            if 'TALENT' in part['target']:
                                concise_parts.append({"resKey": part['resKey'], "target": part['target'], "isToken": part['isToken'],
                                                      "name": part.get(f'name_{lang}') or part.get('name_zh'),
                                                      "displayRangeId": part['displayRangeId'], "rangeId": part['rangeId'], "talentIndex": part['talentIndex'],
                                                      "upgradeDesc": part.get(f'upgradeDesc_{lang}') or part.get('upgradeDesc_zh'),
                                                      })
                        phases.append(
                            {"parts": concise_parts, "attributeBlackboard": phase['attributeBlackboard'], "tokenAttributeBlackboard": phase['tokenAttributeBlackboard']})
                    new_equip['combatData'] = {
                        "phases": phases, "tags": combatData['tags'], "blackboard": combatData['blackboard']}
                uniequip_list.append(new_equip)
            uniequip_list.sort(key=lambda equip: equip['uniEquipId'])
            stats = chara_dict['stats']

            potential = []
            for pot in chara_dict['potential']:
                pot_dict = {"desc": pot.get(f'desc_{lang}') or pot.get('desc_zh'),
                            "attribute": pot['attribute']}
                potential.append(pot_dict)

            favor_data = chara_dict['favorData']

            tokens = []
            for token in chara_dict['tokens']:
                token_skills = []
                for skill in token['skills']:
                    spData = {
                        "maxChargeTime": skill['spData']['maxChargeTime'],
                        "spCost": skill['spData']['spCost'],
                        "initSp": skill['spData']['initSp'],
                        "increment": skill['spData']['increment']
                    }
                    token_skills.append({"skillId": skill['skillId'],
                                         "name": skill.get(f'name_{lang}') or skill.get('name_zh'),
                                         "iconId": skill["iconId"],
                                         "rangeId": skill['rangeId'],
                                         "desc": skill.get(f'desc_{lang}') or skill.get('desc_zh'),
                                         "skillType": skill['skillType'],
                                         "durationType": skill['durationType'],
                                         "spType": skill['spType'],
                                         'spData': spData})
                token_talents = []
                for talent in token['talents']:
                    talent_holder = {
                        "prefabKey": talent["prefabKey"],
                        "name": talent.get(f'name_{lang}') or talent.get('name_zh'),
                        "desc": talent.get(f'desc_{lang}') or talent.get('desc_zh'),
                    }
                    token_talents.append(talent_holder)
                token_dict = {"id": token['id'], "name": token.get(f'name_{lang}') or token.get('name_zh'),
                              "desc": token.get(f'desc_{lang}') or token.get('desc_zh'),
                              "position": token['position'],
                              "stats": token['stats'],
                              "tags": token['tags'], "blackboard": token['blackboard'],
                              "skills": token_skills,
                              "talents": token_talents}
                tokens.append(token_dict)

            tags = chara_dict['tags'][:]
            if not chara_dict.get('name_en'):
                tags.append("not_in_global")

            return_dict = {"id": chara_dict['id'], "appellation": chara_dict['appellation'],
                           "name": chara_dict.get(f'name_{lang}') or chara_dict.get('name_zh'),
                           "desc": chara_dict.get(f'desc_{lang}') or chara_dict.get('desc_zh'),
                           "release_time": chara_dict['release_time'],
                           "tags": tags, "blackboard": chara_dict['blackboard'],
                           "powers": chara_dict['powers'], "position": chara_dict['position'],
                           "isSpChar": chara_dict['isSpChar'], "rarity": chara_dict['rarity'],
                           "profession": chara_dict['profession'], "subProfessionId": chara_dict['subProfessionId'], "stats": stats,
                           'potential': potential, "favorData": favor_data, "tokens": tokens,
                           "skills": skills, "talents": talents, 'uniequip': uniequip_list, }
            data.append(return_dict)
        out_json = f'characters_{lang}.json'
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        if output_gz:
            json_to_gz(out_json, f'characters_{lang}.gz')


def json_to_gz(input_file, output_file=None):
    try:
        # Convert input path to Path object
        input_path = Path(input_file)
        
        # If output file not specified, use input filename with .gz extension
        if not output_file:
            output_file = str(input_path.with_suffix('.gz'))
            
        # Read JSON file with explicit UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Convert to JSON string with non-ASCII characters preserved
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        
        # Write to GZ file
        with gzip.open(output_file, 'wb') as f:
            f.write(json_bytes)
            
        return output_file
        
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
    except UnicodeDecodeError as e:
        print(f"Encoding error: {str(e)}")
        print("Make sure your input file is properly UTF-8 encoded")
    except Exception as e:
        print(f"Error: {str(e)}")
