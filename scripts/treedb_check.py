# treedb_check.py - check glottolog-specific invariants

from __future__ import unicode_literals

import itertools

import sqlalchemy as sa

import treedb_backend as _backend
from treedb import Languoid

FAMILY, LANGUAGE, DIALECT = 'family', 'language', 'dialect'

BOOKKEEPING = 'Bookkeeping'

SPECIAL_FAMILIES = (
    'Unattested',
    'Unclassifiable',
    'Pidgin',
    'Mixed Language',
    'Artificial Language',
    'Speech Register',
    'Sign Language',
)

DUMMY_SESSION = sa.orm.scoped_session(sa.orm.sessionmaker(bind=None))

CHECKS = []


def main(make_session=_backend.Session):
    for check_cls in CHECKS:
        session = make_session()
        check = check_cls(session)
        try:
            check.validate()
        finally:
            session.close()


def check(func):
    cls = type('%sCheck' % func.__name__, (Check,), {'invalid_query': staticmethod(func)})
    CHECKS.append(cls)
    return cls


class Check(object):

    detail = True

    def __init__(self, session=DUMMY_SESSION):
        self.session = session
        self.query = self.invalid_query(session)

    def invalid_query(self, session):
        raise NotImplementedError

    def validate(self):
        self.invalid_count = self.query.count()
        print(self)
        if self.invalid_count:
            if self.detail:
                self.invalid = self.query.all()
                self.show_detail(self.invalid, self.invalid_count)
            return False
        else:
            self.invalid = []
            return True

    def __str__(self):
        if self.invalid_count:
            msg = '%d invalid\n    (violating %s)' % (self.invalid_count, self.__doc__)
        else:
            msg = 'OK'
        return '%s: %s' % (self.__class__.__name__, msg)

    @staticmethod
    def show_detail(invalid, invalid_count, number=25):
        ids = (i.id for i in itertools.islice(invalid, number))
        cont = ', ...' if number < invalid_count else ''
        print('    %s%s' % (', '.join(ids), cont))


@check
def dialect_parent(session):
    """Parent of a dialect is a language or dialect."""
    return session.query(Languoid).filter_by(level=DIALECT).order_by('id')\
        .join(Languoid.parent, aliased=True)\
        .filter(Languoid.level.notin_([LANGUAGE, DIALECT]))


@check
def family_children(session):
    """Family has at least one subfamily or language."""
    return session.query(Languoid).filter_by(level=FAMILY).order_by('id')\
        .filter(~Languoid.children.any(
            Languoid.level.in_([FAMILY, LANGUAGE])))



def family_languages(session, exclude=SPECIAL_FAMILIES):
    """Family has at least two languages."""
    child = sa.orm.aliased(Languoid)
    return
    #session.query(Languoid).filter_by(level='FAMILY').order_by('id')\
    #    .filter(Languoid.family.has(Languoid.name.notin_(exclude)))\
    #    .join(TreeClosureTable, TreeClosureTable.parent_pk == Languoid.pk)\
    #    .outerjoin(child, and_(
    #        TreeClosureTable.child_pk == child.pk,
    #        TreeClosureTable.depth > 0,
    #        child.level == LanguoidLevel.language))\
    #    .group_by(Language.pk, Languoid.pk)\
    #    .having(func.count(child.pk) < 2)\


@check
def bookkeeping_no_children(session):
    """Bookkeeping languoids lack children."""
    return session.query(Languoid).order_by('id')\
        .filter(Languoid.parent.has(name='Bookkeeping'))\
        .filter(Languoid.children.any())


if __name__ == '__main__':
    main()