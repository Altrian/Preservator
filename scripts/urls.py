from dataclasses import dataclass, field

@dataclass
class URLPatterns:
    server: str
    BASE: str = "https://raw.githubusercontent.com/"
    REPO: str = "ArknightsAssets/ArknightsGamedata/"
    BRANCH: str = "refs/heads/master/"
    

    char_table: str = field(init=False)
    patch_table: str = field(init=False)
    skill_table: str = field(init=False)
    uniequip_table: str = field(init=False)
    battle_equip_table: str = field(init=False)
    handbook_info_table: str = field(init=False)
    handbook_team_table: str = field(init=False)
    gacha_table: str = field(init=False)

    def __post_init__(self):
        prefix = f"{self.BASE}{self.REPO}{self.BRANCH}{self.server}/gamedata/excel/"
        self.char_table = f"{prefix}character_table.json"
        self.patch_table = f"{prefix}patch_table.json"
        self.skill_table = f"{prefix}skill_table.json"
        self.uniequip_table = f"{prefix}uniequip_table.json"
        self.battle_equip_table = f"{prefix}battle_equip_table.json"
        self.handbook_info_table = f"{prefix}handbook_info_table.json"
        self.handbook_team_table = f"{prefix}handbook_team_table.json"
        self.gacha_table = f"{prefix}gacha_table.json"
    
cn_urls = URLPatterns(server="cn")
jp_urls = URLPatterns(server="jp")
en_urls = URLPatterns(server="en")