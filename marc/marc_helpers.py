from pymarc.record import Record

def is_holding(record: Record):
    return record.leader[6] in 'uvxy'

def is_authority(record: Record):
    return record.leader[6] in 'z'

def record_type(record: Record):
    if record.leader[6] in 'z':
        return 'authority'
    if record.leader[6] in 'uvxy':
        return 'holding'
    if record.leader[6] in 'w':
        return 'classification'
    if record.leader[6] in 'q':
        return 'community'
    return 'bibliographic'

def record_id(record: Record):
    return record['001'].value()

def extract_values(record: Record, field_tag, subfield_tags):
    values = []
    for field in record.get_fields(field_tag):
        values += field.get_subfields(*subfield_tags)
    return values

def record_fields_to_dict(
        record: Record, 
        fields: list[str], 
        repeatable_fields: list[str]) -> dict[str,str|list[str]]:
    """Returns a dictionary with record field values by tag. Multi 
    valued fields are returned as a list of strings. If a repeatable is
    not correctly identified, only the last instance of that field process
    will be preserved.

    Args:
        record (Record): A MARC record instance.
        fields (list[str]): List of field tags that we want to extract.
        repeatable_fields (list[str]): List of repeatable fields to be extracted.

    Returns:
        dict[str,str|list[str]]: Dictionary mapping requested field tags to value or list of values obtained.
    """
    record_dict = dict()
    record_dict["leader"] = list(record.leader)
    fields = record.get_fields(*fields)
    for field in fields:
        if field.tag not in repeatable_fields:
            assert field.tag not in record_dict.keys(), f"Tag '{field.tag}' found multiple times for `{record.leader}`. You may want to include it in your `repeatable_fields` list."
            record_dict[field.tag] = field.value()
        else:
            if field.tag not in record_dict.keys():
                record_dict[field.tag]=[]
            record_dict[field.tag].append(field.value())
    return record_dict
