import osmnx as ox
import networkx as nx
import random

# from django.contrib.gis.geos import Point
from geopy.distance import geodesic
from pathlib import Path
from django.conf import settings


class TrackingGenerator:
    def generate_tracking_points_for_location(
        location, distance_km, speed_km_h, delta_time_s
    ):
        if location != "Moscow":
            raise ValueError("Пока поддерживается только location='Moscow'")

        roads = TrackingGenerator.load_roads("moscow_roads.graphml")

        path = TrackingGenerator.generate_random_path(distance_km * 1000, roads)

        return TrackingGenerator.generate_tracking_points(
            path, speed_km_h, delta_time_s
        )

    def load_roads(file_name: str):
        data_path = (
            Path(settings.BASE_DIR)
            / "taxi_manager"
            / "tracking_simulator"
            / "geo_data"
            / f"{file_name}"
        )
        return ox.load_graphml(data_path)

    def generate_tracking_points(path, speed_km_h, delta_time_s):
        if not path:
            return []

        if len(path) == 1:
            return path

        _result = []
        current_lon, current_lat, _ = path[0]

        speed_m_s = speed_km_h * 1000 / 3600
        step_distance = speed_m_s * delta_time_s

        start_lon, start_lat, _ = path[0]

        lon, lan, _ = path[0]
        _result = [(lon, lan)]

        used_parts = 0

        total_distance = TrackingGenerator.path_length(path)
        total_parts = max(1, int(total_distance / step_distance))

        for end_lon, end_lat, distance in path[1:-1]:
            count_part = int(total_parts * distance / total_distance)
            used_parts += count_part

            _result.extend(
                TrackingGenerator.split_segment_by_parts(
                    start_lon, start_lat, end_lon, end_lat, count_part
                )[1:]
            )

            start_lon, start_lat = end_lon, end_lat

        end_lon, end_lat, distance = path[-1]
        count_part = max(1, total_parts - used_parts)
        _result.extend(
                TrackingGenerator.split_segment_by_parts(
                    start_lon, start_lat, end_lon, end_lat, count_part
                )[1:]
            )       

        result = []
        time_in_path = 0
        for lon, lat in _result:
            result.append((lon, lat, time_in_path))
            time_in_path += delta_time_s

        return result

    @staticmethod
    def split_segment_by_parts(start_lon, start_lat, end_lon, end_lat, parts):
        if parts <= 0:
            return []

        result = []

        for i in range(parts + 1):
            ratio = i / parts
            lon = start_lon + (end_lon - start_lon) * ratio
            lat = start_lat + (end_lat - start_lat) * ratio
            result.append((lon, lat))

        return result

    def truncate_path_by_length(path, target_length):
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

    def path_to_geo_points_with_distances(roads, path):
        result = []

        first_node = path[0]
        first_lon = roads.nodes[first_node]["x"]
        first_lat = roads.nodes[first_node]["y"]

        result.append((first_lon, first_lat, 0))

        for u, v in zip(path, path[1:]):
            edge_length = roads[u][v][0]["length"]
            lon = roads.nodes[v]["x"]
            lat = roads.nodes[v]["y"]
            result.append((lon, lat, edge_length))

        return result

    def path_length(path):
        return sum(distance_from_prev for _, _, distance_from_prev in path)

    def path_geodesic_length(path):
        current_point = path[0]
        path_length = 0

        for point in path[1:]:
            lon1, lat1, _ = current_point
            lon2, lat2, _ = point

            path_length += geodesic((lat1, lon1), (lat2, lon2)).meters

            current_point = point

        return path_length

    def generate_random_path(distance, roads):
        # start_poin = TrackingGenerator.random_point(roads)
        start_point = TrackingGenerator.random_node(
            roads
        )  # Упростил так как стандартный метод shortest_path ищет путь только между узалми
        res_path = [start_point]
        length = 0
        while length < distance:
            # next_point = TrackingGenerator.random_point(roads)
            next_point = TrackingGenerator.random_node(
                roads
            )  # Упростил так как стандартный метод ищет путь только между узалми
            path_on_graph = ox.routing.shortest_path(
                roads, start_point, next_point, weight="length"
            )
            path = TrackingGenerator.path_to_geo_points_with_distances(
                roads, path_on_graph
            )
            path = TrackingGenerator.truncate_path_by_length(path, distance - length)
            res_path.extend(path)

            length += TrackingGenerator.path_length(path)

        return path

    # def path_to_elapsed_time_points(path, speed_m_s, interval_s):
    #     result = []
    #     elapsed_time = 0.0

    #     for index, (lon, lat, distance_from_prev) in enumerate(path):
    #         if index > 0:
    #             elapsed_time += distance_from_prev / speed_m_s

    #         result.append((lon, lat, int(elapsed_time)))

    #     return result

    @staticmethod
    def random_node(roads):
        return random.choice(list(roads.nodes))

    def random_point(roads: nx.MultiGraph):
        underected_graph = ox.convert.to_undirected(roads)
        return next(iter(ox.utils_geo.sample_points(underected_graph, 1)))
