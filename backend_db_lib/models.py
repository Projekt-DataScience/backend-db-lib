from sqlalchemy import (Column, Integer, String, ForeignKey, DateTime, Boolean)
from sqlalchemy.orm import declarative_base, relationship
from passlib.context import CryptContext

base = declarative_base()
PASSLIB_CONTEXT = CryptContext(
    # in a new application with no previous schemes, start with pbkdf2 SHA512
    schemes=['pbkdf2_sha512'],
    deprecated='auto',
)


class Company(base):
    __tablename__ = 'company'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    company_name = Column('company_name', String(100))


class User(base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    first_name = Column('first_name', String(50))
    last_name = Column('last_name', String(50))
    email = Column('email', String(50))
    password_hash = Column('password_hash', String(255))
    profile_picture_url = Column('profile_picture_url', String(255))

    # foreign keys
    supervisor_id = Column('supervisor_user_id', ForeignKey('user.id'), nullable=True)
    company_id = Column('company_id', Integer, ForeignKey('company.id'), nullable=False)
    role_id = Column('role_id', ForeignKey('role.id'), nullable=False)
    layer_id = Column('layer_id', ForeignKey('layer.id'), nullable=True)
    group_id = Column('group_id', ForeignKey('group.id'), nullable=True)

    # proxy bindings
    supervisor = relationship('User', foreign_keys='User.supervisor_id')
    company = relationship('Company', foreign_keys='User.company_id')
    role = relationship('Role', foreign_keys='User.role_id')
    layer = relationship('Layer', foreign_keys='User.layer_id')
    group = relationship('Group', foreign_keys='User.group_id')

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

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    role_name = Column('role_name', String(50))
    # todo: add permission string


class Group(base):
    __tablename__ = 'group'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    group_name = Column('group_name', String(100))

    #foreign keys
    company_id = Column('company_id', Integer, ForeignKey('company.id'), nullable=False)

    # proxy bindings
    company = relationship('Company', foreign_keys='Group.company_id')


class AuditQuestionAssociation(base):
    __tablename__ = 'audit_question_association'

    id = Column('id', Integer, primary_key=True, autoincrement=True)

    # foreign keys
    audit_id = Column("audit_id", ForeignKey("lpa_audit.id"))
    question_id = Column("question_id", ForeignKey("lpa_question.id"), nullable=False)

    # proxy bindings
    audit = relationship('LPAAudit', foreign_keys='AuditQuestionAssociation.audit_id')
    question = relationship('LPAQuestion', foreign_keys='AuditQuestionAssociation.question_id')


class Layer(base):
    __tablename__ = 'layer'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    layer_name = Column('layer_name', String(100))
    layer_number = Column('Layer_number', Integer)

    # foreign_keys
    company_id = Column('company_id', ForeignKey('company.id'), nullable=False)

    # proxy bindings
    company = relationship('Company', foreign_keys='Layer.company_id')


class LPAAudit(base):
    __tablename__ = 'lpa_audit'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    due_date = Column('due_date', DateTime)
    duration = Column('duration', Integer)
    recurrent_audit = Column('recurrent_audit', Boolean)

    # foreign keys
    created_by_user_id = Column('created_by_user_id', ForeignKey('user.id'), nullable=False)
    audited_user_id = Column('audited_user_id', ForeignKey('user.id'), nullable=False)
    auditor_user_id = Column('auditor_user_id', ForeignKey('user.id'), nullable=False)
    assigned_group_id = Column('assigned_group_id', ForeignKey('group.id'), nullable=False)
    assigned_layer_id = Column('assigned_layer_id', ForeignKey('layer.id'), nullable=False)

    # proxy bindings
    created_by = relationship('User', foreign_keys='LPAAudit.created_by_user_id')
    audited_user = relationship('User', foreign_keys='LPAAudit.audited_user_id')
    auditor = relationship('User', foreign_keys='LPAAudit.auditor_user_id')
    assigned_group = relationship('Group', foreign_keys='LPAAudit.assigned_group_id')
    assigned_layer = relationship('Layer', foreign_keys='LPAAudit.assigned_layer_id')

    # n m relationship
    questions = relationship("LPAQuestion", secondary='audit_question_association')


class LPAQuestionCategory(base):
    __tablename__ = 'lpa_question_category'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    category_name = Column('category_name', String(250))


class LPAQuestion(base):
    __tablename__ = 'lpa_question'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    question = Column('question', String(250))
    description = Column('description', String(250))

    # foreign keys
    category_id = Column('category_id', ForeignKey('lpa_question_category.id'), nullable=False)

    # proxy bindings
    category = relationship('LPAQuestionCategory', foreign_keys='LPAQuestion.category_id')


class LPAAnswer(base):
    __tablename__ = 'lpa_answer'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    answer = Column('answer', Integer)
    comment = Column('comment', String(250))


class LPAAnswerReason(base):
    __tablename__ = 'lpa_answer_reason'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    description = Column('description', String(250))


class LPAAuditRecurrenceType(base):
    __tablename__ = 'lpa_recurrence_type'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    description = Column('description', Integer)


class LPAAuditRecurrence(base):
    __tablename__ = 'lpa_audit_recurrence'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    value = Column('value', Integer)
    question_count = Column('question_count', Integer)

    # foreign keys
    group_id = Column('group_id', ForeignKey('group.id'), nullable=False)
    layer_id = Column('layer_id', ForeignKey('layer.id'), nullable=False)
    recurrence_type_id = Column('recurrence_type_id', ForeignKey('lpa_recurrence_type.id'),
                                nullable=False)

    # proxy bindings
    group = relationship('Group', foreign_keys='LPAAuditRecurrence.group_id')
    layer = relationship('Layer', foreign_keys='LPAAuditRecurrence.layer_id')
    recurrence_type = relationship('LPAAuditRecurrenceType', foreign_keys='LPAAuditRecurrence.recurrence_type_id')
