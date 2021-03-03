import json
import os
from pathlib import Path


def batchWeaponExtract(textmap, args):
    files = {"WeaponExcelConfigData": {},  # Main stats
            "WeaponCurveExcelConfigData": {},  # Stats curves
            "WeaponPromoteExcelConfigData": {}, # Weapon Ascension
            "WeaponLevelExcelConfigData": {},  # Level stats
            "MaterialExcelConfigData": {} # Materials
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    availableWeapons = list(filter(lambda x: textmap[str(x["NameTextMapHash"])] != "", files["WeaponExcelConfigData"]))
    length = len(availableWeapons)

    for count, w in enumerate(availableWeapons):
        print(f"[{w['Id']}] {textmap[str(w['NameTextMapHash'])]} ({count+1}/{length})")
        weapon(textmap, w['Id'], files, args)

def weaponExtraction(textmap, weaponID, args):
    files = {"WeaponExcelConfigData": {},  # Main stats
            "WeaponCurveExcelConfigData": {},  # Stats curves
            "WeaponPromoteExcelConfigData": {}, # Weapon Ascension
            "WeaponLevelExcelConfigData": {},  # Level stats
            "MaterialExcelConfigData": {} # Materials
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    weapon(textmap, weaponID, files, args)

def weapon(textmap, weaponID, files, args):

    weaponData = list(filter(lambda x: x['Id'] == weaponID, files["WeaponExcelConfigData"]))[0]

    # Stats
    weaponStats = {"ATK": {"Base": weaponData["WeaponProp"][0]["InitValue"],
                            "Levels": {}}}
    curves = [weaponData["WeaponProp"][0]["Type"]]

    # In case there is a substat (not the case for 1* and 2* weapons)
    if "PropType" in weaponData["WeaponProp"][1]:
        weaponStats[weaponData["WeaponProp"][1]["PropType"]] = {"Base": weaponData["WeaponProp"][1]["InitValue"], "Levels": {}}
        curves.append(weaponData["WeaponProp"][1]["Type"])

    for level in files["WeaponCurveExcelConfigData"]:
        for i, stat in enumerate(weaponStats):
            weaponStats[stat]["Levels"][level["Level"]] = list(filter(lambda x: x["Type"] == curves[i], level["CurveInfos"]))[0]["Value"]

    #XP requirements
    requiredXP = {}
    for level in files["WeaponLevelExcelConfigData"]:
        requiredXP[level["Level"]] = level["RequiredExps"][weaponData["RankLevel"] - 1]

    # Weapon Ascension
    ascensionData = list(filter(lambda x: x["WeaponPromoteId"] == weaponData["WeaponPromoteId"] if "PromoteLevel" in x else None, files["WeaponPromoteExcelConfigData"]))
    ascensionData = sorted(ascensionData, key=lambda x: x["PromoteLevel"])

    ascensionDict = {}
    ascMats = {}
    for asc in ascensionData:
        stat = list(filter(lambda x: "Value" in x, asc["AddProps"]))[0]
        ascensionDict[asc["PromoteLevel"]] = {}
        ascensionDict[asc["PromoteLevel"]][stat["PropType"]] = stat["Value"]
        ascMats[asc["PromoteLevel"]] = { "Mats": [], "Cost": asc["CoinCost"] if "CoinCost" in asc else 0}

        for mat in list(filter(None, asc["CostItems"])):
            # If mat dict isn't empty
            matData = list(filter(lambda x: x['Id'] == mat["Id"], files['MaterialExcelConfigData']))[0]
            dic = {"Name": textmap[str(matData["NameTextMapHash"])], "TextMapID": matData["NameTextMapHash"], "Count": mat["Count"]}
            ascMats[asc["PromoteLevel"]]["Mats"].append(dic)

    json_dict = {
        "Name": weaponData["NameTextMapHash"],
        "Desc": weaponData["DescTextMapHash"],
        "WeaponType": weaponData["WeaponType"],
        "Rarity": weaponData["RankLevel"],
        "StatsModifier": weaponStats,
        "XPRequirements": requiredXP,
        "Ascension": ascensionDict,
        "Materials": ascMats,
        "StoryFile": f"Weapon{weaponID}"
    }
    Path("res/Weapon/").mkdir(parents=True, exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), f'../res/Weapon/{textmap[str(weaponData["NameTextMapHash"])]} [{weaponID}].json'), 'w') as output_file:
        json.dump(json_dict, output_file)