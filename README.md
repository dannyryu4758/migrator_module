> README Info
>
> > writer/email: 유호건 / hgryu@euclidsoft.co.kr
> > last_modified: 2021.10.05
> > module_version: 0.0.1

> Table of contents

- [Migrate_composer](#migrate-composer)
  - [Guide](#guide)
    - [Install guide](#install-guide)
      - [Basic Function List](#function-list)
  - [Customizing](#customizing)

# Migrate_composer

데이터 전처리를 거쳐 데이터베이스 마이그레이션 혹은 데이터를 파일형태로 저장하기 위한 모듈로써 지정 양식에 따라 사용자에 의해 작성된 명세서(Migration_info)를 참고하여 데이터를 조작한다.

## Guide

### Install guide

1. 모듈 다운로드

   ```
   $ git clone http://euclidai.kr:20080/data_analysis/migrate_composer
   ```

2. 설치방법 (2가지 방법)
   A. Docker를 활용한 설치/실행 (실행 전 Docker 설치 필수)

   ```
    a) 해당 모듈 폴더 안에서 $ /bin/bash deploy.sh 실행
   ```

   B. Docker를 사용하지 않고 설치 및 실행방법

   ```
    a)	Oracle client 다운로드 및 압축 해제
    b)	libaio 설치
    c)	환경변수에 오라클홈 등 필요 변수 설정
    d)	파이썬 3.7 이상 설치
    e)	$ pip install cx_Oracle==8.2.1
    f)	$ pip install pandasql==0.7.3
    g)	$ pip install fastparquet==0.7.1
    h)	$ pip install PyMySQL==1.0.2
    i)	$ python migrate_composer.py
   ```

   C. 실행

   - Migration_Tracer 객체 생성 후 객체 내 migration함수 실행
     - 파라미터
       (1) database_list : 실행할 MIGRATION_INFO 리스트 (생략시 명세서내 작성된 모든 list 실행)
       (2) validation : 명세서(Migration_info) 검증 여부
       (3) seleced_validation: 입력된 databas_list 범위 내 검증 여부
       (4) temp_save : 실행 중 오류 발생시 진행 중이던 주요 데이터 임시저장 여부

   ```
    migration_tracer = Migration_Tracer(
                                        database_list=database_list,
                                        validation=True,
                                        validation_all_list=False,
                                        temp_save=True
                                       )
    migration_tracer.migration()
   ```

### Migration_Info Job List

#### remove_cols(df, target_cols, params):

```
컬럼(열) 삭제
df : DataFrame
target_cols : (list)삭제할 컬럼

return : DataFrame
```

#### copy_cols(df, target_cols, params):

```
특정 컬럼을 복사
df : DataFrame
target_cols : (list)복사되어 들어갈 컬럼명
params : (dict) {'source_cols' : list}
    - source_cols : 복사할 컬럼명

return : DataFrame
```

#### add_groupby_rank(df, target_cols, params):

```
그룹으로 정렬 후 rank 지정
df : DataFrame
target_cols : (list)정렬할기준 컬럼들
params : (dict) {'ranked_col' : str, 'group_col': str, 'new_col':str}
    - ranked_col : rank의 기준 컬럼명
    - group_col : 그룹으로 지정할 컬럼
    - new_col : rank를 넣을 새로운 컬럼명

return : DataFrame
```

#### custom_groupby(df, target_cols, params)

```
기존 DataFrame 컬럼을 모두 유지한 채로 원하는 컬럼별 그룹화 및 집계
df : DataFrame
params : (dict) {'group_cols' : list, 'agg_col': str, 'agg_type' : str}
    - group_cols : (list)그룹화할 컬럼명
    - agg_col : 집계할 컬럼명
    - agg_type : 집계명 string ("min" or "max") 기본값 "max"
return : DataFrame
```

#### custom_groupby_concat(df, target_cols, params)

```
그룹화하여 지정한 컬럼의 여러 행 데이터를 한개의 열 데이터로 변환
데이터가 없으면 concat 하지 않아 ', ,' 같은 불필요 데이터 미발생
df : DataFrame
target_cols : (list)합칠 컬럼명들
params : (dict) {'sum_cols' : list, 'sep': str, 'group_col' : list}
    - sum_cols : (list)합칠 컬럼명들
    - sep : 구분자 (기본값 : ',') 생략가능
    - group_col : (list)그룹화할 컬럼명
return : DataFrame
```

#### custom_col_concat(df, target_cols, params)

```
그룹화하여 지정한 컬럼의 여러 열을 concat 변환
데이터가 없으면 concat 하지 않아 ', ,' 같은 불필요 데이터 미발생
df : DataFrame
params : (dict) {'sum_cols' : list, 'sep': str, 'col_name' : str}
    - sum_cols : (list)합칠 컬럼명들
    - sep : 구분자 (기본값 : ',') 생략가능
    - col_name : concat 결과를 담을 컬럼명
return : DataFrame
```

#### custom_all_concat(df, target_cols, params)

```
그룹화하여 그룹화컬럼을 제와한 모든 컬럼과
열 데이터를 하나의 컬럼으로 list(dict()) 형태로 생성
df : DataFrame
params : (dict) {'group_cols' : list, 'col_name' : str, 'remove_col_yn' : str}
    - group_cols : (list)그룹화할 컬럼명
    - col_name : concat 결과를 담을 컬럼명
    - remove_col_yn : concat 후 group_cols 삭제 여부(Y or N)

return : DataFrame
```

#### comm_cd_join(df, target_cols, param) :

```
공통코드와 JOIN
df : DataFrame
params : (dict) {'code_map_table' : str, 'on':str, 'right_on':str, 'code_map_col' : str, 'new_col_name': str}
    - code_map_table : 사용할 공통코드명
    - on : 조인할 Main_df 컬럼명(좌우 공통시 on 만 입력)
    - right_on : 조인할 Sub_df 컬럼명 (생략가능)
    - code_map_col : 사용할 공통코드 컬럼명
    - new_col_name : 공통코드컬럼 변경명(생략시 기존 컬럼명 사용)

return : DataFrame
```

#### drop_na(df, target_cols, params) :

```
결측값 삭제 처리
df : DataFrame
target_cols : 처리할 컬럼명
params : (dict) {'axis': int}
    - axis : 0 => 행삭제 or 1 => 열삭제 (기본값 0)
return : DataFrame
```

#### drop_duplicates(df, target_cols, params) :

```
결측값 삭제 처리
df : DataFrame
target_cols : 처리할 컬럼명
params : (dict) {'sortby': list, 'keep': 'first' or 'last' or False}
    - sortby : (list)정렬기준 (기본값 None)
    - keep (기본값 : 'first')
        1) 'first': 첫번째 중복데이터 제외한 나머지 중복데이터 삭제
        2) 'last': 마지막 중복데이터 제외한 나머지 중복데이터 삭제
return : DataFrame
```

#### fillna(df, target_cols, params) :

```
결측값 처리
df : DataFrame
target_cols : (list)처리할 컬럼명
params : (dict) {'replace' : str} - replace : 결측값을 대체할 문자열(기본값 : '')
return : DataFrame
```

#### df_query_filter(df, target_cols, params) :

```
DataFrame 필터링
df : DataFrame
params : (dict) {'query' : str } - query : DataFrame 전용 query
return : DataFrame
```

#### df_to_dict(df, target_cols, params) :

```
Dictionary 형태의 데이터 컬럼 생성
df : DataFrame
params : (dict) {'col_name' : str}
    - col_name : dict 타입 데이터를 담을 컬럼명
return : DataFrame
```

#### sort(df, target_cols, params) :

```
DataFrame 정렬
df : DataFrame
params : (dict) {'sort_by_cols' : list,  'order_by' : str }
    - sort_by_cols : (list) 정렬 기준 컬럼명
    - order_by
        1) 'asc' : 오름차순(기본값)
        2) 'desc' : 내림차순
return : DataFrame
```

#### rename_cols(df, target_cols, params) :

```
DataFrame 정렬
df : DataFrame
params : (dict) { '기존컬럼명1' : '변경할 컬럼명1', '기존컬럼명2' : '변경할 컬럼명2', ... }
return : DataFrame
```

#### adapter_dict_to_json(df, target_cols, params) :

```
json 형식으로 변경
df : DataFrame
target_cols : (list)json 형식으로 변경할 컬럼명
return : DataFrame
```

#### adapter_etc_cleaning(df, target_cols, params) :

```
기타 수식문구 정제
df : DataFrame
target_cols : (list)정제할 컬럼명
params : (dict) { 'del_word' : bool, 'space_word' : bool} - del_word : etc_list내 포함 문자열 삭제 여부 (기본값 : True) - space_word : need_space_list내 포함 문자열 앞뒤 띄여쓰기 여부 (기본값 : True)
return : DataFrame
```

#### adapter_bracket_cleaning(df, target_cols, params) :

```
모든 괄호내 문자열(괄호포함) 삭제
df : DataFrame
target_cols : (list)정제할 컬럼명
params : (dict) {'only_bracket' : bool}
only_bracket : 괄호만 삭제 (기본값 False)
return : DataFrame
```

#### adapter_not_word_del(df, target_cols) :

```
문자열(숫자,문자)이 없는 데이터 None 처리
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_replace_not_mean_word(df, target_cols) :

```
연속되는 특수문자 공백으로 처리 ex) '#\s\*@' => '\s'
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_double_space_cleaning(df, target_cols) :

```
연속되는 특수문자 공백으로 처리 ex) '#\s\*@' => '\s'
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_cleaning_organ_nm(df, target_cols) :

```
기관명 정제
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_cleaning_univer_nm(df, target_cols) :

```
대학명 정제
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_cleaning_all_agency_nm(df, target_cols) :

```
기관명,대학명 모두 정제
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_word_unification_cleaning(df, target_cols) :

```
기관명 약어 정제 ex) 한국과학기술원 → KAIST
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_remove_all_special_word(df, target_cols) :

```
모든 특수문자 삭제 후 공백처리
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```

#### adapter_start_end_with_special_char(df, target_cols) :

```
문자열 양 끝 특수문자 제거
df : DataFrame
target_cols : (list)정제할 컬럼명
return : DataFrame
```
