from abc import ABC, abstractmethod

from tarantool.const import ITERATOR_REQ

from app.database.models import FeedItem
from app.database.utils import Pagination, PaginatedCollection
from app.ext.tarantool import Tarantool


class FeedProvider(ABC):

    @abstractmethod
    def load(self, feed_id, page, count) -> PaginatedCollection:
        pass


class TarantoolFeedProvider(FeedProvider):
    model_class = FeedItem
    space_name = 'feed'
    index_name = 'feed_id'
    coll_names = ['id', 'feed_id', 'author', 'author_id', 'content', 'publish_date']

    def __init__(self, db: Tarantool):
        self.db = db

    @property
    def space(self):
        return self.db.space(self.space_name)

    def load(self, feed_id, page, count) -> PaginatedCollection:
        cnt = self.space.call(f'box.space.{self.space_name}.index.{self.index_name}:count', feed_id).data[0]
        offset = (page - 1) * count
        rows = self.space.select(feed_id, iterator=ITERATOR_REQ, index=self.index_name, limit=count, offset=offset)
        items = [self.__to_model(row) for row in rows]
        pagination = Pagination(current_page=page, items_per_page=count, total_items=cnt)
        return PaginatedCollection(items=items, pagination=pagination)

    def __to_model(self, row):
        return self.model_class(**dict(zip(self.coll_names, row)))
