import argparse
import json
import os
import sys

import utils.questlog as questlog
import utils.achievements as achiev
import utils.cooking as cooking
import utils.weapon as weapons
import utils.character as chara

def character(args, textmap):
    if args.ext:
        chara.batchCharaExtract(textmap)
    else:
        for ids in args.args:
            chara.characterExtraction(textmap, ids)

def weapon(args, textmap):
    if args.ext:
        weapons.batchWeaponExtract(textmap, args)
    else:
        for ids in args.args:
            weapons.weaponExtraction(textmap, ids, args)

def achievement(args, textmap):
    if args.ext:
        achiev.batchExtractAchievements(textmap, args)
    else:
        for orderID in args.args:
            achiev.categoryExtract(textmap, orderID, args)

def recipe(args, textmap):
    if args.ext:
        cooking.batchExtractRecipes(textmap, args)

def chapter(args, textmap):
    if args.ext:
        questlog.batchExtractChapters(textmap, args)
    else:
        for ids in args.args:
            # chapter debut ID (example) : 
            # chapter debug ID for recursion : 2010
            questlog.chapterLogger(textmap, ids, args)

def quest(args, textmap):
    if args.ext:
        questlog.batchExtractQuests(textmap, args)
    else:
        for ids in args.args:
            # quest debug ID for multiple choices ending : 309
            # quest debug ID for 5 choices : 396
            # quest debug ID for recursion : 426
            questlog.questLogger(textmap, ids, args)

def extractAll(args, textmap):
    print("Extracting every achievement... (1/6)")
    achiev.batchExtractAchievements(textmap, args)
    print("Extracting every weapon... (2/6)")
    weapons.batchWeaponExtract(textmap, args)
    print("Extracting every recipe... (3/6)")
    cooking.batchExtractRecipes(textmap, args)
    print("Extracting every character... (4/6)")
    chara.batchCharaExtract(textmap)
    print("Extracting every story chapter... (5/6)")
    questlog.batchExtractChapters(textmap, args)
    print("Extracting every quest... (6/6)")
    questlog.batchExtractQuests(textmap, args)
    print("Done. Extracted files are located in res/")

class argCollector(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        commandList = ['achievement', 'chapter', 'quest', 'recipe', 'character', 'weapon']
        ids = []
        setattr(namespace, 'rest', [])
        setattr(namespace, 'ext', False)

        for n, val in enumerate(values):
            if val in commandList:
                setattr(namespace, 'rest', values[n:])
                break
            elif val == 'all':    # If "all" is given, then all the corresponding objects are extracted. Therefore no ID is taken into account.
                setattr(namespace, 'ext', True)
                indexlist = -1
                for i, v in enumerate(values[n:]):  # Checking of a command is remaining in the argsList
                    if v in commandList:
                        indexlist = i
                        break
                if indexlist > -1:  # If a command is found in the remaining args
                    setattr(namespace, 'rest', values[(n+indexlist):])
                return
            elif isinstance(int(val), int):
                ids.append(int(val))
        setattr(namespace, self.dest, ids)
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lang", type=str, default='EN', choices=['CHR', 'CHT', 'DE', 'EN', 'ES', 'FR', 'ID', 'JA', 'KO', 'PT', 'RU', 'TH', 'VI'])
    parser.add_argument("-a", "--all", action="store_true", default=False)
    subparser = parser.add_subparsers(dest='cmd')

    parser_chapter = subparser.add_parser("chapter")
    parser_chapter.add_argument("args", nargs='*', action=argCollector)
    parser_chapter.set_defaults(func=chapter)

    parser_achiev = subparser.add_parser("achievement")
    parser_achiev.add_argument("args", nargs='*', action=argCollector)
    parser_achiev.set_defaults(func=achievement)

    parser_weapon = subparser.add_parser("weapon")
    parser_weapon.add_argument("args", nargs='*', action=argCollector)
    parser_weapon.set_defaults(func=weapon)

    parser_recipe = subparser.add_parser("recipe")
    parser_recipe.add_argument("args", nargs='*', action=argCollector)
    parser_recipe.set_defaults(func=recipe)

    parser_quest = subparser.add_parser("quest")
    parser_quest.add_argument("args", nargs='*', action=argCollector)
    parser_quest.set_defaults(func=quest)

    parser_chara = subparser.add_parser("character")
    parser_chara.add_argument("args", nargs='*', action=argCollector)
    parser_chara.set_defaults(func=character)

    rest = sys.argv
    rest.pop(0)
    # Ty https://stackoverflow.com/questions/25318622/python-argparse-run-one-or-more-sub-commands
    while rest:
        args = parser.parse_args(rest)

        with open(os.path.join(os.path.dirname(__file__), f'data/TextMap/Text{args.lang}.json')) as textmap_json:
            textmap = json.load(textmap_json)
            if args.all: # If the --all flag is specified, then we don't need to process the other arguments and we extract everything
                rest = []
                extractAll(args, textmap)
            else:
                rest = args.rest
                args.func(args, textmap)