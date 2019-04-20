from redisutils import RedisLock
from redisutils import RedisCache
from redis import Redis
import uuid


class TestRedisLock:

    def setup_method(self):
        RedisLock.register_redis(Redis())

    def test_acquire(self):
        lock = RedisLock('TestRedisLock:test_acquire')
        # 第一次获取锁成功
        assert lock.acquire() is True
        # 非阻塞重新获取锁会返回False
        assert lock.acquire(False) is False
        lock.release()

        # 释放锁之后，可以重新获取锁
        assert lock.acquire() is True
        lock.release()

    def test_release(self):
        lock = RedisLock('TestRedisLock:test_release')
        # 可以单独调用释放锁，不影响其他功能
        lock.release()

        # 获取锁之后，可以成功的释放锁
        assert lock.acquire() is True
        lock.release()

    def test_lock(self):
        # 修饰器工作正常
        assert self.__test_lock() == '123'
        assert self.__test_lock() == '123'

    @RedisLock.lock('TestRedisLock:__test_lock')
    def __test_lock(self):
        return '123'


class TestRedisCache:
    def setup_method(self):
        redis = Redis()
        RedisLock.register_redis(redis)
        RedisCache.register_redis(redis)

    def test_cache(self):
        ret = self.__test_cache()
        # 返回 UUID 对象
        assert isinstance(ret, uuid.UUID)

        # 第二次使用函数，则返回一样的值
        ret1 = self.__test_cache()
        assert ret1 == ret

    @RedisCache.cache('TestRedisCache:__test_cache')
    def __test_cache(self):
        return uuid.uuid4()
