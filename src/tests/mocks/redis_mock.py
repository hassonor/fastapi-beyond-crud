class AsyncRedisMock:
    """Mock Redis client for testing"""

    def __init__(self):
        self.storage = {}
        self.is_connected = False

    async def get(self, key):
        return self.storage.get(key)

    async def set(self, name, value, ex=None):
        self.storage[name] = value
        return True

    async def delete(self, *keys):
        for key in keys:
            if key in self.storage:
                del self.storage[key]
        return True

    async def ping(self):
        return True

    async def close(self):
        self.is_connected = False
        self.storage.clear()

    async def connect(self):
        self.is_connected = True
