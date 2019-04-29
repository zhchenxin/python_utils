import collections


class LRUCache:
    """
    LRU 缓存算法（最近最少使用）
    """

    def __init__(self, capacity: int):
        """
        数据结构：链表
        """
        self.dict = collections.OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        """
        从缓存中取出数据，如果没有取到，则返回-1

        算法：
            如果哈希表中存在相应记录，则将其移动到链表的头部
        :param key:
        :return:
        """
        if key in self.dict:
            val = self.dict.pop(key)
            self.dict[key] = val
            return val
        else:
            return -1

    def put(self, key: int, value: int):
        """
        算法：
            如果哈希表中存在相应记录，则修改值，并将其移动到链表头部
            如果缓存已满，则将链表最后一位删除，将新数据添加到链表头部
            其他请款，直接将数据插入到链表头部
        """
        if key in self.dict:
            self.dict.pop(key)
            self.dict[key] = value
        elif len(self.dict) == self.capacity:
            self.dict.popitem(last=False)
            self.dict[key] = value
        else:
            self.dict[key] = value


class LFUCache:
    """
    LFU 缓存算法（最不经常使用）
    """

    def __init__(self, capacity: int):
        """
        数据结构：哈希表
        """
        self.dict = collections.OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        """
        从缓存中取出数据，如果没有取到，则返回-1

        """

    def put(self, key: int, value: int):
        """
        如果键不存在，请设置或插入值。
        当缓存达到其容量时，它应该在插入新项目之前，使最不经常使用的项目无效。
        在此问题中，当存在平局（即两个或更多个键具有相同使用频率）时，最近最少使用的键将被去除。
        """
