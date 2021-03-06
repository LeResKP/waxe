import os
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    ForeignKey,
    Table,
    Boolean,
    UniqueConstraint,
    PrimaryKeyConstraint,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
)

from zope.sqlalchemy import ZopeTransactionExtension
from sqla_declarative import extended_declarative_base
import tw2.sqla as tws
import tw2.forms as twf

from .validator import BCryptValidator

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = extended_declarative_base(DBSession)


ROLE_ADMIN = 'admin'
ROLE_EDITOR = 'editor'
ROLE_CONTRIBUTOR = 'contributor'
ROLE_SUPERVISOR = 'supervisor'

VERSIONING_PATH_STATUS_ALLOWED = 'allowed'
VERSIONING_PATH_STATUS_FORBIDDEN = 'forbidden'

MAX_FILE_NUMBER = 10


user_role = Table(
    'user_role',
    Base.metadata,
    Column('iduser', Integer, ForeignKey('user.iduser')),
    Column('idrole', Integer, ForeignKey('role.idrole')),
    UniqueConstraint('iduser', 'idrole', name='uc_user_role_iduser_idrole')
)



class UserGroup(Base):
    __tablename__ = 'user_group'
    __table_args__ = (
             PrimaryKeyConstraint('iduser', 'idgroup'),
             {},
         )
    iduser = Column(Integer, ForeignKey('user.iduser'))
    idgroup = Column(Integer, ForeignKey('group.idgroup'))

    user = relationship('User', uselist=False)


class Group(Base):
    __table_args__ = (
        UniqueConstraint('name', name='uc_group_name'),)

    idgroup = Column(Integer,
                     nullable=False,
                     autoincrement=True,
                     primary_key=True)
    name = Column(String(255),
                  nullable=False)
    owner_iduser = Column(Integer, ForeignKey('user.iduser'))

    usergroups = relationship('UserGroup', backref='group')


class Role(Base):
    __table_args__ = (
        UniqueConstraint('name', name='uc_role_name'),)

    idrole = Column(Integer,
                    nullable=False,
                    autoincrement=True,
                    primary_key=True)
    name = Column(String(255),
                  nullable=False)

    def __unicode__(self):
        return self.name


class User(Base):
    __table_args__ = (
        UniqueConstraint('login', name='uc_user_login'),)

    iduser = Column(Integer,
                    nullable=False,
                    autoincrement=True,
                    primary_key=True)
    login = Column(String(255),
                   nullable=False)
    password = Column(String(255),
                      nullable=True,
                      info={'edit_widget':
                            twf.PasswordField(validator=BCryptValidator),
                            'view_widget': tws.NoWidget,
                           }
                     )
    idconfig = Column(Integer,
                      ForeignKey('user_config.idconfig'),
                      nullable=True)
    trashed = Column(Boolean, nullable=False, default=False)

    roles = relationship('Role',
                         secondary=user_role,
                         backref='users')
    groups = relationship('Group',
                          primaryjoin='Group.owner_iduser==User.iduser',
                          backref='user')
    config = relationship('UserConfig',
                          backref=backref("user", uselist=False))
    versioning_paths = relationship('VersioningPath',
                                    info={'view_widget':
                                          tws.FactoryWidget(separator='<br />')},
                                    backref=backref("user", uselist=False))

    def __unicode__(self):
        return self.login

    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True
        return False

    def is_admin(self):
        return self.has_role(ROLE_ADMIN)

    def get_search_dirname(self):
        if not self.config or not self.config.root_path:
            return None
        return 'user-%s' % self.iduser

    def add_opened_file(self, path, iduser_owner=None):
        for f in self.opened_files:
            if path == f.path and iduser_owner == f.iduser_owner:
                # Remove occurence of the same path
                # We should not have more than one occurence since we don't
                # insert any duplicate.
                self.opened_files.remove(f)
                DBSession.delete(f)
                break
        o = UserOpenedFile(path=path, iduser=self.iduser,
                           iduser_owner=iduser_owner)
        self.opened_files.insert(0, o)
        self.opened_files = self.opened_files[:MAX_FILE_NUMBER]
        DBSession.add(o)

    def add_commited_file(self, path, iduser_commit=None):
        for f in self.commited_files:
            if path == f.path and f.iduser_commit == iduser_commit:
                # Remove occurence of the same path
                # We should not have more than one occurence since we don't
                # insert any duplicate.
                self.commited_files.remove(f)
                DBSession.delete(f)
                break
        o = UserCommitedFile(path=path, iduser=self.iduser,
                             iduser_commit=iduser_commit)
        self.commited_files.insert(0, o)
        self.commited_files = self.commited_files[:MAX_FILE_NUMBER]
        DBSession.add(o)


class UserConfig(Base):
    __tablename__ = 'user_config'

    idconfig = Column(Integer,
                      nullable=False,
                      primary_key=True)
    root_path = Column(String(255),
                       nullable=True)
    root_template_path = Column(String(255),
                                nullable=True)
    use_versioning = Column(Boolean, nullable=False, default=False)

    versioning_password = Column(
        String(255),
        nullable=True,
        info={'edit_widget':
              twf.PasswordField,
              'view_widget': tws.NoWidget}
    )

    def get_tws_view_html(self):
        return 'path: %s <br /> Versioning: %s' % (
            self.root_path,
            self.use_versioning)


class VersioningPath(Base):
    __tablename__ = 'versioning_path'

    idversioning_path = Column(Integer, nullable=False, primary_key=True)
    iduser = Column(Integer, ForeignKey('user.iduser'))
    status = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)

    def __unicode__(self):
        return '%s: %s' % (self.status, self.path)


class UserOpenedFile(Base):
    __tablename__ = 'user_opened_file'

    iduser_opened_file = Column(Integer,
                                nullable=False,
                                primary_key=True)
    iduser = Column(Integer, ForeignKey('user.iduser'))
    iduser_owner = Column(Integer, ForeignKey('user.iduser'))
    path = Column(String(255), nullable=False)

    user = relationship('User',
                        foreign_keys=[iduser],
                        backref=backref("opened_files"))

    user_owner = relationship(
        'User',
        foreign_keys=[iduser_owner],
    )


class UserCommitedFile(Base):
    __tablename__ = 'user_commited_file'

    iduser_commited_file = Column(Integer,
                                  nullable=False,
                                  primary_key=True)
    iduser = Column(Integer, ForeignKey('user.iduser'))
    # TODO: rename iduser_commit in iduser_owner. Also perhaps we can merge
    # table UserOpenedFile and UserCommitedFile
    iduser_commit = Column(Integer, ForeignKey('user.iduser'))
    path = Column(String(255), nullable=False)

    user = relationship('User',
                        foreign_keys=[iduser],
                        backref=backref("commited_files"))
    user_owner = relationship(
        'User',
        foreign_keys=[iduser_commit],
    )


def get_editors():
    role = DBSession.query(Role).filter_by(name=ROLE_EDITOR).one()
    return [u for u in role.users
            if not u.trashed and u.config and u.config.root_path]


def get_contributors():
    role = DBSession.query(Role).filter_by(name=ROLE_CONTRIBUTOR).one()
    return [u for u in role.users
            if not u.trashed and u.config and u.config.root_path]
