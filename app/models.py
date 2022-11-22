from sqlalchemy import (Column, Integer, String,
                        create_engine, ForeignKey, DateTime, Boolean)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from passlib.context import CryptContext

base = declarative_base()
PASSLIB_CONTEXT = CryptContext(
    # in a new application with no previous schemes, start with pbkdf2 SHA512
    schemes=['pbkdf2_sha512'],
    deprecated='auto',
)

class Company(base):
    __tablename__ = 'company'

    company_id = Column('CompanyID', Integer, primary_key=True, autoincrement=True)
    company_name = Column('CompanyName', String(100))


class User(base):
    __tablename__ = 'user'

    user_id = Column('UserID', Integer, primary_key=True, autoincrement=True)
    first_name = Column('FirstName', String(50))
    last_name = Column('LastName', String(50))
    email = Column('Email', String(50))
    password_hash = Column('PasswordHash', String(255))
    profile_picture_url = Column('ProfilePictureURL', String(255))
    supervisor_user_id = Column('SupervisorUserID', ForeignKey('user.UserID'))
    company_id = Column('CompanyID', Integer, ForeignKey('company.CompanyID'))
    role_id = Column('RoleID', ForeignKey('role.RoleID'))

    @property
    def password(self):
        raise AttributeError('User.password is write-only')

    @password.setter
    def password(self, password):
        self.password_hash = self.generate_hash(password)

    def verify_password(self, password):
        return PASSLIB_CONTEXT.verify(password, self.password_hash)

    @staticmethod
    def generate_hash(password):
        return PASSLIB_CONTEXT.hash(password.encode('utf8'))



class Role(base):
    __tablename__ = 'role'
    role_id = Column('RoleID', Integer, primary_key=True, autoincrement=True)
    role_name = Column('RoleName', String(50))


class Group(base):
    __tablename__ = 'group'
    group_id = Column('GroupID', Integer, primary_key=True, autoincrement=True)
    group_name = Column('GroupName', String(100))


class Audit(base):
    __tablename__ = 'audit'
    audit_id = Column('AuditID', Integer, primary_key=True, autoincrement=True)
    due_date = Column('DueDate', DateTime)
    duration = Column('Duration', Integer)
    recurrent_audit = Column('RecurrentAudit', Boolean)
    created_by = Column('CreatedBy', ForeignKey('user.UserID'))
    audited_user = Column('AuditedUser', ForeignKey('user.UserID'))
    auditor = Column('Auditor', ForeignKey('user.UserID'))
    assigned_group = Column('AssignedGroup', ForeignKey('group.GroupID'))
    questions = relationship('lpa_question_audit')


class Layer(base):
    __tablename__ = 'layer'
    layer_id = Column('LayerID', Integer, primary_key=True, autoincrement=True)
    layer_name = Column('LayerName', String(100))
    layer_number = Column('LayerNumber', Integer)

class LPAQuestionCategory(base):
    __tablename__ = 'lpa_question_audit_category'
    category_id = Column('LPAQuestionAuditCategoryID', Integer, primary_key=True, autoincrement=True)
    category_name = Column('Category', String(250))


class LPAQuestion(base):
    __tablename__ = 'lpa_question_audit'
    group_id = Column('QuestionID', Integer, primary_key=True, autoincrement=True)
    question = Column('Question', String(250))
    description = Column('Description', String(250))
    category_id = Column('CategoryID', ForeignKey('lpa_question_audit_category.LPAQuestionAuditCategoryID'))


class LPAAnswer(base):
    __tablename__ = 'lpa_answer'
    answer_id = Column('LPAAnswerID', Integer, primary_key=True, autoincrement=True)
    answer = Column('Answer', Integer)
    comment = Column('Comment', String(250))


class LPAAnswerReason(base):
    __tablename__ = 'lpa_answer_reason'
    answer_reason_id = Column('LPAAnswerReasonID', Integer, primary_key=True, autoincrement=True)
    description = Column('Description', String(250))


class LPAAuditRecurrenceType(base):
    __tablename__ = 'lpa_audit_recurrence_type'
    recurrence_type_id = Column('LPAAuditRecurrenceTypeID', Integer, primary_key=True, autoincrement=True)
    description = Column('Description', Integer)


class LPAAuditRecurrence(base):
    __tablename__ = 'lpa_audit_recurrence'
    recurrence_id = Column('LPAAuditRecurrenceID', Integer, primary_key=True, autoincrement=True)
    value = Column('Value', Integer)
    question_count = Column('LPAQuestionCount', Integer)
    group_id = Column('GroupID', ForeignKey('group.GroupID'))
    recurrence_type_id = Column('RecurrenceTypeID', ForeignKey('lpa_audit_recurrence_type.LPAAuditRecurrenceTypeID'))




class DatabaseManager:
    def __init__(self, database_url):
        db = create_engine(database_url, echo=True)
        self.create_session = sessionmaker(db)
        base.metadata.create_all(db)
        self.create_initial_data()

    def create_initial_data(self):
        with self.create_session() as session:
            comp = Company(
                company_id=None,
                company_name='Failed Venture. INC'
            )
            session.add(comp)
            role = Role(
                role_id=None,
                role_name='Admin',
            )
            session.add(role)

            session.add(User(
                user_id=None,
                first_name='Franz',
                last_name='Xaver',
                email='franz@hans.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url=None,
                supervisor_user_id=None,
                company_id=comp.company_id,
                role_id=role.role_id,
            ))
            session.commit()