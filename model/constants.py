import math

ATR_ALLOCATION_PCT = {
    1: 70,
    2: 75,
    3: 80,
    4: 85,
    5: 90,
    6: 95,
    7: 100,
    8: 105,
    9: 110,
    10: 115,
    11: 115,
}
AERO_FOCUS = "Aero"
CHASSIS_FOCUS = "Chassis"
ATR_FOCUS = AERO_FOCUS

COST_CAP_MLN = {
    2021: 145,
    2022: 140,
    2023: 135,
    2024: 135,
    2025: 135,
    2026: 215,
    2027: 215,
}
EXTRA_RACE_SUPPLEMENT_MLN = 1.8
RACES_INCLUDED_UNTIL_2025 = 21
RACES_INCLUDED_FROM_2026 = 24

ROAD_MODE = "road"
AIR_MODE = "air"
EARTH_RADIUS_KM = 6371
ROAD_THRESHOLD_KM = 2000
ROAD_DRIVING_HOURS_PER_DAY = 20
MIN_ROAD_TRANSIT_DAYS = 1
FALLBACK_ROAD_DETOUR_FACTOR = 1.3
FALLBACK_ROAD_ONE_DAY_MAX_KM = 1000
FALLBACK_ROAD_TRANSIT_DAYS_SHORT = 1
FALLBACK_ROAD_TRANSIT_DAYS_LONG = 2
AIR_TRANSIT_DAYS = 3
ROAD_RATE_USD_PER_KM = 2
AIR_RATE_USD_PER_KG = 7
AIR_FIXED_FEE_USD = 1000
SHIPMENT_WEIGHT_KG = 300
USD_PER_MLN = 1_000_000

DEFAULT_ALPHA = 0.5
DEFAULT_BETA = 0.3
DEFAULT_PERFORMANCE_TOLERANCE_PCT = 2
MAX_PERFORMANCE_TOLERANCE_PCT = 10
EPSILON = 1e-9

NOT_PLACEABLE_LABEL = "not placeable"
OVER_BUDGET_LABEL = "over budget"
EXCLUDED_FOR_BUDGET_LABEL = "excluded for budget"
EXCLUDED_FOR_OTHERS_LABEL = "excluded in favour of other packages"

DEFAULT_BUDGET_MLN = 8
DEFAULT_POSITION = 5
MAX_WISHLIST_SIZE = 12
DEVELOPMENT_WINDOW_START_MONTH = 9
DEVELOPMENT_WINDOW_START_DAY = 1
DEFAULT_DEVELOPMENT_START_MONTH = 1
DEFAULT_DEVELOPMENT_START_DAY = 1


def air_distance_km(lat1, lng1, lat2, lng2):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def road_transit_days(driving_hours):
    driving_minutes = round(driving_hours * 60)
    minutes_per_day = ROAD_DRIVING_HOURS_PER_DAY * 60
    return max(MIN_ROAD_TRANSIT_DAYS, -(-driving_minutes // minutes_per_day))


def atr_multiplier(position):
    return 100 / ATR_ALLOCATION_PCT[position]


def cost_cap(season, race_count):
    included_races = RACES_INCLUDED_UNTIL_2025 if season <= 2025 else RACES_INCLUDED_FROM_2026
    extra_races = max(0, race_count - included_races)
    return COST_CAP_MLN[season] + extra_races * EXTRA_RACE_SUPPLEMENT_MLN
