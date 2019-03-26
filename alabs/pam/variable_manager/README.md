

# 저장소
* `REST API` 를 이용하여 변수를 선언하여 값을 저장·가져오기 가능한 `변수 관리 서비스` 
* API 서버를 사용하지 않고 `Python Module`로서 사용이 가능
 
# 실행
## 환경변수 설정
```bash
export VM_API_PORT=8011
export EXTERNAL_STORE_ADDRESS_PORT="http://localhost:8200"
export EXTERNAL_STORE_TOKEN={TOKEN}
export EXTERNAL_STORE_NAME=myroot
``` 
## REST API Service
```bash
cd VARIABLE_MANAGER_DIRECTORY
python app/routes.py
```

### End-Point
```bash
# 변수 쓰기, 읽기
http://localhost:8011/api/v1.0/var/variables
# Parameters
path # 변수 위치. ex) path={{ABC.DEF}}

# 문장 치환
http://localhost:8011/api/v1.0/var/convert
# Parameters
data # 치환시킬 문장 ex) Hello {{ABC.DEF}}
```
### POST
```bash
curl -X POST -g \
  'http://localhost:8011/api/v1.0/var/variables' \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -d '{"path": "{{ABC.DEF}}", "data": "World"}'
  
true
```

### GET
```bash
curl -X GET -g \
  'http://localhost:8011/api/v1.0/var/variables?path={{ABC}}' \
  -H 'Cache-Control: no-cache' 

{"DEF": "World"}
```

```bash
curl -X GET -g \
  'http://localhost:8011/api/v1.0/var/convert?data=Hello%20{{ABC.DEF}}' \
  -H 'Cache-Control: no-cache'
```


## As Python Module
```python
from alabs.pam.variable_manager.variable_manager import Variables
vm = Variables()
```


# Argos Vriable 형태
## `JSON` 형태와 1:1 대응 가능
```json
{
    "ABC": {
        "DEF": [
            1, {"GHI": "Hello"}, ["Hi", "By", "World"]
        ]
    },
    "DEF": 2
}
```


|Argos Variable |Value| Description |
| --- | --- | --- |
| {{ABC}} |{"DEF": [1, {"GHI": "Hello"}, 3]} |  |
| {{ABC.DEF}} | [1, {"GHI": "Hello"}, 3] |  문자 `.`을 이용하여 변수의 깊이를 표현 |
| {{ABC.DEF(1)}} | {"GHI": "Hello"} | 변수명 뒤에 괄호와 정수형 값을 이용하여 배열 표현 |
| {{ABC.DEF(1).GHI}}| "Hello" |__지원예정__  |
| {{ABC.DEF(2)}} | ["Hi", "Bye", "World"]||
| {{ABC.DEF(2,2)}} | "World"| 쉼표를 이용하여  2차원 배열 표현 |
| {{ABC.DEF(2,{{DEF}})| "World" | 배열 인덱스에 다른 변수를 중첩하여 사용|
| {{@ABC.DEF}} | [1, {"GHI": "Hello"}, 3] | 변수이름 앞에 기호 `@`를 붙여 외부변수 저장소 사용 |
| {{@ABC.DEF(2,{{DEF}})| "World" | 외부변수 저장소와 로컬변수 혼합 사용|
| Hello {{ABC.DEF(2,2)}}! | "Hello World!"| 문자열 치환 |

## 주의사항
* 변수이름에는 `_`를 제외한 `특수문자` 사용금지


# 동작 다이어그램

```uml
PAM <-> (Variable Manager): {{GROUP.NAME}} 로컬변수 요청
PAM <-> (Variable Manager): {{@GROUP.NAME}} 글로벌변수 요청

(Variable Manager) <-> (Global Store 'Valut'): /public/GROUP/NAME
(Variable Manager) <-> (Local Store): [['GROUP']['NAME']]
```

### 확장형 배열 변수
![image.png](/files/2428211014801066034)
`$` 마지막 인덱스
`+` 마지막 인덱스 뒤에 이어 붙이기

`{{ABC.VARIABLE_TEXT($)}}`
`{{ABC.VARIABLE_TEXT(3)}}`
`{{ABC.VARIABLE_TEXT(7)}}`
`{{ABC.VARIABLE_TEXT(+)}}`