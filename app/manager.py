from sqlalchemy import (create_engine)
from sqlalchemy.orm import sessionmaker
from .models import base, Company, User, Role, Layer, Group


class DatabaseManager:
    def __init__(self, database_base, database_url):
        self._base = database_base
        self._meta = database_base.metadata
        self._db = create_engine(database_url, echo=True)
        self.create_session = sessionmaker(self._db)

        # clean database
        self.drop_all()

        self._meta.create_all(self._db)
        self.create_initial_data()

    def drop_all(self):
        self._meta.drop_all(bind=self._db, tables=self.tables().values())

    def tables(self):
        return self._meta.tables

    def create_initial_data(self):
        with self.create_session() as session:
            # add company
            company = Company(
                id=None,
                company_name='Failed Venture. INC'
            )
            session.add(company)

            # add roles
            role_names = ['worker', 'ceo', 'admin']
            roles = [
                Role(
                    id=None,
                    role_name=x,
                ) for x in role_names
            ]
            for role in roles:
                session.add(role)

            # add groups
            group_names = ['Fertigung', 'QA', 'Marketing']
            groups = [
                Group(
                    id=None,
                    group_name=x,
                ) for x in group_names
            ]
            for group in groups:
                session.add(group)

            # flush, so ids of before created objects are filled
            session.flush()

            # add layers
            layer_names = ['Werkstatt', 'Office', 'Geschäftsführung']
            layers = [
                Layer(
                    id=None,
                    layer_name=x,
                    company_id=company.id,
                    layer_number=i,
                ) for i, x in enumerate(layer_names)
            ]
            for layer in layers:
                session.add(layer)

            session.flush()

            admin_user = User(
                id=None,
                first_name='Josef',
                last_name='Stahl',
                email='josef@test.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url=None,
                supervisor_id=None,
                company_id=company.id,
                role_id=roles[2].id,
                layer_id=None,
                group_id=None,
            )
            session.add(admin_user)

            ceo_user = User(
                id=None,
                first_name='Josef',
                last_name='Stahl',
                email='josef@test.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url=None,
                supervisor_id=None,
                company_id=company.id,
                role_id=roles[1].id,
                layer_id=layers[2].id,
                group_id=groups[2].id,
            )

            session.add(ceo_user)
            session.flush()

            # Worker
            session.add(User(
                id=None,
                first_name='Michl',
                last_name='Baum',
                email='michl@test.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url=None,
                supervisor_id=ceo_user.id,
                company_id=company.id,
                role_id=roles[0].id,
                layer_id=layers[0].id,
                group_id=groups[0].id,
            ))

            session.commit()
