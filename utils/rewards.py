import json
import os

def rewardsFormatter(textmap, rewardID):
    files = {"RewardExcelConfigData": {},
            "MaterialExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    rewardData = list(filter(lambda x: x['RewardId'] == rewardID, files['RewardExcelConfigData']))
    if len(rewardData) == 0:
        return ''
    
    rewardData = rewardData[0]
    # Removing empty dicts in list
    rewardList = list(filter(None, rewardData["RewardItemList"]))

    text = ''
    for reward in rewardList:
        materialData = list(filter(lambda x: x['Id'] == reward["ItemId"], files['MaterialExcelConfigData']))[0]
        text += f'{textmap[str(materialData["NameTextMapHash"])]} x{reward["ItemCount"]}, '

    return text[:-2]