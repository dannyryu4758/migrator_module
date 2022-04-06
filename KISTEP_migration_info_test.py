MIGRATION_INFO_SAMPLE_FORMAT = {
    "SAMPLE": {
        "MERGE_PROCESS": [
            {
                # 불러올 데이터베이스 접속 정보
                "SOURCE_DB_ACCESS_INFO": "SOURCE_ACCESS_INFO_KEY",
                # 소스 테이블 이름
                "SOURCE_TABLE": "SOURCE_TABLE_NAME",
                # WHERE 조건
                "SELECT_CONDITION": "WHERE COL != VAL1 AND COL2 = VAL2",
                # WHERE 조건에 특정 컬럼 LIST 에 해당하는 데이터만 불러오기 추가
                # PK 컬럼값이 존재하는 데이터만 불러오기에 해당 (필요 데이터만 로드)
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                # 필요한 컬럼명
                "SOURCE_COLS": [
                    "*"
                ],
                # 전처리 작업 나열
                "PREPROCESS": [
                    # API 명세서 확인하여 지원하는 데이터 처리 명령어 키워드 입력
                    # 추가적인 상세 설정이 필요한 경우 API 명세서 참고하여 params에 필요한 값 입력.
                    # params 미 입력 시 default 값 적용
                    # 모든 컬럼을 하나씩 순차적으로 동일 job 적용 시 target_cols = ["ALL"]
                    # 전체 DF 에 대해 작업을 진행 필요 시 target_cols = ["SELF"]
                    # remark 에 작업 내용에 대한 주석 정리 가능 (실제 작업에 영향 x)
                    {"job": "job_to_do", "target_cols": ["target_col1", "target_col2"], "params":{
                        "condition1": "val1"}, "remark": "comment"},
                ],
                # 후처리 작업 나열 (앞선 DF와 JOIN 이후 진행할 작업 나열)
                "POSTPROCESS": [
                    {"job": "job_to_do", "target_cols": [
                        "target_col1", "target_col2"], "params":{"condition1": "val1"}},
                ],
                # 앞에서 작업한 DF 와 JOIN 필요 시 JOIN 조건으로 사용할 키 컬럼
                "JOIN_KEY": ["SBJT_ID"],
                # TARGET_DB_ACCESS_INFO 입력 시 DF 를 테이블 OR PARQUET 파일로 저장
                # 해당 키값이 없거나 빈값 기입 시 따로 저장 작업 진행하지 않음
                # DB 저장 시 ACCESS_INFO 의 키값, parquet 저장 시 "parquet"으로 기입
                "TARGET_DB_ACCESS_INFO": "INSERT_ACCESS_INFO_KEY",
                # DB 저장 시 테이블명, parquet 저장 시 저장 경로 및 파일이름
                "TARGET_TABLE": "PS_SBJT",
                # 코멘트 정보가 있으면 코멘트 정보 저장
                "ADD_COMMENT": "Y",
                # 주석
                "REMARK":"입력값 설명 포맷"
            }
        ]
    }
}
ACCESS_INFO = {
    "sample": {
        "NAME": 'ORCLCDB',
        "ENGINE": 'oracle+cx_oracle',
        "USER": 'GRND_PS',
        "PASSWORD":  'dbzmfflem',
        "HOST": '192.168.1.56',
        "PORT": 1521
    },
    "collector": {
        "NAME": "collector",
        "ENGINE": "mysql+pymysql",
        "USER": "anal",
        "PASSWORD": "anal123",
        "HOST": "192.168.1.53",
        "PORT": 3306
    },
}

CODE_MAP_INFO = [
    {
        "SOURCE_DB_ACCESS_INFO": "sample",
        "SOURCE_TABLE": "PS_SORGN",
        "SOURCE_COLS": ['*'],
    },
]

MIGRATION_INFO = {
    "DESIGN": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": "collector",
                "SOURCE_TABLE": "NTIS_SBJT",
                "SELECT_CONDITION": "1=1 limit 10000",
                "SOURCE_COLS": [
                    "*"
                ],
                "POSTPROCESS": [
                    {"comm_cd_join": {"target_cols": [], "params":{
                        "code_map_table": "PS_SORGN", "on": "BSNSR_ORGN_NM", "right_on": "SORGN_NM"}}},
                    {"add_groupby_rank": {"target_cols": ["PRV_SBJT_NO", "SBJT_NO"], "params":{
                        "ranked_col": "SBJT_NO", "new_col": "PRG_SN", "group_col": "PRV_SBJT_NO"}}},

                    {"rename_cols": {"target_cols": [], "params":{
                        "SBJT_NM": "HAN_SBJT_NM", "SBMT_YEAR": "BSNS_YY", "PRV_SBJT_NO": "OVRL_SBJT_ID", "CNTN_SBJT_YN_CD": "SBJT_PROPL_STRC_SE", "CNTN_SBJT_YN": "SBJT_PROPL_STRC_SE_NM", "TOT_RSCH_FNDS_SUM": "SBJT_SPRT_BUD_AM", "TCH_6T_CD_L": "SBJT_TECL_CD", "TCH_6T_L": "SBJT_TECL_NM", "SMMR_RSCH_GOLE": "RSCH_GOLE_CN", "SMMR_EXPE_EFCT": "EXPE_EFCT_CN", "SMMR_HAN_KWD": "KWD_NM"}}},
                    {"add_cols": {"target_cols": ["BSNS_YY", "PRG_SBJT_EXE_ANNL", "PRG_BSNS_YY"], "params":{
                        "source_cols": ["SBMT_YEAR", "PRG_SN", "SBMT_YEAR"]}}},
                    {"remove_cols": {"target_cols": [
                        "", ""], "params":{}}},
                ],
            },
        ]
    }
}
