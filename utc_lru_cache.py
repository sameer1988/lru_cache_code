import unittest
from collections import OrderedDict
from lru_cache import Entity,DatabaseService,CacheService

class TestEntity(unittest.TestCase):
    def test_entity_initialization(self):
        entity = Entity("1", "Data 1")
        self.assertEqual(entity.id, "1")
        self.assertEqual(entity.data, "Data 1")

    def test_entity_repr(self):
        entity = Entity("1", "Data 1")
        self.assertEqual(repr(entity), "Entity(id=1, data=Data 1)")

class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        """New database for each test case"""
        self.db_service = DatabaseService()

    def test_save(self):
        entity = Entity("1", "Data 1")
        self.db_service.save(entity)
        self.assertIn("1", self.db_service.database)
        self.assertEqual(self.db_service.database["1"].id, "1")

    def test_delete(self):
        entity = Entity("1", "Data 1")
        self.db_service.save(entity)
        self.db_service.delete(entity)
        self.assertNotIn("1", self.db_service.database)

    def test_get(self):
        entity = Entity("1", "Data 1")
        self.db_service.save(entity)
        fetched_entity = self.db_service.get(entity)
        self.assertEqual(fetched_entity, entity)

    def test_clear(self):
        entity1 = Entity("1", "Data 1")
        entity2 = Entity("2", "Data 2")
        self.db_service.save(entity1)
        self.db_service.save(entity2)
        self.db_service.clear()
        self.assertEqual(self.db_service.database, {})

class TestCacheService(unittest.TestCase):
    def setUp(self):
        """New cache for each test case"""
        self.db_service = DatabaseService()
        self.cache = CacheService(max_cache_size=4, database_service=self.db_service)

    def test_remove(self):
        entity = Entity("1", "Data 1")
        self.cache.add(entity)
        self.cache.remove(entity)
        self.assertNotIn("1", self.cache.cache)
        self.assertNotIn("1", self.db_service.database)

    def test_remove_all(self):
        entity1 = Entity("1", "Data 1")
        entity2 = Entity("2", "Data 2")
        self.cache.add(entity1)
        self.cache.add(entity2)
        self.cache.remove_all()

        self.assertEqual(self.cache.cache, {})
        self.assertEqual(self.db_service.database, {})

    def test_clear(self):
        entity1 = Entity("1", "Data 1")
        entity2 = Entity("2", "Data 2")
        self.cache.add(entity1)
        self.cache.add(entity2)
        self.cache.clear()

        self.assertEqual(self.cache.cache,{})

    def test_evict_least_used(self):
        # Adding 5 entities will cause the least recently used entity to be evicted
        entity1 = Entity("1", "Data 1")
        entity2 = Entity("2", "Data 2")
        entity3 = Entity("3", "Data 3")
        entity4 = Entity("4", "Data 4")
        entity5 = Entity("5", "Data 5")

        self.cache.add(entity1)
        self.cache.add(entity2)
        self.cache.add(entity3)
        self.cache.add(entity4)

        # Access entity1 to make it the most recently used
        self.cache.get(entity1)

        # Adding entity5 will evict entity2 as it's the least recently used
        self.cache.add(entity5)

        # Check if entity2 was evicted and saved to the database
        self.assertNotIn("2", self.cache.cache)
        self.assertIn("2", self.db_service.database)

    def test_add(self):
        entity = Entity("1", "Data 1")
        self.cache.add(entity)
        self.assertIn("1", self.cache.cache)

    def test_get(self):
        entity1 = Entity("1", "Data 1")
        self.cache.add(entity1)
        self.db_service.save(entity1)

        # Fetch from cache
        fetched_entity = self.cache.get(entity1)
        self.assertEqual(fetched_entity, entity1)

        # Remove entity from cache and fetch from the database
        self.cache.clear()
        fetched_entity = self.cache.get(entity1)
        self.assertEqual(fetched_entity, entity1)

    def test_cache_size_limit(self):
        # Add 4 entities
        entity1 = Entity("1", "Data 1")
        entity2 = Entity("2", "Data 2")
        entity3 = Entity("3", "Data 3")
        entity4 = Entity("4", "Data 4")
        entity5 = Entity("5", "Data 5")

        self.cache.add(entity1)
        self.cache.add(entity2)
        self.cache.add(entity3)
        self.cache.add(entity4)
        self.cache.add(entity5)

        # Only 4 entities should be in the cache, entity1 is evicted
        self.assertEqual(len(self.cache.cache), 4)
        self.assertNotIn("1", self.cache.cache)


if __name__ == '__main__':
    unittest.main()