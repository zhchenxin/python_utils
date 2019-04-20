import uuid
import time
import pickle


class AcquireTimeoutError(Exception):
    """
    在规定时间内，没有获取到到锁时，抛出的异常
    """


class RedisLock:
    """
    redis 分布式锁
    """

    @classmethod
    def register_redis(cls, redis):
        cls.redis = redis

    def __init__(self, lock_key, acquire_time=10, lock_timeout=60):
        """
        :param lock_key     锁名称
        :param acquire_time 尝试获取锁的时间，如果在指定时间内没有获取到锁，则返回 False
        :param lock_timeout 过期时间
        """
        self.lock_key = 'lock:' + lock_key
        self.acquire_time = acquire_time
        self.lock_timeout = lock_timeout
        self.identifier = ''

    def acquire(self, blocking=True):
        """
        :param blocking 是否阻塞
        :return 如果获取到锁，则返回 True，否则 False
        """
        identifier = str(uuid.uuid4())
        end = time.time() + self.acquire_time
        while time.time() < end:
            if self.redis.set(self.lock_key, identifier, ex=self.lock_timeout, nx=True):
                self.identifier = identifier
                return True
            if blocking:
                time.sleep(0.01)
            else:
                return False
        raise AcquireTimeoutError()

    def release(self):
        """
        删除锁
        """
        if self.identifier == '':
            return

        pipe = self.redis.pipeline(True)
        pipe.watch(self.lock_key)
        if pipe.get(self.lock_key).decode(encoding='utf-8') == self.identifier:
            pipe.multi()
            pipe.delete(self.lock_key)
            pipe.execute()
        self.identifier = ''

    @staticmethod
    def lock(lockname, acquire_time=10, lock_timeout=60, blocking=True):
        """

        使用方法:
        @RedisLock.lock('test', acquire_time=1, lock_timeout=60, blocking=False)
        def test():
            pass

        :param lockname:     锁名称
        :param acquire_time: 阻塞获取锁的时间
        :param lock_timeout: 锁的超时时间
        :param blocking:     非阻塞获取锁，如果没有获取到锁，则不会执行修饰的方法
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                lock = RedisLock(lockname, acquire_time=acquire_time, lock_timeout=lock_timeout)
                if lock.acquire(blocking=blocking):
                    try:
                        ret = func(*args, **kwargs)
                        return ret
                    except BaseException as e:
                        raise e
                    finally:
                        lock.release()

            return wrapper

        return decorator


class RedisCache:
    """
    redis 分布式缓存
    """

    @classmethod
    def register_redis(cls, redis):
        cls.redis = redis

    @staticmethod
    def __get_one_name(name):
        """
        获取一级缓存名称
        """
        return "cache:%s" % name

    @staticmethod
    def __get_two_name(name):
        """
        获取二级缓存名称
        """
        return "cache2:%s" % name

    @classmethod
    def cache(cls, cachename, timeout=60):
        """
        使用方法:
        @RedisCache.cache('test', timeout=60)
        def test():
            pass

        :param cachename: 锁名称
        :param timeout:   锁的超时时间
        :return:
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                val = cls.redis.get(cls.__get_one_name(cachename))
                if val is not None:
                    # 从缓存中获取数据
                    return pickle.loads(val)

                # 缓存失效的解决方案：
                # 使用分布式锁，只有一个进程去原始数据中获取
                lock = RedisLock('cachelock.' + cachename, lock_timeout=timeout)
                if lock.acquire() is False:
                    # 没有获取到锁，则使用二级缓存
                    val = cls.redis.get(cls.__get_two_name(cachename))
                    ret = pickle.loads(val)
                else:
                    # 获取到锁，从原始数据获取锁，同时设置一级缓存和二级缓存
                    ret = func(*args, **kwargs)
                    val = pickle.dumps(ret)
                    cls.redis.set(cls.__get_one_name(cachename), val, ex=timeout)
                    cls.redis.set(cls.__get_two_name(cachename), val, ex=timeout * 10)
                    lock.release()

                return ret
            return wrapper

        return decorator
