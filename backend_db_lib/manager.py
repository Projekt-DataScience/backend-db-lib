import random
import string

from datetime import datetime, timedelta

from sqlalchemy import (create_engine)
from sqlalchemy.orm import sessionmaker
from .models import Company, User, Role, Layer, Group, LPAQuestionCategory, LPAQuestion, LPAAnswerReason, LPAAudit, AuditQuestionAssociation, LPAAuditDuration, LPAAnswer

from .recurrence import RecurrenceHelper, RECURRENCE_TYPES, WEEKLY_TYPES, YEARLY_TYPES


class DatabaseManager:
    def __init__(self, database_base, database_url):
        self._base = database_base
        self._meta = database_base.metadata
        self._db = create_engine(database_url, echo=True)
        self.create_session = sessionmaker(self._db)

        # clean database
        #self.drop_all()

        #self._meta.create_all(self._db)
        #self.create_initial_data()

    def create_all(self):
        self._meta.create_all(self._db)

    def drop_all(self):
        self._meta.drop_all(bind=self._db, tables=self.tables().values())

    def tables(self):
        return self._meta.tables

    def create_initial_data(self):
        with self.create_session() as session:
            profile_picture_url = "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"

            # add company
            company = Company(
                id=None,
                company_name='Failed Venture. INC'
            )
            session.add(company)
            session.commit()

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

            session.flush()
            session.commit()

            # add groups
            group_names = ['Fertigung', 'QA', 'Marketing']
            groups = [
                Group(
                    id=None,
                    group_name=x,
		    company_id=company.id
                ) for x in group_names
            ]
            for group in groups:
                session.add(group)

            # flush, so ids of before created objects are filled
            session.flush()
            session.commit()

            # add layers
            layer_names = ['Werkstatt', 'Office', 'Gesch??ftsf??hrung']
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
            session.commit()

            admin_user = User(
                id=None,
                first_name='Josef',
                last_name='Stahl',
                email='josef@test.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url=profile_picture_url,
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
                profile_picture_url="https://images.unsplash.com/photo-1628890920690-9e29d0019b9b?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",
                supervisor_id=None,
                company_id=company.id,
                role_id=roles[1].id,
                layer_id=layers[2].id,
                group_id=groups[2].id,
            )

            session.add(ceo_user)
            session.flush()
            session.commit()

            # Worker
            worker_user = User(
                id=None,
                first_name='Michl',
                last_name='Baum',
                email='michl@test.de',
                password_hash=User.generate_hash('test'),
                profile_picture_url="https://images.unsplash.com/photo-1639747280804-dd2d6b3d88ac?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",
                supervisor_id=ceo_user.id,
                company_id=company.id,
                role_id=roles[0].id,
                layer_id=layers[0].id,
                group_id=groups[0].id,
            )
            session.add(worker_user)
            session.flush()
            session.commit()

            CATEGORIES = ['Umwelt', 'Energie', 'Wirtschaftlichkeit', 'Qualit??t', 'Arbeitssicherheit', 'Fragengruppe']
            for category in CATEGORIES:
                session.add(LPAQuestionCategory(
                    category_name=category
                ))
            session.flush()
            session.commit()

            questions = [{'question': 'Sind Masterteile / Referenzteile verwechslungssicher gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Sind Brandschutzt??ren blockiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden Erstst??ck- und Letztst??ckfreigaben dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Tropft ??l oder ??hnliches aus der Maschine?', 'category': 'Umwelt'}, {'question': 'Ist der Arbeitsbereich frei von Einstellteilen? ', 'category': 'Qualit??t'}, {'question': 'Werden Ausschussbeh??lter regelm????ig geleert?', 'category': 'Qualit??t'}, {'question': 'Werden wassergef??hrdete Stoffe ausschlie??lich auf Auffangwannen gelagert?', 'category': 'Umwelt'}, {'question': 'Tropft ??l oder ??hnliches aus der Maschine?', 'category': 'Energie'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht ??berbr??ckt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist sichergestellt, dass Einstellparameter nicht unbeabsichtigt verstellt werden k??nnen?', 'category': 'Qualit??t'}, {'question': 'Werden Erstst??ck- und Letztst??ckfreigaben dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Sind die Pr??fintervalle klar definiert?', 'category': 'Qualit??t'}, {'question': 'H??ngen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Wurden alle Oberfl??chenmessungen dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Sind die Schaltschrankt??ren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Wird die Konzentration von K??hlschmierstoffen regelm????ig gepr??ft?', 'category': 'Umwelt'}, {'question': 'Sind die roten Ausschussbeh??ltnisse gegen direkten Zugriff gesichert', 'category': 'Qualit??t'}, {'question': 'Werden die Maschinenlogb??cher gef??hrt? Sind diese aktuell?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege frei von Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist der Reinigungsplan ausgef??llt?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die aktuelle Zeichnung am Arbeitsplatz ausgeh??ngt?', 'category': 'Qualit??t'}, {'question': 'K??nnen alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualit??t'}, {'question': 'Ist die Bauteilbeschriftung, die aufgebracht wurde, problemlos lesbar?', 'category': 'Qualit??t'}, {'question': 'Ist geregelt wie Bauteile zur??ckgelagert werden m??ssen? ', 'category': 'Qualit??t'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Auftr??ge abgearbeitet werden m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teile?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualit??t'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'K??nnen alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Energie'}, {'question': 'Wissen Sie was zu tun ist wenn ein Merkmal am Bauteil n.i.O. ist?', 'category': 'Qualit??t'}, {'question': 'Sind alle fertigungsrelevanten Normen der Zeichnung aufgeschl??sselt, oder sind diese zug??nglich?', 'category': 'Qualit??t'}, {'question': 'Werden Produktionsauftr??ge und Arbeitsg??nge korrekt gemeldet?', 'category': 'Qualit??t'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualit??t'}, {'question': 'Haben Fertigungs- und Pr??fanweisungen einen g??ltigen Status?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschuss und Einstellteile im Terminal gemeldet?', 'category': 'Qualit??t'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualit??t'}, {'question': 'Werden ausschlie??lich Nachtragskarten verwendet? ', 'category': 'Energie'}, {'question': 'Werden gefallene Teile von jedem Mitarbeiter ausgeschleust? ', 'category': 'Qualit??t'}, {'question': 'Gibt es an jedem Arbeitsplatz einen klar gekennzeichneten Ausschussbeh??lter?', 'category': 'Qualit??t'}, {'question': 'Ist eine Fertigungszeichnung in DIN A3 am Arbeitsplatz vorhanden?', 'category': 'Qualit??t'}, {'question': 'Schalten Sie die Computer/Bildschirme zum Feierabend aus?', 'category': 'Energie'}, {'question': 'Ablenkungen w??hrend meiner Montaget??tigkeit schaden der Qualit??t, selbst wenn es sich um den Meister handelt. Wenn mich jemand bei der Arbeit unterbrechen will, weise ich ihn h??flich daraufhin.', 'category': 'Qualit??t'}, {'question': 'Pr??fen Sie die Sauberkeit der Blister, bevor Sie diese verwenden?', 'category': 'Qualit??t'}, {'question': 'Sind die Schaltschrankt??ren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle fertigungsrelevanten Normen der Zeichnung aufgeschl??sselt, oder sind diese zug??nglich?', 'category': 'Qualit??t'}, {'question': 'Wechseln Sie regelm????ig (min. 1x pro Woche) Ihre Handschuhe?', 'category': 'Qualit??t'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Qualit??t'}, {'question': 'Haben Hebevorrichtungen einen g??ltigen Status? Z.B. Ameise', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Z.B. Kardex Lichtschranke', 'category': 'Arbeitssicherheit'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Ausschussbeh??lter regelm????ig geleert?', 'category': 'Qualit??t'}, {'question': 'Stimmen die Laufzeiten? ', 'category': 'Qualit??t'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist Rohmaterial eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Ist der Arbeitsbereich frei von Einstellteilen? ', 'category': 'Qualit??t'}, {'question': 'Tropft ??l oder ??hnliches aus der Maschine?', 'category': 'Qualit??t'}, {'question': 'Sind Kabel und sonstige Stromf??hrungen frei von Besch??digungen?', 'category': 'Qualit??t'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitstische frei von Lebensmittel', 'category': 'Qualit??t'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Sind die Hauptwege frei von Besch??digungen, ??llachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist das Mindesthalbarkeitsdatum von O-Ringen erkennbar?', 'category': 'Qualit??t'}, {'question': 'Sind die Hauptwege frei von Besch??digungen, ??llachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Umwelt'}, {'question': 'Sind die Schicht??bergabeprotokolle ausgef??llt?', 'category': 'Qualit??t'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel die 5S-Standards eingehalten?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind auch Beinahe-Unf??lle dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Wird die Konzentration von K??hlschmierstoffen regelm????ig gepr??ft?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege den Mitarbeitern bekannt?', 'category': 'Qualit??t'}, {'question': 'Sind die Arbeitstische frei von Lebensmitteln?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualit??t'}, {'question': 'Gibt es an jedem Arbeitsplatz einen klar gekennzeichneten Ausschussbeh??lter?', 'category': 'Qualit??t'}, {'question': 'Tragen Sie beim Umgang mit metallischen Bauteilen Handschuhe?', 'category': 'Qualit??t'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualit??t'}, {'question': 'Werden ??lige Putzlappen ausschlie??lich in daf??r vorgesehene Beh??lter gesammelt?', 'category': 'Qualit??t'}, {'question': 'Ist ausreichend Verpackungsmateriall f??r Fertigteile vorhanden?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschussbeh??lter regelm????ig geleert?', 'category': 'Qualit??t'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle?', 'category': 'Qualit??t'}, {'question': 'Ist die Verpackung von Werkst??cken/Fertigteilen geregelt/definiert?', 'category': 'Qualit??t'}, {'question': 'Werden Produktionsauftr??ge und Arbeitsg??nge gemeldet?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualit??t'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualit??t'}, {'question': 'Wissen die Mitarbeiter, was bei einer Abweichung im Prozess zu tun ist?', 'category': 'Qualit??t'}, {'question': 'Ist eine Tischkennzeichnung "gepr??f" - "ungepr??ft" vorhanden? ', 'category': 'Qualit??t'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel die 5S-Standards eingehalten?', 'category': 'Qualit??t'}, {'question': 'Werden die Pr??fmittel am Arbeitsplatz regelm????ig ??berpr??ft/justiert?', 'category': 'Qualit??t'}, {'question': 'Finden die Shopfloorstehenungen regelm????ig statt, ist die Anwesenheitsliste gef??hrt?', 'category': 'Qualit??t'}, {'question': 'Gibt es besch??digte oder defekte Pr??fmittel am Arbeitsplatz?', 'category': 'Qualit??t'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualit??t'}, {'question': 'Sind alle Kisten/Gitterk??rbe fortlaufend nummeriert (Hydac)?', 'category': 'Qualit??t'}, {'question': 'Darf der Mitarbeiter den Prozess stoppen, wenn er einen Fehler feststellt?', 'category': 'Qualit??t'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualit??t'}, {'question': 'Finden die Shopfloorstehenungen regelm????ig statt, ist die Anwesenheitsliste gef??hrt?', 'category': 'Qualit??t'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Kabel und sonstige Stromf??hrungen frei von Besch??digungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es dokumentierte Vorgaben f??r das manuelle Entgraten?', 'category': 'Qualit??t'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teilen?', 'category': 'Qualit??t'}, {'question': 'Haben Sie 100% Messungen? Sind diese vorgeschrieben und dokumentiert? F??hren Sie diese durch?', 'category': 'Qualit??t'}, {'question': 'Sind alle Verletzungen im Verbandsbuch dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind auch Beinahe-Unf??lle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie, ob ein Lunker i.O. oder n.i.O. ist? (Schulung, Fehlerkatalog)', 'category': 'Arbeitssicherheit'}, {'question': 'Wurden Sie auf den Standard "Safe Launch" geschult - Wissen Sie was zu tun ist?', 'category': 'Qualit??t'}, {'question': 'Sind alle Fluchtwege frei zug??nglich?', 'category': 'Qualit??t'}, {'question': 'Ist jedem Mitarbeiter der Wiederanlaufprozess bekannt?', 'category': 'Qualit??t'}, {'question': 'Befindet sich an Ihrem Arbeitsplatz ein rotes Ausschussbeh??ltniss?', 'category': 'Qualit??t'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teilen?', 'category': 'Qualit??t'}, {'question': 'Sind Kabel und sonstige Stromf??hrungen frei von Besch??digungen? (Blanke Kabel?)', 'category': 'Arbeitssicherheit'}, {'question': 'Werden ??lige Putzlappen ausschlie??lich in daf??r vorgesehene Beh??lter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Kennen Sie die  SFB Qualit??tspolitik?', 'category': 'Qualit??t'}, {'question': 'Sind die Feuerl??scher zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualit??t'}, {'question': 'K??nnen alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualit??t'}, {'question': 'Sind Gefahrstoffbeh??lter als solche gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualit??t'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualit??t'}, {'question': 'Sind Ihnen die Fluchtwege bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualit??t'}, {'question': 'Befinden Trinkflaschen nur in den daf??r vorgesehenen Flaschenhaltern?', 'category': 'Qualit??t'}, {'question': 'Sind auch Beinahe-Unf??lle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Fluchtwege frei zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Kennen Sie die  SFB Qualit??tspolitik?', 'category': 'Qualit??t'}, {'question': 'Kennen Sie die  SFB Qualit??tspolitik?', 'category': 'Qualit??t'}, {'question': 'Sind die Arbeitstische frei von Lebensmittel', 'category': 'Qualit??t'}, {'question': 'Ist die Zeichnung gut lesbar?', 'category': 'Qualit??t'}, {'question': 'Sind alle Fluchtwege frei zug??nglich', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es an Ihrem Arbeitsplatz einen klar gekennzeichneten Ausschussbeh??lter?', 'category': 'Qualit??t'}, {'question': 'Befinden sich die von Ihnen kommissionierte Ware in den vorgeschriebenen Bereichen?', 'category': 'Qualit??t'}, {'question': 'Gibt es besch??digte oder defekte Pr??fmittel am Arbeitsplatz?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie was Sie tun m??ssen wenn keine Arbeitsanweisung vorhanden ist?', 'category': 'Qualit??t'}, {'question': 'Ist eine Fertigungszeichnung in DIN A3 am Arbeitsplatz vorhanden?', 'category': 'Qualit??t'}, {'question': 'Werden die Verpackungseinheiten von Beh??ltnissen eingehalten?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Pr??fen Sie Ihre Messmittel vor Arbeitsbeginn? (Toleranz kleiner 0,05mm)', 'category': 'Qualit??t'}, {'question': 'Sind alle Fluchtwege frei zug??nglich', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Aush??nge oder Anweisungen im Fertigungsbereich ausschlie??lich gelenkte Dokumente?', 'category': 'Qualit??t'}, {'question': 'F??hren Sie/Ihre Kollegen beim Abr??umen eine 100% Pr??fung durch?', 'category': 'Qualit??t'}, {'question': 'Haben Sie 100% Messungen? Sind diese vorgeschrieben und dokumentiert? F??hren Sie diese durch?', 'category': 'Qualit??t'}, {'question': 'Haben Hebevorrichtungen einen g??ltigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Masterteile / Referenzteile verwechslungssicher gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Gibt es einen klar definierten Reinigungsplan f??r den Arbeitsplatz.', 'category': 'Qualit??t'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Pr??fplakette?', 'category': 'Qualit??t'}, {'question': 'Sind alle Werkzeuge wie Schraubenschl??ssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Produktionsauftr??ge und Arbeitsg??nge korrekt gemeldet?', 'category': 'Qualit??t'}, {'question': 'Wurden Sie/Ihre Kollegen auf den Standard "R??cksortierung" geschult?', 'category': 'Qualit??t'}, {'question': 'Wurden Sie/Ihre Kollegen auf den Standard "SafeLaunch" geschult?', 'category': 'Qualit??t'}, {'question': 'Werden die Bauteile beim Abr??umen in den vorgeschriebenen Messbereich gelegt?', 'category': 'Qualit??t'}, {'question': 'Ist eine Tischkennzeichnung "gepr??ft" und "ungepr??ft" vorhanden?', 'category': 'Qualit??t'}, {'question': 'F??hren Sie beim Abr??umen eine Sichtpr??fung am letzten Teil durch?', 'category': 'Qualit??t'}, {'question': 'F??hren Sie die Pr??fungen laut Maschinenplatzpr??fplan durch?', 'category': 'Qualit??t'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualit??t'}, {'question': 'Ist eine Lupe am Messtisch vorhanden?', 'category': 'Qualit??t'}, {'question': 'F??hren Sie bei Fehlbest??nden eine Inventurbuchung durch?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind alle Kisten fortlaufend nummeriert?', 'category': 'Qualit??t'}, {'question': 'Werden die Ergebnisse des Safelaunch im PC gespeichert?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschussbeh??lter regelm????ig geleert?', 'category': 'Qualit??t'}, {'question': 'Sind Aush??nge oder Anweisungen im Fertigungsbereich ausschlie??lich gelenkte Dokumente?', 'category': 'Qualit??t'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Auftr??ge abgearbeitet werden m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Pr??fplakette? Z.B. Die Waage', 'category': 'Qualit??t'}, {'question': 'Sind die Z??hlwaagen frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Sind die Wiegebeh??lter frei von Schmutz/ sauber?', 'category': 'Qualit??t'}, {'question': 'Sind Pr??fvorrichtungen frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Bearbeiten Sie die Auftr??ge der Reihe nach ab? Keine Gleichzeitige Bearbeitung der Auftr??ge!', 'category': 'Qualit??t'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschussteile dokumentiert/abgeschrieben?', 'category': 'Qualit??t'}, {'question': 'Ist die Zeichnung gut lesbar? ', 'category': 'Qualit??t'}, {'question': 'Wird das Mindesthalbarkeitsdatum von O-Ringen eingehalten?', 'category': 'Qualit??t'}, {'question': 'Werden gefallene Teile von Ihnen ausgeschleust/verschrottet? ', 'category': 'Qualit??t'}, {'question': 'Sind die Feuerl??scher zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden sich offene Getr??nke auf den Arbeitsfl??chen?', 'category': 'Qualit??t'}, {'question': 'Haben alle vorhandenen Messmittel eine Pr??fmittelnummer?', 'category': 'Qualit??t'}, {'question': 'Sind Pr??fvorrichtungen frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Sind Sie an diesem Arbeitsplatz geschult?', 'category': 'Qualit??t'}, {'question': 'Halten Sie beim Auslagern FIFO ein?', 'category': 'Qualit??t'}, {'question': 'Sind Brandschutzt??ren frei von Behinderungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden Trinkflaschen nur in den daf??r vorgesehenen Flaschenhaltern?', 'category': 'Qualit??t'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen? Eindeutige Kennzeichnung der Beh??ltnisse?', 'category': 'Qualit??t'}, {'question': 'Werden die Arbeits- Pausenzeiten eingehalten?', 'category': 'Qualit??t'}, {'question': 'Kennen Sie die  SFB Qualit??tspolitik?', 'category': 'Qualit??t'}, {'question': 'Befinden Trinkflaschen nur in den daf??r vorgesehenen Flaschenhaltern?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualit??t'}, { 'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualit??t'}, {'question': 'Sind Kabel und sonstige Stromf??hrungen frei von Besch??digungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden die Verpackungseinheiten von Beh??ltnissen eingehalten?', 'category': 'Qualit??t'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualit??t'}, {'question': 'Werden die Maschinenlogb??cher gef??hrt? Sind diese aktuell?', 'category': 'Qualit??t'}, {'question': 'Pr??fen Sie die Sauberkeit der Blister, bevor Sie diese f??r den Ablageplan verwenden?', 'category': 'Qualit??t'}, {'question': 'Darf der Mitarbeiter den Prozess stoppen, wenn er einen Fehler feststellt?', 'category': 'Qualit??t'}, {'question': 'Finden die Shopfloorstehenungen regelm????ig statt, ist die Anwesenheitsliste gef??hrt?', 'category': 'Qualit??t'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualit??t'}, {'question': 'Werden Messmittel (Millime??, Messschieber, etc.) regelm????ig justiert/genullt?', 'category': 'Qualit??t'}, {'question': 'Ist der vorliegende Zeichnungsstand aktuell?', 'category': 'Qualit??t'}, {'question': 'Sind die Arbeitstische frei von Lebensmitteln?', 'category': 'Qualit??t'}, {'question': 'Ist sichergestellt, dass nur die ben??tigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualit??t'}, {'question': 'Ist die aktuelle Zeichnung am Arbeitsplatz ausgeh??ngt?', 'category': 'Qualit??t'}, {'question': 'Haben alle vorhandenen Messmittel eine Pr??fmittelnummer?', 'category': 'Qualit??t'}, {'question': 'Finden die Shopfloorstehungen regelm????ig statt, ist die Anwesenheitsliste gef??hrt?', 'category': 'Qualit??t'}, {'question': 'Sind Aush??nge oder Anweisungen im Fertigungsbereich ausschlie??lich gelenkte Dokumente?', 'category': 'Energie'}, {'question': 'Werden wassergef??hrdete Stoffe ausschlie??lich auf Auffangwannen gelagert?', 'category': 'Qualit??t'}, {'question': 'Sind die Pr??fintervalle klar definiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie was zu tun ist, wenn Teile nicht montagef??hig sind?', 'category': 'Qualit??t'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Qualit??t'}, {'question': 'Werden Pr??feinrichtungen regelm????ig ??berpr??ft? Check the Checker?', 'category': 'Qualit??t'}, {'question': 'Sind Gefahrstoffbeh??lter als solche gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Stimmen die Laufzeiten/Taktzeiten f??r den aktuellen Auftrag?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden die Verpackungseinheiten von Beh??ltnissen eingehalten?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Ungekennzeichnete Bauteile m??ssen dem Abteilungsmeister gemeldet werden.', 'category': 'Qualit??t'}, {'question': 'Werden wassergef??hrdete Stoffe ausschlie??lich auf Auffangwannen gelagert?', 'category': 'Umwelt'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualit??t'}, {'question': 'Haben Arbeitsanweisungen einen g??ltigen Status?', 'category': 'Qualit??t'}, {'question': 'Wissen die Mitarbeiter, was bei einer Abweichung im Prozess zu tun ist?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die Verpackung von Werkst??cken/Fertigteilen geregelt/definiert?', 'category': 'Umwelt'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden gefallene Teile von Ihnen ausgeschleust/verschrottet? ', 'category': 'Qualit??t'}, {'question': 'Sind die Feuerl??scher zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Tragen Sie beim Umgang mit metallischen Bauteilen Handschuhe?', 'category': 'Qualit??t'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Produktionsauftr??ge und Arbeitsg??nge korrekt gemeldet?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualit??t'}, {'question': 'Stimmen alle fertigungsbegleitenden Dokumente mit dem aktuellen Zeichnungsstand ??berein?', 'category': 'Qualit??t'}, {'question': 'Sind die Pr??fintervalle klar definiert?', 'category': 'Qualit??t'}, {'question': 'Sind die korrekten Werkzeuge im Einsatz? ', 'category': 'Qualit??t'}, {'question': 'Ist ausreichend Verpackungsmateriall f??r Fertigteile vorhanden?', 'category': 'Qualit??t'}, {'question': 'Sind  alle Dokumente der St??ckliste f??r Sie zug??nglich?', 'category': 'Qualit??t'}, {'question': 'Sind Pr??fvorrichtungen frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Sind die Schaltschrankt??ren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualit??t'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Sind Gefahrstoffbeh??lter als solche gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Gibt es in Ihrem Arbeitsbereich einen klar gekennzeichneten Ausschussbeh??lter?', 'category': 'Qualit??t'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel der 5S-Standard eingehalten?', 'category': 'Qualit??t'}, {'question': 'Ungekennzeichnete Bauteile m??ssen dem Abteilungsmeister gemeldet werden.', 'category': 'Qualit??t'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualit??t'}, {'question': 'Werden die Ergebnisse des Safe Launch im PC dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Wurden Sie zum Thema ???Lunker??? geschult?', 'category': 'Energie'}, {'question': 'Sind alle Fluchtwege frei zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualit??t'}, {'question': 'Ist die Zeichnung gut lesbar? ', 'category': 'Qualit??t'}, {'question': 'Werden die Bauteile beim Abr??umen in den vorgeschriebenen Messbereich gelegt?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'F??hren Sie beim Abr??umen eine 100% Pr??fung durch?', 'category': 'Qualit??t'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Qualit??t'}, {'question': 'Werden die Arbeits- Pausenzeiten eingehalten?', 'category': 'Qualit??t'}, {'question': 'Ist der vorliegende Montageanweisung aktuell?', 'category': 'Qualit??t'}, {'question': 'Ist die Verpackung von Werkst??cken/Fertigteilen geregelt/definiert?', 'category': 'Qualit??t'}, {'question': 'Befinden sich in den Beh??ltnissen im Lager ein Rostschutz (Branorost, VCI-Beutel etc.)?', 'category': 'Qualit??t'}, {'question': 'Wurden Sie auf den Standard "R??cksortierung" geschult? - Wissen Sie was zu tun ist?', 'category': 'Qualit??t'}, {'question': 'H??ngen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Ablenkungen w??hrend meiner Montaget??tigkeit schaden der Qualit??t, selbst wenn es sich um den Meister handelt. Wenn mich jemand bei der Arbeit unterbrechen will, weise ich ihn h??flich daraufhin.', 'category': 'Qualit??t'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie was zu tun ist wenn die Pickliste nicht funktioniert?', 'category': 'Qualit??t'}, {'question': 'Sind 100% Pr??fungen vorgeschrieben und dokumentiert?', 'category': 'Qualit??t'}, {'question': 'Befinden sich offene Getr??nke auf den Arbeitsfl??chen?', 'category': 'Qualit??t'}, {'question': 'Ist eine Lupe am Messtisch vorhanden?', 'category': 'Qualit??t'}, {'question': 'Wird das MHD von Klebern eingehalten?', 'category': 'Qualit??t'}, {'question': 'Ist ausreichend Verpackungsmaterial zur Kommissionierung vorhanden? (Systemboxen, KLT ???)', 'category': 'Qualit??t'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualit??t'}, {'question': 'Zeigt die Arbeitsanweisung auch die Werkzeuge, die f??r den jeweiligen Montageschritt ben??tigt werden?', 'category': 'Qualit??t'}, {'question': 'Ist jedem Mitarbeiter der Wiederanlaufprozess bekannt?', 'category': 'Qualit??t'}, {'question': 'Bremsenreiniger darf niemals zur Vorbehandlung einer Klebefl??che verwendet werden.', 'category': 'Qualit??t'}, {'question': 'Wissen Sie, was bei einer Abweichung zu tun ist?', 'category': 'Qualit??t'}, {'question': 'Sind die Feuerl??scher zug??nglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es einen klardefinierten Reinigungsplan f??r den Arbeitsplatz.', 'category': 'Qualit??t'}, {'question': 'Pr??fen Sie Aufzieh??lsen vor Arbeitsbeginn auf Besch??digungen?', 'category': 'Qualit??t'}, {'question': 'Haben Hebevorrichtungen einen g??ltigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie welchen Auftrag Sie als n??chstes fertigen m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Bauteile eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschuss und Fehlteile korrekt gebucht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Hauptwege frei von Besch??digungen, ??llachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Pr??fplakette?', 'category': 'Qualit??t'}, {'question': 'H??ngen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Brandschutzt??ren blockiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Sie an diesem Arbeitsplatz geschult?', 'category': 'Qualit??t'}, {'question': 'Sind alle Kisten/K??rbe mit Warenbegleitkarten gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualit??t'}, {'question': 'Ist sichergestellt, dass nur die ben??tigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualit??t'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teile?', 'category': 'Qualit??t'}, {'question': 'Stimmen alle fertigungsbegleitenden Dokumente mit dem aktuellen Zeichnungsstand ??berein?', 'category': 'Qualit??t'}, {'question': 'Haben alle vorhandenen Messmittel eine Pr??fmittelnummer?', 'category': 'Qualit??t'}, {'question': 'Sind Gefahrstoffbeh??lter als solche gekennzeichnet?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht ??berbr??ckt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualit??t'}, {'question': 'Werden ??lige Putzlappen ausschlie??lich in daf??r vorgesehene Beh??lter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden Pr??feinrichtungen regelm????ig ??berpr??ft?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie wie der Ablageplan funktioniert?', 'category': 'Qualit??t'}, {'question': 'Werden die Verpackungseinheiten von Beh??ltnissen eingehalten?', 'category': 'Qualit??t'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle? 5S?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Energie'}, {'question': 'Werden Ausschussteile dokumentiert/abgeschrieben?', 'category': 'Qualit??t'}, {'question': 'Werden gefallene Teile von Ihnen verschrottet/ausgeschleust? ', 'category': 'Qualit??t'}, {'question': 'Sind die Schicht??bergabeprotokolle ausgef??llt?', 'category': 'Qualit??t'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualit??t'}, {'question': 'K??nnen alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualit??t'}, {'question': 'Kennen Sie Ihre Funktionsbeschreibung?', 'category': 'Qualit??t'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Umwelt'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualit??t'}, {'question': 'Pr??fen Sie vor Arbeitsbeginn das eingestellte Drehmoment am Drehmomentschl??ssel?', 'category': 'Qualit??t'}, {'question': 'Sind alle Werkzeuge wie Schraubenschl??ssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Qualit??t'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist der Umgang mit Restmengen geregelt?', 'category': 'Qualit??t'}, {'question': 'Ist ausreichend Verpackungsmateriall f??r Fertigteile vorhanden?', 'category': 'Qualit??t'}, {'question': 'Sind die korrekten Werkzeuge im Einsatz? Entsprechend der Arbeitsanweisung?', 'category': 'Qualit??t'}, {'question': 'Sind alle umgef??llten Stoffe eindeutig zuordenbar und mit den vorgeschriebenen Piktogrammen/Warnhinweisen gekennzeichnet.', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Brandschutzt??ren frei von Behinderungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist sichergestellt, dass nur die ben??tigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie welchen Auftrag Sie als n??chstes fertigen m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Beinahe-Unf??lle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Stimmen die Vorgabezeiten (R??sten, Fertigung)?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Pr??fplakette?', 'category': 'Qualit??t'}, {'question': 'Ist die Montageanweisung gut verst??ndlich? ', 'category': 'Qualit??t'}, {'question': 'Ist das MHD von Klebern erkennbar?', 'category': 'Qualit??t'}, {'question': 'Schalten Sie die Computer/Bildschirme zum Feierabend aus?', 'category': 'Energie'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Gibt es besch??digte oder defekte Pr??fmittel am Arbeitsplatz?', 'category': 'Qualit??t'}, {'question': 'Sind die Fluchtwege den Mitarbeitern bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden sich offene Getr??nke auf den Arbeitsfl??chen?', 'category': 'Qualit??t'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Auftr??ge abgearbeitet werden m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Fluchtwege gekennzeichnet? Sind diese frei von Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Werkzeuge wie Schraubenschl??ssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist dem Mitarbeiter der Prozess und sind die eingesetzten Werkzeuge klar?', 'category': 'Qualit??t'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Auftr??ge abgearbeitet werden m??ssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Vorrichtungen oder sonstige Fertigungshilfsmittel frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Werden ??lige Putzlappen ausschlie??lich in daf??r vorgesehene Beh??lter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden Ausschuss und Fehlteile korrekt gebucht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist Ihnen der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Umwelt'}, {'question': 'Befinden Trinkflaschen nur in den daf??r vorgesehenen Flaschenhaltern?', 'category': 'Qualit??t'}, {'question': 'Haben Hebevorrichtungen einen g??ltigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist dem Mitarbeiter der Prozess und sind die eingesetzten Werkzeuge klar?', 'category': 'Qualit??t'}, {'question': 'Ist die Stellfl??che f??r Ware gr??n/orange gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Ist dem Mitarbeiter der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist die Bauteilbeschriftung, die aufgebracht wurde, problemlos lesbar?', 'category': 'Qualit??t'}, {'question': 'Sind Vorrichtungen oder sonstige Fertigungshilfsmittel frei von Schmutz?', 'category': 'Qualit??t'}, {'question': 'Werden die Safe Launch Pr??fungen durchgef??hrt?', 'category': 'Qualit??t'}, {'question': 'Werden die Safe Launch Pr??fungen durchgef??hrt?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie was nach einer Unterbrechung zu tun ist und Sie wieder beginnen?', 'category': 'Qualit??t'}, {'question': 'Wissen Sie was zu tun ist wenn die Pickliste nicht funktioniert?', 'category': 'Qualit??t'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Hauptwege frei von Besch??digungen, ??llachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Bauteile eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'H??ngen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist dem Mitarbeiter der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht ??berbr??ckt?', 'category': 'Arbeitssicherheit'}, {'question': 'Wechseln Sie regelm????ig (min. 1x pro Woche) Ihre Montagehandschuhe?', 'category': 'Qualit??t'}, {'question': 'F??hren Sie Pr??fungen laut Maschinenplatzpr??fplan durch?', 'category': 'Qualit??t'}, {'question': 'Sind die Schaltschrankt??ren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden die Maschinenlogb??cher gef??hrt? Sind diese aktuell?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Befinden sich offene Getr??nke auf den Arbeitsfl??chen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist Rohmaterial eindeutig gekennzeichnet?', 'category': 'Qualit??t'}, {'question': 'Werden Ausschuss und Einstellteile im Terminal gemeldet?', 'category': 'Qualit??t'}, {'question': 'Haben Fertigungs- und Pr??fanweisungen einen g??ltigen Status?', 'category': 'Qualit??t'}, {'question': 'Sind Ihnen die Fluchtwege bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es besch??digte oder defekte Pr??fmittel am Arbeitsplatz?', 'category': 'Qualit??t'}]

            question_data = []
            for question in questions:
                question = LPAQuestion(
                        question=question["question"],
                        description=question["question"],
                        category_id=session.query(LPAQuestionCategory).filter(
                            LPAQuestionCategory.category_name == question["category"]
                        ).first().id,
                        layer_id=layers[0].id,
                        group_id=groups[0].id,
                    )
                session.add(question)
                question_data.append(question)
            session.flush()
            session.commit()

            # Generate answer reasons
            answer_reason_description = [
                "Frage unverst??ndlich",
                "Keine Vorgabe",
                "Nicht umsetzbar",
            ]
            answer_reasons = []
            for i in range(len(answer_reason_description)):
                reason = LPAAnswerReason(description=answer_reason_description[i])
                session.add(reason)
                answer_reasons.append(reason)

            session.flush()
            session.commit()

            # Generate audits
            for i in range(10):
                due_date = datetime.now() + timedelta(days=random.randint(5, 15))
                if i % 2 == 0:
                    recurrent_audit = False
                else:
                    recurrent_audit = True

                created_by_user_id = ceo_user.id
                auditor_user_id = ceo_user.id
                assigned_group_id = worker_user.group_id
                assigned_layer_id = worker_user.layer_id

                audit = LPAAudit(
                    due_date=due_date,
                    recurrent_audit=recurrent_audit,
                    created_by_user_id=created_by_user_id,
                    auditor_user_id=auditor_user_id,
                    assigned_group_id=assigned_group_id,
                    assigned_layer_id=assigned_layer_id,
                )
                session.add(audit)
                session.flush()
                session.commit()

                # Generate audit questions
                for i in range(0, random.randint(3, 8)):
                    question = random.choice(question_data)

                    session.add(
                        AuditQuestionAssociation(
                            audit_id=audit.id,
                            question_id=question.id,
                        )
                    )

            # Generate complete audits
            durations = [
                {
                    "context": "overview",
                    "time": 233
                },
                {
                    "context": "question-id 1",
                    "time": 12
                },
                {
                    "context": "overview",
                    "time": 234
                },
                {
                    "context": "question-id 1",
                    "time": 233
                },
                {
                    "context": "overview",
                    "time": 234
                },
                {
                    "context": "question-id 2",
                    "time": 233
                },

            ]
            duration = 1179

            # Generate completed audits
            for i in range(3):
                due_date = datetime.now() + timedelta(days=random.randint(5, 15))
                complete_date = datetime.now() + timedelta(days=3)
                recurrent_audit = False

                created_by_user_id = ceo_user.id
                auditor_user_id = ceo_user.id
                assigned_group_id = worker_user.group_id
                assigned_layer_id = worker_user.layer_id

                audit = LPAAudit(
                    due_date=due_date,
                    complete_datetime=complete_date,
                    duration=duration,
                    recurrent_audit=recurrent_audit,
                    created_by_user_id=created_by_user_id,
                    auditor_user_id=auditor_user_id,
                    assigned_group_id=assigned_group_id,
                    assigned_layer_id=assigned_layer_id,
                )
                session.add(audit)
                session.flush()
                session.commit()

                # Generate audit questions
                nr_questions = 3
                questions = []
                answer_nr = [0, 1, 2]
                for i in range(nr_questions):
                    question = random.choice(question_data)
                    questions.append(question)

                    session.add(
                        AuditQuestionAssociation(
                            audit_id=audit.id,
                            question_id=question.id,
                        )
                    )

                    if answer_nr[i] != 2:
                        session.add(
                            LPAAnswer(
                                answer=answer_nr[i],
                                comment="Test comment",
                                audit_id=audit.id,
                                question_id=question.id,
                            )
                        )
                    else:
                        reason = session.query(LPAAnswerReason).filter(LPAAnswerReason.description == "Frage unverst??ndlich").first()

                        session.add(
                            LPAAnswer(
                                answer=2,
                                comment="Test comment",
                                audit_id=audit.id,
                                question_id=question.id,
                                lpa_answer_reason_id=reason.id,
                            )
                        )

                # TODO: make more realistic
                for d in durations:
                    context = d["context"]
                    duration = d["time"]

                    session.add(
                        LPAAuditDuration(
                            context=context,
                            duration=duration,
                            audit=audit,
                        )
                    )


                # Create Recurrence
                RecurrenceHelper.create_rhytm(
                    session,
                    ceo_user,
                    groups[0],
                    layers[0],
                    RECURRENCE_TYPES.WEEKLY,
                    3, 
                    [ WEEKLY_TYPES.MONDAY, WEEKLY_TYPES.WEDNESDAY, WEEKLY_TYPES.FRIDAY ],
                )

                RecurrenceHelper.create_rhytm(
                    session,
                    worker_user,
                    groups[0],
                    layers[0],
                    RECURRENCE_TYPES.WEEKLY,
                    3, 
                    [ WEEKLY_TYPES.MONDAY, WEEKLY_TYPES.WEDNESDAY, WEEKLY_TYPES.FRIDAY ],
                )

                RecurrenceHelper.create_rhytm(
                    session,
                    worker_user,
                    groups[1],
                    layers[1],
                    RECURRENCE_TYPES.WEEKLY,
                    3, 
                    [ WEEKLY_TYPES.MONDAY, WEEKLY_TYPES.WEDNESDAY, WEEKLY_TYPES.FRIDAY ],
                )

                RecurrenceHelper.create_rhytm(
                    session,
                    worker_user,
                    groups[2],
                    layers[2],
                    RECURRENCE_TYPES.WEEKLY,
                    3, 
                    [ WEEKLY_TYPES.MONDAY, WEEKLY_TYPES.WEDNESDAY, WEEKLY_TYPES.FRIDAY ],
                )

                RecurrenceHelper.create_rhytm(
                    session,
                    worker_user,
                    groups[0],
                    layers[0],
                    RECURRENCE_TYPES.MONTHLY,
                    3, 
                    [ 1, 15, 20 ],
                )

                RecurrenceHelper.create_rhytm(
                    session,
                    worker_user,
                    groups[0],
                    layers[0],
                    RECURRENCE_TYPES.YEARLY,
                    3, 
                    [ YEARLY_TYPES.JANUARY, YEARLY_TYPES.MARCH, YEARLY_TYPES.MAY, YEARLY_TYPES.DECEMBER ],
                )

            session.commit()
