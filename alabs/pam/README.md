# PAM Manager
## 동작 다이어그램
@startuml
title
PAM 생성 및 시나리오 등록
end title

' 선언
actor "STU/Chief" as USER  
participant "PAM Manager(//Agent//)" as PM
participant "PAM(//Runner//)" as PAM
database "Repository" as REPOSITORY
' collections BOT

== Scenario 목록 보기 ==

USER -> PM: 저장되어 있는 Scenario 목록 요청
activate PM
PM -> REPOSITORY: 위치확인
REPOSITORY [#blue]-> PM: Scenario 목록
return: Scenario 정보 목록 반환


== Scenario 등록 ==
USER -> PM: Scenario 저장소에 등록
activate PM
PM -> REPOSITORY: Scenario 저장 (홈디렉토리)
activate REPOSITORY 
return 저장 성공 유무 
return 저장 성공 유무

== PAM 목록 보기 ==
USER -> PM: 생성되어 있는 PAM 목록 요청
activate PM 
return PAM 목록 반환  

== PAM에 Scenario 설정 ==
USER -> PM: PAM이 실행할 Scenario 지정 요청
activate PM
PM -> REPOSITORY: Scenario 경로 가져오기
activate REPOSITORY
REPOSITORY [#blue]-> PM: Scenario 경로 반환
deactivate REPOSITORY
PM -> PAM: PAM에 Scenario 지정
activate PAM
return Scenario 지정 성공 유무
return Boolean 

== PAM 시작 ==
USER -> PM: 지정된 PAM 시작 요청
PM -> PAM: PAM 시작
activate PAM
PAM -> PAM: Scenario 작업 수행
return 작업 최종 결과 반환

== PAM 잠시 멈춤 ==
USER -> PM: 지정된 PAM 잠시 멈춤 요청
activate PM
PM -> PAM: 잠시 멈춤 메세지 전송
activate PAM
PAM -> PAM: 잠시 멈춤 시도
return 멈춤 유무 값 반환
return 멈춤 유무 값 반환

== PAM 정지 ==
USER -> PM: 지정된 PAM 정지 요청
PM -> PAM: 정지, PAM 삭제 메세지 전송
activate PAM
PAM -> PAM: 정지 시도
return 

== PAM 삭제 ==
USER -> PM: 지정한 PAM 삭제 요청
activate PM 
PM -> PM: 지정된 PAM 삭제
return 











@enduml