from scripts.chara import update_characters
from scripts.chara_talents import update_chara_talents
from scripts.chara_skills import update_chara_skills
from scripts.uniequip import update_uniequip
from scripts.tokens import update_tokens
from scripts.recruitment import update_recruitment
from scripts.util import Report, split_characters_by_language
from pathlib import Path

def main():
    script_dir = Path(__file__).parent
    json_dir = script_dir.parent / 'json'
    report_path = json_dir / 'report.json'
    latest_path = json_dir / 'latest_report.json'
    report = Report()
    report.append(update_chara_skills())
    report.append(update_chara_talents())
    report.append(update_uniequip())
    report.append(update_tokens())
    report.append(update_recruitment())
    report.append(update_characters())
    split_characters_by_language(input_file=json_dir / 'characters.json', languages=['zh', 'ja', 'en'], output_gz=True)
    report.save(report_path, latest_path)

if __name__ == "__main__":
    main()