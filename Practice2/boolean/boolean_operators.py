temperature = 22
is_sunny = True
perfect_weather = temperature > 20 and is_sunny
print(f"Perfect weather: {perfect_weather}")


is_weekend = False
is_holiday = True
can_relax = is_weekend or is_holiday
print(f"Can relax: {can_relax}")


is_raining = False
should_go_outside = not is_raining
print(f"Should go outside: {should_go_outside}")


age = 16
has_license = False
parent_present = True
can_drive = (age >= 18 and has_license) or (age >= 16 and parent_present)
print(f"Can drive: {can_drive}")

is_member = True
purchase_amount = 150
has_coupon = False
gets_discount = (is_member and purchase_amount > 100) or has_coupon
print(f"Gets discount: {gets_discount}")


age = 25
has_ticket = True
can_enter = age >= 18 and has_ticket
print(f"Can enter: {can_enter}")