from DbMapper import RequiredModelResults
from DbMapper import ModelResultTypes


def to_values_str(attributes):
    return ','.join(str(attributes[key]) for key in sorted(attributes))


def sql_insert(table, values):
    return "INSERT INTO {0} VALUES({1})".format(table, values)


def sql_select_into(cols, new_table, old_tables, where):
    return "SELECT {0} INTO {1} FROM {2} WHERE {3}".format(cols, new_table, old_tables, where)


class ArchWriter(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def insert_into_rmr(self, fmrs):
        file = open(self.file_path, 'w')

        for fmr in fmrs:
            query = sql_insert('RequiredModelResults', to_values_str(fmr.to_dict_col_index_value()))
            print(query)
            file.writelines(query)
        file.close()

    def insert_into_mrt(self):
        pass


class DrmsWriter(object):
    def __init__(self):
        pass

    def insert_into_view(self):
        pass

    def insert_into_jp(self):
        pass


rmr1 = RequiredModelResults(42, None, 108, 'ABC', 'P', 'LIVE', 0)
rmr2 = RequiredModelResults(42, None, 108, None, 'P', 'LIVE', 0)
#print(to_values_str(rmr1.get_col_values_dict()))
print(sql_insert('RequiredModelResults', to_values_str(rmr1.to_dict_col_index_value())))
print(sql_insert('RequiredModelResults', to_values_str(rmr2.to_dict_col_index_value())))

