# 궤도점프 앱스토어 출시 가이드

이 폴더에는 iOS 앱 프로젝트, 아이콘, 런치 화면, 스크린샷, 스토어 문구, 개인정보처리방침이 모두 준비되어 있어요. 아래 순서대로 진행하면 됩니다. 1~2단계는 한 번만 하면 돼요.

## 0. 준비물

- **Mac**과 **Xcode** (App Store에서 무료 설치). iOS 앱 빌드와 업로드는 Mac에서만 할 수 있어요.
- **Apple Developer Program** 가입 (연 $99, 한국 129,000원). https://developer.apple.com/programs/ 에서 가입하고, 승인까지 보통 하루에서 이틀 걸려요.
- Node.js 20 이상 (https://nodejs.org)

## 1. 본인 정보로 바꾸기

1. `capacitor.config.json`의 `appId`를 본인 것으로 바꾸세요. 예: `com.hongildong.orbithop`. 전 세계에서 유일해야 하고, 출시 후에는 바꿀 수 없어요.
2. 같은 값을 Xcode에서도 설정합니다 (3단계에서 안내).
3. `store/privacy-policy.html`의 `[연락받을 이메일 주소]` 두 곳을 채우세요.

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

이미 설정해 둔 것: iPhone 전용, 세로 화면 고정, 상태 표시줄 숨김, 암호화 수출 규정 질문 자동 응답, 아이콘, 런치 화면.

## 4. 내 iPhone에서 먼저 해보기

iPhone을 케이블로 연결하고 Xcode 위쪽에서 기기를 고른 뒤 ▶ 버튼을 누르세요. 진동은 시뮬레이터가 아닌 실제 기기에서만 느낄 수 있어요.

운영자 모드로 테스트하고 싶으면 `npm run ios:dev`로 여세요. 이 빌드는 **절대 업로드하지 마세요.** 업로드 전에는 항상 `npm run ios`로 다시 빌드합니다.

## 5. App Store Connect에 앱 만들기

https://appstoreconnect.apple.com > **앱** > **+** > **신규 앱**

- 플랫폼: iOS
- 이름, 기본 언어, 번들 ID, SKU: `store/listing.md` 참고

## 6. 업로드

1. Xcode 위쪽 기기 목록에서 **Any iOS Device (arm64)** 선택
2. 메뉴 **Product > Archive**
3. Organizer 창이 열리면 **Distribute App > App Store Connect > Upload**
4. 10~30분 뒤 App Store Connect의 **TestFlight** 탭에 빌드가 나타나요. 여기서 지인들에게 먼저 테스트를 부탁할 수 있어요.

## 7. 스토어 정보 입력하고 심사 제출

`store/listing.md`의 값을 각 칸에 붙여 넣으세요.

- 스크린샷: `store/screenshots/`의 PNG 네 장 (iPhone 6.9")
- 개인정보처리방침 URL: `privacy-policy.html`을 공개 주소에 올려야 해요. GitHub Pages가 가장 간단해요.
- 앱 개인정보 보호: "데이터를 수집하지 않음"
- 빌드: 6단계에서 올린 빌드 선택
- **심사에 제출**. 보통 1~2일 안에 결과가 나와요.

## 심사에서 주의할 점

- **4.2 최소 기능**: 웹 화면을 감싸기만 한 앱은 거절될 수 있어요. 이 앱은 오프라인으로 실행되고, 네이티브 진동과 네이티브 저장소를 쓰는 완결된 게임이라 해당될 가능성은 낮지만, 거절되면 대개 Game Center 리더보드 같은 네이티브 기능을 추가하면 통과돼요.
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
