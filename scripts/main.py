from chara import update_characters
from chara_talents import update_chara_talents
from chara_skills import update_chara_skills
from uniequip import update_uniequip
from tokens import update_tokens
from recruitment import update_recruitment
from util import Report
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
    report.save(report_path, latest_path)

if __name__ == "__main__":
    main()