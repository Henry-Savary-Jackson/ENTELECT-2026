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

segements = list()

current_weather = dict()

weathers = dict()

def read_race_file(file_path):
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
def total_tyre_friction(tyre_degradation, straight_distance, initial_speed, final_speed, radius, bese_friction_coefficient, weather_multiplier):
    total_degration = straight_degradation(tyre_degradation, straight_distance) + braking_degradation(initial_speed, final_speed, tyre_degradation) + corner_degradation(initial_speed, radius, tyre_degradation)
    tyre_friction = (bese_friction_coefficient - total_degration) * weather_multiplier
    return tyre_friction

def fuel_Usage(initial_speed, final_speed, distance):
    fuel_consumed = (k_base + k_drag * ((initial_speed - final_speed)/2)**2) * distance
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

def base_score_level_2_and_3(time_reference, time, fuel_used,fuel_soft_cap_limit_l):
    fuel_bonus = -500000 * (1 - fuel_used/fuel_soft_cap_limit_l)**2 + 500000
    

def main():
    read_race_file("example4.json") 


if __name__ == "__main__":
    main()