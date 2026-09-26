from database.DB_connect import DBConnect
from model.component import Component
from model.constructor import Constructor
from model.race import Race

RAIN_PROB_OVERRIDES = {
    (2027, "portimao"): 2,
}


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def get_seasons():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connection failed")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select distinct r.season
                    from races r
                    order by r.season"""
            cursor.execute(query)

            for row in cursor:
                result.append(row["season"])

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_races(season):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connection failed")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select r.race_id, r.season, r.round, r.race_name, r.date, r.is_sprint,
                        c.circuit_id, c.circuit_name, c.locality, c.country, c.lat, c.lng,
                        c.aero_index, c.chassis_index, c.power_index, c.rain_prob
                    from races r, circuits c
                    where r.circuit_id = c.circuit_id
                    and r.season = %s
                    order by r.date"""
            cursor.execute(query, (season,))

            for row in cursor:
                rain_prob = RAIN_PROB_OVERRIDES.get((row["season"], row["circuit_id"]), row["rain_prob"])
                result.append(Race(race_id=row["race_id"],
                                   season=row["season"],
                                   round=row["round"],
                                   race_name=row["race_name"],
                                   date=row["date"],
                                   is_sprint=bool(row["is_sprint"]),
                                   circuit_id=row["circuit_id"],
                                   circuit_name=row["circuit_name"],
                                   locality=row["locality"],
                                   country=row["country"],
                                   lat=float(row["lat"]),
                                   lng=float(row["lng"]),
                                   aero_index=row["aero_index"],
                                   chassis_index=row["chassis_index"],
                                   power_index=row["power_index"],
                                   rain_prob=rain_prob / 100))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_components():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connection failed")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select c.component_id, c.package_size, c.focus, c.base_gain_s,
                        c.cost_mln, c.base_lead_time_days
                    from components c
                    order by c.component_id"""
            cursor.execute(query)

            for row in cursor:
                result.append(Component(component_id=row["component_id"],
                                        package_size=row["package_size"],
                                        focus=row["focus"],
                                        base_gain_s=row["base_gain_s"],
                                        cost_mln=float(row["cost_mln"]),
                                        base_lead_time_days=row["base_lead_time_days"]))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_constructors(season):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connection failed")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select c.constructor_id, c.name, c.nationality, c.url, c.base_city,
                        c.base_country, c.base_lat, c.base_lng, c.first_season, c.last_season
                    from constructors c
                    where c.first_season <= %s
                    and (c.last_season is null or c.last_season >= %s)
                    order by c.name"""
            cursor.execute(query, (season, season))

            for row in cursor:
                result.append(Constructor(constructor_id=row["constructor_id"],
                                          name=row["name"],
                                          nationality=row["nationality"],
                                          url=row["url"],
                                          base_city=row["base_city"],
                                          base_country=row["base_country"],
                                          base_lat=float(row["base_lat"]),
                                          base_lng=float(row["base_lng"]),
                                          first_season=row["first_season"],
                                          last_season=row["last_season"]))

            cursor.close()
            cnx.close()
        return result
