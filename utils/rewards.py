import json
import os

def rewardLogger(textmap, rewardID):
    files = {"RewardExcelConfigData": {},
            "MaterialExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)
    
    rewardsFormatter(textmap, files, rewardID)

def rewardsFormatter(textmap, files, rewardID):

    rewardData = list(filter(lambda x: x['RewardId'] == rewardID, files['RewardExcelConfigData']))
    if len(rewardData) == 0:
        return ''
    
    rewardData = rewardData[0]
    # Removing empty dicts in list
    rewardList = list(filter(None, rewardData["RewardItemList"]))
    text = ''
    for reward in rewardList:
        materialData = list(filter(lambda x: x['Id'] == reward["ItemId"], files['MaterialExcelConfigData']))
        # Bugfix for questID=307 which rewards a weapon
        if len(materialData) == 0:
            weapon = json.load(open(os.path.join(os.path.dirname(__file__), f'../data/Excel/WeaponExcelConfigData.json')))
            weaponreward = list(filter(lambda x: x['Id'] == reward["ItemId"], weapon))
            # Bugfix for questID=21003 which rewards an artifact
            if len(weaponreward) == 0:
                artifact = json.load(open(os.path.join(os.path.dirname(__file__), f'../data/Excel/ReliquaryExcelConfigData.json')))
                artifactreward = list(filter(lambda x: x['Id'] == reward["ItemId"], artifact))
                name = artifactreward[0]['NameTextMapHash']
            else:
                name = weaponreward[0]["NameTextMapHash"]
        else:
            name = materialData[0]["NameTextMapHash"]
        text += f'{textmap[str(name)]} x{reward["ItemCount"]}, '

    return text[:-2]