import json

ids_to_update = [
    "blaster_cannon_light_twin", "blaster_cannon_light_quad",
    "blaster_cannon_med_twin", "blaster_cannon_med_quad",
    "blaster_cannon_hvy_twin", "blaster_cannon_hvy_quad",
    "laser_light_twin", "laser_light_quad",
    "laser_med_twin", "laser_med_quad",
    "laser_hvy_twin", "laser_hvy_quad",
    "ion_cannon_light_twin", "ion_cannon_light_quad",
    "turbolaser_light_twin", "turbolaser_light_quad"
]

with open('data.json', 'r') as f:
    data = json.load(f)

count = 0
for item in data['EQUIPMENT']:
    if item['id'] in ids_to_update:
        if "Can fire normally or in Autofire mode" not in item['description']:
            item['description'] += " Can fire normally or in Autofire mode, with a Swift Action required to switch between the two."
            count += 1

with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)

print(f"Updated {count} descriptions.")
