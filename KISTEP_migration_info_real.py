MIGRATION_INFO_SAMPLE_FORMAT = {
    "MIGRATION_INFO": {
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
                        {"job_to_do": {"target_cols": ["target_col1", "target_col2"], "params":{
                            "condition1": "val1"}, "remark": "comment"}},
                    ],
                    # 후처리 작업 나열 (앞선 DF와 JOIN 이후 진행할 작업 나열)
                    "POSTPROCESS": [
                        {"job_to_do": {"target_cols": [
                            "target_col1", "target_col2"], "params":{"condition1": "val1"}}},
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
}
ACCESS_INFO = {
    "ORIGINAL_SUBJECT": {
        "NAME": "GRND",
        "ENGINE": "oracle+cx_oracle",
        "USER": "UT_TEMP_UCLD",
        "PASSWORD": "@1#15l4tM!",
        "HOST": "192.168.101.88",
        "PORT": 1521
    },
    "COPY_SUBJECT": {
        "NAME": "GRND_PS",
        "ENGINE": "mysql+pymysql",
        "USER": "root",
        "PASSWORD": "mysql8password",
        "HOST": "127.0.0.1",
        "PORT": 3306
    },
    "ORIGINAL_STANDARD_MANAGEMENT": {
        "NAME": "ORCLCDB",
        "ENGINE": "oracle+cx_oracle",
        "USER": "C##TEST_USER3",
        "PASSWORD": "1234",
        "HOST": "192.168.1.53",
        "PORT": 1521
    },
    "COPY_STANDARD_MANAGEMENT": {
        "NAME": "docu_test",
        "ENGINE": "mysql+pymysql",
        "USER": "airflow_user",
        "PASSWORD": "airflow_pass",
        "HOST": "192.168.1.53",
        "PORT": 43306
    },
    "ANALYSIS_SUBJECT": {
        "NAME": "docu_test",
        "ENGINE": "mysql+pymysql",
        "USER": "airflow_user",
        "PASSWORD": "airflow_pass",
        "HOST": "192.168.1.53",
        "PORT": 43306
    },
    "TEST_DB1": {
        "NAME": "docu_test",
        "ENGINE": "mysql+pymysql",
        "USER": "airflow_user",
        "PASSWORD": "airflow_pass",
        "HOST": "192.168.1.53",
        "PORT": 43306
    },
    "TEST_DB2": {
        "NAME": "docu_test2",
        "ENGINE": "mysql+pymysql",
        "USER": "airflow_user",
        "PASSWORD": "airflow_pass",
        "HOST": "192.168.1.53",
        "PORT": 43306
    }
}
DEFAULT_SOURCE = "ORIGINAL_SUBJECT"
DEFAULT_TARGET = "COPY_SUBJECT"
COPY_SOURCE = "ORIGINAL_SUBJECT"

ORIGINAL_STANDARD_MANAGEMENT = "ORIGINAL_STANDARD_MANAGEMENT"
COPY_STANDARD_MANAGEMENT = "COPY_STANDARD_MANAGEMENT"
CODE_MAP_INFO = [
    {
        "SOURCE_DB_ACCESS_INFO": "COPY_SOURCE",
        "SOURCE_TABLE": "PO_TECL_CD",
        "SOURCE_COLS": ['*'],
        "REMARK": """
        """
    },
    {
        "SOURCE_DB_ACCESS_INFO": "COPY_SOURCE",
        "SOURCE_TABLE": "PO_ORGN",
        "SOURCE_COLS": ['*'],
        "REMARK": """
        """
    },
    {
        "SOURCE_DB_ACCESS_INFO": "COPY_SOURCE",
        "SOURCE_TABLE": "PO_COMM_CD",
        "SOURCE_COLS": ['*'],
        "REMARK": """
        """
    },
]

MIGRATION_INFO = {
    "TEST": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_TECL",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "SBJT_TECL_GRP_CD", "SBJT_TECL_CD", "PRIO_RK", "WGHT_PT"],
                # "SELECT_CONDITION": "SBJT_TECL_GRP_CD = 'T0001' AND PRIO_RK = 1",
                "TARGET_DB_ACCESS_INFO": "parquet",
                "TARGET_TABLE": "/mnt/d/parquet_files/tech",
                # "JOIN_KEY":["SBJT_ID","PRG_SN","PTC_PRG_SN"],
                "PREPROCESS": [
                    {"comm_cd_mapping": {"target_col": ["SBJT_TECL_CD"], "params":{
                        "source_table": "PO_TECL_CD", "mapping_key_col": "TECL_CD", "mapping_value_col": "SBJT_TECL_NM"}}}
                ],
            },
        ]
    },
    "ORIGINAL_COPY": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"연구개발 과제 테이블, 과제 ID 및 기본 정보 추출용 테이블"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_KWD",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_KWD",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 키워드"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_TOT_ANNL",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_TOT_ANNL",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 목표, 범위 내용, 기대효과 sbjt_id 로 합침"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_CFRSR_IPRS",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_CFRSR_IPRS",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 연구책임자 지식재산권 테이블, 국내외특허 출원 구분 포함"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_ORGN_RSCH_EXE",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_ORGN_RSCH_EXE",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 수행기관 연구 수행, 과제 현황 테이블"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_CFRSR_REXE",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_CFRSR_REXE",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 연구책임자 연구 수행, 과제 현황 테이블"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_ORGN_IPRS",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_ORGN_IPRS",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 수행기관 지식재산권 테이블, 국내외 출원 구분 포함"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_CFRSR_THES",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_CFRSR_THES",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 연구책임자 논문 현황 관리, 주관기관 책임자와 공동연구기관 책임자 해당"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_CFRSR_ETC",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_CFRSR_ETC",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제 연구책임자 기타 실적"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_RSCH_MBR",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_RSCH_MBR",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제를 수행하는 참여기관의 책임자와 참여연구원만 해당"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_RSCH_ORGN",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_RSCH_ORGN",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제를 수행하는 참여기관의 책임자와 참여연구원만 해당"
            },
            {
                "SOURCE_DB_ACCESS_INFO": DEFAULT_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_TECL",
                "TARGET_DB_ACCESS_INFO": DEFAULT_TARGET,
                "TARGET_TABLE": "PS_SBJT_TECL",
                "SOURCE_COLS": [
                    "*"
                ],
                "ADD_COMMENT": "Y",
                "REMARK":"과제를 수행하는 참여기관의 책임자와 참여연구원만 해당"
            }
        ]

    },
    "CODE": {
        "MERGE_PROCESS": [

        ]
    },
    "SUBJECT": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_PRG_PTC",
                "SOURCE_COLS": ['SBJT_ID', 'PRG_SN', 'PTC_PRG_SN'],
                "REMARK": """
                    -과제 세부 진행
                    - 컬럼명: 과제 ID, 	진행 순번, 	세부 진행 순번
                    - 과제에 대한 중분류이하의 업무가 발생한 생애주기 데이타의 관리
                    - 진행순번, 세부진행순번에 따라 중복데이터 발생 예상
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT",
                "SELECT_CONDITION": "",
                "SOURCE_COLS": ['SBJT_ID', 'HAN_SBJT_NM', 'ENG_SBJT_NM', 'BSNS_YY', 'OVRL_SBJT_ID', 'SORGN_BSNS_CD',
                                'SBJT_PROPL_STRC_SE', 'PRG_SBJT_EXE_ANNL', 'PRG_BSNS_YY', 'PRG_SORGN_BSNS_CD', 
                                'RND_SBJT_NO','HAN_OVRL_RND_NM','ENG_OVRL_RND_NM', ],
                "JOIN_KEY":["SBJT_ID"],
                "PREPROCESS": [
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "SBJT_PROPL_STRC_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "SBJT_PROPL_STRC_SE_NM"}}}
                ],
                "POSTPROCESS": [],
                # "TARGET_DB_ACCESS_INFO" : "parquet",
                # "TARGET_TABLE": "/mnt/d/parquet_files/join_test",
                "REMARK": """
                    -연구 개발 과제
                    -컬럼명: 과제 ID, 한글 과제 명,	영문 과제 명,	사업 년도, 	총괄 과제 ID, 전문기관 사업 코드, 
                        과제 추진 체계 구분,진행 과제 수행 연차, 	진행 사업 년도,진행 전문기관 사업 코드 ,
                        연구개발 과제번호, 한글 총괄 연구개발명, 영문 총괄 연구개발명
                    -코드 컬럼: SBJT_PROPL_STRC_SE
                    -공고를 통해 접수(생성)된 개념(사전)및 연구개발 계획서 단위를 과제로 지정및 해당 기본 정보의 관리
                    - sbjt_id, prg_sn, ptc_prg_sn, sbjt_step 별로 데이터 존재. 선택하는 기준 또는 통합 기준 필요함
                """
            },
            {

                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_KWD",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "KWD_NM", "KREN_SE","KWD_OR"],
                "JOIN_KEY": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "KREN_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "KREN_SE_NM"}}}
                ],
                "REMARK": """
                    -컬럼명: 	과제 ID, 진행 순번, 세부 진행 순번, 키워드 명, 한영 구분
                    -코드 컬럼: KREN_SE
                    1.과제를 표현하는 대표적인 키워드로 등록된 용어로 과제 접수시 접수자가 등록 - 개념계획서및 사업계획서
                    >>과제단위이므로 수행연차 = 0 으로 지정한다
                    +
                    2.연구개발결과서 (연차/단계/최종결과보고서) 제출시 보고서단위 키워드의 관리
                    >>연차와 단계및 최종보고서의 키워드는 는 해당 수행연차로 구분하되 보고서제출및안내 엔티티의 제출대상수행연차와 동일값이여야한다
                    
                    ★해당 엔티티의 데이타 IUD 발생업무 : 과제키워드:과제접수 + 협약변경 >> 과제접수시 등록된 키워드가 협약변경을 통해 변경되는 형태
                                                                                    보고서키워드: 보고서제출 - 신규만 발생함에 따라 협약변경을 통하지 않고 보고서제출 업무에서 바로 들어온다
                    
                    연구초록의 관리와 해당 키워드 관리는 통합에서 제외되나 이관을 위해 가져감
                    (과제를 대표하는 키워드및 연구초록에서 발생하는 키워드의 관리)
                    
                    ★텍스트마이닝시 적용되는 키워드
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SORGN_YY_BSNS",
                "SOURCE_COLS": ["BSNS_YY", "SORGN_BSNS_CD", "HIRK_SORGN_BSNS_CD", "SORGN_ID", "SORGN_BSNS_NM", "BSNS_CSRT_SE", "BSNS_TP_SE",
                                "SBJT_SPRT_BUD_AM", "BSNS_PRG_SE"],
                "JOIN_KEY": ["BSNS_YY", "SORGN_BSNS_CD"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SORGN_BSNS_CD"],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "BSNS_CSRT_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "BSNS_CSRT_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "BSNS_TP_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "BSNS_TP_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "BSNS_PRG_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "BSNS_PRG_SE_NM"}}},
                ],
                "REMARK": """
                    - 전문기관 사업 체계
                    - 컬럼명: 사업 년도, 전문기관 사업 코드, 	상위 전문기관 사업 코드, 전문기관 ID, 전문기관 사업 명, 사업 구조 구분, 사업 유형 구분, 
                        과제 지원 예산 금액, 기획 평가 예산 금액, 사업 진행 구분
                    - 코드 컬럼 : BSNS_CSRT_SE, BSNS_TP_SE, BSNS_PRG_SE
                    - 예산에 대한 정보는 어떤 데이터를 써야하는지 확인 필요
                    - 전문기관별 년도+사업의 메타와 구조 관리
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SORGN",
                "SOURCE_COLS": ["SORGN_ID", "HIRK_SORGN_ID", "SORGN_NM", "SORGN_ROLE_SE", "BLNG_GOVD_SE", "ORGN_ID"],
                "JOIN_KEY": ["SORGN_ID"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": [],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "SORGN_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "SORGN_ROLE_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "BLNG_GOVD_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "BLNG_GOVD_SE_NM"}}},
                ],
                "REMARK": """
                    - 전문기관
                    - 컬럼명: 전문기관 ID, 상위 전문기관 ID, 전문기관 명, 전문기관 역할 구분, 소속 부처 구분, 기관 ID
                    - 코드 컬럼 : SORGN_ROLE_SE, BLNG_GOVD_SE, 
                    - ORGN_ID 는 PO_ORGN 이랑 맵핑
                    - 기관엔티티중 전문기관의 기본정보를 별도 관리
                    20개 전문기관이라서 전문기관 전용항목이 기관엔티티의 많은 빈데이타가 발생함메 따라 분리함
                    
                    전문기관이 분할되거나 통합되더라도 사업자등록번호를 기준한 기관엔티티도 신규로 발생됨에 따라 기관ID도 UNIQUE하다
                    
                    ※워터마크 관리:전문기관단위로 관리하지 않고 IRIS 통합으로 관리, 서버에 물리적으로 파일하나만 존재 따라서 별도의 메타관리는 없다
                    ※서버인증서:전문기관별 식별자가 붙은 인증서 파일을 서버에서 파일형태로 관리 APP에서는 식별할수 있는 전문기관 약어명을 인증서 솔루션에 제공한다
                    
                    [사업단의 기능 정의]
                    1.하나의 전문기관에만 속한다
                    2.전문기관 자율적 구성하는 시스템적 설정등은 사업단 자체는 할수 없고 상위 전문기관의 설정을 따라야한다
                    3.사업단(연구단)도 전문기관과 동일 역할을 할경우 전문기관 형태로 관리하며, 상위 전문기관과의 연결을 가져간다
                    4.전문기관 단위 정보연계가 이뤄지는 경우 전문기관 소속 사업단은 해당 전문기관 연계서버를 통해 연계가 발생한다(따라서 연계기준에 전문기관이 구분처리된다)
                    
                    사업단의 속성을 등록을 별도로 할건지 상위 전문기관의 체계로 고정할것인지에 대한 결정이 필요
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_RSCH_ORGN",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "RSCH_ORGN_ID", "RSCH_ORGN_ROLE_SE", "AGRT_ORGN_ID", "RSCH_ORGN_NM", "NAT_SE", "LOC_ZNE_SE", ],
                "JOIN_KEY": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "RSCH_ORGN_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "SORGN_ROLE_SE_NM"}}},
                    {"custom_all_concat": {"target_cols": [
                        "SBJT_ID", "PRG_SN", "PTC_PRG_SN"], "params":{"col_name": "PS_SBJT_RSCH_ORGN"}}}
                ],
                "REMARK": """
                    - 과제 연구 기관
                    - 컬럼명: ~~~,연구 기관 ID,	연구 기관 역할 구분, 협약 기관 ID, 	연구 기관 명,국가 구분, 소재지 지역 구분
                    - 코드 컬럼 : RSCH_ORGN_ROLE_SE
                    - 좀 더 엄밀하게 맵핑하기 위해서는 과제 수행 연차(SBJT_EXE_ANNL) 까지 조인키로 사용해야함. 하지만 수행연차가 1인 데이터만 들고 올 것으로 예정되어 있어 제외했음
                    - 해당 테이블은 조인키로 묶기전에 키 컬럼 외 컬럼을 dict list 형태로 변환하여 -> PS_SBJT_RSCH_ORGN 컬럼으로 변환
                    - 연구를 직접 수행하는 주관기관 + 공동연구기관 + 수요처기관의 기본정보 관리
                    TIPA의 투자처및 수요(수혜)처는 과제지원기관으로 관리
                    산업부의 수요처는 해당 엔티티에서 관리 : 연구비를 지원및 분담하기때문
                    종료후 실시권을 가진 실시기관(업)
                    시스템적 업무 역할로써 성과실시기관등
                    
                    TIPA의 창업지원사업의 경우 사업계획서때는 미창업기관으로 들어와서 수정사업계획서때 기관등록되어 협약을 실시한다
                    
                    ※혁신법 외국기관 과제 참여 규정
                        - 한국에 지사형태의 사업자등록번호를 가진 외국기관만 사업 참여 가능
                        - 따라서 기존 전문기관에서 관리하던 외국기관(사업자번호를 관리하지 않고 과제의기관에 종속되어 DUMMY ID부여한 형태)은 과제 수행동안에는 유지(이관)되지만
                        협약변경으로 기관이 추가또는 변경되거나 할경우는 사업자번호 있는 외국기관만 참여처리
                    - 아래 외국기관 관리 형태는 모두 폐기됨
                    - 기관의 DUMMY는 TIPA의 미창업기관만 해당
                    
                    ★외국기관 관리
                    - 기관ID는 DUMMY
                    -계좌개설이 불가함으로 협약때 계좌정보를 받지않는다
                    -협약 결과의 연구비집행 SYS연계시는 주관기관 계좌를 매핑하여 연계 - 이지바로 확인필요
                    -연구비 지급시는 건별의 경우 연구비집행 시스템에서 부여하는 가상계좌로 지급되고, 일괄이나 집행시스템을 사용하지 않는경우 주관기관에 지급 - 최종확인필요
                    
                    ★산업부와 중기부의 수요처의 기능 차이 확인 필요
                    >>중기부의 수요처는 수혜기관으로 변경되며, 수요처부담금을 지원하는 지원기관의 역할
                    >> 산업부의 수요처는 과제연구를 수행하지는 않으나 종료후 해당과제의 성과를 구입 활용하기위해 과제에 참여하는 기관으로써 자체 정부지원금및 민간부담금을 가질수있다
                            과제연구기관중 주관기관을 제외한 공동연구기관이 수요처 역할을 할수도 있고, 단독 기업이 해당 수요처 역할을 할수도 있다
                            수요처 관리 - 정부지원금및 민간현금 부담비율의 중소기업 기준으로 완롸 + 산정기술료 책정시도 중소기준으로 책정
                    
                    ★외국기업과 미창업기관(TIPA)은 기관ID가 DUMMY
                        즉, 기관T에 물리적ID는 존재하나 상세정보는 과제지원에서 해당 엔티티에서 관리해야하는 형태
                        따라서, 외국기업의 경우 기관명(직접등록한)/기관유형/국가구분(대한민국제외)/소재지지역구분 = 해외로 설정
                                    미창업기관의 경우 기관명 = 미창업기업으로 설정/그외 시점항목은 NULL
                    
                    ★미창업기관의 설정은 년도+전문기관사업의 규정설정에서 사업특성 규정그룹내 규정중 창업지원사업이면 화면에서 기관등록을 하지 않고 DUMMY인 미창업기관을 지정/수정할수 없게 해야한다

                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_RSCH_MBR",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "RSCR_MBR_ID", "RSCR_ROLE_SE", "RSCR_NM", "NAT_SE", "SCH_NM", "PSTN_NM", "MAJ_NM", "DEG_SE",
                                "RSCH_CHRG_FILD_CN", "ETC_SBJT_PTCP_PT", "ETC_PTCP_SBJT_CT"],
                "JOIN_KEY": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "RSCR_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "RSCR_ROLE_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "NAT_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "NAT_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "MAJ_SERS_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "MAJ_SERS_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "DEG_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "DEG_SE_NM"}}},
                    {"custom_all_concat": {"target_cols": [
                        "SBJT_ID", "PRG_SN", "PTC_PRG_SN"], "params":{"col_name": "PS_SBJT_RSCH_MBR"}}}
                ],
                "REMARK": """
                    - 과제 연구 인력
                    - 컬럼명: ~~~,연구자 인력 ID, 연구자 역할 구분, 연구자 명, 국가 구분,학교 명, 	직위 명,전공 명, 학위 구분,
                    	연구 담당 분야 내용, 기타 과제 참여 비율,기타 참여 과제 수
                    - 코드 컬럼 : RSCR_ROLE_SE, NAT_SE, MAJ_SERS_SE, DEG_SE
                    - 개인정보 활용 동의한 인원 데이터만 가져오려면 PTCP_CSNT_DT 컬럼 값을 확인해야 할 것으로 보임
                    - 해당 테이블은 조인키로 묶기전에 키 컬럼 외 컬럼을 dict list 형태로 변환하여 -> PS_SBJT_RSCH_MBR 컬럼으로 변환
                    - 과제를 수행하는 참여기관의 책임자와 참여연구원만 해당
                    [2020.12.3 - 이윤장T,업무표준화 연구개발계획서 ]
                    1.기존 영리기관(중소/중견만)의 연구지원전문가 관리 형태가 과제연구인력으로 흡수 - 연구인력역할구분의 연구지원인력으로 통합관리
                        - 비영리의 경우 간접비에서 연구지원인력의 인건비를 계상했고, 영리기관에 동일 보전을 위해 직접비에서 계상토록함
                        -
                    동일 인력이 참여역할이 한 업무에서 바뀔수있어 참여역할도 PK로 지정
                    동일 연차 + 참여기관 + 동일인력 + 최종=Y + 참여종료일 =99991231 인 경우는 2건이상은 없다
                    
                    연구원 = 책임자 + 일반연구원
                    
                    연구원의 학력관련 사항은 연구자의 학력의 대표학력이나 최종학력 기준 존재할경우 적용 처리
                    단, 연구자의 학력관리 항목중 전공은 텍스트로 관리됨에 따라 별도 입력해야한다
                    외국인도 별도 입력 대상
                    
                    참여연구원중 채용예정을 제외하고 학력사항은 필수 처리 대상
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_SPRT_ORGN",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "SPRT_ORGN_ID", "SPRT_ORGN_ROLE_SE", "SPRT_ORGN_NM", "ORGN_TP_SE", "NAT_SE", "ORGN_ROLE_DSCR", ],
                "JOIN_KEY": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "PREPROCESS":[
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_COMM_CD", "on": "SPRT_ORGN_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "SPRT_ORGN_ROLE_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "ORGN_TP_SE", "on": "RSCR_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "ORGN_TP_SE_NM"}}},
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "NAT_SE", "on": "RSCR_ROLE_SE",
                                                                   "right_on": "COMM_CD", "code_map_col": "COMM_CD_NM", "new_col_name": "NAT_SE_NM"}}},
                    {"custom_all_concat": {"target_cols": [
                        "SBJT_ID", "PRG_SN", "PTC_PRG_SN"], "params":{"col_name": "PS_SBJT_SPRT_ORGN"}}}
                ],
                "REMARK": """
                    - 과제 지원 기관
                    - 컬럼명: ~~~,지원 기관 ID, 지원 기관 역할 구분, 지원 기관 명,	기관 유형 구분, 국가 구분, 기관 역할 설명
                    - 코드 컬럼 : SPRT_ORGN_ROLE_SE, ORGN_TP_SE, NAT_SE
                    - 해당 테이블은 조인키로 묶기전에 키 컬럼 외 컬럼을 dict list 형태로 변환하여 -> PS_SBJT_SPRT_ORGN 컬럼으로 변환
                    - 과제 수행에 참여하지 않지만 재원은 분담하면서 집행등의 수행을 하지 않는 기관의 관리
                    해당 지원기관이 지원하는 분담금의 내역은 과제분담연구비에서 연차별+참여기관별로 관리됨에 따라 별도 관리하지 않는다
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_ORGN_RSCH_EXE",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "TTL_RSCH_STR_DE", "TTL_RSCH_END_DE", "RSCT_AM"],
                "JOIN_KEY": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "PREPROCESS":[

                ],
                "REMARK":"""
                    - 과제 기관 연구 수행
                    - 과제 수행기관의 주요연구수행실적및 수행중인 과제 현황의 관리
                    - 컬럼명: ~~~,	총 연구 시작 일자, 총 연구 종료 일자, 연구비 금액
                    - 실 데이터 확인 가능 시 , 다른 테이블 참조하지말고, 해당 테이블에 기관/부처 키값, 과제 카테고리, 과제 내용, 키워드만 추가해서 사용 가능 여부 확인
                    - 과제 수행에 참여하지 않지만 재원은 분담하면서 집행등의 수행을 하지 않는 기관의 관리
                    해당 지원기관이 지원하는 분담금의 내역은 과제분담연구비에서 연차별+참여기관별로 관리됨에 따라 별도 관리하지 않는다
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_TECL",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "SBJT_TECL_CD"],
                "SELECT_CONDITION": "SBJT_TECL_GRP_CD = 'T0001' AND PRIO_RK = 1",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "JOIN_KEY":["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "PREPROCESS": [
                    {"comm_cd_join": {"target_cols": [], "params":{"code_map_table": "PO_TECL_CD", "on": "SBJT_TECL_CD",
                                                                   "right_on": "TECL_CD", "code_map_col": "", "new_col_name": "SBJT_TECL_CD_NM"}}},
                ],
                "REMARK": """
                    -과제 기술및 유형/특성 분류
                    -컬럼명: ~~~, 과제 기술분류 코드
                    -한 과제에 여러 값이 존재할것으로 보임. 이 테이블은 PO_TECL_CD 테이블과 조인 후 , 
                    우선순위별(PRIO_RK)로 오름차순 정렬 후 첫번째 값만 남기고 맵핑 또는 groupby해서 리스트나 dict 값으로 여러값을 같이 가져갈 것
                    -PRIO_RK 1 값이 있으면 그 값으로 우선 채워넣고, NULL 존재하는지 확인 
                    -SBJT_TECL_GRP_CD=T0001(국가과학기술표준분류에 해당하는 자료만 들고온다)
                    - PO_TECL_CD 테이블의 TECL_CD과 SBJT_TECL_CD 맵핑
                    T0001		국가과학기술표준분류
                    T0016		6T관련기술코드
                    T0017		기술수명주기
                    T0018		범부처정책분류
                    T0019		과제 특성·유형
                    T0003		학술표준분류
                    T0009		보건의료기술분류체계
                    T0002		산업기술분류
                    T0023		보건의료평가가능분야
                    T0015		과제개발유형
                    T0008		식품의약품등의안전기술분류
                    T0020		산림과학기술분류
                    T0025		기초연구_평가전문분야(기초연구사업)
                    T0026		인문사회학술연구_평가전문분야(인문사회연구사업)
                    T0027		국책연구_평가전문분야(국책연구사업)
                    T0028		NTRM분류
                    T0006		과학기술분야분류
                    T0004		기술성숙도(TRL)
                    T0007		원천기술개발분야분류
                    T0010		농림식품과학기술분류
                    T0011		ICT연구개발기술분류
                    T0012		기상기술분류
                    T0013		해양수산과학기술분류
                    T0014		원자력안전연구기술분류
                    T0022		품목표준코드
                    T0005		연구개발 단계
                    T0021		재난안전기술분류체계
                    -과제에 대한 다양한 기술적 + 일반 분류를 통합관리
                    일반분류의 경우 RFP의 분류를 상속해서 가져간다
                    
                    이력관리하지 않으나 사용여부가 들어간 이유는 동일 기술분류그룹이 코드재개정될경우 분류그룹이 추가생성되며, 관련 모든 데이타가 마이그된다
                    이때, 기존 코드가 뭐였는지를 남기고 사용여부 = N처리한다 >> 업무변경됨
                    업무표준화팀의 요청에 따라 연구개발계획서에 포함된 기술분류의 경우도 협약변경으로 변경할수있게 요청함에 따라 위 규칙이 변경되어 사용여부는 관리 삭제되고
                    
                    
                    ★과제접수시 표준기술분류그룹.설정구분 = R*D공통인것 + 전문기관 사업단위 기술분류그룹에서 설정한 기술분류
                    + 지정공모.RFP별 지정된 기술+일반분류 코드의 상속(성과소유주체 추가)
                    
                    
                    1.기술분류
                    산업기술분류코드
                    과학기술분류코드(연구분야+적용분야)
                    6T
                    녹색기술분류
                    국가중점과학기술분류
                    +
                    IITP :ICT 기술분류
                    
                    2.NTIS추가
                    - 연구개발단계(기초/응용/개발연구/기타)
                    - 연구개발성격:아이디어개발/시작품개발/제품또는 공정개발/기타개발
                    - 기술수명주기 - 성과계획으로 년차별 관리위해
                    - 세부과제성격 - 연구개발/연구시설장비/유지비,연구관리
                    
                    2019 조분평 추가 항목
                    0.성젠더 분석대상 과제 여부
                    1.부처연계협력기술개발 과제인지 여부 :아래 조건중 부처연계협력기술개발에 해당하는지에 대한 YN
                    1.민군협력유형:민군기술개발 - 민군겸용기술개발(민군공통활용 소재,부품,공정등의 기술개발
                                                                            부처연계협력기술개발(각부처의 고유사업중 민군협력이 가능한 기술개발)
                                                                            무기체계등의 개발(방위사업법에 따른 무기체계등 민군공동활용 체계개발)
                                                                            전력지원체계개발(민군공동활용 가능한 방위사업법에 따른 비무기체계 개발)
                                                민군기술이전 - 민군기술적용연구(민과 군 보유기술의 상호이전으로 실용화 가능성 연구)
                                                                        민군실용화연계(민군협력 기술개발로 확보한 기술의 군사적 시법및 민간의 수요 검증을 거쳐 실용화)
                                                민군규격표준화 - 민군규격표준화(민간규격과 국방규격의 표준화)
                                                민군기술정보교류 - 민군기술정보교류(연구개발성과,전문기술인력,국내외 기술개발 동향등 기술정보 교류)
                    
                    3.TRL분류 & 연구개발단계 분류코드
                    - TRL 선택시 매핑된 연구개발단계 코드를 세팅
                """
            },
            {
                "SOURCE_DB_ACCESS_INFO": COPY_SOURCE,
                "SOURCE_TABLE": "PS_SBJT_TOT_ANNL",
                "SOURCE_COLS": ["SBJT_ID", "PRG_SN", "PTC_PRG_SN", "RSCH_GOLE_CN", "RSCH_RANG_CN", "EXPE_EFCT_CN", "PRSPT_FRUT_CN"],
                "SELECT_CONDITION": "",
                "FILTER_BY_COL_VALS": ["SBJT_ID"],
                "JOIN_KEY":["SBJT_ID", "PRG_SN", "PTC_PRG_SN"],
                "PREPROCESS": [
                    {"custom_col_concat": {"target_cols": ["RSCH_GOLE_CN", "RSCH_RANG_CN", "EXPE_EFCT_CN", "PRSPT_FRUT_CN"], "params":{
                        "sep": "\n", "col_name": "content"}}},
                ],
                "REMARK": """
                    - 과제 종합 연차
                    - 컬럼명: 	연구 목표 내용, 연구 범위 내용, 기대 효과 내용, 예상 성과 내용
                    - 과제의 수행연차의 정보중 총괄및 단계별 기간및 목표/내용등의 메타 관리.

                """
            }
        ]
    },
    "PATENT": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": "PATENT_COPY",
                "SOURCE_TABLE": "PS_FRUT_IPRS",
                "SELECT_CONDITION": "IPRS_SE = '특허'",
                "SOURCE_COLS": ["IPRS_NM", "APLY_REGR_NM_LST", "INVTR_NM_LST", "IPRS_ABST_CN", "BLNG_ORGN_BSNSR_REG_NO_LST", "APLY_NO", "APLY_DE", "IPC_CL_CD"],
                "PREPROCESS": [
                    {}
                ],
                "TARGET_DB_ACCESS_INFO": "IN_MEMORY",
                "TARGET_TABLE": "patent_df",
                "POSTPROCESS": [
                    {
                        "rename_col": {
                            "target_cols": [
                                {
                                    "APLY_NO": "DOC_ID",
                                    "IPRS_NM": "TITLE",
                                    "APLY_REG_DE": "APP_DT",
                                    "APLYR_NM_LST": "PUBLISHER",
                                    "INVTR_NM_LST": "INVENTORS",
                                }
                            ]
                        }
                    }
                ],
                "REMARK": """
                    - 	과제 지식재산권 성과
                    - 과제수행및 종료후 발생하는 성과로써의 지식재산권 정보를 관리
                    - 컬럼명: 지식재산권 명, 	출원 등록자 명 목록, 발명자 명 목록, 	지식재산권 초록 내용, 소속 기관 사업자 등록 번호 목록, 	출원 번호, 	출원 일자, IPC 분류 코드
                """
            }
        ]
    },
    "THESIS": {
        "MERGE_PROCESS": [
            {
                "SOURCE_DB_ACCESS_INFO": "PATENT_COPY",
                "SOURCE_TABLE": "PS_FRUT_THES",
                "SELECT_CONDITION": "",
                "SOURCE_COLS": ["ENG_THES_NM", "MAUTHR_NM", "JONT_AUTHR_NM_LST", "ISSN_NO", "DOI_NO", "ISSU_NAT_SE", "THES_ABST_CN", "THES_KWD_CN", "JOUR_PRSS_DE", "RLNG_THES_NM"],
                "PREPROCESS": [
                    {}
                ],
                "TARGET_DB_ACCESS_INFO": "IN_MEMORY",
                "TARGET_TABLE": "patent_df",
                "POSTPROCESS": [
                    {
                        "rename_col": {
                            "target_cols": [
                                {
                                    "APLY_NO": "DOC_ID",
                                    "IPRS_NM": "TITLE",
                                    "APLY_REG_DE": "APP_DT",
                                    "APLYR_NM_LST": "PUBLISHER",
                                    "INVTR_NM_LST": "INVENTORS",
                                }
                            ]
                        }
                    }
                ],
                "REMARK": """
                    - 과제 논문 성과
                    - 과제+성과소유기관 단위의 과제수행 시작에서 성과활용기간동안 발생한 논문 성과의 관리
                    - 컬럼명: 영문 논문 명, 	주저자 명, 공동 저자 명 목록, ISSN 번호, 	DOI 번호, 	발행 국가 구분,  논문 초록 내용, 	논문 키워드 내용, 	학술지 출판 일자, 원어 논문 명
                """
            }
        ]
    }
}
