import json
import math

k_straight = 0.0000166
k_braking = 0.0398 
k_corner = 0.000265
k_base = 0.0005
k_drag = 0.0000000015
gravity = 9.81

car = dict()

tyres = dict()

segments = list()

current_weather = dict()

weathers = list()

craw_constant = 0

def read_race_file(file_path):
    global car , race, tyres,segments, weathers, current_weather
    with open(file_path, "r") as file:
        full_data = json.load(file)

# tire friction calculation
def straight_degradation(tyre_degradation, straight_distance):
    degradation = tyre_degradation * straight_distance * k_straight
    return degradation

def braking_degradation(initial_speed, final_speed, tyre_degradation_rate):
    degradation = ((initial_speed/100)**2 -(final_speed/100)**2) * k_braking * tyre_degradation_rate
    return degradation

def corner_degradation(current_speed, radius, tyre_degradation_rate):
    degradation = k_corner * (((current_speed)**2) / radius) * tyre_degradation_rate
    return degradation

# total_friction(tyre_degradation, straight_distance, initial_speed, final_speed, radius, , bese_friction_coefficient, weather_multiplier)
def total_tyre_friction(base_friction_coefficient, accumulated_degradation, weather_multiplier):
    tyre_friction = (base_friction_coefficient - accumulated_degradation) * weather_multiplier
    return tyre_friction

def fuel_Usage(initial_speed, final_speed, distance):
    fuel_consumed = (k_base + k_drag * ((initial_speed + final_speed)/2)**2) * distance
    return fuel_consumed

def refueling_time(refuel_amount, refuel_rate):
    time = refuel_amount/refuel_rate
    return time


def max_corner_speed(tyre_degradation, straight_distance, initial_speed, final_speed, radius, bese_friction_coefficient, weather_multiplier, crawl_constant):
    tyre_friction = total_tyre_friction(tyre_degradation, straight_distance, initial_speed, final_speed, radius, bese_friction_coefficient, weather_multiplier)
    max_speed = math.sqrt(tyre_friction * radius * gravity) + crawl_constant
    return max_speed

def pit_stop_time(refuel_amount, refuel_rate, pit_tire_swap_time, base_pit_stop_time):
    time = refueling_time(refuel_amount, refuel_rate) + pit_tire_swap_time + base_pit_stop_time
    return time

def base_score_level_1(time_reference, time):
    score = 500000 * ((time_reference / time) ** 3)
    return score

def score_level_2_and_3(time_reference, time, fuel_used,fuel_soft_cap_limit_l):
    fuel_bonus = -500000 * (1 - fuel_used/fuel_soft_cap_limit_l)**2 + 500000
    final_score = base_score_level_1(time_reference, time) + fuel_bonus
    return final_score
    race = full_data["race"]
    car  = full_data["car"]
    
    craw_constant = car["crawl_constant"]
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


def score_level_4(base_friction_coefficient, weather_multiplier, accumulated_degradation, number_of_blowouts):
    tyre_bonus = 100000 * total_tyre_friction(base_friction_coefficient, accumulated_degradation, weather_multiplier) - 50000 * number_of_blowouts
    return tyre_bonus

def main():
    read_race_file("1.txt")

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
    max_score = 0
    for output in outputs:
        # get score, if greater than max, update max
        score = base_score_level_1(0, output[1])
        if score >= max_score:
            max_output = output 
            max_score = score

    return max_output



def calc_lap(lap, output_dict,tyre ,time, fuel_used, wear,weather,speed):
    # choose a tire if at all
    for i in range(len(segments)):
        segment = segments[i]
        length = segment["length_m"]
        seg_type = segment["type"]
        accel = car["accel_m/e2"]
        break_acc = car["brake_m/e2"]
        if (segment["type"] == "straight"):
            # choose
            degradation = straight_degradation(tyre["degradation"], length)
            # get the new corner's speed
            if i != len(segments)-1:
                corner = segments[i+1]

                max_corner = max_corner_speed(tyre["dry_degradation"], ,weather["acceleration_multiplier"], speed,,corner["radius"] , craw_constant)

        else:
            degradation = corner_degradation(speed,segment["radius"], tyre["dry_degradation"] )
    
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