# 궤도점프 (Orbit Hop)

탭 한 번으로 행성 궤도 사이를 뛰어오르는 하이퍼캐주얼 게임. iOS 앱은 Capacitor로 만듭니다.

![스크린샷](store/screenshots/preview.png)

## 바로 해보기

`src/game.html`을 브라우저로 열면 웹 버전이 실행돼요. 메뉴에서 제목을 빠르게 5번 탭하면 운영자 모드가 열립니다.

## 명령어

| 명령 | 하는 일 |
|---|---|
| `npm install` | 의존성 설치 (처음 한 번) |
| `npm run ios` | 스토어용 빌드 후 Xcode 열기 (운영자 모드 꺼짐) |
| `npm run ios:dev` | 테스트용 빌드 후 Xcode 열기 (운영자 모드 켜짐, 업로드 금지) |
| `npm run art` | 아이콘과 런치 화면 다시 그리기 (Python, Pillow 필요) |
| `npm run store-shots` | 스토어 스크린샷 다시 촬영하고 문구 프레임 씌우기 |

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `src/game.html` | 게임 원본. 게임을 고칠 때는 이 파일만 수정 |
| `scripts/` | 앱 빌드, 아트, 스크린샷 스크립트 |
| `ios/` | Xcode 프로젝트 |
| `resources/` | 아이콘, 런치 화면, 내장 폰트 (SIL OFL) |
| `store/` | 스토어 문구, 개인정보처리방침, 스크린샷 |

출시 절차는 [RELEASE.md](RELEASE.md)에 있어요.
