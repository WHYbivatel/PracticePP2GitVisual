import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

price_pattern = r'\b\d{1,3}(?:\s\d{3})*,\d{2}\b'
prices = re.findall(price_pattern, text)

def normalize_price(p):
    return float(p.replace(" ", "").replace(",", "."))

price_values = [normalize_price(p) for p in prices]

product_pattern = r'\d+\.\s*\n?(.+?)\n\d'
products = re.findall(product_pattern, text)
products = [p.strip() for p in products]

calculated_total = sum(price_values[:-1])

datetime_pattern = r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2}:\d{2})'
datetime_match = re.search(datetime_pattern, text)
datetime_value = datetime_match.group(1) if datetime_match else None

payment_pattern = r'(Банковская карта|Наличные)'
payment_match = re.search(payment_pattern, text)
payment_method = payment_match.group(1) if payment_match else None

receipt_data = {
    "products": products,
    "prices": price_values,
    "calculated_total": round(calculated_total, 2),
    "date_time": datetime_value,
    "payment_method": payment_method
}

print(json.dumps(receipt_data, indent=4, ensure_ascii=False))

