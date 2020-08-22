from app.database.models import Profile
from app.database.utils import PaginatedCollection, Pagination
from app.ext.tarantool import Tarantool


class TarantoolProfilesRepo:
    space_name = 'soc_net_profiles'
    model_class = Profile
    coll_names = ['id', 'first_name', 'last_name', 'interests', 'birth_date', 'gender', 'city_id']

    def __init__(self, db: Tarantool):
        self.db = db

    @property
    def space(self):
        return self.db.space(self.space_name)

    def __to_model(self, row):
        return self.model_class(**dict(zip(self.coll_names, row)))

    def find_paginate(self, page=1, count=10) -> PaginatedCollection:
        cnt = self.space.call(f'box.space.{self.space_name}:count').data[0]
        rows = self.space.select(limit=count, offset=(page - 1) * count)
        items = [self.__to_model(row) for row in rows]
        pagination = Pagination(current_page=page, items_per_page=count, total_items=cnt)
        return PaginatedCollection(items=items, pagination=pagination)

    def search(self, first_name, last_name, page, count):
        result = self.space.call('search_profiles', [first_name, last_name, page, count]).data[0]
        cnt = result.get('cnt', 0)
        items = [self.__to_model(row) for row in result.get('items', [])]
        pagination = Pagination(current_page=page, items_per_page=count, total_items=cnt)
        return PaginatedCollection(items=items, pagination=pagination)
