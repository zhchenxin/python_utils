from cache import LRUCache


class TestLRUCache:

    def test_default(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        assert cache.get(1) == 1
        # 该操作会使得密钥 2 作废
        cache.put(3, 3)
        assert cache.get(2) == -1

        # 该操作会使得密钥 1 作废
        cache.put(4, 4)
        assert cache.get(1) == -1
        assert cache.get(3) == 3
        assert cache.get(4) == 4
