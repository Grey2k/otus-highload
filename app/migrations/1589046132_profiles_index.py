
def up(db):
    db.query('CREATE FULLTEXT INDEX ln_fn_idx on profiles(last_name, first_name)')


def down(db):
    db.query('ALTER TABLE profiles DROP index ln_fn_idx')
