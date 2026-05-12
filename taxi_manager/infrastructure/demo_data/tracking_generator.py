import osmnx as ox
import networkx as nx
import random

# from django.contrib.gis.geos import Point
from geopy.distance import geodesic
from pathlib import Path
from django.conf import settings


class TrackingGenerator:
    _roads_cache = {}

    def __init__(self, random_generator):
        self.random = random_generator
        
    def generate_tracking_points_for_location(self,
        location, distance_km, speed_km_h, delta_time_s
    ):
        if location != "Moscow":
            raise ValueError("Пока поддерживается только location='Moscow'")

        roads = self.load_roads("moscow_roads.graphml")

        path = self.generate_random_path(distance_km * 1000, roads)

        return self.generate_tracking_points(
            path, speed_km_h, delta_time_s
        )

    def load_roads(self, file_name: str):
        if file_name in self._roads_cache:
            return self._roads_cache[file_name]
        
        data_path = (
            Path(settings.BASE_DIR)
            / "infrastructure"
            / "demo_data"
            / "geo_data"
            / f"{file_name}"
        )

        roads = ox.load_graphml(data_path)

        self._roads_cache[file_name] = roads

        return roads 

    def generate_tracking_points(self, path, speed_km_h, delta_time_s):
        if not path:
            return []

        if len(path) == 1:
            lon, lat, _ = path[0]
            return [(lon, lat, 0)]

        if speed_km_h <= 0:
            raise ValueError("speed_km_h must be greater than 0")

        if delta_time_s <= 0:
            raise ValueError("delta_time_s must be greater than 0")

        speed_m_s = speed_km_h * 1000 / 3600
        step_distance = speed_m_s * delta_time_s

        result = []

        start_lon, start_lat, _ = path[0]
        result.append((start_lon, start_lat, 0))

        distance_from_start = 0
        next_tracking_distance = step_distance

        for end_lon, end_lat, segment_distance in path[1:]:
            if segment_distance <= 0:
                continue

            segment_start_distance = distance_from_start
            segment_end_distance = distance_from_start + segment_distance

            while next_tracking_distance < segment_end_distance:
                ratio = (
                    (next_tracking_distance - segment_start_distance)
                    / segment_distance
                )

                lon = start_lon + (end_lon - start_lon) * ratio
                lat = start_lat + (end_lat - start_lat) * ratio
                time_in_path = next_tracking_distance / speed_m_s

                result.append((lon, lat, round(time_in_path, 3)))
                next_tracking_distance += step_distance

            distance_from_start = segment_end_distance
            time_in_path = distance_from_start / speed_m_s

            if result[-1][0] != end_lon or result[-1][1] != end_lat:
                result.append((end_lon, end_lat, round(time_in_path, 3)))

            start_lon, start_lat = end_lon, end_lat

        return result

    def split_segment_by_parts(self, start_lon, start_lat, end_lon, end_lat, parts):
        if parts <= 0:
            return []

        result = []

        for i in range(parts + 1):
            ratio = i / parts
            lon = start_lon + (end_lon - start_lon) * ratio
            lat = start_lat + (end_lat - start_lat) * ratio
            result.append((lon, lat))

        return result

    def truncate_path_by_length(self, path, target_length):
        result = [path[0]]

        current_length = 0
        for lon, lat, distance_from_prev in path[1:]:
            prev_lon, prev_lat, _ = result[-1]

            if current_length + distance_from_prev < target_length:
                result.append((lon, lat, distance_from_prev))
                current_length += distance_from_prev
                continue

            remaining_length = target_length - current_length

            if distance_from_prev > 0:
                ratio = remaining_length / distance_from_prev
                cut_lon = prev_lon + (lon - prev_lon) * ratio
                cut_lat = prev_lat + (lat - prev_lat) * ratio
                result.append((cut_lon, cut_lat, remaining_length))

            break

        return result

    def path_to_geo_points_with_distances(self, roads, path):
        result = []

        first_node = path[0]
        first_lon = roads.nodes[first_node]["x"]
        first_lat = roads.nodes[first_node]["y"]

        result.append((first_lon, first_lat, 0))

        for u, v in zip(path, path[1:]):
            edge_data = min(
                roads[u][v].values(),
                key=lambda data: data.get("length", 0),
            )

            geometry = edge_data.get("geometry")

            if geometry is None:
                edge_length = edge_data["length"]
                lon = roads.nodes[v]["x"]
                lat = roads.nodes[v]["y"]
                result.append((lon, lat, edge_length))
                continue

            coords = list(geometry.coords)

            for lon, lat in coords[1:]:
                prev_lon, prev_lat, _ = result[-1]
                distance_from_prev = geodesic((prev_lat, prev_lon), (lat, lon)).meters
                result.append((lon, lat, distance_from_prev))

        return result

    def path_length(self, path):
        return sum(distance_from_prev for _, _, distance_from_prev in path)

    def path_geodesic_length(self, path):
        current_point = path[0]
        path_length = 0

        for point in path[1:]:
            lon1, lat1, _ = current_point
            lon2, lat2, _ = point

            path_length += geodesic((lat1, lon1), (lat2, lon2)).meters

            current_point = point

        return path_length

    def generate_random_path(self, distance, roads):
        # start_poin = TrackingGenerator.random_point(roads)
        start_point = self.random_node(
            roads
        )  # Упростил так как стандартный метод shortest_path ищет путь только между узалми
        
        attempt = 0
        res_path = []

        length = 0
        while length < distance:
            # next_point = TrackingGenerator.random_point(roads)
            next_point = self.random_node(
                roads
            )  # Упростил так как стандартный метод ищет путь только между узалми

            path_on_graph = ox.routing.shortest_path(
                roads, start_point, next_point, weight="length"
            )

            if not path_on_graph and attempt < 50:  # были две точки по которым не удалось найти кратчайший путь
                attempt += 1
                start_point = self.random_node(
                    roads
                )
                continue

            if not path_on_graph:
                raise Exception(f"Не удалось за {attempt} попыток, найти точки между которыми возможен маршрут")
            
            attempt = 0


            path = self.path_to_geo_points_with_distances(
                roads, path_on_graph
            )
            path = self.truncate_path_by_length(path, distance - length)
            if not res_path:
                res_path.extend(path)
            else:
                res_path.extend(path[1:])

            length += self.path_length(path)
            start_point = path_on_graph[-1]

        return res_path

    # def path_to_elapsed_time_points(path, speed_m_s, interval_s):
    #     result = []
    #     elapsed_time = 0.0

    #     for index, (lon, lat, distance_from_prev) in enumerate(path):
    #         if index > 0:
    #             elapsed_time += distance_from_prev / speed_m_s

    #         result.append((lon, lat, int(elapsed_time)))

    #     return result

    def random_node(self, roads):
        return self.random.choice(list(roads.nodes))

    def random_point(self, roads: nx.MultiGraph):
        underected_graph = ox.convert.to_undirected(roads)
        return next(iter(ox.utils_geo.sample_points(underected_graph, 1)))
