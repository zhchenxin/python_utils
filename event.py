class Event:
    """
    事件基类
    """


class Listen:
    def handle(self, e: Event):
        """
        事件发生的时候，处理事件
        :param e:
        :return:
        """


class Dispatcher:
    listen = {}

    def fire(self, e: Event):
        """
        触发事件
        :param e:
        :return:
        """
        for listen in self.__get_listeners(e):
            listen.handle(e)

    def __get_listeners(self, e: Event) -> list:
        ret = []
        obj_cls = self._get_object_class(e)
        if obj_cls in self.listen:
            for listener in self.listen[obj_cls]:
                ret.append(self._get_class(listener)())
        return ret

    @staticmethod
    def _get_class(kls: str):
        """
        根据 class 名称获取 class type。
        例如：
        get_class('datetime.datetime')
        :param kls:
        :return:
        """
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    @staticmethod
    def _get_object_class(obj: object) -> str:
        """
        获取变量对应的类名，类名为 "module.class"
        :param obj:
        :return:
        """
        return obj.__class__.__module__ + '.' + obj.__class__.__name__


def event(e: Event):
    Dispatcher().fire(e)
