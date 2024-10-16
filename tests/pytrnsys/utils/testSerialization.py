import copy as _cp
import dataclasses as _dc
import json as _json
import typing as _tp
import uuid as _uuid

import dataclasses_jsonschema as _dcj
import pytest as _pt

import pytrnsys.utils.serialization as _ser


@_dc.dataclass
class PersonVersion0(_ser.UpgradableJsonSchemaMixinVersion0):
    firstName: str
    age: int
    heightInM: float

    @classmethod
    def getVersion(cls) -> _uuid.UUID:
        return _uuid.UUID("ff2ba3c8-4fef-4a64-a026-11212ab35d6b")


@_dc.dataclass
class PersonVersion1(_ser.UpgradableJsonSchemaMixin):
    firstName: str

    lastName: str
    age: int
    heightInCm: int

    @classmethod
    def getSupersededClass(cls) -> _tp.Type[PersonVersion0]:
        return PersonVersion0

    @classmethod
    def upgrade(cls, superseded: _ser.UpgradableJsonSchemaMixinVersion0) -> "PersonVersion1":
        assert isinstance(superseded, PersonVersion0)

        lastName = ""
        heightInCm = round(superseded.heightInM * 100)
        return PersonVersion1(superseded.firstName, lastName, superseded.age, heightInCm)

    @classmethod
    def getVersion(cls) -> _uuid.UUID:
        return _uuid.UUID("70d5694f-032c-4ca8-b13c-c020b05f2179")


@_dc.dataclass
class HasTitle:
    title: str


@_dc.dataclass
class Person(HasTitle, _ser.UpgradableJsonSchemaMixin):
    lastName: str
    ageInYears: int
    heightInCm: int

    @classmethod
    def getSupersededClass(cls) -> _tp.Type[PersonVersion1]:
        return PersonVersion1

    @classmethod
    def upgrade(cls, superseded: _ser.UpgradableJsonSchemaMixinVersion0) -> "Person":
        assert isinstance(superseded, PersonVersion1)

        title = ""
        ageInYears = superseded.age
        return Person(title, superseded.lastName, ageInYears, superseded.heightInCm)

    @classmethod
    def getVersion(cls) -> _uuid.UUID:
        return _uuid.UUID("1774d088-3917-4c29-a76a-0a4514ef6cf5")


@_dc.dataclass
class Team(_ser.UpgradableJsonSchemaMixinVersion0):
    members: _tp.Sequence[Person]

    def __post_init__(self):
        if not self.members:
            raise ValueError("Team must have at least one member.")

    @classmethod
    def getVersion(cls) -> _uuid.UUID:
        return _uuid.UUID("9e322099-c043-4f23-b6df-4087bb5950d7")


class TestSerialization:
    SERIALIZED_P0 = {
        "__version__": "ff2ba3c8-4fef-4a64-a026-11212ab35d6b",
        "age": 32,
        "firstName": "Damian",
        "heightInM": 1.73,
    }
    SERIALIZED_P1 = {
        "__version__": "70d5694f-032c-4ca8-b13c-c020b05f2179",
        "age": 32,
        "firstName": "Damian",
        "heightInCm": 173,
        "lastName": "Birchler",
    }
    SERIALIZED_P = {
        "__version__": "1774d088-3917-4c29-a76a-0a4514ef6cf5",
        "ageInYears": 32,
        "heightInCm": 173,
        "lastName": "Birchler",
        "title": "Mr.",
    }
    SERIALIZED_T0 = {
        "__version__": "9e322099-c043-4f23-b6df-4087bb5950d7",
        "members": [
            {
                "__version__": "ff2ba3c8-4fef-4a64-a026-11212ab35d6b",
                "age": 32,
                "firstName": "Damian",
                "heightInM": 1.73,
            },
            {
                "__version__": "70d5694f-032c-4ca8-b13c-c020b05f2179",
                "age": 32,
                "firstName": "Damian",
                "heightInCm": 173,
                "lastName": "Birchler",
            },
            {
                "__version__": "1774d088-3917-4c29-a76a-0a4514ef6cf5",
                "ageInYears": 32,
                "heightInCm": 173,
                "lastName": "Birchler",
                "title": "Mr.",
            },
        ],
    }

    def testSerialization(self):
        person0 = PersonVersion0(firstName="Damian", age=32, heightInM=1.73)
        assert person0.to_dict() == self.SERIALIZED_P0

        person1 = PersonVersion1(firstName="Damian", lastName="Birchler", age=32, heightInCm=173)
        assert person1.to_dict() == self.SERIALIZED_P1

        person = Person(title="Mr.", lastName="Birchler", ageInYears=32, heightInCm=173)
        assert person.to_dict() == self.SERIALIZED_P

        team = Team([person0, person1, person])
        assert team.to_dict() == self.SERIALIZED_T0

    def testStandardUseCase(self):
        json = _json.dumps(self.SERIALIZED_P0)

        person = Person.from_json(json)

        assert person.title == ""
        assert person.lastName == ""
        assert person.ageInYears == self.SERIALIZED_P0["age"]
        assert person.heightInCm == self.SERIALIZED_P0["heightInM"] * 100

    def testWrongVersionRaises(self):
        serializedP1 = _cp.deepcopy(self.SERIALIZED_P1)
        serializedP1["__version__"] = 4
        json = _json.dumps(serializedP1)

        with _pt.raises(_ser.SerializationError):
            Person.from_json(json)

    def testWrongVersion0Raises(self):
        serializedP1 = _cp.deepcopy(self.SERIALIZED_P0)
        serializedP1["__version__"] = "2cba32bd-4c8a-49fc-9f0b-a6b312adcf24"
        json = _json.dumps(serializedP1)

        with _pt.raises(_ser.SerializationError):
            Person.from_json(json)

    def testMissingVersion0DoesNotRaise(self):
        serializedP0 = _cp.deepcopy(self.SERIALIZED_P0)
        del serializedP0["__version__"]

        json = _json.dumps(serializedP0)

        Person.from_json(json)

    def testMissingVersionRaises(self):
        serializedP = _cp.deepcopy(self.SERIALIZED_P)
        del serializedP["__version__"]

        json = _json.dumps(serializedP)

        with _pt.raises(_ser.SerializationError):
            Person.from_json(json)

    def testLoadVersion1(self):
        json = _json.dumps(self.SERIALIZED_P1)

        person1 = PersonVersion1.from_json(json)
        person = Person.from_json(json)

        assert person.title == ""
        assert person.lastName == person1.lastName
        assert person.ageInYears == person1.age
        assert person.heightInCm == person1.heightInCm

    def testWrongFormatRaises(self):
        phonyP1 = self.SERIALIZED_P0.copy()
        firstName = phonyP1["firstName"]
        del phonyP1["firstName"]
        phonyP1["first-mohican"] = firstName

        json = _json.dumps(phonyP1)

        with _pt.raises(_ser.SerializationError):
            Person.from_json(json)

        with _pt.raises(_ser.SerializationError):
            PersonVersion0.from_json(json)

    def testUnknownFieldRaises(self):
        phonyP1 = self.SERIALIZED_P0.copy()
        phonyP1["unknown_field"] = 42

        json = _json.dumps(phonyP1)

        with _pt.raises(_ser.SerializationError):
            Person.from_json(json)

        with _pt.raises(_ser.SerializationError):
            PersonVersion0.from_json(json)

    def testNested(self):
        json = _json.dumps(self.SERIALIZED_T0)
        
        actualSchema = _json.dumps(Team.json_schema(), indent=4)
        print(actualSchema)
        expectedSchema = """\
{
    "type": "object",
    "required": [
        "members"
    ],
    "properties": {
        "members": {
            "type": "array",
            "items": {
                "$ref": "#/definitions/Person"
            }
        },
        "__version__": {
            "const": "9e322099-c043-4f23-b6df-4087bb5950d7"
        }
    },
    "description": "Team(members: Sequence[tests.pytrnsys.utils.testSerialization.Person])",
    "$schema": "http://json-schema.org/draft-06/schema#",
    "definitions": {
        "Person": {
            "anyOf": [
                {
                    "type": "object",
                    "required": [
                        "title",
                        "lastName",
                        "ageInYears",
                        "heightInCm",
                        "__version__"
                    ],
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "lastName": {
                            "type": "string"
                        },
                        "ageInYears": {
                            "type": "integer"
                        },
                        "heightInCm": {
                            "type": "integer"
                        },
                        "__version__": {
                            "const": "1774d088-3917-4c29-a76a-0a4514ef6cf5"
                        }
                    },
                    "description": "Person(title: str, lastName: str, ageInYears: int, heightInCm: int)",
                    "additionalProperties": false
                },
                {
                    "$ref": "#/definitions/PersonVersion1"
                }
            ]
        },
        "PersonVersion1": {
            "anyOf": [
                {
                    "type": "object",
                    "required": [
                        "firstName",
                        "lastName",
                        "age",
                        "heightInCm",
                        "__version__"
                    ],
                    "properties": {
                        "firstName": {
                            "type": "string"
                        },
                        "lastName": {
                            "type": "string"
                        },
                        "age": {
                            "type": "integer"
                        },
                        "heightInCm": {
                            "type": "integer"
                        },
                        "__version__": {
                            "const": "70d5694f-032c-4ca8-b13c-c020b05f2179"
                        }
                    },
                    "description": "PersonVersion1(firstName: str, lastName: str, age: int, heightInCm: int)",
                    "additionalProperties": false
                },
                {
                    "$ref": "#/definitions/PersonVersion0"
                }
            ]
        },
        "PersonVersion0": {
            "type": "object",
            "required": [
                "firstName",
                "age",
                "heightInM"
            ],
            "properties": {
                "firstName": {
                    "type": "string"
                },
                "age": {
                    "type": "integer"
                },
                "heightInM": {
                    "type": "number"
                },
                "__version__": {
                    "const": "ff2ba3c8-4fef-4a64-a026-11212ab35d6b"
                }
            },
            "description": "PersonVersion0(firstName: str, age: int, heightInM: float)",
            "additionalProperties": false
        }
    },
    "additionalProperties": false
}"""
        
        assert actualSchema == expectedSchema
        
        team = Team.from_json(json)

        expectedMembers = [Person.from_dict(d) for d in [self.SERIALIZED_P0, self.SERIALIZED_P1, self.SERIALIZED_P]]

        assert team.members == expectedMembers

    @staticmethod
    def testDataclassInUnion():
        outerObject = OuterClass(Variable("Voldemort"))

        json = outerObject.to_json()

        assert json == """{"values": {"name": "Voldemort"}}"""

        deserializedOuterObject = OuterClass.from_json(json)

        assert deserializedOuterObject == outerObject


@_dc.dataclass
class Variable(_dcj.JsonSchemaMixin):
    name: str


Value = _tp.Union[Variable, float]


@_dc.dataclass
class OuterClass(_dcj.JsonSchemaMixin):
    values: Value
