from base_processor import BaseProcessor
from marc.marc_helpers import is_holding, Record, record_type
from sys import stderr
import re

def extract_record_fields(record: Record, fields: list[str], repeatable_fields: list[str]):
        """This function is a utility to extract MARC fields from a Record object and return a dictionary"""
        record_dict = dict()
        fields = record.get_fields(*fields)
        for field in fields:
            if field.tag not in repeatable_fields:
                record_dict[field.tag] = field.value()
            else:
                if field.tag not in record_dict.keys():
                    record_dict[field.tag]=[]
                record_dict[field.tag].append(field.value())
        return record_dict


class DataSetReport(BaseProcessor):
    def __init__(self, reporter):
        self.reporter = reporter
        self.dataset_bibids = set()
        print("Initiated DataSetReport Processor", file=stderr)

    def is_dataset_holding(self, record: Record):
        return record.get_fields("004")[0].value() in self.dataset_bibids

    @staticmethod
    def is_dataset_record(record: Record):
        is_dataset = False
        for f090 in record.get_fields("090"):
            # Consider dataset by Yale local call number at https://web.library.yale.edu/cataloging/manuscript/0xx
            if re.match(r"yuldset", f090.value()):
                is_dataset = True
                break
        for f336 in record.get_fields("336"):
            # Matches quicksearch filter at https://github.com/yalelibrary/search-frontend/blob/main/lib/traject/macros/marc_format_classifier.rb
            if re.match(r"dataset", f336.value()):
                is_dataset = True
                break
        return is_dataset
    
    def marc_record(self, record: Record):
        """Generate report that includes fields
        001, 090, 245, 264, 300, 336 and 856 for bibligraphic
        datasets and related holdings that may have 856.

        Args:
            record: Record: _description_
        """
        fields = [ "001", "090", "245", "264", "300", "336","852" ,"856" ]
        hold_fields = ["001","004","090","245","264","300","336","852","856"]
        repeatable_fields = ["090", "264", "300", "336", "852", "856"]
        if is_holding(record):
            # Holding Record Processing
            try:
                if self.is_dataset_holding(record):
                    hold_dict = extract_record_fields(record, hold_fields, repeatable_fields)
                    print(hold_dict)
            except IndexError:
                hold_dict = extract_record_fields(record, ["001","090","245","264","300","004","852","856"], repeatable_fields)
                known_error = False
                for v852 in hold_dict.get("852", []):
                    if "circBDIR" in v852:
                        known_error = True
                if not known_error:
                    print(hold_dict, file=stderr)
        else:
            # Bibligraphic Record Processing
            if DataSetReport.is_dataset_record(record):
                    bib_dict = extract_record_fields(record,fields,repeatable_fields)
                    if "001" in bib_dict.keys():
                        self.dataset_bibids.add(bib_dict["001"])
                    else:
                        print(f"WARNING Missing 001: {bib_dict}", file=stderr)
                    print(bib_dict)

