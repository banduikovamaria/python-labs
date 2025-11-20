sales = [
    {"product": "apple", "quantity": 50,  "price": 10},
    {"product": "banana", "quantity": 20, "price": 15},
    {"product": "milk", "quantity": 100,  "price": 12},
    {"product": "apple", "quantity": 70,  "price": 10},
]

def calculate_income(sales_list):
    income = {}

    for item in sales_list:
        product = item["product"]
        quantity = item["quantity"]
        price = item["price"]
        total = quantity * price

        if product not in income:
            income[product] = 0

        income[product] += total

    return income

income_dict = calculate_income(sales)
print("Дохід кожного продукту:", income_dict)

big_income = [product for product, inc in income_dict.items() if inc > 1000]
print("Продукти з доходом > 1000:", big_income)
