from abc import ABC
from collections import defaultdict

from app.database.models import Profile, Model, Dialog, DialogMessage, DialogType, DialogParticipant
from app.ext.mysql import MysqlPool


class BaseRepo(ABC):
    table_name = None
    model_class = None

    def __init__(self, db: MysqlPool):
        self.pool = db

    @property
    def db(self):
        return self.pool.master

    def find_all(self):
        query = f'SELECT * from `{self.table_name}`'
        with self.db.cursor() as cursor:
            cursor.execute(query)
            items = [self.model_class(**row) for row in cursor.fetchall()]

        return items

    def find_by_id(self, entity_id):
        return self._find_one_by_attribute('id', entity_id)

    def find_by_ids(self, ids):
        if not ids:
            return []
        query = f'SELECT * from `{self.table_name}` WHERE id in %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [set(ids)])
            items = {row['id']: self.model_class(**row) for row in cursor.fetchall()}

        return items

    def _find_one_by_attribute(self, attr, value):
        sql = f'SELECT * FROM `{self.table_name}` where {attr}=%s'
        row = self.db.query(sql, (value,)).fetchone()
        return self.model_class(**row) if row else None

    def save(self, entity: Model):
        if not entity.id:
            return self._add(entity)
        return self._update(entity)

    def _add(self, entity: Model):
        data = {k: v for k, v in entity.to_dict().items() if v is not None and not isinstance(v, dict)}
        keys = ','.join(map(lambda k: f'`{k}`', data.keys()))
        values = ','.join(map(lambda k: f'%({k})s', data.keys()))
        query = f'INSERT INTO `{self.table_name}` ({keys}) VALUES ({values})'
        with self.db.cursor() as cursor:
            cursor.execute(query, data)
            if hasattr(entity, 'id'):
                entity.id = cursor.lastrowid
        return entity

    def _update(self, entity: Model):
        data = {k: v for k, v in entity.to_dict().items() if not isinstance(v, dict)}
        del data['id']
        placeholders = ', '.join(map(lambda key: f'`{key}` = %({key})s', data.keys()))
        query = f'UPDATE `{self.table_name}` SET {placeholders} WHERE id = %(id)s'
        with self.db.cursor() as cursor:
            cursor.execute(query, {'id': entity.id, **data})
        return entity

    def remove(self, entity):
        query = f'DELETE from `{self.table_name}` WHERE id = %s'
        with self.db.cursor() as cursor:
            cursor.execute(query, [entity.id])
            self.db.commit()

    def project(self, model: Model, row):
        return {key: row.get(key) for key in model.fields() if row.get(key) is not None}


class ProfileRepo(BaseRepo):
    table_name = 'profiles'
    model_class = Profile


class DialogsRepo(BaseRepo):
    table_name = 'dialogs'
    model_class = Dialog

    def find_by_id(self, entity_id):
        dialog = super().find_by_id(entity_id)
        if not dialog:
            return None
        profiles = self._find_dialogs_participants([dialog.id])
        dialog.participants = profiles.get(dialog.id, [])
        return dialog

    def find_direct(self, profile_one, profile_two):
        query = f'''
            SELECT t.* from `{self.table_name}` as t
            JOIN dialogs_participants as dp1 on dp1.dialog_id = t.id
            JOIN dialogs_participants as dp2 on dp2.dialog_id = t.id
            WHERE t.type=%(type)s and dp1.profile_id=%(one)s and dp2.profile_id=%(two)s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'one': profile_one, 'two': profile_two, 'type': DialogType.DIRECT})
            if cursor.rowcount == 0:
                return None
            return self.model_class(**cursor.fetchone())

    def _find_dialogs_participants(self, dialogs_id):
        if not dialogs_id:
            return []
        profiles_query = f'''
           SELECT t.id, t.first_name, t.last_name, dp.dialog_id from `profiles` as t
           JOIN dialogs_participants as dp on dp.profile_id = t.id
           WHERE dp.dialog_id in %s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(profiles_query, [dialogs_id])
            profiles = defaultdict(list)
            for row in cursor.fetchall():
                profiles[row.pop('dialog_id')].append(Profile(**row))
            return profiles

    def find_dialogs(self, profile_id):
        dialogs_query = f'''
           SELECT t.* from `{self.table_name}` as t
           JOIN dialogs_participants as dp on dp.dialog_id = t.id
           WHERE dp.profile_id = %(profile_id)s
        '''
        with self.db.cursor() as cursor:
            cursor.execute(dialogs_query, {'profile_id': profile_id})
            dialogs = [self.model_class(**row) for row in cursor.fetchall()]
            profiles = self._find_dialogs_participants([d.id for d in dialogs])
            for dialog in dialogs:
                dialog.participants = profiles.get(dialog.id, [])

            return dialogs


class DialogMessagesRepo(BaseRepo):
    table_name = 'dialogs_messages'
    model_class = DialogMessage

    def find_by_dialog(self, dialog_id):
        query = f'''
           SELECT * from `{self.table_name}`
           WHERE dialog_id = %(dialog_id)s
           ORDER BY id ASC
        '''
        with self.db.cursor() as cursor:
            cursor.execute(query, {'dialog_id': dialog_id})
            return [self.model_class(**row) for row in cursor.fetchall()]


class DialogParticipantsRepo(BaseRepo):
    table_name = 'dialogs_participants'
    model_class = DialogParticipant

    def save(self, entity: Model):
        return super()._add(entity)

