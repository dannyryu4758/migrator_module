import sys
from pathlib import Path
import datetime
from re import L
from typing import ValuesView
from numpy import diff
from sqlalchemy.dialects.mysql.types import LONGTEXT
from sqlalchemy.sql.schema import Column, MetaData, Table
from sqlalchemy.sql.sqltypes import Date, String
# from tracer import Tracer
from tracer_module.tracer import Tracer
from sqlalchemy import create_engine, types
from urllib.parse import quote
import pandas as pd
from pandasql import sqldf
import logging
import os
import traceback
from KISTEP_migration_info import *
# from KISTEP_migration_info_test import *
logging.basicConfig(level=logging.ERROR)

base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)))

validation_migration_info_type = {
    "SOURCE_DB_ACCESS_INFO": str,
    "SOURCE_TABLE": str,
    "SELECT_CONDITION": str,
    "SOURCE_COLS": list,
    "FILTER_BY_COL_VALS": list,
    "PREPROCESS": list,
    "POSTPROCESS": list,
    "JOIN_KEY": list,
    "SELECT_CONDITION": str,
    "TARGET_DB_ACCESS_INFO": str,
    "TARGET_TABLE": str,
    "ADD_COMMENT": str,
    "REMARK": str,
    "remark": str,
}

tracer_params_validation = {
    "remove_cols": {"target_cols": list},
    "copy_cols": {"target_cols": list, "params": {"required": {'source_cols': list}}},
    "add_groupby_rank": {"target_cols": list, "params": {"required": {'ranked_col': str, 'group_col': str, 'new_col': str}}},
    "add_cols": {"target_cols": list, "params": {'source_cols': list}},
    "custom_groupby": {"params": {"required": {'group_cols': list, 'agg_col': str}, 'agg_type': str}},
    "custom_groupby_concat": {"params": {"required": {'sum_cols': list, 'group_col': list}, 'sep': str}},
    "custom_col_concat": {"params": {"required": {'sum_cols': list, 'col_name': str}, 'sep': str}},
    "custom_all_concat": {"params": {"required": {'group_cols': list, 'col_name': str}, 'remove_col_yn': str}},
    "comm_cd_join": {"params": {"required": {'code_map_table': str, 'on': str}, 'code_map_col': str, 'right_on': str, 'new_col_name': str}},
    "drop_na": {"target_cols": list, "params": {'axis': int}},
    "drop_duplicates": {"target_cols": list, "params": {"sortby": list, 'keep': str}},
    "fillna": {"target_cols": list},
    "df_query_filter": {"params": {"required": {'query': str}}},
    "df_to_dict": {"params": {"required": {'col_name': str}}},
    "sort": {"params": {"required": {'sort_by_cols': list}}, 'order_by': str},
    "rename_cols": {"params": dict},
    "col_dict_to_json":{"target_cols":list},
    "adapter_dict_to_json": {"target_cols": list},
    "adapter_etc_cleaning": {"target_cols": list, "params": {'del_word': bool, 'space_word': bool}},
    "adapter_bracket_cleaning": {"target_cols": list, "params": {'only_bracket': bool}},
    "adapter_not_word_del": {"target_cols": list},
    "adapter_replace_not_mean_word": {"target_cols": list},
    "adapter_double_space_cleaning": {"target_cols": list},
    "adapter_cleaning_organ_nm": {"target_cols": list},
    "adapter_cleaning_univer_nm": {"target_cols": list},
    "adapter_cleaning_all_agency_nm": {"target_cols": list},
    "adapter_word_unification_cleaning": {"target_cols": list},
    "adapter_remove_all_special_word": {"target_cols": list},
    "adapter_start_end_with_special_char": {"target_cols": list},
}


class Migration_Tracer():
    def __init__(self, database_list=None, validation=True, selected_validation=False, temp_save=True):
        # ?????? ????????? ?????? ????????? ????????? ???????????? ??????
        self.temp_save = temp_save
        print(f"?????? ????????? ???????????? : {self.temp_save}\n?????? ?????? ?????? : {validation}")
        self.migration_info_list = list(MIGRATION_INFO.keys())
        if database_list and len(database_list) > 0:
            self.migration_info_list = database_list

        # self.val_dic = {}
        self.tracer = Tracer()
        self.processing_df = pd.DataFrame()
        self.step = None

        # ???????????? ????????? ??????
        self.code_map_dict = {}
        prev_engine_info = None
        engine = None
        engine_info = None
        for code_info in CODE_MAP_INFO:
            if code_info['SOURCE_TABLE'] in self.code_map_dict.keys():
                logging.error(
                    f"???????????????{code_info['SOURCE_TABLE']}??? ???????????????. ?????? ??? SOURCE_TABLE ??? ????????? ?????????.")
                sys.exit()
            sql = None
            if prev_engine_info != ACCESS_INFO[code_info["SOURCE_DB_ACCESS_INFO"]]:
                engine_info = ACCESS_INFO[code_info["SOURCE_DB_ACCESS_INFO"]]
                engine = self.set_engine(engine_info)
                prev_engine_info = engine_info
            if engine:
                sql = f"SELECT {','.join(code_info['SOURCE_COLS'])} FROM {code_info['SOURCE_TABLE']}"
                df = self.sql_excute(sql, engine)
                self.code_map_dict[code_info['SOURCE_TABLE']] = df
        if engine:
            engine.dispose()
        if validation:
            self.validation_migration_info(database_list, selected_validation)

    def migration(self):
        try:
            for merge_process in self.migration_info_list:
                val_dic = {}
                data = MIGRATION_INFO[merge_process]

                for index, merge_info in enumerate(data["MERGE_PROCESS"]):
                    self.step = {
                        merge_process: "MERGE_PROCESS " + str(index+1) + "?????? ??????"}
                    SOURCE_DB_ACCESS_INFO, source_engine, SOURCE_TABLE, SELECT_CONDITION, SOURCE_COLS, PREPROCESS, POSTPROCESS, FILTER_BY_COL_VALS, JOIN_KEY, TARGET_DB_ACCESS_INFO, target_engine, TARGET_TABLE = self.set_val(
                        merge_info)

                    # Key ?????? ???????????? ????????? ??????
                    df = pd.DataFrame()
                    sql = None

                    # ????????? ?????? ?????? ?????????
                    if SOURCE_DB_ACCESS_INFO in ["in_memory", "parquet"]:
                        sql = f"SELECT {','.join(SOURCE_COLS)} FROM df"
                    else:
                        sql = f"SELECT {','.join(SOURCE_COLS)} FROM {SOURCE_TABLE}"
                    where_list = []
                    if SELECT_CONDITION or FILTER_BY_COL_VALS:
                        sql += " WHERE "
                    if SELECT_CONDITION:
                        where_list.append(SELECT_CONDITION)
                    if FILTER_BY_COL_VALS:
                        for col in FILTER_BY_COL_VALS:
                            where_list.append(
                                f"('0',{col}) in {tuple(self.make_filter_by_col_vals(col))}")
                    if where_list and len(where_list) > 0:
                        sql += ' AND '.join(where_list)

                    if SOURCE_DB_ACCESS_INFO == "in_memory":
                        df = val_dic[SOURCE_TABLE]
                        if sql:
                            df = sqldf(sql, locals())
                    elif SOURCE_DB_ACCESS_INFO == "parquet":
                        df = pd.read_parquet(
                            f"{SOURCE_TABLE}.parquet")
                        if sql:
                            df = sqldf(sql, locals())
                    else:
                        df = self.sql_excute(sql, source_engine)

                    if source_engine:
                        source_engine.dispose()
                    # JOIN ??? ?????????
                    if PREPROCESS:
                        df = self.process(df, PREPROCESS, JOIN_KEY)

                    # JOIN
                    if JOIN_KEY:
                        cols_to_use = list(df.columns.difference(
                            self.processing_df.columns))
                        for _JOIN_KEY in JOIN_KEY:
                            if not _JOIN_KEY in cols_to_use:
                                cols_to_use.append(_JOIN_KEY)
                        df = pd.merge(self.processing_df, df[cols_to_use],
                                      how="left", on=JOIN_KEY)
                    # JOIN ??? ?????????
                    if POSTPROCESS:
                        df = self.process(df, POSTPROCESS, JOIN_KEY)

                    # ????????? ??????
                    if TARGET_DB_ACCESS_INFO:
                        # dict ?????? ????????? ?????? ?????? ??????
                        if TARGET_DB_ACCESS_INFO.lower() == "in_memory":
                            val_dic[TARGET_TABLE] = df
                        # parquet ????????? ??????
                        elif TARGET_DB_ACCESS_INFO.lower() == "parquet":
                            parquet_file_path = TARGET_TABLE[0:TARGET_TABLE.rfind(
                                "/")]
                            Path(parquet_file_path).mkdir(
                                parents=True, exist_ok=True)
                            df.to_parquet(f"{TARGET_TABLE}.parquet")
                        # DB ??????
                        else:
                            df.to_sql(name=TARGET_TABLE, con=target_engine,
                                      if_exists='append', chunksize=1000, index=False)

                        if target_engine:
                            target_engine.dispose()

                    self.processing_df = df.copy()

                # ?????? ????????? ?????? ?????????????????? ?????????
                self.processing_df = pd.DataFrame()
                # memory ????????? prefix ???????????? ??????
                # val_dic = {
                #     f"{merge_process}_"+k: v for k, v in val_dic.items()}
                # self.val_dic.update(val_dic)
        except:
            if not self.temp_save:
                logging.error(traceback.format_exc())
            else:
                Path(f"{base_path}/temp/").mkdir(parents=True, exist_ok=True)
                if not self.processing_df.empty:
                    self.processing_df.to_parquet(
                        f"{base_path}/temp/processing_df({datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}).parquet")
                    logging.error(
                        f"{self.step}\n??????????????? ???????????? {base_path}/temp/processing_df({datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}).parquet??? ???????????? ?????????.\n{traceback.format_exc()}")
                else:
                    logging.error(
                        f"{self.step}\n{traceback.format_exc()}")
            sys.exit()
        finally:
            if source_engine:
                source_engine.dispose()
            if target_engine:
                target_engine.dispose()

    # db_engine ??????

    def set_engine(self, info):
        engine = create_engine(
            f'{info["ENGINE"]}://{info["USER"]}:{quote(info["PASSWORD"])}@{info["HOST"]}:{info["PORT"]}/{info["NAME"]}', pool_size=5, pool_timeout=30, max_identifier_length=128)
        return engine

    # ?????? ????????????
    def set_val(self, merge_info):
        # ????????? ?????????????????? ???????????? ??????
        SOURCE_DB_ACCESS_INFO = None
        source_engine = None
        # ????????? ????????????
        SOURCE_TABLE = None
        # ?????? ?????????
        SELECT_CONDITION = None
        # ????????? ?????????
        SOURCE_COLS = None
        # ????????? ????????? ????????? ????????????
        PREPROCESS = None
        # JOIN ??? ????????? ????????? ????????????
        POSTPROCESS = None
        # PK ?????? ?????? ?????? ??? ?????????
        FILTER_BY_COL_VALS = None

        # ?????? ??????????????? ????????? ????????? ?????????
        JOIN_KEY = None

        # ????????? ?????????????????? ???????????? ??????
        TARGET_DB_ACCESS_INFO = None
        target_engine = None
        # ????????? ????????????
        TARGET_TABLE = None

        # ????????? ?????????????????? ????????????
        if "SOURCE_DB_ACCESS_INFO" in merge_info.keys() and merge_info["SOURCE_DB_ACCESS_INFO"]:
            if merge_info["SOURCE_DB_ACCESS_INFO"].lower() in ["in_memory", "parquet"]:
                SOURCE_DB_ACCESS_INFO = merge_info["SOURCE_DB_ACCESS_INFO"].lower(
                )
            else:
                SOURCE_DB_ACCESS_INFO = ACCESS_INFO[merge_info["SOURCE_DB_ACCESS_INFO"]]
                source_engine = self.set_engine(
                    SOURCE_DB_ACCESS_INFO)

        # ????????? ????????????
        if "SOURCE_TABLE" in merge_info.keys() and merge_info["SOURCE_TABLE"]:
            SOURCE_TABLE = merge_info["SOURCE_TABLE"]

        # ?????? ?????????
        if "SELECT_CONDITION" in merge_info.keys() and merge_info["SELECT_CONDITION"]:
            SELECT_CONDITION = merge_info["SELECT_CONDITION"]

        # ????????? ?????????
        if "SOURCE_COLS" in merge_info.keys() and merge_info["SOURCE_COLS"]:
            SOURCE_COLS = merge_info["SOURCE_COLS"]

        # PK ?????? ?????? ??????
        if "FILTER_BY_COL_VALS" in merge_info.keys() and merge_info["FILTER_BY_COL_VALS"]:
            FILTER_BY_COL_VALS = merge_info["FILTER_BY_COL_VALS"]

        # ????????? ????????? ????????? ????????????
        if "PREPROCESS" in merge_info.keys() and merge_info["PREPROCESS"]:
            PREPROCESS = merge_info["PREPROCESS"]

        # JOIN ??? ????????? ????????? ????????????
        if "POSTPROCESS" in merge_info.keys() and merge_info["POSTPROCESS"]:
            POSTPROCESS = merge_info["POSTPROCESS"]

    # ============================================================================================================================================

        # ?????? ??????????????? ????????? ????????? ?????????
        if "JOIN_KEY" in merge_info.keys() and merge_info["JOIN_KEY"]:
            JOIN_KEY = merge_info["JOIN_KEY"]

    # ============================================================================================================================================

        # ????????? ?????????????????? ????????????
        if "TARGET_DB_ACCESS_INFO" in merge_info.keys() and merge_info["TARGET_DB_ACCESS_INFO"]:
            TARGET_DB_ACCESS_INFO = merge_info["TARGET_DB_ACCESS_INFO"]
            if not TARGET_DB_ACCESS_INFO.lower() in ["in_memory", "parquet"]:
                target_db_access_info = ACCESS_INFO[merge_info["TARGET_DB_ACCESS_INFO"]]
                target_engine = self.set_engine(
                    target_db_access_info)

        # ????????? ????????????
        if "TARGET_TABLE" in merge_info.keys() and merge_info["TARGET_TABLE"]:
            TARGET_TABLE = merge_info["TARGET_TABLE"]
        return SOURCE_DB_ACCESS_INFO, source_engine, SOURCE_TABLE, SELECT_CONDITION, SOURCE_COLS, PREPROCESS, POSTPROCESS, FILTER_BY_COL_VALS, JOIN_KEY, TARGET_DB_ACCESS_INFO, target_engine, TARGET_TABLE

    # sql ?????? + DB ????????? ???????????? ??????
    def sql_excute(self, sql, engine):
        df = pd.read_sql(sql, engine)
        real_cols = self.receive_db_columns(engine, sql)
        df_cols = sorted(df.columns)
        chan_col_dict = {}
        for r_col in real_cols:
            for d_col in df_cols:
                if r_col.lower() == d_col.lower():
                    chan_col_dict[d_col] = r_col
        if len(chan_col_dict) > 0:
            df = df.rename(columns=chan_col_dict)
        return df

    # DB ?????? ??????(???????????? ??????)?????? ????????????
    def receive_db_columns(self, engine, sql):
        result = engine.execute(sql).cursor.description
        real_cols = list(pd.DataFrame(result)[0])
        real_cols.sort()
        return real_cols

    # ?????? ??????
    def process(self, df, process, join_key):
        for fun_dict in process:
            fun = list(fun_dict.keys())[0]
            target_cols = None
            params = None

            if "params" in fun_dict[fun].keys():
                params = fun_dict[fun]["params"]
            if not params and join_key:
                params = {"on": join_key}
            elif params and not "on" in params.keys() and join_key:
                params["on"] = join_key

            if "target_cols" in fun_dict[fun].keys():
                target_cols = fun_dict[fun]["target_cols"]
                if "all" in target_cols or "ALL" in target_cols:
                    target_cols = list(df.columns)

            if fun == "comm_cd_join":
                # ????????????================================================================
                if "right_on" in params.keys():
                    if "code_map_col" in params.keys() and params["code_map_col"]:
                        params["code_map_table"] = self.code_map_dict[params["code_map_table"]
                                                                      ][[params["code_map_col"], params["right_on"]]]
                    else:
                        params["code_map_table"] = self.code_map_dict[params["code_map_table"]]
                else:
                    params["code_map_table"] = self.code_map_dict[params["code_map_table"]
                                                                  ][[params["code_map_col"], params["on"]]]

            if not params:
                df = getattr(self.tracer, fun)(
                    df, target_cols=target_cols)
            else:
                df = getattr(self.tracer, fun)(
                    df, target_cols=target_cols, params=params)
        return df

    def make_filter_by_col_vals(self, col):
        result = []
        for item in self.processing_df[col].values.tolist():
            result.append(('0', item))
        return result

    # ?????? ??????
    def validation_migration_info(self, database_list, seleed_validation):
        try:
            # ACCESS_INFO ??????
            if ACCESS_INFO and not isinstance(ACCESS_INFO, dict):
                raise ValueError(
                    f"ACCESS_INFO ?????? {dict} ????????? ?????????.")
            else:
                for access in ACCESS_INFO.keys():
                    if not isinstance(ACCESS_INFO[access], dict):
                        raise ValueError(
                            f"ACCESS_INFO??? {access}?????? {dict} ????????? ?????????.")

            # CODE_MAP_INFO ??????
            if CODE_MAP_INFO and not isinstance(CODE_MAP_INFO, list):
                raise ValueError(
                    f"CODE_MAP_INFO ?????? {list} ????????? ?????????.")
            elif len(CODE_MAP_INFO) > 0 and not isinstance(CODE_MAP_INFO[0], dict):
                raise ValueError(
                    f"CODE_MAP_INFO ??? ?????? ?????? {dict} ????????? ?????????.")

            # MIGRATION_INFO ??????
            if not isinstance(MIGRATION_INFO, dict):
                raise ValueError(
                    f"MIGRATION_INFO ?????? {dict} ????????? ?????????.")

            # MIGRATION_INFO ?????? ??????
            if not seleed_validation:
                result, diff_list = self.find_different_list(
                    list(MIGRATION_INFO.keys()), database_list)
                if result:
                    raise ValueError(
                        f"???????????? {diff_list}???/???  MIGRATION_INFO ??? ???????????? ????????????.")

            for merge_info_key in self.migration_info_list:
                merge_process = MIGRATION_INFO[merge_info_key]["MERGE_PROCESS"]
                db_access_info = None
                engine = None
                for sub_index, merge_info in enumerate(merge_process):
                    # ?????? ??????/?????? ??????
                    for info_key in merge_info.keys():
                        if not info_key in validation_migration_info_type.keys():
                            raise ValueError(
                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? key?????? ??????/????????? ????????????.({info_key}).")

                    for info_key in merge_info.keys():
                        # MIGRATION_INFO ?????? ?????? ??????
                        if not isinstance(merge_info[info_key], validation_migration_info_type[info_key]):
                            raise ValueError(
                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}?????? {validation_migration_info_type[info_key]} ????????? ?????????.")

                        # PREPROCESS, POSTPROCESS ??? ?????? ?????? ??????
                        if info_key in ["PREPROCESS", "POSTPROCESS"] and len(merge_info[info_key]) > 0:
                            for index, item in enumerate(merge_info[info_key]):
                                if not item or not isinstance(item, dict):
                                    raise ValueError(
                                        f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? ?????? ?????????????????????. {dict}??? ???????????????.")
                                # ?????? ?????? ???????????? ??????====================================================
                                if list(item.keys())[0] in tracer_params_validation.keys():
                                    job_key = list(item.keys())[0]
                                    if "target_cols" in tracer_params_validation[job_key].keys():
                                        if not "target_cols" in item[job_key].keys():
                                            raise ValueError(
                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}??? target_cols??? ?????? ??? ?????????.")
                                        elif len(item[job_key]["target_cols"]) == 0:
                                            raise ValueError(
                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}??? target_cols ??? ????????? ????????????. (length==0)")

                                    if "params" in tracer_params_validation[job_key].keys():
                                        if not "params" in item[job_key].keys():
                                            raise ValueError(
                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}??? params??? ?????? ??? ?????????.")
                                        elif "required" in tracer_params_validation[job_key]["params"].keys():
                                            for required_key in tracer_params_validation[job_key]["params"]["required"].keys():
                                                if not required_key in item[job_key]["params"].keys():
                                                    raise ValueError(
                                                        f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? {required_key}??? ?????? ??? ?????????.")
                                                elif not isinstance(item[job_key]["params"][required_key], tracer_params_validation[job_key]["params"]["required"][required_key]):
                                                    param_type = tracer_params_validation[
                                                        job_key]["params"]["required"][required_key]
                                                    raise ValueError(
                                                        f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? {required_key}??? {param_type}????????? ?????????.")
                                                elif list == tracer_params_validation[job_key]["params"]["required"][required_key] and len(item[job_key]["params"][required_key]) == 0:
                                                    raise ValueError(
                                                        f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? {required_key}??? list ??? ????????? ?????? ??? ?????????.")

                                        else:
                                            for param_key in item[job_key]["params"].keys():
                                                if param_key in tracer_params_validation[job_key]["params"].keys():
                                                    if not isinstance(item[job_key]["params"][param_key], tracer_params_validation[job_key]["params"][param_key]):
                                                        param_type = tracer_params_validation[
                                                            job_key]["params"][param_key]
                                                        raise ValueError(
                                                            f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? {param_key}??? {param_type}????????? ?????????.")
                                                    elif job_key == "custom_groupby" and param_key == "agg_type":
                                                        if not item[job_key]["params"]["agg_type"] in ["min", "max", None]:
                                                            raise ValueError(
                                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? agg_type??? 'min'?????? 'max', ?????? None ????????? ?????????.")
                                                    elif job_key == "drop_na" and param_key == "axis":
                                                        if not item[job_key]["params"]["axis"] in [0, 1, None]:
                                                            raise ValueError(
                                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? axis??? 0 ?????? 1, ?????? None ????????? ?????????.")
                                                    elif job_key == "drop_duplicates" and param_key == "keep":
                                                        if not item[job_key]["params"]["keep"] in ['first', 'last', None]:
                                                            raise ValueError(
                                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? keep??? 'first'?????? 'last', ?????? None ????????? ?????????.")
                                                    elif job_key == "sort" and param_key == "order_by":
                                                        if not item[job_key]["params"]["order_by"] in ['asc', 'desc', None]:
                                                            raise ValueError(
                                                                f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? {job_key}, params??? keep??? 'asc'?????? 'desc', ?????? None ????????? ?????????.")
                                # ?????? ?????? ???????????? ?????? ??????====================================================
                                item_key = list(item.keys())[0]
                                if not item_key in tracer_params_validation.keys():
                                    raise ValueError(
                                        f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}, {index+1}?????? ?????????({item_key})??? ???????????? ????????????.")

                        # SOURCE_DB_ACCESS_INFO ??? ?????? ?????? ??????
                        if info_key in ["SOURCE_DB_ACCESS_INFO", "TARGET_DB_ACCESS_INFO"]:
                            info_sub_key = "SOURCE_TABLE"
                            if info_key == "TARGET_DB_ACCESS_INFO":
                                info_sub_key = "TARGET_TABLE"
                            # else:
                            #     # DB ?????? ?????? ?????? ??????
                            #     if merge_info[info_key] in ACCESS_INFO.keys() and not merge_info[info_key].lower() in ["in_memory", "parquet"] and (merge_info["SOURCE_COLS"] and not "*" in merge_info["SOURCE_COLS"]):
                            #         if db_access_info != ACCESS_INFO[merge_info[info_key]]:
                            #             db_access_info = ACCESS_INFO[merge_info[info_key]]
                            #             engine = self.set_engine(
                            #                 db_access_info)
                            #         sql = f"SELECT * FROM {merge_info[info_sub_key]}"
                            #         result, diff_list = self.find_different_list(self.receive_db_columns(
                            #             engine, sql), merge_info["SOURCE_COLS"])
                            #         if result:
                            #             raise ValueError(
                            #                 f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? SOURCE_COLS??? DB??? ???????????? ?????? ????????? ????????????.{diff_list}")
                            if not merge_info[info_key] in ACCESS_INFO.keys() and not merge_info[info_key].lower() in ["in_memory", "parquet"]:
                                raise ValueError(
                                    f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}???/??? 'ACCESS_INFO' ??? ???????????? ?????? ??? ?????????.")
                            if not info_sub_key in merge_info.keys() or not merge_info[info_sub_key]:
                                raise ValueError(
                                    f"???????????? migration_info?????? {merge_info_key}??? {sub_index+1}?????? {info_key}??? ??????????????? {info_sub_key}???/??? ?????? ?????? ??????????????? ?????????.")
        except:
            logging.error(traceback.format_exc())
            sys.exit()

    def find_different_list(self, master_list, sub_list):
        different_list = []
        result = False
        different_list = list(set(sub_list).difference(set(master_list)))
        if len(different_list) > 0:
            result = True
        return result, different_list


if __name__ == "__main__":
    input_tables = input("????????? table?????? ','??? ???????????? ??????????????????.")
    database_list = []
    if input_tables:
        database_list = list(set(input_tables.replace(" ", "").split(",")))

    migration_tracer = Migration_Tracer(database_list=[], validation=True,
                                        selected_validation=False, temp_save=True)
    migration_tracer.migration()
