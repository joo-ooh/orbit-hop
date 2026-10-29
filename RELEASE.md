# 궤도점프 앱스토어 출시 가이드

이 폴더에는 iOS 앱 프로젝트, 아이콘, 런치 화면, 스크린샷, 스토어 문구, 개인정보처리방침이 모두 준비되어 있어요. 아래 순서대로 진행하면 됩니다. 1~2단계는 한 번만 하면 돼요.

## 0. 준비물

- **Mac**(MacBook 포함)과 **Xcode 26 이상** (Mac App Store에서 무료 설치). Xcode 26은 macOS Sequoia 15.6 이상에서 돌아가요. 2026년 4월부터 App Store 업로드에는 Xcode 26 빌드가 필수예요.
- **Apple Developer Program** 가입 (연 $99, 한국 129,000원). https://developer.apple.com/programs/ 에서 가입하고, 승인까지 보통 하루에서 이틀 걸려요.
- Node.js 22 (https://nodejs.org 에서 LTS 설치)
- Git (터미널에서 `git --version`을 처음 실행하면 설치 안내가 떠요)

## 1. 본인 정보로 바꾸기

1. `capacitor.config.json`의 `appId`를 본인 것으로 바꾸세요. 예: `com.hongildong.orbithop`. 전 세계에서 유일해야 하고, 출시 후에는 바꿀 수 없어요.
2. 같은 값을 Xcode에서도 설정합니다 (3단계에서 안내).
3. 개인정보처리방침(https://joo-ooh.github.io/orbit-hop/privacy/)과 지원 페이지(https://joo-ooh.github.io/orbit-hop/support/)는 GitHub Pages에 올라가 있어요. 문의 이메일을 바꾸려면 `privacy/index.html`과 `support/index.html`을 고치세요.

## 2. Mac에서 프로젝트 열기

```bash
cd orbit-hop
npm install
npm run ios        # 스토어용으로 빌드하고 Xcode를 엽니다
```

## 3. Xcode 설정 (처음 한 번)

1. 왼쪽에서 **App** 프로젝트 > **TARGETS: App** > **Signing & Capabilities**
2. **Team**에서 본인 개발자 계정을 고르고, **Bundle Identifier**를 1단계에서 정한 값으로 바꾸세요.
3. **General** 탭에서 **Version**은 `1.0.0`, **Build**는 `1`로 두세요. 업로드할 때마다 Build 숫자를 1씩 올려야 해요.

이미 설정해 둔 것: iPhone 전용, 세로 화면 고정, 상태 표시줄 숨김, 암호화 수출 규정 질문 자동 응답, 아이콘, 런치 화면, Game Center 기능(capability).

**Signing & Capabilities** 탭에 **Game Center**가 보이는지 확인하세요. 서명에서 오류가 나면 **+ Capability**로 Game Center를 한 번 다시 추가하면 됩니다.

## 4. 내 iPhone에서 먼저 해보기

처음 한 번만 iPhone 준비가 필요해요.
- iPhone **설정 > 개인정보 보호 및 보안 > 개발자 모드**를 켜고 재시동하세요. 이 메뉴는 케이블로 Mac에 한 번 연결한 뒤에 나타나요.
- 처음 설치한 앱이 열리지 않으면 **설정 > 일반 > VPN 및 기기 관리**에서 본인 개발자 인증서를 신뢰하세요.

**개발자 계정 승인 전 무료 Apple ID로 테스트할 때:** Xcode의 Team에 개인 Apple ID(Personal Team)를 고르면 돼요. 단, 무료 계정은 Game Center를 지원하지 않아서 서명 오류가 나요. **Signing & Capabilities**에서 Game Center 옆의 ✕를 눌러 잠시 빼고 테스트하세요. 이 변경은 GitHub에 올리지 말고, 유료 계정이 승인되면 **+ Capability > Game Center**로 다시 추가하세요. 무료 계정으로 설치한 앱은 7일 뒤 다시 설치해야 해요.

iPhone을 케이블로 연결하고 Xcode 위쪽에서 기기를 고른 뒤 ▶ 버튼을 누르세요. 진동은 시뮬레이터가 아닌 실제 기기에서만 느낄 수 있어요.

운영자 모드로 테스트하고 싶으면 `npm run ios:dev`로 여세요. 이 빌드는 **절대 업로드하지 마세요.** 업로드 전에는 항상 `npm run ios`로 다시 빌드합니다.

## 5. App Store Connect에 앱 만들기

https://appstoreconnect.apple.com > **앱** > **+** > **신규 앱**

- 플랫폼: iOS
- 이름, 기본 언어, 번들 ID, SKU: `store/listing.md` 참고

## 5-1. Game Center 리더보드 만들기

게임은 점수를 `orbithop.best`라는 리더보드로 보내요. 이 리더보드를 App Store Connect에서 만들어야 랭킹이 동작합니다.

1. 5단계에서 만든 앱을 열고 **Game Center** 메뉴로 갑니다 (서비스 또는 기능 탭 안에 있어요).
2. 리더보드 **+** > **클래식 리더보드**
3. 아래처럼 입력하세요.

| 항목 | 값 |
|---|---|
| 참조 이름 | 최고 점수 |
| **리더보드 ID** | **`orbithop.best`** (한 글자라도 다르면 점수가 안 올라가요) |
| 점수 형식 | 정수 |
| 점수 제출 방식 | 최고 점수 |
| 정렬 순서 | 높은 점수 순 |

4. **현지화**에서 한국어를 추가하고 표시 이름은 "최고 점수", 점수 접미사는 "점"으로 하세요.
5. 7단계에서 앱 버전 화면의 **Game Center** 항목을 켜고 이 리더보드를 추가하세요. 첫 리더보드는 앱과 함께 심사받아요.

**내 iPhone에서 랭킹 테스트하기:** 리더보드를 만든 뒤 Xcode에서 ▶로 실행하면 Apple의 테스트용 랭킹에 점수가 올라가요. iPhone의 **설정 > Game Center**에 로그인되어 있어야 해요. 로그인되어 있지 않으면 게임 첫 실행 때 로그인 화면이 나와요.

## 6. 업로드

1. Xcode 위쪽 기기 목록에서 **Any iOS Device (arm64)** 선택
2. 메뉴 **Product > Archive**
3. Organizer 창이 열리면 **Distribute App > App Store Connect > Upload**
4. 10~30분 뒤 App Store Connect의 **TestFlight** 탭에 빌드가 나타나요. 여기서 지인들에게 먼저 테스트를 부탁할 수 있어요.

## 7. 스토어 정보 입력하고 심사 제출

`store/listing.md`의 값을 각 칸에 붙여 넣으세요.

- 스크린샷: `store/screenshots/`의 PNG 네 장 (iPhone 6.9")
- 개인정보처리방침 URL: https://joo-ooh.github.io/orbit-hop/privacy/
- 지원 URL: https://joo-ooh.github.io/orbit-hop/support/
- 앱 개인정보 보호: "데이터를 수집하지 않음"
- 빌드: 6단계에서 올린 빌드 선택
- Game Center: 켜고 `orbithop.best` 리더보드 추가 (5-1단계)
- **심사에 제출**. 보통 1~2일 안에 결과가 나와요.

## 심사에서 주의할 점

- **4.2 최소 기능**: 웹 화면을 감싸기만 한 앱은 거절될 수 있어요. 이 앱은 오프라인으로 실행되고, 네이티브 진동, 네이티브 저장소, Game Center 리더보드를 쓰는 완결된 게임이라 해당될 가능성은 낮아요.
- **2.3.1 숨겨진 기능**: 운영자 모드는 스토어 빌드에서 코드로 꺼져 있어요 (`npm run build`). 제목을 다섯 번 탭해도 열리지 않아요.
- 영어 스토어 문구를 함께 올리면 게임 안 글자도 영어가 필요하다는 지적을 받을 수 있어요. 처음에는 한국어로만 출시하는 걸 권해요.

## 파일 구성

| 경로 | 내용 |
|---|---|
| `src/game.html` | 게임 원본. 여기만 고치면 됩니다 |
| `scripts/build.mjs` | `src/game.html`을 앱용 `www/`로 변환 (폰트 내장, 운영자 모드 on/off) |
| `ios/` | Xcode 프로젝트 |
| `resources/icon.png`, `resources/splash.png` | 아이콘(1024×1024)과 런치 화면 원본 |
| `resources/fonts/` | 앱에 내장한 폰트와 라이선스 (SIL OFL, 상업적 이용 가능) |
| `scripts/make_art.py` | 아이콘과 런치 화면을 다시 그리고 Xcode에 복사 |
| `scripts/screenshots.mjs`, `scripts/frame_screenshots.py` | 스크린샷 촬영과 문구 프레임 |
| `store/` | 스토어 문구, 개인정보처리방침, 스크린샷 |

## 게임을 고친 뒤

```bash
npm run ios          # 다시 빌드하고 Xcode 열기
```

Xcode에서 Build 숫자를 올리고 6단계부터 반복하세요.
