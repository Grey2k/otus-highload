import abc


class ResourceDto(abc.ABC):

    @abc.abstractmethod
    def as_dict(self):
        pass


def resource(dto: ResourceDto):
    return dto.as_dict()


class CounterResource(ResourceDto):

    def __init__(self, count):
        self.count = count

    def as_dict(self):
        return {
            'success': True,
            'unread_count': self.count,
        }
