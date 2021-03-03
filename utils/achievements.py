import json
import os

from pathlib import Path

import utils.rewards as rewards

def batchExtractAchievements(textmap, args):
    excelData = json.load(open(os.path.join(os.path.dirname(__file__), f'../data/Excel/AchievementGoalExcelConfigData.json')))
    excelData = sorted(excelData, key=lambda x: x['OrderId'])

    length = len(excelData)

    for count, category in enumerate(excelData):
        print(f'Achievement category ({count+1}/{length})')
        categoryExtract(textmap, category['OrderId'], args)

def categoryExtract(textmap, catOrderID, args):
    files = {"AchievementGoalExcelConfigData": {},
            "AchievementExcelConfigData": {},
            "RewardExcelConfigData": {},
            "MaterialExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    category = list(filter(lambda x: x['OrderId'] == catOrderID, files["AchievementGoalExcelConfigData"]))[0]

    categoryAchievements = list(filter(lambda x: x['GoalId'] == category['Id'] if ('GoalId' in x and category['OrderId'] > 1) else ('GoalId' not in x and category['OrderId'] == 1), files["AchievementExcelConfigData"]))
    categoryAchievements = sorted(categoryAchievements, key=lambda i: i['OrderId'])
    
    length = len(categoryAchievements)

    Path("res/Achievement/").mkdir(parents=True, exist_ok=True)
    with open(os.path.join(f'res/Achievement/{textmap["4154938841"]} - {textmap[str(category["NameTextMapHash"])]} [{catOrderID}] - {args.lang}.txt'), 'w') as file:
        print(f'[{catOrderID}] Achievements : {textmap[str(category["NameTextMapHash"])]}')
        file.write(f'{textmap["4154938841"]} : {textmap[str(category["NameTextMapHash"])]}\n\n')
        file.write(f'{textmap["276798818"]} : {rewards.rewardsFormatter(textmap, {"RewardExcelConfigData": files["RewardExcelConfigData"], "MaterialExcelConfigData": files["MaterialExcelConfigData"]}, category["FinishRewardId"])}\n' if "FinishRewardId" in category else "\n")
        file.write("\n================================\n\n")
        for count, ach in enumerate(categoryAchievements):
            print(f"[{ach['Id']}] Achievement progress: ({count+1}/{length})")
            achievement(textmap, ach, files, file)

def achievement(textmap, ach, files, file):
    file.write(f'[{ach["Id"]}] {textmap[str(ach["TitleTextMapHash"])]}\n\n')
    file.write(f'{textmap[str(ach["DescTextMapHash"])]}\n\n')
    file.write(f'{textmap["276798818"]} : {rewards.rewardsFormatter(textmap, {"RewardExcelConfigData": files["RewardExcelConfigData"], "MaterialExcelConfigData": files["MaterialExcelConfigData"]}, ach["FinishRewardId"])}\n')
    file.write("\n\n================================\n\n")