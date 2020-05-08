import glob
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from time import time

import click
from flask.cli import AppGroup


class Migrate:
    name = "migrate"

    def __init__(self, app, db):
        cmd_group = AppGroup(self.name)
        app.cli.add_command(cmd_group)
        path = os.path.join(app.root_path, app.config.get('MIGRATE_FOLDER', 'migrations'))
        migrate = _Migrate(db, path)

        @cmd_group.command()
        def init():
            """Инициализация директории и таблицы миграций"""
            migrate.init()

        @cmd_group.command()
        @click.argument('name')
        def create(name):
            """Создание файла миграций"""
            migrate.create(name)

        @cmd_group.command()
        def status():
            """Показать список миграций к применению"""
            migrate.status()

        @cmd_group.command()
        def up():
            """Применение новых миграций"""
            migrate.apply()

        @cmd_group.command()
        @click.option("--count", default=1)
        def down(count):
            """Откат --count миграций"""
            migrate.rollback(count)


class _MigrateFolder:
    def __init__(self, path):
        self.path = path

    def create(self):
        try:
            os.makedirs(self.path)
            click.echo(f"Directory `{self.path}` created")
        except FileExistsError:
            click.echo(f"Directory `{self.path}` already exists")
        except OSError as e:
            click.echo(e)

    def get_files(self):
        self.__change_work_dir()
        extension = ".py"
        mask = "*.py"
        return list(map(lambda x: x.replace(extension, ""), glob.glob(mask)))

    def create_file(self, name, content):
        self.__check_folder_exists()
        file_name = os.path.join(self.path, name)
        with open(file_name, "w") as f:
            f.write(content)

    def import_file(self, revision_name):
        self.__check_folder_exists()
        self.__change_work_dir()
        return __import__(revision_name)

    def __change_work_dir(self):
        sys.path.append(self.path)
        os.chdir(self.path)

    def __check_folder_exists(self):
        if not os.path.isdir(self.path):
            raise Exception("You should run flask migrate init")


class _Migrate:

    def __init__(self, db, path):
        self.db = db
        self.path = path
        self.folder = _MigrateFolder(path)
        self.repo = MigrationRepo(db)

    def init(self):
        self.repo.create_table()
        self.folder.create()

    def status(self):
        files = self.__get_unapplied_migrations()
        click.echo("Migrations for apply:")
        click.echo(files)

    def __get_unapplied_migrations(self):
        applied_migrations = self.repo.find_all()
        files = self.folder.get_files()
        for migration in applied_migrations:
            files.remove(migration.name)
        return files

    def apply(self):
        files = self.__get_unapplied_migrations()
        for file in files:
            revision = self.folder.import_file(file)
            revision.up(self.db)
            self.repo.insert_migration(file)
            click.echo(f"Up: {file}")

    def rollback(self, count):
        migrations = self.repo.find_last(count)
        click.echo("Next migrations will be down:")
        click.echo([m.name for m in migrations])
        if input("Are you sure[y/n]?: ") != "y":
            return
        for migration in migrations:
            revision = self.folder.import_file(migration.name)
            revision.down(self.db)
            self.repo.delete(migration.id)
            click.echo(f"Down: {migration.name}")

    def create(self, name):
        self.folder.create_file(f"{int(time())}_{name}.py", _migration_template)


class MigrationRepo:

    def __init__(self, db):
        self.db = db

    def create_table(self):
        self.db.query(
            '''CREATE TABLE IF NOT EXISTS `migrations` (
                id bigint auto_increment,
                name varchar(255) not null,
                created_at DATETIME default NOW(),
                constraint users_pk
                    primary key (id)
            )'''
        )

    def insert_migration(self, name):
        self.db.query('INSERT INTO `migrations` (`name`) VALUES (%s)', (name,))
        self.db.commit()

    def find_all(self):
        cur = self.db.query('SELECT * from migrations')
        return [Migration(**data) for data in cur.fetchall()]

    def find_last(self, count):
        cur = self.db.query('SELECT * from migrations ORDER BY id DESC LIMIT %s', (count,))
        return [Migration(**data) for data in cur.fetchall()]

    def delete(self, id):
        self.db.query('DELETE from migrations where id=%s', (id,))
        self.db.commit()


@dataclass
class Migration:
    id: int
    name: str
    created_at: datetime


_migration_template = """
def up(db):
    pass


def down(db):
    pass
"""
