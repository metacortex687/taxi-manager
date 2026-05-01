from django.test import TestCase

import networkx as nx
import random

from shapely.geometry import LineString
from .tracking_generator import TrackingGenerator





# Create your tests here.
class TrackingGeneratorTest(TestCase):
    def setUp(self):
        self.tracking_generator = TrackingGenerator(random.Random(0))
    #     ox.settings.use_cache = True
    #     ox.settings.cache_folder = "/home/taxi-manager/.cache/osmnx"
    #     ox.settings.requests_timeout = 1800
    #     ox.settings.log_console = True
    #     ox.settings.overpass_url = "https://overpass.kumi.systems/api"


    def test_generate_sample_points_in_line(self):
        road = nx.MultiGraph(crs="EPSG:3857")
        p1 = (1.0, 2.0)
        p2 = (31.0, 42.0)
        road.add_node(1, x=p1[0], y=p1[1])
        road.add_node(2, x=p2[0], y=p2[1])

        line = LineString([p1, p2])
        road.add_edge(1, 2, 1, geometry=line, length= line.length)

        p1 = self.tracking_generator.random_point(road)
        self.assertTrue(line.distance(p1)  < 1e-6)

        p2 = self.tracking_generator.random_point(road)
        self.assertTrue(p1.distance(p2)  > 1e-6)    

    def test_generate_graph_road_distanse_2500(self):
        distance = 2500

        roads = self.tracking_generator.load_roads("moscow_roads.graphml")
        path = self.tracking_generator.generate_random_path(distance, roads)
        self.assertAlmostEqual(self.tracking_generator.path_length(path),distance)
        self.assertAlmostEqual(self.tracking_generator.path_geodesic_length(path),2500,delta=150)


    def test_generate_tracking_points_empty(self):      
        res = self.tracking_generator.generate_tracking_points([], 40, 20)
        self.assertEqual(res, [])   


    def test_generate_tracking_points_one_point(self):      
        res = self.tracking_generator.generate_tracking_points([(37.4911993, 55.8571161, 0)], 40, 20)
        self.assertEqual(res, [(37.4911993, 55.8571161, 0)])        

    def test_generate_tracking_points_for_one_edge_count(self):
        path = [
                (37.4911993, 55.8571161, 0),
                (37.5713158, 55.8571161, 5000.0),
               ]  
        
        res = self.tracking_generator.generate_tracking_points(path, 40, 20)

        count = 5.0/40.*3600/20

        self.assertAlmostEqual(len(res), count, delta=2) 


    def test_generate_tracking_points_for_one_edge_time(self):
        path = [
                (37.4911993, 55.8571161, 0),
                (37.5713158, 55.8571161, 5000.0),
               ]  
        expected_time = 5.0/40.0*3600  
        
        delta_time_s = 20
        res = self.tracking_generator.generate_tracking_points(path, 40, delta_time_s)

        _, _, time = res[-1]      

        self.assertAlmostEqual(time, expected_time, delta=delta_time_s) 


    def test_generate_tracking__for_two_edge(self):
        path = [
                (37.4911993, 55.8571161, 0),
                (37.5713158, 55.8571161, 5000.0),
                (37.6819000, 55.8602000, 7000.0),
               ]        
        
        res = self.tracking_generator.generate_tracking_points(path, 40, 20)

        count = int(12.0/40.*3600/20)+2

        self.assertAlmostEqual(len(res), count, delta=2) 

    def test_generate_tracking_points_for_two_edge_time(self):
        path = [
                (37.4911993, 55.8571161, 0),
                (37.5713158, 55.8571161, 5000.0),
                (37.6819000, 55.8602000, 7000.0),
               ]   
        
        expected_time = (5.0+7.0)/40.0*3600
        
        delta_time_s = 20
        expected_time += delta_time_s*(len(path)-2) #Задержка в узле графа
        
        res = self.tracking_generator.generate_tracking_points(path, 40, delta_time_s)

        _, _, time = res[-1]      

        self.assertAlmostEqual(time, expected_time, delta=delta_time_s) 


    def test_generate_tracking_points_for_location_not_empty_result(self):
        result = self.tracking_generator.generate_tracking_points_for_location("Moscow",5,40,20)

        self.assertAlmostEqual(5./40.*3600./20., len(result), delta=1)

    def test_generate_tracking_points_for_location_seed_3(self):
        random_generator = random.Random(3)
        generator = TrackingGenerator(random_generator)

        points = generator.generate_tracking_points_for_location(
            location="Moscow",
            distance_km=6.702791534208636,
            speed_km_h=39.09938178236782,
            delta_time_s=60,
        )

        self.assertGreater(len(points), 1)

        first_lon, first_lat, first_time = points[0]
        last_lon, last_lat, last_time = points[-1]

        self.assertIsInstance(first_lon, float)
        self.assertIsInstance(first_lat, float)
        self.assertEqual(first_time, 0)

        self.assertIsInstance(last_lon, float)
        self.assertIsInstance(last_lat, float)
        self.assertGreater(last_time, first_time)
        

