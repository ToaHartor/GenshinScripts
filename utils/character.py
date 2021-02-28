import json
import os
import re

def batchCharaExtract(textmap):
    files = {"AvatarExcelConfigData": {}, # Main character excel
            "AvatarCodexExcelConfigData": {}, # Release dates
            "AvatarLevelExcelConfigData": {}, # Character XP requirements
            "AvatarPromoteExcelConfigData": {}, # Character ascension buff
            "AvatarSkillDepotExcelConfigData": {}, # Bindings between main excel and Talents/Skills/Constellations
            "AvatarSkillExcelConfigData": {},  # Main Skill Excel
            "AvatarTalentExcelConfigData": {}, # Character Talents
            "AvatarCurveExcelConfigData": {}, # HP/ATK/DEF calculations
            "AvatarPromoteExcelConfigData": {}, # Ascension const
            "ProudSkillExcelConfigData": {}, # Skills
            "MaterialExcelConfigData": {},   # Material Excel
            "FetterInfoExcelConfigData": {},  # Character info
            "FetterStoryExcelConfigData": {},  # Character stories
            "FettersExcelConfigData": {}  # Character quotes
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    releaseCharaID = [char["AvatarId"] for char in files["AvatarCodexExcelConfigData"]]
    releasedAvatars = list(filter(lambda x: x["Id"] in releaseCharaID, files["AvatarExcelConfigData"]))

    length = len(releasedAvatars)

    for count, avatar in enumerate(releasedAvatars):
        print(f"[{avatar['Id']}] {textmap[str(avatar['NameTextMapHash'])]} ({count+1}/{length})")
        character(textmap, avatar['Id'], files)


def characterExtraction(textmap, charID):
    files = {"AvatarExcelConfigData": {}, # Main character excel
            "AvatarCodexExcelConfigData": {}, # Release dates
            "AvatarLevelExcelConfigData": {}, # Character XP requirements
            "AvatarPromoteExcelConfigData": {}, # Character ascension buff
            "AvatarSkillDepotExcelConfigData": {}, # Bindings between main excel and Talents/Skills/Constellations
            "AvatarSkillExcelConfigData": {},  # Main Skill Excel
            "AvatarTalentExcelConfigData": {}, # Character Talents
            "AvatarCurveExcelConfigData": {}, # HP/ATK/DEF calculations
            "AvatarPromoteExcelConfigData": {}, # Ascension const
            "ProudSkillExcelConfigData": {}, # Skills
            "MaterialExcelConfigData": {},   # Material Excel
            "FetterInfoExcelConfigData": {},  # Character info
            "FetterStoryExcelConfigData": {},  # Character stories
            "FettersExcelConfigData": {}  # Character quotes
            }

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    character(textmap, charID, files)

def character(textmap, charID, files):
    # Fix for Beidou, Keqing, Noelle
    correspondanceDict = {"charged attack cycling dmg": "charged attack spinning dmg",
                        "lightning stiletto dmg ": "lightning stiletto dmg",
                        "elemental burst dmg": "burst dmg"}

    avatarData = list(filter(lambda x: x['Id'] == charID, files["AvatarExcelConfigData"]))[0]

    # Main stats curves
    HPcurve = list(filter(lambda x: x['Type'] == "FIGHT_PROP_BASE_HP", avatarData["PropGrowCurves"]))[0]["GrowCurve"]
    ATKcurve = list(filter(lambda x: x['Type'] == "FIGHT_PROP_BASE_ATTACK", avatarData["PropGrowCurves"]))[0]["GrowCurve"]
    DEFcurve = list(filter(lambda x: x['Type'] == "FIGHT_PROP_BASE_DEFENSE", avatarData["PropGrowCurves"]))[0]["GrowCurve"]

    statmodifier = {"HP":{},
                "ATK":{},
                "DEF":{},
                "Ascension": []}

    for level in files["AvatarCurveExcelConfigData"]:
        statmodifier["HP"][str(level["Level"])] = list(filter(lambda x: x['Type'] == HPcurve, level["CurveInfos"]))[0]["Value"]
        statmodifier["ATK"][str(level["Level"])] = list(filter(lambda x: x['Type'] == ATKcurve, level["CurveInfos"]))[0]["Value"]
        statmodifier["DEF"][str(level["Level"])] = list(filter(lambda x: x['Type'] == DEFcurve, level["CurveInfos"]))[0]["Value"]

    materialsDict = {"Ascensions": [],
                    "Talents": []}

    # Retrieving Ascension constants

    promoteConsts = list(filter(lambda x: x['AvatarPromoteId'] == avatarData["AvatarPromoteId"] if "PromoteLevel" in x else None, files["AvatarPromoteExcelConfigData"]))
    promoteConsts = sorted(promoteConsts, key=lambda x: x['PromoteLevel'])
    # 
    for i, prom in enumerate(promoteConsts):
        ascDict = {}
        for stat in prom['AddProps']:
            ascDict[stat['PropType']] = stat['Value'] if 'Value' in stat else 0.0
        statmodifier["Ascension"].append(ascDict)

        # Materials
        materialsDict["Ascensions"].append({"Mats": [], "Cost": prom["ScoinCost"]})
        for mat in list(filter(None, prom["CostItems"])):
            # If mat dict isn't empty
            matData = list(filter(lambda x: x['Id'] == mat["Id"], files['MaterialExcelConfigData']))[0]
            dic = {"Name": textmap[str(matData["NameTextMapHash"])], "TextMapID": matData["NameTextMapHash"], "Count": mat["Count"]}
            materialsDict["Ascensions"][i]["Mats"].append(dic)

    # Corresponding character skill depot
    skillDepot = list(filter(lambda x: x['Id'] == avatarData['SkillDepotId'], files["AvatarSkillDepotExcelConfigData"]))[0]

    # Elemental burst skill ID -> skillDepot["EnergySkill"]
    # Other Skills
    skills = [i for i in skillDepot["Skills"] if i != 0]
    skills.append(skillDepot["EnergySkill"])

    # Retreiving skills
    skillsList = []
    for skillNum, sk in enumerate(skills):
        main = list(filter(lambda x: x['Id'] == sk, files["AvatarSkillExcelConfigData"]))[0]
        # Retrieving data for each skill level
        skillDetails = list(filter(lambda x: x['ProudSkillGroupId'] == main["ProudSkillGroupId"], files["ProudSkillExcelConfigData"]))
        skillDetails = sorted(skillDetails, key=lambda x:x['Level'])
        
        skillDict = {"Name": main["NameTextMapHash"],
                    "Desc": main["DescTextMapHash"],
                    "Param": {}}

        talentMatDict = []

        for count, skillLevel in enumerate(skillDetails):
            # Using a regex to filter the skill desc in the textmap to know how many parameters in ParamList correspond to the text.
            indexDesc, indexList = 0,0

            paramList = paramListCorrecter(skillLevel['ParamList'], charID, skillNum)

            while textmap[str(skillLevel['ParamDescList'][indexDesc])] != '':
                # Bugfix for normal attacks which use 5 hits instead of 6, the 6th would usually have a parameter of zero
                while paramList[indexList] == 0.0:
                    indexList += 1
                # Regex to find how many parameters correspond to the ParamDesc
                res = re.findall(r'(\{param.*?\})', textmap[str(skillLevel['ParamDescList'][indexDesc])])
                if res != None:
                    # Text without parameters will be our key
                    key = textmap[str(skillLevel['ParamDescList'][indexDesc])].split('|', 1)[0].lower()
                    # Correspondance bugfix
                    if key in correspondanceDict:
                        key = correspondanceDict[key]

                    if key not in skillDict["Param"]:
                        skillDict["Param"][key] = {"Name": skillLevel['ParamDescList'][indexDesc], "Levels": []}
                    # For parameters needed for a single description
                    paramlist = []
                    # If a param appears more than once (ex: Venti's normal attack)
                    oldparams = []
                    for i, par in enumerate(res):
                        # If we already used the said parameter, then we get its value from the list 
                        if par in oldparams:
                            ind = oldparams.index(par)
                            appParam = paramList[indexList-(i-ind)]
                        else:
                            appParam = paramList[indexList]
                            oldparams.append(par)
                            indexList += 1
                        paramlist.append(appParam)

                    skillDict["Param"][key]["Levels"].append(paramlist)
                indexDesc += 1
            matList = list(filter(None, skillLevel["CostItems"]))

            if len(matList) > 0:
                talentMatDict.append({"Mats": [], "Cost": skillLevel["CoinCost"]})
                for mat in matList:
                    matData = list(filter(lambda x: x['Id'] == mat["Id"], files['MaterialExcelConfigData']))[0]
                    dic = {"Name": textmap[str(matData["NameTextMapHash"])], "TextMapID": matData["NameTextMapHash"], "Count": mat["Count"]}
                    talentMatDict[count-1]["Mats"].append(dic)

        materialsDict["Talents"].append(talentMatDict)
        skillsList.append(skillDict)

    # Passives Skills
    passiveskills = list(filter(None, skillDepot['InherentProudSkillOpens']))
    passList = []
    for pas in passiveskills:
        skill = list(filter(lambda x: x['ProudSkillGroupId'] == pas['ProudSkillGroupId'], files['ProudSkillExcelConfigData']))[0]
        dic = {"Name": skill["NameTextMapHash"],
            "Desc": skill["DescTextMapHash"],
            "Unlock": pas['NeedAvatarPromoteLevel'] if 'NeedAvatarPromoteLevel' in pas else 0
        }
        passList.append(dic)

    # Constellations
    constellations = []
    for cons in sorted(skillDepot["Talents"]):
        data = list(filter(lambda x: x['TalentId'] == cons, files['AvatarTalentExcelConfigData']))[0]
        dic = {"Name": data["NameTextMapHash"],
            "Desc": data["DescTextMapHash"]}
        constellations.append(dic)

    # Character info
    charaData = list(filter(lambda x: x['AvatarId'] == avatarData['Id'], files['FetterInfoExcelConfigData']))[0]
    storyData = list(filter(lambda x: x['AvatarId'] == avatarData['Id'], files['FetterStoryExcelConfigData']))
    storyData = sorted(storyData, key=lambda x: x['FetterId'])

    storyList = []
    for story in storyData:
        dic = {"Title": story["StoryTitleTextMapHash"],
                "Text": story["StoryContextTextMapHash"],
                "Unlock": story["Tips"]}
        storyList.append(dic)

    quotesData = list(filter(lambda x: x['AvatarId'] == avatarData['Id'], files['FettersExcelConfigData']))
    quotesData = sorted(quotesData, key=lambda x: x['FetterId'])

    quotesList = []
    for quote in quotesData:
        dic = {"Title": quote["VoiceTitleTextMapHash"],
                "Text": quote["VoiceFileTextTextMapHash"]}
        quotesList.append(dic)

    codexData = list(filter(lambda x: x['AvatarId'] == avatarData['Id'], files['AvatarCodexExcelConfigData']))[0]

    charainfo = {"Release Date": codexData["BeginTime"],
                "Birth": [charaData['InfoBirthMonth'],charaData['InfoBirthDay']],
                "Vision": charaData['AvatarVisionBeforTextMapHash'],
                "Constellation": charaData['AvatarConstellationBeforTextMapHash'],
                "Region": charaData['AvatarAssocType'],
                "VA": {
                    "Chinese": charaData['CvChineseTextMapHash'],
                    "Japanese": charaData['CvJapaneseTextMapHash'],
                    "English": charaData['CvEnglishTextMapHash'],
                    "Korean": charaData['CvKoreanTextMapHash']
                },
                "Stories": storyList,
                "Quotes": quotesList}

    json_dict = {
        "Name": avatarData["NameTextMapHash"],
        "Desc": avatarData["DescTextMapHash"],
        "CharaInfo": charainfo,
        "Weapon": avatarData["WeaponType"],
        "Rarity": avatarData["QualityType"],
        "StaminaRecovery": avatarData["StaminaRecoverSpeed"],
        "BaseHP": avatarData["HpBase"],
        "BaseATK": avatarData["AttackBase"],
        "BaseDEF": avatarData["DefenseBase"],
        "CritRate": avatarData["Critical"],
        "CritDMG": avatarData["CriticalHurt"],
        "StatsModifier": statmodifier,
        "Skills": skillsList,
        "Passives": passList,
        "Constellations": constellations,
        "Materials": materialsDict
    }
    # print(json_dict)
    with open(os.path.join(os.path.dirname(__file__), f'../res/{textmap[str(avatarData["NameTextMapHash"])]}.json'), 'w') as output_file:
        json.dump(json_dict, output_file)

# A hardcoded function which corrects the paramList of some skills
def paramListCorrecter(paramList, charaID, skillNum):
    # Amber
    if charaID == 10000021:
        # Elemental Skill
        if skillNum == 1:
            paramList.pop(2)
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(1, paramList.pop(3))
            paramList.insert(2, paramList.pop(4))
    # Barbara's Elemental Skill
    elif charaID == 10000014 and skillNum == 1:
        paramList.insert(0, paramList.pop(2))
        paramList.insert(1, paramList.pop(3))
    # Chongyun's Elemental Skill
    elif charaID == 10000036 and skillNum == 1:
        paramList.insert(2, paramList.pop(3))
    # Diona
    elif charaID == 10000039:
        # Elemental Skill
        if skillNum == 1:
            paramList.insert(3, paramList.pop(5))
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(4, paramList.pop(6))
    # Klee
    elif charaID == 10000029:
        # Elemental Skill
        if skillNum == 1:
            paramList.pop(1)
            paramList.pop(1)
        # Elemental Burst
        elif skillNum == 2:
            paramList.insert(1, paramList.pop(4))
            paramList.pop(4)
    # Lisa's Elemental Skill
    elif charaID == 10000006 and skillNum == 1:
        paramList.insert(0, paramList.pop(5))
        paramList.insert(1, paramList.pop(6))
    # Mona's Elemental Burst
    elif charaID == 10000041 and skillNum == 2:
        paramList.insert(2, paramList.pop(9))
        paramList.pop(3)
    # Ningguang's Elemental Skill
    elif charaID == 10000027 and skillNum == 1:
        paramList.pop(0)
        paramList.insert(0, paramList.pop(1))
    # Noelle's Elemental Skill
    elif charaID == 10000034 and skillNum == 1:
        paramList.insert(0, paramList.pop(5))
        paramList.insert(2, paramList.pop(6))
        paramList.insert(4, paramList.pop(7))
    # Qiqi
    elif charaID == 10000035:
        if skillNum == 1:
            paramList.insert(0, paramList.pop(7))
        elif skillNum == 2:
            paramList.insert(0, paramList.pop(2))
    # Tartaglia
    elif charaID == 10000033:
        # Normal Attack
        if skillNum == 0:
            paramList.insert(10, paramList.pop(13))
        # Elemental Skill
        elif skillNum == 1:
            paramList.insert(10, paramList.pop(11))
    # Xinyan's Elemental Burst
    elif charaID == 10000044 and skillNum == 2:
        paramList.insert(2, paramList.pop(4))

    return paramList