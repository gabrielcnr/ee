from sqlalchemy import Column, String, JSON, create_engine, Integer, ForeignKey
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from ee.models import EnvironmentDefinition, ApplicationEnvironment, Application
from ee.store.gateway import EnvGateway

# ORM Models

Base = declarative_base()


class EnvDef(Base):
    __tablename__ = "env_def"

    id = Column(String(8), primary_key=True)  # short hash
    long_hash = Column(String(32), unique=True)
    env_def = Column(JSON, nullable=False)  # schema validation not enforced on the database layer

    app_envs = relationship("AppEnv", back_populates="env_def")


# TODO: audit trail?
class AppEnv(Base):
    __tablename__ = "app_env"

    id = Column(Integer, primary_key=True)
    app = Column(String(50))  # TODO: should have a table for apps?
    env_name = Column(String(50))
    env_def_id = Column(String(8), ForeignKey('env_def.id'))

    env_def = relationship("EnvDef", back_populates="app_envs")


# Gateway Implementation

class EnvSqliteGateway(EnvGateway):

    def __init__(self, session):
        self.session = session

    @classmethod
    def create(cls, db=""):
        engine = create_engine(f"sqlite://{db}", echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return cls(Session())

    def save_env_def(self, env_def: EnvironmentDefinition):
        new_env_def = EnvDef(id=env_def.id, long_hash=env_def.long_id, env_def=env_def.env_def)
        self.session.add(new_env_def)
        self.session.commit()

    def get_env_def(self, env_id: str) -> EnvironmentDefinition:
        try:
            env_def_orm_obj = self.session.query(EnvDef).filter(EnvDef.id == env_id).one()
        except NoResultFound:
            return None
        else:
            return self._env_def_from_orm_to_business_model(env_def_orm_obj)

    @classmethod
    def _env_def_from_orm_to_business_model(cls, env_def_orm_obj: EnvDef) -> EnvironmentDefinition:
        env_def = EnvironmentDefinition.from_dict(env_def_orm_obj.env_def)
        if env_def.id != env_def_orm_obj.id:  # sanity check
            raise EnvironmentPersistenceError(f"IDs do not match: {env_def.id = } != {env_def_orm_obj.id = }")
        return env_def

    def save_app_env(self, app_env: ApplicationEnvironment):
        app_env_orm = AppEnv(app=app_env.app.name, env_name=app_env.env, env_def_id=app_env.env_def.id)
        self.session.add(app_env_orm)
        self.session.commit()

    def get_app_env(self, app_name: str, env_name: str) -> ApplicationEnvironment:
        app_env_orm = self.session.query(AppEnv).filter(AppEnv.app == app_name,
                                                        AppEnv.env_name == env_name).one()
        env_def = self._env_def_from_orm_to_business_model(app_env_orm.env_def)
        app_env = ApplicationEnvironment(app=Application(app_env_orm.app),
                                         env=app_env_orm.env_name,
                                         env_def=env_def)
        return app_env


# Exceptions
class EnvironmentPersistenceError(Exception):
    pass
