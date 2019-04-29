from event import Event, Listen, Dispatcher, event

num = 1


class SaveEvent(Event):
    def __init__(self, name):
        self.name = name


class Listen1(Listen):
    def __init__(self):
        print('init listen1')

    def handle(self, e: SaveEvent):
        print(e.name)
        global num
        num = num + e.name


def test_event():
    # 配置事件监听者
    Dispatcher.listen = {
        'tests.test_event.SaveEvent': [
            'tests.test_event.Listen1'
        ],
    }

    # 事件的触发
    event(SaveEvent(12))
    assert num == 13

    event(SaveEvent(1))
    assert num == 14
