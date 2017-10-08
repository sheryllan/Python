from enum import Enum
from types import *


def transform(data):
    return bound_with_single_quote(data) if type(data) is str else null_str_tenary(data)


def bound_with_single_quote(s):
    return "'{0}'".format(s)


def null_str_tenary(val):
    return val if val is not None else "NULL"


class ColumnsRmr(Enum):
    sec_type = 1
    sec_class = 2
    result_id = 3
    model_name = 4
    breakdown_level = 5
    publish_type = 6
    kdb_only = 7


class ColumnsMrt(Enum):
    result_id = 1
    result_name = 2


class Column(object):
    def __init__(self, name, index, is_id, data):
        self.name = name
        self.index = index
        self.is_id = is_id
        self.data = data


class TableBase(object):
    def to_dict_col_index_value(self):
        return {col.index: transform(col.data) for _, col in self.__dict__.items()}


class RequiredModelResults(TableBase):
    def __init__(self, sec_type, sec_class, result_id, model_name, breakdown_level, publish_type, kdb_only):
        self.sec_type = Column(ColumnsRmr.sec_type.name, ColumnsRmr.sec_type.value, True, sec_type)
        self.sec_class = Column(ColumnsRmr.sec_class.name, ColumnsRmr.sec_class.value, True, sec_class)
        self.result_id = Column(ColumnsRmr.result_id.name, ColumnsRmr.result_id.value, True, result_id)
        self.model_name = Column(ColumnsRmr.model_name.name, ColumnsRmr.model_name.value, True, model_name)
        self.breakdown_level = Column(ColumnsRmr.breakdown_level.name, ColumnsRmr.breakdown_level.value, True,
                                      breakdown_level)
        self.publish_type = Column(ColumnsRmr.publish_type.name, ColumnsRmr.publish_type.value, True, publish_type)
        self.kdb_only = Column(ColumnsRmr.kdb_only.name, ColumnsRmr.kdb_only.value, False, kdb_only)


class ModelResultTypes(TableBase):
    def __init__(self, result_id, result_name):
        self.result_id = Column(ColumnsMrt.result_id.name, ColumnsMrt.result_id.value, True, result_id)
        self.result_name = Column(ColumnsMrt.result_name.name, ColumnsMrt.result_name.value, True, result_name)


rmr1 = RequiredModelResults(42, None, 108, 'ABC', 'P', 'LIVE', 0)
#print(rmr1.sec_type.data_type, rmr1.sec_class.data_type)
print(rmr1.sec_class.name)
print(rmr1.to_dict_col_index_value())
