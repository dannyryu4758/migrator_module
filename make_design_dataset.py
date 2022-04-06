
from urllib.parse import quote
from sqlalchemy.engine import create_engine
import pandas as pd
from datetime import datetime


class Design():
    def __init__(self):
        sample_pw = 'dbzmfflem'
        self.sample_engine = create_engine(
            f'oracle+cx_oracle://GRND_PS:{quote(sample_pw)}@192.168.1.56:1521/ORCLCDB')
        collector_pw = 'anal123'
        self.collector_engine = create_engine(
            f'mysql+pymysql://anal:{quote(collector_pw)}@192.168.1.53:3306/collector')

    def make_design_dataset(self):
        sample_sub_df = pd.read_sql("""
                            SELECT * from PS_SORGN
                            """, con=self.sample_engine)
        sample_sub_df.columns = sample_sub_df.columns.str.lower()

        collector_main_df = pd.read_sql("""
                            SELECT * from NTIS_SBJT
                            """, con=self.collector_engine)
        collector_main_df.columns = collector_main_df.columns.str.lower()

        df = collector_main_df.copy().sort_values(
            ["prv_sbjt_no", "sbjt_no"]).reset_index(drop=True)
        df["prg_sn"] = 0
        # all_df = self.get_all_df().sort_values("sbjt_no").reset_index(drop=True)
        # all_df = all_df[all_df["sbjt_no"].isin(
        #     list(set((df["prv_sbjt_no"].to_list()))))].reset_index(drop=True)
        # all_df["sbjt_no"].apply(lambda x: self.set_prg_sn(df=df, id=x))
        df["ptc_prg_sn"] = 0
        df = pd.merge(collector_main_df, sample_sub_df,
                      left_on="rprsr_spins", right_on="sorgn_nm")
        df["invention_title_en"] = None
        df = df.rename(columns={"sbjt_nm": "han_sbjt_nm", "bsns_yy": "sbmt_year",
                                "prv_sbjt_no": "ovrl_sbjt_id", "sbjt_no": "sbjt_id"})

    def get_all_df(self):
        main_df = pd.read_sql("""
                            (SELECT PRV_SBJT_NO AS SBJT_NO FROM NTIS_SBJT WHERE TRIM(IFNULL(PRV_SBJT_NO,'')) != '')
                            UNION
                            (SELECT SBJT_NO AS SBJT_NO FROM NTIS_SBJT WHERE TRIM(IFNULL(SBJT_NO,'')) != '')
                            """, con=self.collector_engine)
        main_df.columns = main_df.columns.str.lower()
        return main_df
        # =========================================================================================================================
        # =========================================================================================================================
        # sql = "SELECT * from DIF_SBJT limit 1000"
        # collector_main_df = self.sql_excute(sql, self.collector_engine)
        # collector_main_df.columns = collector_main_df.columns.str.upper()
        # collector_main_df["PRG_SN"] = collector_main_df["SBJT_EXE_ANNL"]
        # collector_main_df["BSNS_YY"] = collector_main_df["DVLM_STR_DE"].apply(
        #     lambda x: x[:4])

        # collector_main_df = collector_main_df.rename(columns={""})

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

    def set_prg_sn(self, df, id):
        temp = df[df["prv_sbjt_no"] == id].copy().reset_index(drop=False)
        temp["prg_sn"] = temp.index
        temp = temp.set_index("index", drop=True)
        df[df["prv_sbjt_no"] == id] = temp
        return df

    # DB 실제 컬럼(대소문자 구분)하여 가져오기
    def receive_db_columns(self, engine, sql):
        result = engine.execute(sql).cursor.description
        real_cols = list(pd.DataFrame(result)[0])
        real_cols.sort()
        return real_cols


if "__main__" == __name__:
    design = Design()
    design.make_design_dataset()
