import pandas as pd

prod = pd.read_json("products.json")

prod = prod["products"]

for i in prod:
    print("INSERT INTO products \n(`id`, `name`, `description`, `picture`, `priceUsd`, `categories`) \nVALUES (")
    print(" '%s',\n '%s',\n '%s',\n '%s',\n '%s',\n '%s'\n);" % (
            i["id"], 
            i["name"],
            i["description"],
            i["picture"],
            str(i["priceUsd"]).replace("'",'"'),
            str(i["categories"]).replace("'",'"')
            )
    )