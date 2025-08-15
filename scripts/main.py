from chara import update_characters
from chara_talents import update_chara_talents
from chara_skills import update_chara_skills
from uniequip import update_uniequip
from tokens import update_tokens
from recruitment import update_recruitment


def setup():
    print("Setting up environment...")

def main():
    setup()
    update_chara_skills()
    update_chara_talents()
    update_uniequip()
    update_tokens()
    update_recruitment()
    update_characters()

if __name__ == "__main__":
    main()