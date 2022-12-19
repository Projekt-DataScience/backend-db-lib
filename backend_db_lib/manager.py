import random
import string

from datetime import datetime, timedelta

from sqlalchemy import (create_engine)
from sqlalchemy.orm import sessionmaker
from .models import Company, User, Role, Layer, Group, LPAQuestionCategory, LPAQuestion, LPAAnswerReason, LPAAudit, AuditQuestionAssociation, LPAAuditDuration, LPAAnswer

from .helpers.recurrence import RecurrenceHelper, RECURRENCE_TYPES, WEEKLY_TYPES, YEARLY_TYPES


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

            CATEGORIES = ['Umwelt', 'Energie', 'Wirtschaftlichkeit', 'Qualität', 'Arbeitssicherheit', 'Fragengruppe']
            for category in CATEGORIES:
                session.add(LPAQuestionCategory(
                    category_name=category
                ))
            session.flush()
            session.commit()

            questions = [{'question': 'Sind Masterteile / Referenzteile verwechslungssicher gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Sind Brandschutztüren blockiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden Erststück- und Letztstückfreigaben dokumentiert?', 'category': 'Qualität'}, {'question': 'Tropft Öl oder Ähnliches aus der Maschine?', 'category': 'Umwelt'}, {'question': 'Ist der Arbeitsbereich frei von Einstellteilen? ', 'category': 'Qualität'}, {'question': 'Werden Ausschussbehälter regelmäßig geleert?', 'category': 'Qualität'}, {'question': 'Werden wassergefährdete Stoffe ausschließlich auf Auffangwannen gelagert?', 'category': 'Umwelt'}, {'question': 'Tropft Öl oder Ähnliches aus der Maschine?', 'category': 'Energie'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht überbrückt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist sichergestellt, dass Einstellparameter nicht unbeabsichtigt verstellt werden können?', 'category': 'Qualität'}, {'question': 'Werden Erststück- und Letztstückfreigaben dokumentiert?', 'category': 'Qualität'}, {'question': 'Sind die Prüfintervalle klar definiert?', 'category': 'Qualität'}, {'question': 'Hängen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Wurden alle Oberflächenmessungen dokumentiert?', 'category': 'Qualität'}, {'question': 'Sind die Schaltschranktüren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Wird die Konzentration von Kühlschmierstoffen regelmäßig geprüft?', 'category': 'Umwelt'}, {'question': 'Sind die roten Ausschussbehältnisse gegen direkten Zugriff gesichert', 'category': 'Qualität'}, {'question': 'Werden die Maschinenlogbücher geführt? Sind diese aktuell?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege frei von Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist der Reinigungsplan ausgefüllt?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die aktuelle Zeichnung am Arbeitsplatz ausgehängt?', 'category': 'Qualität'}, {'question': 'Können alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualität'}, {'question': 'Ist die Bauteilbeschriftung, die aufgebracht wurde, problemlos lesbar?', 'category': 'Qualität'}, {'question': 'Ist geregelt wie Bauteile zurückgelagert werden müssen? ', 'category': 'Qualität'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Aufträge abgearbeitet werden müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teile?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualität'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Können alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Energie'}, {'question': 'Wissen Sie was zu tun ist wenn ein Merkmal am Bauteil n.i.O. ist?', 'category': 'Qualität'}, {'question': 'Sind alle fertigungsrelevanten Normen der Zeichnung aufgeschlüsselt, oder sind diese zugänglich?', 'category': 'Qualität'}, {'question': 'Werden Produktionsaufträge und Arbeitsgänge korrekt gemeldet?', 'category': 'Qualität'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualität'}, {'question': 'Haben Fertigungs- und Prüfanweisungen einen gültigen Status?', 'category': 'Qualität'}, {'question': 'Werden Ausschuss und Einstellteile im Terminal gemeldet?', 'category': 'Qualität'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualität'}, {'question': 'Werden ausschließlich Nachtragskarten verwendet? ', 'category': 'Energie'}, {'question': 'Werden gefallene Teile von jedem Mitarbeiter ausgeschleust? ', 'category': 'Qualität'}, {'question': 'Gibt es an jedem Arbeitsplatz einen klar gekennzeichneten Ausschussbehälter?', 'category': 'Qualität'}, {'question': 'Ist eine Fertigungszeichnung in DIN A3 am Arbeitsplatz vorhanden?', 'category': 'Qualität'}, {'question': 'Schalten Sie die Computer/Bildschirme zum Feierabend aus?', 'category': 'Energie'}, {'question': 'Ablenkungen während meiner Montagetätigkeit schaden der Qualität, selbst wenn es sich um den Meister handelt. Wenn mich jemand bei der Arbeit unterbrechen will, weise ich ihn höflich daraufhin.', 'category': 'Qualität'}, {'question': 'Prüfen Sie die Sauberkeit der Blister, bevor Sie diese verwenden?', 'category': 'Qualität'}, {'question': 'Sind die Schaltschranktüren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle fertigungsrelevanten Normen der Zeichnung aufgeschlüsselt, oder sind diese zugänglich?', 'category': 'Qualität'}, {'question': 'Wechseln Sie regelmäßig (min. 1x pro Woche) Ihre Handschuhe?', 'category': 'Qualität'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Qualität'}, {'question': 'Haben Hebevorrichtungen einen gültigen Status? Z.B. Ameise', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Z.B. Kardex Lichtschranke', 'category': 'Arbeitssicherheit'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Ausschussbehälter regelmäßig geleert?', 'category': 'Qualität'}, {'question': 'Stimmen die Laufzeiten? ', 'category': 'Qualität'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist Rohmaterial eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Ist der Arbeitsbereich frei von Einstellteilen? ', 'category': 'Qualität'}, {'question': 'Tropft Öl oder Ähnliches aus der Maschine?', 'category': 'Qualität'}, {'question': 'Sind Kabel und sonstige Stromführungen frei von Beschädigungen?', 'category': 'Qualität'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitstische frei von Lebensmittel', 'category': 'Qualität'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Sind die Hauptwege frei von Beschädigungen, Öllachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist das Mindesthalbarkeitsdatum von O-Ringen erkennbar?', 'category': 'Qualität'}, {'question': 'Sind die Hauptwege frei von Beschädigungen, Öllachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Umwelt'}, {'question': 'Sind die Schichtübergabeprotokolle ausgefüllt?', 'category': 'Qualität'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel die 5S-Standards eingehalten?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind auch Beinahe-Unfälle dokumentiert?', 'category': 'Qualität'}, {'question': 'Wird die Konzentration von Kühlschmierstoffen regelmäßig geprüft?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege den Mitarbeitern bekannt?', 'category': 'Qualität'}, {'question': 'Sind die Arbeitstische frei von Lebensmitteln?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualität'}, {'question': 'Gibt es an jedem Arbeitsplatz einen klar gekennzeichneten Ausschussbehälter?', 'category': 'Qualität'}, {'question': 'Tragen Sie beim Umgang mit metallischen Bauteilen Handschuhe?', 'category': 'Qualität'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualität'}, {'question': 'Werden ölige Putzlappen ausschließlich in dafür vorgesehene Behälter gesammelt?', 'category': 'Qualität'}, {'question': 'Ist ausreichend Verpackungsmateriall für Fertigteile vorhanden?', 'category': 'Qualität'}, {'question': 'Werden Ausschussbehälter regelmäßig geleert?', 'category': 'Qualität'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle?', 'category': 'Qualität'}, {'question': 'Ist die Verpackung von Werkstücken/Fertigteilen geregelt/definiert?', 'category': 'Qualität'}, {'question': 'Werden Produktionsaufträge und Arbeitsgänge gemeldet?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualität'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualität'}, {'question': 'Wissen die Mitarbeiter, was bei einer Abweichung im Prozess zu tun ist?', 'category': 'Qualität'}, {'question': 'Ist eine Tischkennzeichnung "geprüf" - "ungeprüft" vorhanden? ', 'category': 'Qualität'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel die 5S-Standards eingehalten?', 'category': 'Qualität'}, {'question': 'Werden die Prüfmittel am Arbeitsplatz regelmäßig überprüft/justiert?', 'category': 'Qualität'}, {'question': 'Finden die Shopfloorstehenungen regelmäßig statt, ist die Anwesenheitsliste geführt?', 'category': 'Qualität'}, {'question': 'Gibt es beschädigte oder defekte Prüfmittel am Arbeitsplatz?', 'category': 'Qualität'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualität'}, {'question': 'Sind alle Kisten/Gitterkörbe fortlaufend nummeriert (Hydac)?', 'category': 'Qualität'}, {'question': 'Darf der Mitarbeiter den Prozess stoppen, wenn er einen Fehler feststellt?', 'category': 'Qualität'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualität'}, {'question': 'Finden die Shopfloorstehenungen regelmäßig statt, ist die Anwesenheitsliste geführt?', 'category': 'Qualität'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Kabel und sonstige Stromführungen frei von Beschädigungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es dokumentierte Vorgaben für das manuelle Entgraten?', 'category': 'Qualität'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teilen?', 'category': 'Qualität'}, {'question': 'Haben Sie 100% Messungen? Sind diese vorgeschrieben und dokumentiert? Führen Sie diese durch?', 'category': 'Qualität'}, {'question': 'Sind alle Verletzungen im Verbandsbuch dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind auch Beinahe-Unfälle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie, ob ein Lunker i.O. oder n.i.O. ist? (Schulung, Fehlerkatalog)', 'category': 'Arbeitssicherheit'}, {'question': 'Wurden Sie auf den Standard "Safe Launch" geschult - Wissen Sie was zu tun ist?', 'category': 'Qualität'}, {'question': 'Sind alle Fluchtwege frei zugänglich?', 'category': 'Qualität'}, {'question': 'Ist jedem Mitarbeiter der Wiederanlaufprozess bekannt?', 'category': 'Qualität'}, {'question': 'Befindet sich an Ihrem Arbeitsplatz ein rotes Ausschussbehältniss?', 'category': 'Qualität'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teilen?', 'category': 'Qualität'}, {'question': 'Sind Kabel und sonstige Stromführungen frei von Beschädigungen? (Blanke Kabel?)', 'category': 'Arbeitssicherheit'}, {'question': 'Werden ölige Putzlappen ausschließlich in dafür vorgesehene Behälter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Kennen Sie die  SFB Qualitätspolitik?', 'category': 'Qualität'}, {'question': 'Sind die Feuerlöscher zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualität'}, {'question': 'Können alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualität'}, {'question': 'Sind Gefahrstoffbehälter als solche gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualität'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualität'}, {'question': 'Sind Ihnen die Fluchtwege bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualität'}, {'question': 'Befinden Trinkflaschen nur in den dafür vorgesehenen Flaschenhaltern?', 'category': 'Qualität'}, {'question': 'Sind auch Beinahe-Unfälle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Fluchtwege frei zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Kennen Sie die  SFB Qualitätspolitik?', 'category': 'Qualität'}, {'question': 'Kennen Sie die  SFB Qualitätspolitik?', 'category': 'Qualität'}, {'question': 'Sind die Arbeitstische frei von Lebensmittel', 'category': 'Qualität'}, {'question': 'Ist die Zeichnung gut lesbar?', 'category': 'Qualität'}, {'question': 'Sind alle Fluchtwege frei zugänglich', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es an Ihrem Arbeitsplatz einen klar gekennzeichneten Ausschussbehälter?', 'category': 'Qualität'}, {'question': 'Befinden sich die von Ihnen kommissionierte Ware in den vorgeschriebenen Bereichen?', 'category': 'Qualität'}, {'question': 'Gibt es beschädigte oder defekte Prüfmittel am Arbeitsplatz?', 'category': 'Qualität'}, {'question': 'Wissen Sie was Sie tun müssen wenn keine Arbeitsanweisung vorhanden ist?', 'category': 'Qualität'}, {'question': 'Ist eine Fertigungszeichnung in DIN A3 am Arbeitsplatz vorhanden?', 'category': 'Qualität'}, {'question': 'Werden die Verpackungseinheiten von Behältnissen eingehalten?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Prüfen Sie Ihre Messmittel vor Arbeitsbeginn? (Toleranz kleiner 0,05mm)', 'category': 'Qualität'}, {'question': 'Sind alle Fluchtwege frei zugänglich', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Aushänge oder Anweisungen im Fertigungsbereich ausschließlich gelenkte Dokumente?', 'category': 'Qualität'}, {'question': 'Führen Sie/Ihre Kollegen beim Abräumen eine 100% Prüfung durch?', 'category': 'Qualität'}, {'question': 'Haben Sie 100% Messungen? Sind diese vorgeschrieben und dokumentiert? Führen Sie diese durch?', 'category': 'Qualität'}, {'question': 'Haben Hebevorrichtungen einen gültigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Masterteile / Referenzteile verwechslungssicher gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Gibt es einen klar definierten Reinigungsplan für den Arbeitsplatz.', 'category': 'Qualität'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Prüfplakette?', 'category': 'Qualität'}, {'question': 'Sind alle Werkzeuge wie Schraubenschlüssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Produktionsaufträge und Arbeitsgänge korrekt gemeldet?', 'category': 'Qualität'}, {'question': 'Wurden Sie/Ihre Kollegen auf den Standard "Rücksortierung" geschult?', 'category': 'Qualität'}, {'question': 'Wurden Sie/Ihre Kollegen auf den Standard "SafeLaunch" geschult?', 'category': 'Qualität'}, {'question': 'Werden die Bauteile beim Abräumen in den vorgeschriebenen Messbereich gelegt?', 'category': 'Qualität'}, {'question': 'Ist eine Tischkennzeichnung "geprüft" und "ungeprüft" vorhanden?', 'category': 'Qualität'}, {'question': 'Führen Sie beim Abräumen eine Sichtprüfung am letzten Teil durch?', 'category': 'Qualität'}, {'question': 'Führen Sie die Prüfungen laut Maschinenplatzprüfplan durch?', 'category': 'Qualität'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualität'}, {'question': 'Ist eine Lupe am Messtisch vorhanden?', 'category': 'Qualität'}, {'question': 'Führen Sie bei Fehlbeständen eine Inventurbuchung durch?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind alle Kisten fortlaufend nummeriert?', 'category': 'Qualität'}, {'question': 'Werden die Ergebnisse des Safelaunch im PC gespeichert?', 'category': 'Qualität'}, {'question': 'Werden Ausschussbehälter regelmäßig geleert?', 'category': 'Qualität'}, {'question': 'Sind Aushänge oder Anweisungen im Fertigungsbereich ausschließlich gelenkte Dokumente?', 'category': 'Qualität'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Aufträge abgearbeitet werden müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Prüfplakette? Z.B. Die Waage', 'category': 'Qualität'}, {'question': 'Sind die Zählwaagen frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Sind die Wiegebehälter frei von Schmutz/ sauber?', 'category': 'Qualität'}, {'question': 'Sind Prüfvorrichtungen frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Bearbeiten Sie die Aufträge der Reihe nach ab? Keine Gleichzeitige Bearbeitung der Aufträge!', 'category': 'Qualität'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualität'}, {'question': 'Werden Ausschussteile dokumentiert/abgeschrieben?', 'category': 'Qualität'}, {'question': 'Ist die Zeichnung gut lesbar? ', 'category': 'Qualität'}, {'question': 'Wird das Mindesthalbarkeitsdatum von O-Ringen eingehalten?', 'category': 'Qualität'}, {'question': 'Werden gefallene Teile von Ihnen ausgeschleust/verschrottet? ', 'category': 'Qualität'}, {'question': 'Sind die Feuerlöscher zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden sich offene Getränke auf den Arbeitsflächen?', 'category': 'Qualität'}, {'question': 'Haben alle vorhandenen Messmittel eine Prüfmittelnummer?', 'category': 'Qualität'}, {'question': 'Sind Prüfvorrichtungen frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Sind Sie an diesem Arbeitsplatz geschult?', 'category': 'Qualität'}, {'question': 'Halten Sie beim Auslagern FIFO ein?', 'category': 'Qualität'}, {'question': 'Sind Brandschutztüren frei von Behinderungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden Trinkflaschen nur in den dafür vorgesehenen Flaschenhaltern?', 'category': 'Qualität'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen? Eindeutige Kennzeichnung der Behältnisse?', 'category': 'Qualität'}, {'question': 'Werden die Arbeits- Pausenzeiten eingehalten?', 'category': 'Qualität'}, {'question': 'Kennen Sie die  SFB Qualitätspolitik?', 'category': 'Qualität'}, {'question': 'Befinden Trinkflaschen nur in den dafür vorgesehenen Flaschenhaltern?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Qualität'}, { 'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualität'}, {'question': 'Sind Kabel und sonstige Stromführungen frei von Beschädigungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden die Verpackungseinheiten von Behältnissen eingehalten?', 'category': 'Qualität'}, {'question': 'Ist eine Materialverwechslung ausgeschlossen?', 'category': 'Qualität'}, {'question': 'Werden die Maschinenlogbücher geführt? Sind diese aktuell?', 'category': 'Qualität'}, {'question': 'Prüfen Sie die Sauberkeit der Blister, bevor Sie diese für den Ablageplan verwenden?', 'category': 'Qualität'}, {'question': 'Darf der Mitarbeiter den Prozess stoppen, wenn er einen Fehler feststellt?', 'category': 'Qualität'}, {'question': 'Finden die Shopfloorstehenungen regelmäßig statt, ist die Anwesenheitsliste geführt?', 'category': 'Qualität'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualität'}, {'question': 'Werden Messmittel (Millimeß, Messschieber, etc.) regelmäßig justiert/genullt?', 'category': 'Qualität'}, {'question': 'Ist der vorliegende Zeichnungsstand aktuell?', 'category': 'Qualität'}, {'question': 'Sind die Arbeitstische frei von Lebensmitteln?', 'category': 'Qualität'}, {'question': 'Ist sichergestellt, dass nur die benötigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualität'}, {'question': 'Ist die aktuelle Zeichnung am Arbeitsplatz ausgehängt?', 'category': 'Qualität'}, {'question': 'Haben alle vorhandenen Messmittel eine Prüfmittelnummer?', 'category': 'Qualität'}, {'question': 'Finden die Shopfloorstehungen regelmäßig statt, ist die Anwesenheitsliste geführt?', 'category': 'Qualität'}, {'question': 'Sind Aushänge oder Anweisungen im Fertigungsbereich ausschließlich gelenkte Dokumente?', 'category': 'Energie'}, {'question': 'Werden wassergefährdete Stoffe ausschließlich auf Auffangwannen gelagert?', 'category': 'Qualität'}, {'question': 'Sind die Prüfintervalle klar definiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie was zu tun ist, wenn Teile nicht montagefähig sind?', 'category': 'Qualität'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Qualität'}, {'question': 'Werden Prüfeinrichtungen regelmäßig überprüft? Check the Checker?', 'category': 'Qualität'}, {'question': 'Sind Gefahrstoffbehälter als solche gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Stimmen die Laufzeiten/Taktzeiten für den aktuellen Auftrag?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden die Verpackungseinheiten von Behältnissen eingehalten?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Ungekennzeichnete Bauteile müssen dem Abteilungsmeister gemeldet werden.', 'category': 'Qualität'}, {'question': 'Werden wassergefährdete Stoffe ausschließlich auf Auffangwannen gelagert?', 'category': 'Umwelt'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualität'}, {'question': 'Haben Arbeitsanweisungen einen gültigen Status?', 'category': 'Qualität'}, {'question': 'Wissen die Mitarbeiter, was bei einer Abweichung im Prozess zu tun ist?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist die Verpackung von Werkstücken/Fertigteilen geregelt/definiert?', 'category': 'Umwelt'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden gefallene Teile von Ihnen ausgeschleust/verschrottet? ', 'category': 'Qualität'}, {'question': 'Sind die Feuerlöscher zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Tragen Sie beim Umgang mit metallischen Bauteilen Handschuhe?', 'category': 'Qualität'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Produktionsaufträge und Arbeitsgänge korrekt gemeldet?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualität'}, {'question': 'Stimmen alle fertigungsbegleitenden Dokumente mit dem aktuellen Zeichnungsstand überein?', 'category': 'Qualität'}, {'question': 'Sind die Prüfintervalle klar definiert?', 'category': 'Qualität'}, {'question': 'Sind die korrekten Werkzeuge im Einsatz? ', 'category': 'Qualität'}, {'question': 'Ist ausreichend Verpackungsmateriall für Fertigteile vorhanden?', 'category': 'Qualität'}, {'question': 'Sind  alle Dokumente der Stückliste für Sie zugänglich?', 'category': 'Qualität'}, {'question': 'Sind Prüfvorrichtungen frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Sind die Schaltschranktüren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Frage ich nach wenn ich eine Auditfrage nicht verstanden habe?', 'category': 'Qualität'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Sind Gefahrstoffbehälter als solche gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Gibt es in Ihrem Arbeitsbereich einen klar gekennzeichneten Ausschussbehälter?', 'category': 'Qualität'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Wird nach Arbeitsende oder Schichtwechsel der 5S-Standard eingehalten?', 'category': 'Qualität'}, {'question': 'Ungekennzeichnete Bauteile müssen dem Abteilungsmeister gemeldet werden.', 'category': 'Qualität'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualität'}, {'question': 'Werden die Ergebnisse des Safe Launch im PC dokumentiert?', 'category': 'Qualität'}, {'question': 'Wurden Sie zum Thema „Lunker“ geschult?', 'category': 'Energie'}, {'question': 'Sind alle Fluchtwege frei zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Kundenreklamationen den Mitarbeitern und Kollegen bekannt?', 'category': 'Qualität'}, {'question': 'Ist die Zeichnung gut lesbar? ', 'category': 'Qualität'}, {'question': 'Werden die Bauteile beim Abräumen in den vorgeschriebenen Messbereich gelegt?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege gekennzeichnet?', 'category': 'Arbeitssicherheit'}, {'question': 'Führen Sie beim Abräumen eine 100% Prüfung durch?', 'category': 'Qualität'}, {'question': 'Werden die Werkzeugwechselintervalle eingehalten?', 'category': 'Qualität'}, {'question': 'Werden die Arbeits- Pausenzeiten eingehalten?', 'category': 'Qualität'}, {'question': 'Ist der vorliegende Montageanweisung aktuell?', 'category': 'Qualität'}, {'question': 'Ist die Verpackung von Werkstücken/Fertigteilen geregelt/definiert?', 'category': 'Qualität'}, {'question': 'Befinden sich in den Behältnissen im Lager ein Rostschutz (Branorost, VCI-Beutel etc.)?', 'category': 'Qualität'}, {'question': 'Wurden Sie auf den Standard "Rücksortierung" geschult? - Wissen Sie was zu tun ist?', 'category': 'Qualität'}, {'question': 'Hängen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Ablenkungen während meiner Montagetätigkeit schaden der Qualität, selbst wenn es sich um den Meister handelt. Wenn mich jemand bei der Arbeit unterbrechen will, weise ich ihn höflich daraufhin.', 'category': 'Qualität'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Wissen Sie was zu tun ist wenn die Pickliste nicht funktioniert?', 'category': 'Qualität'}, {'question': 'Sind 100% Prüfungen vorgeschrieben und dokumentiert?', 'category': 'Qualität'}, {'question': 'Befinden sich offene Getränke auf den Arbeitsflächen?', 'category': 'Qualität'}, {'question': 'Ist eine Lupe am Messtisch vorhanden?', 'category': 'Qualität'}, {'question': 'Wird das MHD von Klebern eingehalten?', 'category': 'Qualität'}, {'question': 'Ist ausreichend Verpackungsmaterial zur Kommissionierung vorhanden? (Systemboxen, KLT …)', 'category': 'Qualität'}, {'question': 'Befinden Sich Fertigware, Rohmaterial etc. in den gekennzeichneten Bereichen?', 'category': 'Qualität'}, {'question': 'Zeigt die Arbeitsanweisung auch die Werkzeuge, die für den jeweiligen Montageschritt benötigt werden?', 'category': 'Qualität'}, {'question': 'Ist jedem Mitarbeiter der Wiederanlaufprozess bekannt?', 'category': 'Qualität'}, {'question': 'Bremsenreiniger darf niemals zur Vorbehandlung einer Klebefläche verwendet werden.', 'category': 'Qualität'}, {'question': 'Wissen Sie, was bei einer Abweichung zu tun ist?', 'category': 'Qualität'}, {'question': 'Sind die Feuerlöscher zugänglich?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es einen klardefinierten Reinigungsplan für den Arbeitsplatz.', 'category': 'Qualität'}, {'question': 'Prüfen Sie Aufziehülsen vor Arbeitsbeginn auf Beschädigungen?', 'category': 'Qualität'}, {'question': 'Haben Hebevorrichtungen einen gültigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden Messmittel sorgsam behandelt?', 'category': 'Qualität'}, {'question': 'Wissen Sie welchen Auftrag Sie als nächstes fertigen müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Bauteile eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Werden Ausschuss und Fehlteile korrekt gebucht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Hauptwege frei von Beschädigungen, Öllachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Prüfplakette?', 'category': 'Qualität'}, {'question': 'Hängen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Brandschutztüren blockiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Sie an diesem Arbeitsplatz geschult?', 'category': 'Qualität'}, {'question': 'Sind alle Kisten/Körbe mit Warenbegleitkarten gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualität'}, {'question': 'Ist sichergestellt, dass nur die benötigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualität'}, {'question': 'Ist der Arbeitsbereich frei von auftragsfremden Teile?', 'category': 'Qualität'}, {'question': 'Stimmen alle fertigungsbegleitenden Dokumente mit dem aktuellen Zeichnungsstand überein?', 'category': 'Qualität'}, {'question': 'Haben alle vorhandenen Messmittel eine Prüfmittelnummer?', 'category': 'Qualität'}, {'question': 'Sind Gefahrstoffbehälter als solche gekennzeichnet?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht überbrückt?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist Ware in der Produktion eindeutig gekennzeichnet? ', 'category': 'Qualität'}, {'question': 'Werden ölige Putzlappen ausschließlich in dafür vorgesehene Behälter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden Prüfeinrichtungen regelmäßig überprüft?', 'category': 'Qualität'}, {'question': 'Wissen Sie wie der Ablageplan funktioniert?', 'category': 'Qualität'}, {'question': 'Werden die Verpackungseinheiten von Behältnissen eingehalten?', 'category': 'Qualität'}, {'question': 'Werden gesperrte Teile mit Gesperrt-Karten eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Sind alle Werkzeuge an Ort und Stelle? 5S?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Druckluftleitungen dicht?', 'category': 'Energie'}, {'question': 'Werden Ausschussteile dokumentiert/abgeschrieben?', 'category': 'Qualität'}, {'question': 'Werden gefallene Teile von Ihnen verschrottet/ausgeschleust? ', 'category': 'Qualität'}, {'question': 'Sind die Schichtübergabeprotokolle ausgefüllt?', 'category': 'Qualität'}, {'question': 'Ist die Chargenreinheit (wenn gefordert) einhaltbar? ', 'category': 'Qualität'}, {'question': 'Können alle bestehenden Reklamationen zu einem Produkt eingesehen werden?', 'category': 'Qualität'}, {'question': 'Kennen Sie Ihre Funktionsbeschreibung?', 'category': 'Qualität'}, {'question': 'Sind die richtigen und ausreichend Putzmittel im Arbeitsbereich vorhanden?', 'category': 'Umwelt'}, {'question': 'Werden die Arbeitsanweisungen eingehalten? Wird nach Standard gearbeitet?', 'category': 'Qualität'}, {'question': 'Prüfen Sie vor Arbeitsbeginn das eingestellte Drehmoment am Drehmomentschlüssel?', 'category': 'Qualität'}, {'question': 'Sind alle Werkzeuge wie Schraubenschlüssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Qualität'}, {'question': 'Dokumentieren Sie alle Ihre Verletzungen im Verbandsbuch?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist der Umgang mit Restmengen geregelt?', 'category': 'Qualität'}, {'question': 'Ist ausreichend Verpackungsmateriall für Fertigteile vorhanden?', 'category': 'Qualität'}, {'question': 'Sind die korrekten Werkzeuge im Einsatz? Entsprechend der Arbeitsanweisung?', 'category': 'Qualität'}, {'question': 'Sind alle umgefüllten Stoffe eindeutig zuordenbar und mit den vorgeschriebenen Piktogrammen/Warnhinweisen gekennzeichnet.', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Brandschutztüren frei von Behinderungen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist sichergestellt, dass nur die benötigten Artikel / Bauteile am Arbeitsplatz vorhanden sind?', 'category': 'Qualität'}, {'question': 'Wissen Sie welchen Auftrag Sie als nächstes fertigen müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Werden Beinahe-Unfälle an der Shopfloortafel dokumentiert?', 'category': 'Arbeitssicherheit'}, {'question': 'Stimmen die Vorgabezeiten (Rüsten, Fertigung)?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Haben alle vorhandenen Messmittel eine aktuelle Prüfplakette?', 'category': 'Qualität'}, {'question': 'Ist die Montageanweisung gut verständlich? ', 'category': 'Qualität'}, {'question': 'Ist das MHD von Klebern erkennbar?', 'category': 'Qualität'}, {'question': 'Schalten Sie die Computer/Bildschirme zum Feierabend aus?', 'category': 'Energie'}, {'question': 'Werden Arbeitsschuhe in den vorgegebenen Bereichen getragen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden nachzuarbeitende Teile eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Gibt es beschädigte oder defekte Prüfmittel am Arbeitsplatz?', 'category': 'Qualität'}, {'question': 'Sind die Fluchtwege den Mitarbeitern bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Befinden sich offene Getränke auf den Arbeitsflächen?', 'category': 'Qualität'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Aufträge abgearbeitet werden müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Fluchtwege gekennzeichnet? Sind diese frei von Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind alle Werkzeuge wie Schraubenschlüssel / Zangen am Arbeitsplatz vorhanden? ', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist dem Mitarbeiter der Prozess und sind die eingesetzten Werkzeuge klar?', 'category': 'Qualität'}, {'question': 'Gibt es eine klare Auftragsreihenfolge, nach der Produkte/Aufträge abgearbeitet werden müssen?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind Vorrichtungen oder sonstige Fertigungshilfsmittel frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Werden ölige Putzlappen ausschließlich in dafür vorgesehene Behälter gesammelt?', 'category': 'Umwelt'}, {'question': 'Werden Ausschuss und Fehlteile korrekt gebucht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist Ihnen der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Umwelt'}, {'question': 'Befinden Trinkflaschen nur in den dafür vorgesehenen Flaschenhaltern?', 'category': 'Qualität'}, {'question': 'Haben Hebevorrichtungen einen gültigen Status?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist dem Mitarbeiter der Prozess und sind die eingesetzten Werkzeuge klar?', 'category': 'Qualität'}, {'question': 'Ist die Stellfläche für Ware grün/orange gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Ist dem Mitarbeiter der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Liegt eine Arbeitsvorratsliste vor? Ist bekannt wieviel Arbeitsvorrat besteht?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Ist die Bauteilbeschriftung, die aufgebracht wurde, problemlos lesbar?', 'category': 'Qualität'}, {'question': 'Sind Vorrichtungen oder sonstige Fertigungshilfsmittel frei von Schmutz?', 'category': 'Qualität'}, {'question': 'Werden die Safe Launch Prüfungen durchgeführt?', 'category': 'Qualität'}, {'question': 'Werden die Safe Launch Prüfungen durchgeführt?', 'category': 'Qualität'}, {'question': 'Wissen Sie was nach einer Unterbrechung zu tun ist und Sie wieder beginnen?', 'category': 'Qualität'}, {'question': 'Wissen Sie was zu tun ist wenn die Pickliste nicht funktioniert?', 'category': 'Qualität'}, {'question': 'Sind alle Reparaturen im Wartungslogbuch erfasst?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Sind die Hauptwege frei von Beschädigungen, Öllachen oder Hindernissen?', 'category': 'Arbeitssicherheit'}, {'question': 'Sind Bauteile eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Hängen die Unterweisungen zum Umgang mit chemischen Stoffen aus?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist dem Mitarbeiter der Umgang mit chemischen Stoffen am Arbeitsplatz bekannt?', 'category': 'Umwelt'}, {'question': 'Sind die Arbeitsschutzeinrichtungen intakt? Sind diese nicht überbrückt?', 'category': 'Arbeitssicherheit'}, {'question': 'Wechseln Sie regelmäßig (min. 1x pro Woche) Ihre Montagehandschuhe?', 'category': 'Qualität'}, {'question': 'Führen Sie Prüfungen laut Maschinenplatzprüfplan durch?', 'category': 'Qualität'}, {'question': 'Sind die Schaltschranktüren verschlossen?', 'category': 'Arbeitssicherheit'}, {'question': 'Werden die Maschinenlogbücher geführt? Sind diese aktuell?', 'category': 'Wirtschaftlichkeit'}, {'question': 'Befinden sich offene Getränke auf den Arbeitsflächen?', 'category': 'Arbeitssicherheit'}, {'question': 'Ist Rohmaterial eindeutig gekennzeichnet?', 'category': 'Qualität'}, {'question': 'Werden Ausschuss und Einstellteile im Terminal gemeldet?', 'category': 'Qualität'}, {'question': 'Haben Fertigungs- und Prüfanweisungen einen gültigen Status?', 'category': 'Qualität'}, {'question': 'Sind Ihnen die Fluchtwege bekannt?', 'category': 'Arbeitssicherheit'}, {'question': 'Gibt es beschädigte oder defekte Prüfmittel am Arbeitsplatz?', 'category': 'Qualität'}]

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
                "Frage unverständlich",
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
                        reason = session.query(LPAAnswerReason).filter(LPAAnswerReason.description == "Frage unverständlich").first()

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
