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
        # 오류 발생시 진행 중이던 데이터 임시저장 여부
        self.temp_save = temp_save
        print(f"오류 발생시 임시저장 : {self.temp_save}\n자료 검증 여부 : {validation}")
        self.migration_info_list = list(MIGRATION_INFO.keys())
        if database_list and len(database_list) > 0:
            self.migration_info_list = database_list

        # self.val_dic = {}
        self.tracer = Tracer()
        self.processing_df = pd.DataFrame()
        self.step = None

        # 공통코드 자료집 구성
        self.code_map_dict = {}
        prev_engine_info = None
        engine = None
        engine_info = None
        for code_info in CODE_MAP_INFO:
            if code_info['SOURCE_TABLE'] in self.code_map_dict.keys():
                logging.error(
                    f"공통코드명{code_info['SOURCE_TABLE']}이 중복됩니다. 확인 후 SOURCE_TABLE 을 수정해 주세요.")
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
                        merge_process: "MERGE_PROCESS " + str(index+1) + "번째 요소"}
                    SOURCE_DB_ACCESS_INFO, source_engine, SOURCE_TABLE, SELECT_CONDITION, SOURCE_COLS, PREPROCESS, POSTPROCESS, FILTER_BY_COL_VALS, JOIN_KEY, TARGET_DB_ACCESS_INFO, target_engine, TARGET_TABLE = self.set_val(
                        merge_info)

                    # Key 필터 적용하여 데이터 조회
                    df = pd.DataFrame()
                    sql = None

                    # 데이터 조회 쿼리 만들기
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
                    # JOIN 전 전처리
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
                    # JOIN 후 전처리
                    if POSTPROCESS:
                        df = self.process(df, POSTPROCESS, JOIN_KEY)

                    # 데이터 저장
                    if TARGET_DB_ACCESS_INFO:
                        # dict 타입 형태로 객체 안에 저장
                        if TARGET_DB_ACCESS_INFO.lower() == "in_memory":
                            val_dic[TARGET_TABLE] = df
                        # parquet 파일로 저장
                        elif TARGET_DB_ACCESS_INFO.lower() == "parquet":
                            parquet_file_path = TARGET_TABLE[0:TARGET_TABLE.rfind(
                                "/")]
                            Path(parquet_file_path).mkdir(
                                parents=True, exist_ok=True)
                            df.to_parquet(f"{TARGET_TABLE}.parquet")
                        # DB 저장
                        else:
                            df.to_sql(name=TARGET_TABLE, con=target_engine,
                                      if_exists='append', chunksize=1000, index=False)

                        if target_engine:
                            target_engine.dispose()

                    self.processing_df = df.copy()

                # 진행 중이건 기준 데이터프레임 초기화
                self.processing_df = pd.DataFrame()
                # memory 데이터 prefix 추가하여 관리
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
                        f"{self.step}\n진행중이던 데이터를 {base_path}/temp/processing_df({datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}).parquet로 임지저장 합니다.\n{traceback.format_exc()}")
                else:
                    logging.error(
                        f"{self.step}\n{traceback.format_exc()}")
            sys.exit()
        finally:
            if source_engine:
                source_engine.dispose()
            if target_engine:
                target_engine.dispose()

    # db_engine 생성

    def set_engine(self, info):
        engine = create_engine(
            f'{info["ENGINE"]}://{info["USER"]}:{quote(info["PASSWORD"])}@{info["HOST"]}:{info["PORT"]}/{info["NAME"]}', pool_size=5, pool_timeout=30, max_identifier_length=128)
        return engine

    # 변수 세팅함수
    def set_val(self, merge_info):
        # 조회할 데이터베이스 엔진생성 정보
        SOURCE_DB_ACCESS_INFO = None
        source_engine = None
        # 조회할 테이블명
        SOURCE_TABLE = None
        # 조회 조건절
        SELECT_CONDITION = None
        # 조회할 컬럼명
        SOURCE_COLS = None
        # 조회된 데이터 전처리 프로세스
        PREPROCESS = None
        # JOIN 후 데이터 전처리 프로세스
        POSTPROCESS = None
        # PK 필터 적용 여부 및 컬럼명
        FILTER_BY_COL_VALS = None

        # 앞전 데이터셋과 조인할 컬럼명 리스트
        JOIN_KEY = None

        # 저장할 데이터베이스 엔진생성 정보
        TARGET_DB_ACCESS_INFO = None
        target_engine = None
        # 저장할 테이블명
        TARGET_TABLE = None

        # 조회할 데이터베이스 엔진생성
        if "SOURCE_DB_ACCESS_INFO" in merge_info.keys() and merge_info["SOURCE_DB_ACCESS_INFO"]:
            if merge_info["SOURCE_DB_ACCESS_INFO"].lower() in ["in_memory", "parquet"]:
                SOURCE_DB_ACCESS_INFO = merge_info["SOURCE_DB_ACCESS_INFO"].lower(
                )
            else:
                SOURCE_DB_ACCESS_INFO = ACCESS_INFO[merge_info["SOURCE_DB_ACCESS_INFO"]]
                source_engine = self.set_engine(
                    SOURCE_DB_ACCESS_INFO)

        # 조회할 테이블명
        if "SOURCE_TABLE" in merge_info.keys() and merge_info["SOURCE_TABLE"]:
            SOURCE_TABLE = merge_info["SOURCE_TABLE"]

        # 조회 조건절
        if "SELECT_CONDITION" in merge_info.keys() and merge_info["SELECT_CONDITION"]:
            SELECT_CONDITION = merge_info["SELECT_CONDITION"]

        # 조회할 컬럼명
        if "SOURCE_COLS" in merge_info.keys() and merge_info["SOURCE_COLS"]:
            SOURCE_COLS = merge_info["SOURCE_COLS"]

        # PK 필터 사용 여부
        if "FILTER_BY_COL_VALS" in merge_info.keys() and merge_info["FILTER_BY_COL_VALS"]:
            FILTER_BY_COL_VALS = merge_info["FILTER_BY_COL_VALS"]

        # 조회된 데이터 전처리 프로세스
        if "PREPROCESS" in merge_info.keys() and merge_info["PREPROCESS"]:
            PREPROCESS = merge_info["PREPROCESS"]

        # JOIN 후 데이터 전처리 프로세스
        if "POSTPROCESS" in merge_info.keys() and merge_info["POSTPROCESS"]:
            POSTPROCESS = merge_info["POSTPROCESS"]

    # ============================================================================================================================================

        # 앞전 데이터셋과 조인할 컬럼명 리스트
        if "JOIN_KEY" in merge_info.keys() and merge_info["JOIN_KEY"]:
            JOIN_KEY = merge_info["JOIN_KEY"]

    # ============================================================================================================================================

        # 저장할 데이터베이스 엔진생성
        if "TARGET_DB_ACCESS_INFO" in merge_info.keys() and merge_info["TARGET_DB_ACCESS_INFO"]:
            TARGET_DB_ACCESS_INFO = merge_info["TARGET_DB_ACCESS_INFO"]
            if not TARGET_DB_ACCESS_INFO.lower() in ["in_memory", "parquet"]:
                target_db_access_info = ACCESS_INFO[merge_info["TARGET_DB_ACCESS_INFO"]]
                target_engine = self.set_engine(
                    target_db_access_info)

        # 저장할 테이블명
        if "TARGET_TABLE" in merge_info.keys() and merge_info["TARGET_TABLE"]:
            TARGET_TABLE = merge_info["TARGET_TABLE"]
        return SOURCE_DB_ACCESS_INFO, source_engine, SOURCE_TABLE, SELECT_CONDITION, SOURCE_COLS, PREPROCESS, POSTPROCESS, FILTER_BY_COL_VALS, JOIN_KEY, TARGET_DB_ACCESS_INFO, target_engine, TARGET_TABLE

    # sql 실행 + DB 컬럼명 대소문자 유지
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

    # DB 실제 컬럼(대소문자 구분)하여 가져오기
    def receive_db_columns(self, engine, sql):
        result = engine.execute(sql).cursor.description
        real_cols = list(pd.DataFrame(result)[0])
        real_cols.sort()
        return real_cols

    # 함수 처리
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
                # 검증추가================================================================
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

    # 자료 검증
    def validation_migration_info(self, database_list, seleed_validation):
        try:
            # ACCESS_INFO 검증
            if ACCESS_INFO and not isinstance(ACCESS_INFO, dict):
                raise ValueError(
                    f"ACCESS_INFO 값은 {dict} 이어야 합니다.")
            else:
                for access in ACCESS_INFO.keys():
                    if not isinstance(ACCESS_INFO[access], dict):
                        raise ValueError(
                            f"ACCESS_INFO의 {access}값은 {dict} 이어야 합니다.")

            # CODE_MAP_INFO 검증
            if CODE_MAP_INFO and not isinstance(CODE_MAP_INFO, list):
                raise ValueError(
                    f"CODE_MAP_INFO 값은 {list} 이어야 합니다.")
            elif len(CODE_MAP_INFO) > 0 and not isinstance(CODE_MAP_INFO[0], dict):
                raise ValueError(
                    f"CODE_MAP_INFO 내 속성 값은 {dict} 이어야 합니다.")

            # MIGRATION_INFO 검증
            if not isinstance(MIGRATION_INFO, dict):
                raise ValueError(
                    f"MIGRATION_INFO 값은 {dict} 이어야 합니다.")

            # MIGRATION_INFO 내부 검증
            if not seleed_validation:
                result, diff_list = self.find_different_list(
                    list(MIGRATION_INFO.keys()), database_list)
                if result:
                    raise ValueError(
                        f"입력하신 {diff_list}는/은  MIGRATION_INFO 에 존재하지 않습니다.")

            for merge_info_key in self.migration_info_list:
                merge_process = MIGRATION_INFO[merge_info_key]["MERGE_PROCESS"]
                db_access_info = None
                engine = None
                for sub_index, merge_info in enumerate(merge_process):
                    # 키값 오류/오타 검증
                    for info_key in merge_info.keys():
                        if not info_key in validation_migration_info_type.keys():
                            raise ValueError(
                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 key값에 오류/오타가 있습니다.({info_key}).")

                    for info_key in merge_info.keys():
                        # MIGRATION_INFO 내부 기본 검증
                        if not isinstance(merge_info[info_key], validation_migration_info_type[info_key]):
                            raise ValueError(
                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}값은 {validation_migration_info_type[info_key]} 이어야 합니다.")

                        # PREPROCESS, POSTPROCESS 및 내부 상세 검증
                        if info_key in ["PREPROCESS", "POSTPROCESS"] and len(merge_info[info_key]) > 0:
                            for index, item in enumerate(merge_info[info_key]):
                                if not item or not isinstance(item, dict):
                                    raise ValueError(
                                        f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 값이 잘못되었습니다. {dict}로 변경하세요.")
                                # 함수 검증 파라미터 검증====================================================
                                if list(item.keys())[0] in tracer_params_validation.keys():
                                    job_key = list(item.keys())[0]
                                    if "target_cols" in tracer_params_validation[job_key].keys():
                                        if not "target_cols" in item[job_key].keys():
                                            raise ValueError(
                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}의 target_cols은 필수 값 입니다.")
                                        elif len(item[job_key]["target_cols"]) == 0:
                                            raise ValueError(
                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}의 target_cols 내 요소가 없습니다. (length==0)")

                                    if "params" in tracer_params_validation[job_key].keys():
                                        if not "params" in item[job_key].keys():
                                            raise ValueError(
                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}의 params은 필수 값 입니다.")
                                        elif "required" in tracer_params_validation[job_key]["params"].keys():
                                            for required_key in tracer_params_validation[job_key]["params"]["required"].keys():
                                                if not required_key in item[job_key]["params"].keys():
                                                    raise ValueError(
                                                        f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 {required_key}은 필수 값 입니다.")
                                                elif not isinstance(item[job_key]["params"][required_key], tracer_params_validation[job_key]["params"]["required"][required_key]):
                                                    param_type = tracer_params_validation[
                                                        job_key]["params"]["required"][required_key]
                                                    raise ValueError(
                                                        f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 {required_key}은 {param_type}이어야 합니다.")
                                                elif list == tracer_params_validation[job_key]["params"]["required"][required_key] and len(item[job_key]["params"][required_key]) == 0:
                                                    raise ValueError(
                                                        f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 {required_key}은 list 내 요소는 필수 값 입니다.")

                                        else:
                                            for param_key in item[job_key]["params"].keys():
                                                if param_key in tracer_params_validation[job_key]["params"].keys():
                                                    if not isinstance(item[job_key]["params"][param_key], tracer_params_validation[job_key]["params"][param_key]):
                                                        param_type = tracer_params_validation[
                                                            job_key]["params"][param_key]
                                                        raise ValueError(
                                                            f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 {param_key}은 {param_type}이어야 합니다.")
                                                    elif job_key == "custom_groupby" and param_key == "agg_type":
                                                        if not item[job_key]["params"]["agg_type"] in ["min", "max", None]:
                                                            raise ValueError(
                                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 agg_type은 'min'이나 'max', 혹은 None 이어야 합니다.")
                                                    elif job_key == "drop_na" and param_key == "axis":
                                                        if not item[job_key]["params"]["axis"] in [0, 1, None]:
                                                            raise ValueError(
                                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 axis은 0 이나 1, 혹은 None 이어야 합니다.")
                                                    elif job_key == "drop_duplicates" and param_key == "keep":
                                                        if not item[job_key]["params"]["keep"] in ['first', 'last', None]:
                                                            raise ValueError(
                                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 keep은 'first'이나 'last', 혹은 None 이어야 합니다.")
                                                    elif job_key == "sort" and param_key == "order_by":
                                                        if not item[job_key]["params"]["order_by"] in ['asc', 'desc', None]:
                                                            raise ValueError(
                                                                f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 {job_key}, params의 keep은 'asc'이나 'desc', 혹은 None 이어야 합니다.")
                                # 함수 검증 파라미터 검증 종료====================================================
                                item_key = list(item.keys())[0]
                                if not item_key in tracer_params_validation.keys():
                                    raise ValueError(
                                        f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}, {index+1}번째 함수명({item_key})은 존재하지 않습니다.")

                        # SOURCE_DB_ACCESS_INFO 및 내부 상세 검증
                        if info_key in ["SOURCE_DB_ACCESS_INFO", "TARGET_DB_ACCESS_INFO"]:
                            info_sub_key = "SOURCE_TABLE"
                            if info_key == "TARGET_DB_ACCESS_INFO":
                                info_sub_key = "TARGET_TABLE"
                            # else:
                            #     # DB 컬럼 존재 여부 검증
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
                            #                 f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 SOURCE_COLS에 DB내 존재하지 않는 컬럼이 있습니다.{diff_list}")
                            if not merge_info[info_key] in ACCESS_INFO.keys() and not merge_info[info_key].lower() in ["in_memory", "parquet"]:
                                raise ValueError(
                                    f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}는/은 'ACCESS_INFO' 내 존재하지 않는 값 입니다.")
                            if not info_sub_key in merge_info.keys() or not merge_info[info_sub_key]:
                                raise ValueError(
                                    f"작성하신 migration_info에서 {merge_info_key}의 {sub_index+1}번째 {info_key}가 존재하므로 {info_sub_key}는/은 필수 값로 입력되어야 합니다.")
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
    input_tables = input("처리할 table명을 ','로 구분하여 입력해주세요.")
    database_list = []
    if input_tables:
        database_list = list(set(input_tables.replace(" ", "").split(",")))

    migration_tracer = Migration_Tracer(database_list=[], validation=True,
                                        selected_validation=False, temp_save=True)
    migration_tracer.migration()
