import json
from  copy import deepcopy
from itertools import product 


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

def decision_at_lap(lap, output_dict, tyre, tyres, time, fuel_used, wear, weather, speed):
    outputs = []
    # consider refuel
    # combinations of refuel no refuel , and change in tyre
    # enter pit or no
    tyre = deepcopy(tyre)
    tyres = deepcopy(tyres)
    output_dict = deepcopy(output_dict)


    for new_tyre, change in tyres:

        # ignore if not changing but tire worn out
        if not change and new_tyre["degradation"] <= 0:
            continue

        # reduce number of tyres
        # calc lap 
        lap_decision, lap_time, lap_fuel, lap_wear, lap_weather,lap_speed = calc_lap(lap, output_dict, tyre, time, fuel_used, wear, weather, speed)
        # the recursively continue con
        race_decision, race_time, race_fuel, fuel_needed_at_lap , race_wear = decision_at_lap(lap+1, lap_decision, tyre, tyres, lap_time, lap_fuel, lap_wear,lap_weather,lap_speed  )
        # calculate
        outputs.append( (race_decision, race_time, race_fuel,fuel_needed_at_lap, race_wear ))
        # how much needed at last lap
        
   # get if not  
    max_output = []
    for output in outputs:
        # get score, if greater than max, update max
        max_output = output

    return max_output

        
    


def calc_lap(lap, output_dict,tyre ,time, fuel_used, wear,weather,speed):
    # choose a tire if at all
    for i in range(len(segments)):
        segment = segments[i]
        length = segment["length_m"]
        seg_type = segment["type"]
        max_accel = car["accel_m/e2"]
        max_break = car["brake_m/e2"]
        # choose target speed
        # choose brake distance
        # fail if there is a crash or impossible
        # if limp mode, continue until next pit stop, you WILL take pit stop
        # if there is a corner crash, record it and 




def decision_tree():
    total_time = 0
    total_fuel_usage = 0
    total_wear = 0
    weather = None # initial
    output_dict = dict()
    current_lap = 0

    return output_dict

    print(f"Current weather {current_weather}\n")
    for s in weathers:
        print(s)
if __name__ == "__main__":
    main()