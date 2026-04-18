import json


car = dict()

tyres = dict()

segments = list()

current_weather = dict()

weathers = list()

def read_race_file(file_path):
    global car , race, tyres,segments, weathers, current_weather
    with open(file_path, "r") as file:
        full_data = json.load(file)

    race = full_data["race"]
    car  = full_data["car"]
    
    for seg in full_data["track"]["segments"]:
        segment = {
            "id" : seg["id"],"type" : seg["type"],"length" : seg["length_m"],}
        if seg["type"] == "corner":
            segment["radius"] = seg ["radius_m"]
        segments.append(segment) # cleanned up segments appeded
    
    tyre_properties = full_data["tyres"]["properties"]

    for available_set in full_data["available_sets"]:
        compound = available_set["compound"]
        props = tyre_properties[compound]

        for tyre_id in available_set["ids"]:
            tyres[tyre_id] = {
                "id":       tyre_id,
                "compound": compound,

                "life_span":    props["life_span"],
                "degradation":  0.0,

                "dry_friction_multiplier":        props["dry_friction_multiplier"],
                "cold_friction_multiplier":       props["cold_friction_multiplier"],
                "light_rain_friction_multiplier": props["light_rain_friction_multiplier"],
                "heavy_rain_friction_multiplier": props["heavy_rain_friction_multiplier"],

                "dry_degradation":        props["dry_degradation"],
                "cold_degradation":       props["cold_degradation"],
                "light_rain_degradation": props["light_rain_degradation"],
                "heavy_rain_degradation": props["heavy_rain_degradation"],
            }
    for condition in full_data["weather"]["conditions"]:
        weathers.append({
            "id":                    condition["id"],
            "condition":             condition["condition"],
            "duration_s":            condition["duration_s"],
            "acceleration_multiplier": condition["acceleration_multiplier"],
            "deceleration_multiplier": condition["deceleration_multiplier"],
        })
    starting_id = full_data["race"]["starting_weather_condition_id"]
    current_weather.update(next(w for w in weathers if w["id"] == starting_id))   

    

def main():
    read_race_file("example4.json")

    print(car)
    print(f"Race lap{race['laps']}")
    for i in segments:
        print(i)
    
    print(f"Current weather {current_weather}\n")
    for s in weathers:
        print(s)
if __name__ == "__main__":
    main()