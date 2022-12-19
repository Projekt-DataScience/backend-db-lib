from datetime import datetime, timedelta
from typing import List, Union

from models import LPAAuditRecurrence, User, Group, Layer

class WEEKLY_TYPES:
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    TYPES = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]

class YEARLY_TYPES:
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

    TYPES = [JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
             JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER]


class RECURRENCE_TYPES:
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    TYPES = [WEEKLY, MONTHLY, YEARLY]
    VALUES = {
        WEEKLY: WEEKLY_TYPES.TYPES,
        MONTHLY: [str(i) for i in range(1, 32)],
        YEARLY: YEARLY_TYPES.TYPES
    }


class WEEKLY_VALUES:
    MONDAY = 0b0000001
    TUESDAY = 0b0000010
    WEDNESDAY = 0b0000100
    THURSDAY = 0b0001000
    FRIDAY = 0b0010000
    SATURDAY = 0b0100000
    SUNDAY = 0b1000000

    VALUES = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]


class YEARLY_VALUES:
    JANUARY = 0b000000000001
    FEBRUARY = 0b000000000010
    MARCH = 0b000000000100
    APRIL = 0b000000001000
    MAY = 0b000000010000
    JUNE = 0b000000100000
    JULY = 0b000001000000
    AUGUST = 0b000010000000
    SEPTEMBER = 0b000100000000
    OCTOBER = 0b001000000000
    NOVEMBER = 0b010000000000
    DECEMBER = 0b100000000000

    VALUES = [JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
              JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER]


MONTH_VALUES = [
    0b0000000000000000000000000000001,
    0b0000000000000000000000000000010,
    0b0000000000000000000000000000100,
    0b0000000000000000000000000001000,
    0b0000000000000000000000000010000,
    0b0000000000000000000000000100000,
    0b0000000000000000000000001000000,
    0b0000000000000000000000010000000,
    0b0000000000000000000000100000000,
    0b0000000000000000000001000000000,
    0b0000000000000000000010000000000,
    0b0000000000000000000100000000000,
    0b0000000000000000001000000000000,
    0b0000000000000000010000000000000,
    0b0000000000000000100000000000000,
    0b0000000000000001000000000000000,
    0b0000000000000010000000000000000,
    0b0000000000000100000000000000000,
    0b0000000000001000000000000000000,
    0b0000000000010000000000000000000,
    0b0000000000100000000000000000000,
    0b0000000001000000000000000000000,
    0b0000000010000000000000000000000,
    0b0000000100000000000000000000000,
    0b0000001000000000000000000000000,
    0b0000010000000000000000000000000,
    0b0000100000000000000000000000000,
    0b0001000000000000000000000000000,
    0b0010000000000000000000000000000,
    0b0100000000000000000000000000000,
    0b1000000000000000000000000000000,
]

class RecurrenceHelper:

    @staticmethod
    def get_recurrence_types():
        return RECURRENCE_TYPES.TYPES

    @staticmethod
    def get_recurrence_values(type: str) -> List[str]:
        return RECURRENCE_TYPES.VALUES[type]

    @staticmethod
    def get_rhytm(id: int, session) -> Union[LPAAuditRecurrence, None]:
        recurrence = session.query(LPAAuditRecurrence).get(id)
        recurrence.values = RecurrenceHelper.backend_to_frontend_recurrence_value(recurrence.type, recurrence.value)
        return recurrence

    @staticmethod
    def create_rhytm(session, auditor: User, group: Group, layer: Layer, type: str, question_count: int, values: List[str]) -> LPAAuditRecurrence:
        value = RecurrenceHelper.frontend_recurrence_value_to_backend_recurrence_value(
            type,
            values
        )
        
        r = LPAAuditRecurrence(
            auditor_id=auditor.id,
            group_id=group.id,
            layer_id=layer.id,
            type=type,
            question_count=question_count,
            value=value
        )

        session.add(r)
        session.flush()
        session.commit()
        session.refresh(r)

        return r

    @staticmethod
    def backend_to_frontend_recurrence_value(type, value):
        if type == RECURRENCE_TYPES.WEEKLY:
            days = []
            if value & WEEKLY_VALUES.MONDAY:
                days.append(WEEKLY_TYPES.MONDAY)
            if value & WEEKLY_VALUES.TUESDAY:
                days.append(WEEKLY_TYPES.TUESDAY)
            if value & WEEKLY_VALUES.WEDNESDAY:
                days.append(WEEKLY_TYPES.WEDNESDAY)
            if value & WEEKLY_VALUES.THURSDAY:
                days.append(WEEKLY_TYPES.THURSDAY)
            if value & WEEKLY_VALUES.FRIDAY:
                days.append(WEEKLY_TYPES.FRIDAY)
            if value & WEEKLY_VALUES.SATURDAY:
                days.append(WEEKLY_TYPES.SATURDAY)
            if value & WEEKLY_VALUES.SUNDAY:
                days.append(WEEKLY_TYPES.SUNDAY)
            return days

        elif type == RECURRENCE_TYPES.MONTHLY:
            days = []
            for i in range(31):
                if value & MONTH_VALUES[i]:
                    days.append(str(i + 1))
            return days

        elif type == RECURRENCE_TYPES.YEARLY:
            months = []
            if value & YEARLY_VALUES.JANUARY:
                months.append(YEARLY_TYPES.JANUARY)
            if value & YEARLY_VALUES.FEBRUARY:
                months.append(YEARLY_TYPES.FEBRUARY)
            if value & YEARLY_VALUES.MARCH:
                months.append(YEARLY_TYPES.MARCH)
            if value & YEARLY_VALUES.APRIL:
                months.append(YEARLY_TYPES.APRIL)
            if value & YEARLY_VALUES.MAY:
                months.append(YEARLY_TYPES.MAY)
            if value & YEARLY_VALUES.JUNE:
                months.append(YEARLY_TYPES.JUNE)
            if value & YEARLY_VALUES.JULY:
                months.append(YEARLY_TYPES.JULY)
            if value & YEARLY_VALUES.AUGUST:
                months.append(YEARLY_TYPES.AUGUST)
            if value & YEARLY_VALUES.SEPTEMBER:
                months.append(YEARLY_TYPES.SEPTEMBER)
            if value & YEARLY_VALUES.OCTOBER:
                months.append(YEARLY_TYPES.OCTOBER)
            if value & YEARLY_VALUES.NOVEMBER:
                months.append(YEARLY_TYPES.NOVEMBER)
            if value & YEARLY_VALUES.DECEMBER:
                months.append(YEARLY_TYPES.DECEMBER)
            return months

        return []


    @staticmethod
    def frontend_recurrence_value_to_backend_recurrence_value(type, values):
        value = 0
        if type == RECURRENCE_TYPES.WEEKLY:
            for day in values:
                if day == WEEKLY_TYPES.MONDAY:
                    value += WEEKLY_VALUES.MONDAY
                elif day == WEEKLY_TYPES.TUESDAY:
                    value += WEEKLY_VALUES.TUESDAY
                elif day == WEEKLY_TYPES.WEDNESDAY:
                    value += WEEKLY_VALUES.WEDNESDAY
                elif day == WEEKLY_TYPES.THURSDAY:
                    value += WEEKLY_VALUES.THURSDAY
                elif day == WEEKLY_TYPES.FRIDAY:
                    value += WEEKLY_VALUES.FRIDAY
                elif day == WEEKLY_TYPES.SATURDAY:
                    value += WEEKLY_VALUES.SATURDAY
                elif day == WEEKLY_TYPES.SUNDAY:
                    value += WEEKLY_VALUES.SUNDAY

        elif type == RECURRENCE_TYPES.MONTHLY:
            for day in values:
                d = int(day)
                value += MONTH_VALUES[d - 1]

        elif type == RECURRENCE_TYPES.YEARLY:
            for month in values:
                if month == YEARLY_TYPES.JANUARY:
                    value += YEARLY_VALUES.JANUARY
                elif month == YEARLY_TYPES.FEBRUARY:
                    value += YEARLY_VALUES.FEBRUARY
                elif month == YEARLY_TYPES.MARCH:
                    value += YEARLY_VALUES.MARCH
                elif month == YEARLY_TYPES.APRIL:
                    value += YEARLY_VALUES.APRIL
                elif month == YEARLY_TYPES.MAY:
                    value += YEARLY_VALUES.MAY
                elif month == YEARLY_TYPES.JUNE:
                    value += YEARLY_VALUES.JUNE
                elif month == YEARLY_TYPES.JULY:
                    value += YEARLY_VALUES.JULY
                elif month == YEARLY_TYPES.AUGUST:
                    value += YEARLY_VALUES.AUGUST
                elif month == YEARLY_TYPES.SEPTEMBER:
                    value += YEARLY_VALUES.SEPTEMBER
                elif month == YEARLY_TYPES.OCTOBER:
                    value += YEARLY_VALUES.OCTOBER
                elif month == YEARLY_TYPES.NOVEMBER:
                    value += YEARLY_VALUES.NOVEMBER
                elif month == YEARLY_TYPES.DECEMBER:
                    value += YEARLY_VALUES.DECEMBER

        return value


    @staticmethod
    def reccurrence_value_to_date(type, value):
        now = datetime.now()
        dates = []
        if type == RECURRENCE_TYPES.WEEKLY:
            days = RecurrenceHelper.backend_to_frontend_recurrence_value(type, value)
            for day in days:
                day_to_num = {
                    WEEKLY_TYPES.MONDAY: 0,
                    WEEKLY_TYPES.TUESDAY: 1,
                    WEEKLY_TYPES.WEDNESDAY: 2,
                    WEEKLY_TYPES.THURSDAY: 3,
                    WEEKLY_TYPES.FRIDAY: 4,
                    WEEKLY_TYPES.SATURDAY: 5,
                    WEEKLY_TYPES.SUNDAY: 6,
                }
                days_ahead = day_to_num[day] - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7

                d = now + timedelta(days_ahead)
                d = d.replace(hour=0)
                d = d.replace(minute=0)
                d = d.replace(second=0)
                d = d.replace(microsecond=0)
                dates.append(d)

        elif type == RECURRENCE_TYPES.MONTHLY:
            days = RecurrenceHelper.backend_to_frontend_recurrence_value(type, value)
            for day in days:
                day = int(day)
                d = now.replace(day=day)
                d = d.replace(hour=0)
                d = d.replace(minute=0)
                d = d.replace(second=0)
                d = d.replace(microsecond=0)

                if d >= now:
                    dates.append(d)

        elif type == RECURRENCE_TYPES.YEARLY:
            months = RecurrenceHelper.backend_to_frontend_recurrence_value(type, value)
            for month in months:
                m = YEARLY_TYPES.TYPES.index(month) + 1
                d = now.replace(month=m)
                d = d.replace(day=1)
                d = d.replace(hour=0)
                d = d.replace(minute=0)
                d = d.replace(second=0)
                d = d.replace(microsecond=0)
                if d >= now:
                    dates.append(d)

        return dates