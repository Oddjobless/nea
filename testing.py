import unittest
from smoothing_kernel import SmoothingKernel
from spatial_map import SpatialMap

class TestSmoothingKernel(unittest.TestCase):
    def test_poly_6_kernel(self):
        kernel = SmoothingKernel(smoothing_length=1, poly_6=True)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=0.5), 0.0625)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=1), 0)

    def test_cubic_spline_kernel(self):
        kernel = SmoothingKernel(smoothing_length=1, cubic_spline=True)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=0.5), 0.125)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=1), 0)

    def test_gaussian_kernel(self):
        kernel = SmoothingKernel(smoothing_length=1, gaussian=True)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=0.5), 0)
        self.assertAlmostEqual(kernel.calculate_density_contribution(particle_radius=1), 0)

class TestSpatialMap(unittest.TestCase):
    def test_insert_particle(self):
        map = SpatialMap(noOfRows=3, noOfCols=3)
        particle = object()
        map.insert_particle(particle)
        self.assertIn(particle, map.grid[1])

    def test_remove_particle(self):
        map = SpatialMap(noOfRows=3, noOfCols=3)
        particle = object()
        map.insert_particle(particle)
        map.remove_particle(particle)
        self.assertNotIn(particle, map.grid[1])

    def test_get_neighbouring_particles(self):
        map = SpatialMap(noOfRows=3, noOfCols=3)
        particle1 = object()
        particle2 = object()
        particle3 = object()
        map.insert_particle(particle1)
        map.insert_particle(particle2)
        map.insert_particle(particle3)
        neighbours = map.get_neighbouring_particles(particle1)
        self.assertIn(particle2, neighbours)
        self.assertIn(particle3, neighbours)
        self.assertNotIn(particle1, neighbours)

if __name__ == '__main__':
    unittest.main()