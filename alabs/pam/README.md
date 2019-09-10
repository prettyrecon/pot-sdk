# PAM Manager
## 동작 다이어그램
@startuml
title
Runner(Task) 생성 및 Scenario 등록
end title

' 선언
actor "STU/Chief" as USER  
participant "PAM(//Agent//)" as PAM
participant "Runner(//Task//)" as Runner
database "Repository" as REPOSITORY
' collections BOT

== Scenario 목록 보기 ==

USER -> PAM: 저장되어 있는 Scenario 목록 요청
activate PAM
PAM -> REPOSITORY: 위치확인
REPOSITORY [#blue]-> PAM: Scenario 목록
return: Scenario 정보 목록 반환


== Scenario 등록 ==
USER -> PAM: Scenario 저장소에 등록
activate PAM
PAM -> REPOSITORY: Scenario 저장 (홈디렉토리)
activate REPOSITORY 
return 저장 성공 유무 
return 저장 성공 유무

== Runner 목록 보기 ==
USER -> PAM: 생성되어 있는 Runner 목록 요청
activate PAM 
return Runner 목록 반환  

== Runner에 Scenario 설정 ==
USER -> PAM: Runner를 실행할 Scenario 지정 요청
activate PAM
PAM -> REPOSITORY: Scenario 경로 가져오기
activate REPOSITORY
REPOSITORY [#blue]-> PAM: Scenario 경로 반환
deactivate REPOSITORY
PAM -> Runner: Runner에 Scenario 지정
activate Runner
return Scenario 지정 성공 유무
return Boolean 

== Runner Scenario 수행 시작 ==
USER -> PAM: 지정된 Runner 시작 요청
PAM -> Runner: Runner 시작
activate Runner
Runner -> Runner: Scenario 작업 수행
return 작업 최종 결과 반환

== Runner 잠시 멈춤 ==
USER -> PAM: 지정된 PAM 잠시 멈춤 요청
activate PAM
PAM -> Runner: 잠시 멈춤 메세지 전송
activate Runner
Runner -> Runner: 잠시 멈춤 시도
return 멈춤 유무 값 반환
return 멈춤 유무 값 반환

== Runner 정지 ==
USER -> PAM: 지정된 PAM 정지 요청
PAM -> Runner: 정지, PAM 삭제 메세지 전송
activate Runner
Runner -> Runner: 정지 시도
return 

== Runner 삭제 ==
USER -> PAM: 지정한 Runner 삭제 요청
activate PAM 
PAM -> PAM: 지정된 Runner 삭제
return 











@enduml