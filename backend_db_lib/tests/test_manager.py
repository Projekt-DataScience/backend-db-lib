import unittest
from backend_db_lib.models import (
    base, User, Company, Role, Group,
    Layer, LPAQuestionCategory, LPAQuestion,
    LPAAnswerReason, LPAAudit, AuditQuestionAssociation,
    LPAAuditDuration, LPAAnswer
    )
from backend_db_lib.manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseManager(base, "sqlite:///test.db")   
        self.db.create_all()
        self.db.create_initial_data()

    def tearDown(self) -> None:
        self.db.drop_all()
        

    def test_database_intialize(self):

        models = [
            User, Company, Role, Group, Layer,
            LPAQuestionCategory, LPAQuestion, 
            LPAAnswerReason, LPAAudit, AuditQuestionAssociation, 
            LPAAuditDuration, LPAAnswer
        ]

        with self.db.create_session() as session:
            for model in models:
                self.__test_init(session, model)

    def __test_init(self, session, model):
        data = session.query(model).all()
        self.assertGreater(len(data), 0)


        

if __name__ == '__main__':
    unittest.main()