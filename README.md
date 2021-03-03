# [WIP] GenshinScripts

A collection of scripts to be used with the data from https://github.com/Dimbreath/GenshinData (huge thanks to them btw)

## What can these scripts generate ?

- Quests (Daily commissions and World Quests) and Chapters (Archon, Story and Event Quests) (.txt)
- Cooking recipes (.txt)
- Achievements (.txt)
- Characters (.json with textmap IDs)
- Weapons (.json with textmap IDs)

And more to come...

## Requirements

- Python 3.9+

## How to use it

- Python 3.9+ should be installed
- Download the data from https://github.com/Dimbreath/GenshinData and extract it in a data/ folder at the root of the project.
- The files structure should look like this :
```
GenshinScripts/     (main folder)
├── data/             (from Dimbreath/GenshinData)
│   ├── Excel/
│   │   ├── _.json
│   │   ...
│   ├── Readable/       (books and items descriptions)
│   │   ├── {lang}/...
│   │   ...
│   └── TextMap/
│       ├──text_.json
│       ...
├── res/            (folder containing the generated files)
├── utils/
│   ├── _.py
│   ...
├── main.py
└── README.md
```

## Usage and examples

- `main.py` can be used with the parameter `--lang EN|FR|JP|....` to change the language of the files generated (with EN being the default language) 
- `main.py --lang EN --all` will generate all the files in English (`--all` flag can only be used alone)

To extract specific files, it's possible to use the subcommands `{achievement,chapter,weapon,recipe,quest,character}` followed by specific IDs :

- `achievement` requires an order ID of the achievement category (`OrderId` in `AchievementGoalExcelConfigData.json`)
- `chapter` requires a chapter ID (`Id` in `ChapterExcelConfigData.json`)
- `weapon` requires a weapon ID (`Id` in `WeaponExcelConfigData.json`)
- `recipe` only uses the `all` argument, since all the recipes are written in a single file
- `quest` requires a quest ID (`Id` in `MainQuestExcelConfigData.json`)
- `character` requires a character ID (`Id` in `AvatarExcelConfigData.json`)

It's also possible to use the `all` keyword to extract every possible files for a subcommand.

Complete example :

- `main.py --lang JP achievement 1 2 3 chapters 1001 weapon all` will generate the files in Japanese, for the achievements with `OrderId`s 1, 2 and 3, the chapter with the `Id` 1001 and files for every weapon.


