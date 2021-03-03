import json
import os 

from pathlib import Path

def batchExtractRecipes(textmap, args):
    files = {"MaterialExcelConfigData": {},
            "CookBonusExcelConfigData": {},
            "CookRecipeExcelConfigData": {},
            "AvatarExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)
    
    Path("res/Recipe/").mkdir(parents=True, exist_ok=True)
    with open(os.path.join(f'res/Recipe/{textmap["4091925326"]} - {args.lang}.txt'), 'w') as file:
        length = len(files["CookRecipeExcelConfigData"])
        for count, recipeData in enumerate(files["CookRecipeExcelConfigData"]):
            print(f'[{recipeData["Id"]}] Recipe ({count+1}/{length}) : {textmap[str(recipeData["NameTextMapHash"])]}')
            file.write(f'[{recipeData["Id"]}] {textmap[str(recipeData["NameTextMapHash"])]} ({recipeData["RankLevel"]}*)\n\n{textmap[str(recipeData["DescTextMapHash"])]}\n\n{textmap["1178114658"]} {recipeData["MaxProficiency"]}\n')
            
            # Cooking bonus
            recipeBonusData = list(filter(lambda x: x['RecipeId'] == recipeData['Id'], files["CookBonusExcelConfigData"]))
            avatar = []
            if len(recipeBonusData) == 1:
                avatar = list(filter(lambda x: x['Id'] == recipeBonusData[0]["AvatarId"], files["AvatarExcelConfigData"]))
            
            file.write(f'{textmap["4260484728"]} : {textmap[str(avatar[0]["NameTextMapHash"])]}\n' if len(avatar) > 0 else '\n')

            # Ingredients required
            ingredients = list(filter(None, recipeData["InputVec"]))
            ingRequired = ''
            for i in ingredients:
                ing = list(filter(lambda x: x['Id'] == i['Id'], files["MaterialExcelConfigData"]))
                ingRequired += f'{textmap[str(ing[0]["NameTextMapHash"])]} x{i["Count"]}, '
            
            file.write(f'{textmap["1910786070"]} : {ingRequired[:-2]}\n')
            file.write("\n================================\n\n")


