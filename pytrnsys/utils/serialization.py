__all__ = [
    "UpgradableJsonSchemaMixinVersion0",
    "UpgradableJsonSchemaMixin",
    "SerializationError",
]

import abc as _abc
import json as _json
import logging as _log
import typing as _tp
import uuid as _uuid

import dataclasses_jsonschema as _dcj

_S = _tp.TypeVar("_S", bound="UpgradableJsonSchemaMixinVersion0")
_T = _tp.TypeVar("_T", bound="UpgradableJsonSchemaMixin")


_logger = _log.getLogger("root")


class SerializationError(ValueError):
    pass


class ValidationError(SerializationError):
    def __init__(self, data: str, schema: str, *args: _tp.Any) -> None:
        self.data = data
        self.schema = schema
        super().__init__(*args)

    @staticmethod
    def create(data: _dcj.JsonDict, schema: _dcj.JsonDict, *args: _tp.Any) -> "ValidationError":
        serializedData = _json.dumps(data, indent=4)
        serializedSchema = _json.dumps(schema, indent=4)
        return ValidationError(serializedData, serializedSchema, *args)

    def __str__(self) -> str:
        return f"""\
<{type(self).__name__}

data =
    
{self.data}
    
schema = 
    
{self.schema}

>"""


class UpgradableJsonSchemaMixinVersion0(_dcj.JsonSchemaMixin):
    @classmethod
    def from_dict(
        cls: _tp.Type[_S],
        data: _dcj.JsonDict,
        validate=True,
        validate_enums: bool = True,
        schema_type: _dcj.SchemaType = _dcj.DEFAULT_SCHEMA_TYPE,  # /NOSONAR
    ) -> _S:
        if cls._doesRequireVersion() and "__version__" not in data:
            raise SerializationError("No '__version__' field found.")

        if "__version__" in data:
            data = data.copy()
            actualVersion = data.pop("__version__")
            expectedVersion = str(cls.getVersion())

            if actualVersion != expectedVersion:
                raise SerializationError(f"Version mismatch: expected {expectedVersion}, got {actualVersion}.")

        try:
            deserializedObject = super().from_dict(data, validate, validate_enums, schema_type)
        except _dcj.ValidationError as error:
            cls._raiseValidationErrorFrom(error, data, validate_enums, schema_type)

        return _tp.cast(_S, deserializedObject)

    def to_dict(
        self,
        omit_none: bool = True,
        validate: bool = False,
        validate_enums: bool = True,
        schema_type: _dcj.SchemaType = _dcj.DEFAULT_SCHEMA_TYPE,  # /NOSONAR
    ) -> _dcj.JsonDict:
        data = super().to_dict(omit_none, validate, validate_enums, schema_type)

        assert (
            "__version__" not in data
        ), "Serialized object dictionary from dataclasses-json already contained '__version__' key!"

        data["__version__"] = str(self.getVersion())

        return data

    @classmethod
    def _raiseValidationErrorFrom(
        cls,
        error: _dcj.ValidationError,
        data: _dcj.JsonDict,
        validate_enums: bool,  # pylint: disable=invalid-name
        schema_type: _dcj.SchemaType,  # pylint: disable=invalid-name
    ) -> _tp.NoReturn:
        schema = cls.json_schema(embeddable=False, schema_type=schema_type, validate_enums=validate_enums)

        validationError = ValidationError.create(data, schema, data)  # pylint: disable=arguments-out-of-order

        raise validationError from error

    @classmethod
    def json_schema(
        cls,
        embeddable: bool = False,
        schema_type: _dcj.SchemaType = _dcj.DEFAULT_SCHEMA_TYPE,
        validate_enums: bool = True,
        **kwargs,
    ) -> _dcj.JsonDict:
        fullSchema = super().json_schema(embeddable, schema_type, validate_enums, **kwargs)

        schema = fullSchema[cls.__name__] if embeddable else fullSchema

        schema = cls._addVersionToSchema(schema)
        schema = cls._addAdditionalPropertiesToSchema(schema)

        return {**fullSchema, cls.__name__: schema} if embeddable else schema

    @classmethod
    def _addVersionToSchema(cls, schema):
        properties = schema.get("properties", {})
        properties = {**properties, "__version__": {"const": str(cls.getVersion())}}

        required = schema.get("required", [])
        if cls._doesRequireVersion():
            required = [*required, "__version__"]

        schema = {
            **schema,
            "properties": properties,
            "required": required,
        }

        return schema

    @classmethod
    def _addAdditionalPropertiesToSchema(cls, schema):
        return {**schema, "additionalProperties": cls.additionalProperties()}

    @classmethod
    @_abc.abstractmethod
    def getVersion(cls) -> _uuid.UUID:
        """To be overwritten in subclass. Use
        .. code-block:: python

            import uuid
            print(str(uuid.uuid4()))

        to generate a version and return that version
        as a *constant* like so:

            .. code-block:: python

            def getVersion(cls):
                return uuid.UUID("41280f1d-67f5-4827-a306-4b2d71cba4c2")
        """
        raise NotImplementedError()

    @classmethod
    def additionalProperties(cls) -> bool:
        return False

    @classmethod
    def _doesRequireVersion(cls) -> bool:
        return False


class UpgradableJsonSchemaMixin(UpgradableJsonSchemaMixinVersion0, _abc.ABC):
    @classmethod
    def from_dict(
        cls: _tp.Type[_T],
        data: _dcj.JsonDict,
        validate=True,
        validate_enums: bool = True,
        schema_type: _dcj.SchemaType = _dcj.DEFAULT_SCHEMA_TYPE,  # /NOSONAR
    ) -> _T:
        if validate:
            try:
                cls._validate(data, validate_enums)
            except _dcj.ValidationError as error:
                cls._raiseValidationErrorFrom(error, data, validate_enums, schema_type)

        try:
            return super().from_dict(data, validate=False, validate_enums=validate_enums, schema_type=schema_type)
        except SerializationError:
            supersededClass = cls.getSupersededClass()

            supersededInstance = supersededClass.from_dict(
                data, validate=False, validate_enums=validate_enums, schema_type=schema_type
            )

            return cls.upgrade(supersededInstance)

    @classmethod
    def json_schema(
        cls,
        embeddable: bool = False,
        schema_type: _dcj.SchemaType = _dcj.DEFAULT_SCHEMA_TYPE,
        validate_enums: bool = True,
        **kwargs,
    ) -> _dcj.JsonDict:
        if embeddable:
            return cls._getEmbeddableSchema(kwargs, schema_type, validate_enums)

        return cls._getSchema(kwargs, schema_type, validate_enums)

    @classmethod
    def _getEmbeddableSchema(cls, kwargs, schemaType, validateEnums):
        embeddableSchema = super().json_schema(
            embeddable=True,
            schema_type=schemaType,
            validate_enums=validateEnums,
            **kwargs,
        )

        supersededClass = cls.getSupersededClass()
        embeddableSupersededSchema = supersededClass.json_schema(
            embeddable=True,
            schema_type=schemaType,
            validate_enums=validateEnums,
            **kwargs,
        )

        combinedEmbeddableSchema = cls._addSupersededSchemaToEmbeddable(
            embeddableSchema, embeddableSupersededSchema, schemaType, supersededClass
        )
        return combinedEmbeddableSchema

    @classmethod
    def _addSupersededSchemaToEmbeddable(
        cls, embeddableSchema, embeddableSupersededSchema, schemaType, supersededClass
    ):
        schema = embeddableSchema[cls.__name__]
        schemaReference = _dcj.schema_reference(schemaType, supersededClass.__name__)
        combinedSchema = {"anyOf": [schema, schemaReference]}
        combinedEmbeddableSchema = {
            **embeddableSchema,
            cls.__name__: combinedSchema,
            **embeddableSupersededSchema,
        }
        return combinedEmbeddableSchema

    @classmethod
    def _getSchema(cls, kwargs, schemaType, validateEnums):
        fullSchema = super().json_schema(
            embeddable=False,
            schema_type=schemaType,
            validate_enums=validateEnums,
            **kwargs,
        )

        supersededClass = cls.getSupersededClass()
        fullSupersededSchema = supersededClass.json_schema(
            embeddable=True,
            schema_type=schemaType,
            validate_enums=validateEnums,
            **kwargs,
        )

        combinedFullSchema = cls._addSupersededSchemaToTopLevel(
            fullSupersededSchema, fullSchema, supersededClass, schemaType
        )
        return combinedFullSchema

    @classmethod
    def _addSupersededSchemaToTopLevel(cls, fullSupersededSchema, fullSchema, supersededClass, schemaType):
        definitions = fullSchema.get("definitions", {})

        cls._assertNoCollidingDefinitions(definitions, fullSupersededSchema)

        allDefinitions = definitions | fullSupersededSchema

        keys = {"type", "properties", "required", "description", "additionalProperties"}
        schema = {k: v for k, v in fullSchema.items() if k in keys}
        remainingSchema = {k: v for k, v in fullSchema.items() if k not in keys}

        schemaReference = _dcj.schema_reference(schemaType, supersededClass.__name__)
        combinedSchema = {"anyOf": [schema, schemaReference]}

        combinedFullSchema = {**remainingSchema, **combinedSchema, "definitions": allDefinitions}
        return combinedFullSchema

    @classmethod
    def _assertNoCollidingDefinitions(cls, definitions, fullSupersededSchema):
        collidingDefinitions = [
            (k, v) for k, v in fullSupersededSchema.items() if k in definitions and definitions[k] != v
        ]
        if collidingDefinitions:
            key, newDefinition = collidingDefinitions[0]
            currentDefinition = definitions[key]
            raise AssertionError(
                f"Colliding definition for {key}: old = {_json.dumps(currentDefinition)}, "
                f"new = {_json.dumps(newDefinition)}"
            )

    @classmethod
    def fromInstance(cls: _tp.Type[_T], instance: UpgradableJsonSchemaMixinVersion0) -> _T:
        supersededClass = cls.getSupersededClass()
        if type(instance) == supersededClass:  # pylint: disable=unidiomatic-typecheck
            return cls.upgrade(instance)

        if issubclass(supersededClass, UpgradableJsonSchemaMixin):
            partiallyUpgradedInstance = supersededClass.fromInstance(instance)

            return cls.upgrade(partiallyUpgradedInstance)

        raise ValueError("`instance' isn't an instance of current or any previous version.")

    @classmethod
    def _doesRequireVersion(cls) -> bool:
        return True

    @classmethod
    @_abc.abstractmethod
    def getSupersededClass(cls) -> _tp.Type[UpgradableJsonSchemaMixinVersion0]:
        raise NotImplementedError()

    @classmethod
    @_abc.abstractmethod
    def upgrade(cls: _tp.Type[_T], superseded: UpgradableJsonSchemaMixinVersion0) -> _T:
        raise NotImplementedError()
