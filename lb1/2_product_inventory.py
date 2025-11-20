inventory = {
    "apple": 10,
    "banana": 3,
    "milk": 7,
    "bread": 2
}

def update_inventory(product, amount):
    """
    product — назва продукту
    amount — може бути +n або -n
    """
    if product not in inventory:
        inventory[product] = 0

    inventory[product] += amount

    if inventory[product] < 0:
        inventory[product] = 0


update_inventory("apple", -3)   # забрали зі складу
update_inventory("banana", 10)  # додали
update_inventory("water", 4)    # новий товар

print("Оновлений склад:", inventory)

low_stock = [item for item, qty in inventory.items() if qty < 5]
print("Продукти з кількістю менше 5:", low_stock)
