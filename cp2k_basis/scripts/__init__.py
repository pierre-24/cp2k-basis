from schema import Schema, Optional, Or

SCHEMA_METADATA = Schema({
    str: {
        'description': str,
        'references': [str],
        Optional('kind'): [str]
    }
})

SCHEMA_FILE = Schema({
    'name': str,
    'type': Or('BASIS_SETS', 'POTENTIALS'),
    Optional('patch'): str,
    Optional('family_name'): {str: str},
    Optional('variant'): {str: str}
})

SCHEMA_LIBRARY_SOURCE_FILE = Schema({
    'repositories': [{
        'base': str,
        Optional('data'): {str: object},
        'files': [SCHEMA_FILE]
    }],
    'metadata': SCHEMA_METADATA,
    str: object  # skip other stuffs
})

SCHEMA_EXPLORE_SOURCE_FILE = Schema({
    'files': [SCHEMA_FILE],
    Optional('metadata'): SCHEMA_METADATA,
    str: object  # skip other stuffs
})
