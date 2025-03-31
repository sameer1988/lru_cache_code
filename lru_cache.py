from collections import OrderedDict

class Entity:
    def __init__(self, id, data):
        self.id = id
        self.data = data

    def __repr__(self):
        return f"Entity(id={self.id}, data={self.data})"

class DatabaseService:
    def __init__(self):
        # Here database is assumed as python dictionary
        self.database = {}

    def save(self, entity):
        try:
            # Saving to the database i.e. python dictionary
            self.database[entity.id] = entity
            print(f"Saved to database: {entity}")
        except Exception as e:
            print(f"Error saving entity {entity} to the database: {e}")
            raise

    def delete(self, entity):
        try:
            # Deleting from the database i.e. python dictionary
            if entity.id in self.database:
                del self.database[entity.id]
                print(f"Deleted from database: {entity}")
            else:
                print(f"Entity {entity} not found in the database.")
        except Exception as e:
            print(f"Error deleting entity {entity} from the database: {e}")
            raise

    def get(self, entity):
        try:
            # Fetching from the database i.e. python dictionary
            return self.database.get(entity.id, None)
        except Exception as e:
            print(f"Error fetching entity {entity} from the database: {e}")
            raise

    def clear(self):
        try:
            # Clear all entries in the database
            self.database.clear()
            print("Database cleared")
        except Exception as e:
            print(f"Error clearing the database: {e}")
            raise

class CacheService:
    def __init__(self, max_cache_size, database_service):
        if max_cache_size <= 0:
            raise ValueError("Max cache size must be greater than 0.")
        self.max_cache_size = max_cache_size
        self.cache = OrderedDict()
        self.database_service = database_service

    def remove(self, entity):
        try:
            if not isinstance(entity, Entity):
                raise TypeError("Expected entity to be of type 'Entity'.")

            # Remove from both cache and database
            if entity.id in self.cache:
                del self.cache[entity.id]
            self.database_service.delete(entity)

        except Exception as e:
            print(f"Error removing entity {entity} from cache and database: {e}")
            raise

    def remove_all(self):
        try:
            # Remove all entities from both cache and database
            self.cache.clear()
            print("Cache cleared")
            self.database_service.clear()

        except Exception as e:
            print(f"Error removing all entities from cache and database: {e}")
            raise

    def clear(self):
        try:
            # Clears the internal cache but does not delete from the database
            self.cache.clear()
            print("Cache cleared.")
        except Exception as e:
            print(f"Error clearing cache: {e}")
            raise

    def evict_least_used(self):
        try:
            # Evict the LRU entity from OrderedDict
            least_used_id, (entity) = self.cache.popitem(last=False)
            # Save new entity to the database
            self.database_service.save(entity)
            print(f"Evicted from cache and saved to database: {entity}")
        except Exception as e:
            print(f"Error evicting least used entity from cache: {e}")
            raise

    def add(self, entity):
        try:
            if not isinstance(entity, Entity):
                raise TypeError("Expected entity to be of type 'Entity'.")

            # If the cache size > max_cache_size then evict the LRU item from cache
            if len(self.cache) >= self.max_cache_size:
                self.evict_least_used()

            # Add or update the cache and mark the entity as most recently used
            self.cache[entity.id] = (entity)
            print(f"Entity added to cache: {entity}")

        except Exception as e:
            print(f"Error adding entity {entity} to the cache: {e}")
            raise

    def get(self, entity):
        try:
            if not isinstance(entity, Entity):
                raise TypeError("Expected entity to be of type 'Entity'.")

            # If entity is in cache, return it; else fetch from database
            if entity.id in self.cache:
                # Move the entity to end of cache as most recently used
                self.cache.move_to_end(entity.id)
                print(f"Entity {entity} fetched from cache.")
                return self.cache[entity.id]
            else:
                # Fetch from database and add to cache
                db_entity = self.database_service.get(entity)
                if db_entity:
                    self.add(db_entity)
                    print(f"Entity {entity} fetched from database.")
                return db_entity

        except Exception as e:
            print(f"Error retrieving entity {entity}: {e}")
            raise

try:
    # database service object
    db_service = DatabaseService()

    # Initialize the cache with a max size of 4
    cache_service = CacheService(max_cache_size=4, database_service=db_service)

    # Create entities
    entity1 = Entity("1", "Data 1")
    entity2 = Entity("2", "Data 2")
    entity3 = Entity("3", "Data 3")
    entity4 = Entity("4", "Data 4")
    entity5 = Entity("5", "Data 5")

    # Add entities to the cache
    cache_service.add(entity1)
    cache_service.add(entity2)
    cache_service.add(entity3)
    cache_service.add(entity4)

    # Get entity 1 to make it the most recently used
    print(cache_service.get(entity1))

    # Add entity 5, which will trigger eviction as max cache size is 4
    cache_service.add(entity5)

    # Check the cache and database service state
    print(f"Cache: {cache_service.cache}")
    print(f"Database: {db_service.database}")

    # Remove an entity
    cache_service.remove(entity2)

    # Remove all entities
    cache_service.remove_all()

    # Clear the cache
    cache_service.clear()

except Exception as e:
    print(f"An error occurred: {e}")
