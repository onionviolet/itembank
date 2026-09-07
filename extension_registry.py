"""Validation for small, first-party extension declaration registries."""
import re

ENTRY_FIELDS = frozenset(("name", "version", "handler", "capability", "fallback", "check"))
NAME_RE = re.compile(r"[a-z][a-z0-9_]*")
VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


class RegistrationError(ValueError):
    """A first-party extension declaration is malformed or duplicated."""


def build_registry(entries):
    handlers, versions, descriptions = {}, {}, {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise RegistrationError("entry %d must be a dictionary" % index)
        fields = set(entry)
        missing, extra = sorted(ENTRY_FIELDS - fields), sorted(fields - ENTRY_FIELDS)
        if missing:
            raise RegistrationError("entry %d missing field %s" % (index, missing[0]))
        if extra:
            raise RegistrationError("entry %d has extra field %s" % (index, extra[0]))
        name = entry["name"]
        if not isinstance(name, str) or NAME_RE.fullmatch(name) is None:
            raise RegistrationError("entry %d field name is invalid" % index)
        if name in handlers:
            raise RegistrationError("entry %d duplicates name %s" % (index, name))
        version = entry["version"]
        if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
            raise RegistrationError("entry %d field version is invalid" % index)
        if not callable(entry["handler"]):
            raise RegistrationError("entry %d field handler must be callable" % index)
        for field in ("capability", "fallback", "check"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise RegistrationError("entry %d field %s must be a nonblank string" % (index, field))
        handlers[name] = entry["handler"]
        versions[name] = version
        descriptions[name] = {field: entry[field] for field in ENTRY_FIELDS if field != "handler"}
    return handlers, versions, descriptions
