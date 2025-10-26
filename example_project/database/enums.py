from enum import Enum as PyEnum

class EnumLenFix:
    def __len__(self):
        return len(str(self.value))

class GradeEnum(EnumLenFix, PyEnum):
    """
    G_1 = 1 | G_2 = 2 | G_3 = 3 | G_4 = 4 | G_5 = 5 | G_6 = 6 | G_7 = 7 | G_8 = 8 | G_9 = 9 | G_10 = 10`{s.value}`
    """
    G_1 = 1
    G_2 = 2
    G_3 = 3
    G_4 = 4
    G_5 = 5
    G_6 = 6
    G_7 = 7
    G_8 = 8
    G_9 = 9
    G_10 = 10


class RegisterStatus(EnumLenFix, PyEnum):
    ZERO = "ZERO"
    PHONE = "PHONE"
    REGISTERED = "REGISTERED"
    SERVICE_CUSTOMER = "SERVICE_CUSTOMER"

class StudentYear(EnumLenFix, PyEnum):
    """FIRST | SECOND | THIRD | FOURTH | FIFTH | SIXTH | SEVENTH | EIGHTH | NINTH | TENTH | ELEVENTH"""
    FIRST = "FIRST"
    SECOND = "SECOND"
    THIRD = "THIRD"
    FOURTH = "FOURTH"
    FIFTH = "FIFTH"
    SIXTH = "SIXTH"
    SEVENTH = "SEVENTH"
    EIGHTH = "EIGHTH"
    NINTH = "NINTH"
    TENTH = "TENTH"
    ELEVENTH = "ELEVENTH"

class StudentInstitution(EnumLenFix, PyEnum):
    """SCHOOL | UNIVERSITY | COLLEGE | INSTITUTE | ACADEMY | OTHER"""
    SCHOOL = "SCHOOL"
    UNIVERSITY = "UNIVERSITY"
    COLLEGE = "COLLEGE"
    INSTITUTE = "INSTITUTE"
    ACADEMY = "ACADEMY"
    OTHER = "OTHER"


class UserResidence(EnumLenFix, PyEnum):
    """KARAKALPAGHISTAN | UZ_REGION | TASHKENT | WHOLE_UZB | ASIA | CENTRAL_ASIA | EUROPE | BEYOND_SEA | WHOLE_WORLD"""
    KARAKALPAGHISTAN = "KARAKALPAGHISTAN"
    UZ_REGION = "UZ_REGION"
    TASHKENT = "TASHKENT"
    WHOLE_UZB = "WHOLE_UZB"
    ASIA = "ASIA"
    CENTRAL_ASIA = "CENTRAL_ASIA"
    EUROPE = "EUROPE"
    BEYOND_SEA = "BEYOND_SEA"
    WHOLE_WORLD = "WHOLE_WORLD"


class UserRelative(EnumLenFix, PyEnum):
    """FATHER | MOTHER | HUSBAND | WIFE | CHILD | BROTHER | UNCLE | GRANDFATHER"""
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    HUSBAND = "HUSBAND"
    WIFE = "WIFE"
    CHILD = "CHILD"
    BROTHER = "BROTHER"
    UNCLE = "UNCLE"
    GRANDFATHER = "GRANDFATHER"
