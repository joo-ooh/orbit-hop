# 궤도점프 Google Play 출시 가이드

Android 앱은 **GitHub가 대신 빌드**해요. `main`에 올릴 때마다 GitHub Actions가 앱을 만들어 두기 때문에, Android Studio 없이도 출시할 수 있어요. iOS 가이드는 [RELEASE.md](RELEASE.md)에 있어요.

## 지금 바로 휴대폰에서 해보기

1. https://github.com/joo-ooh/orbit-hop/actions 에서 가장 최근의 초록색 **Android build** 실행을 엽니다.
2. 아래 **Artifacts**에서 `orbit-hop-test-apk`를 받아 압축을 풉니다.
3. 안드로이드 폰으로 `orbit-hop-test.apk`를 옮겨 열고 설치합니다. "출처를 알 수 없는 앱" 설치를 한 번 허용해야 해요.

이 테스트 APK는 운영자 모드가 켜져 있어요. 메뉴에서 제목을 다섯 번 탭하면 열립니다. 스토어에 올리는 파일은 따로 만들어져요 (아래 4단계).

## 0. 준비물

- **Google Play 개발자 계정** (1회 $25): https://play.google.com/console/signup. 신원 확인에 며칠 걸릴 수 있어요.
- iOS와 같은 개인정보처리방침 공개 주소

## 1. 꼭 알아둘 것: 14일 비공개 테스트

2023년 11월 이후 만든 **개인 개발자 계정**은 정식 출시 전에 **테스터 12명 이상이 14일 연속 참여한 비공개 테스트**를 거쳐야 해요. 그래서 Android를 일찍 시작하는 거예요.

- 친구, 가족, 동료 12명 이상의 Gmail 주소를 미리 모아 두세요. 여유 있게 15~20명을 권해요.
- 14일 동안 테스터가 앱을 지우지 않고 가끔 실행해 주면 좋아요.

## 2. 패키지 이름 정하기

`capacitor.config.json`의 `appId`, `android/app/build.gradle`의 `namespace`와 `applicationId`가 모두 `com.yourname.orbithop`이에요. iOS 번들 ID와 같은 값으로 세 곳을 바꾸세요. **처음 업로드한 뒤에는 바꿀 수 없어요.** 바꾸기 어려우면 정한 이름을 알려주세요. 제가 바꿔 드릴게요 (Java 폴더 이름도 같이 바뀌어야 해요).

## 3. 업로드 키 만들기 (한 번만)

Google Play에 올리는 파일은 본인만 가진 **업로드 키**로 서명해야 해요. 둘 중 편한 방법을 쓰세요.

**A. 터미널 (Java가 설치된 컴퓨터)**
```bash
keytool -genkeypair -v -keystore orbit-hop-upload.jks -alias upload \
  -keyalg RSA -keysize 2048 -validity 10000
```
비밀번호 두 개(키 저장소, 키)와 이름을 물어봐요. 같은 비밀번호를 써도 됩니다.

**B. Android Studio**: **Build > Generate Signed App Bundle or APK > Create new...**

만든 `.jks` 파일과 비밀번호는 **안전한 곳 두 군데 이상에 보관**하세요. **GitHub 저장소에는 절대 올리지 마세요.** 잃어버려도 Play Console에서 재설정을 요청할 수 있지만 며칠 걸려요.

## 4. GitHub에 업로드 키 등록

https://github.com/joo-ooh/orbit-hop/settings/secrets/actions > **New repository secret**으로 네 개를 추가하세요.

| 이름 | 값 |
|---|---|
| `ANDROID_KEYSTORE_BASE64` | `.jks` 파일을 base64로 바꾼 글자. Mac은 `base64 -i orbit-hop-upload.jks \| pbcopy`, Windows PowerShell은 `[Convert]::ToBase64String([IO.File]::ReadAllBytes("orbit-hop-upload.jks")) \| Set-Clipboard` |
| `ANDROID_KEYSTORE_PASSWORD` | 키 저장소 비밀번호 |
| `ANDROID_KEY_ALIAS` | `upload` (위 명령 그대로라면) |
| `ANDROID_KEY_PASSWORD` | 키 비밀번호 |

등록한 뒤 Actions 탭에서 **Android build > Run workflow**를 누르면, `orbit-hop-release-aab` 파일도 함께 만들어져요. 이게 Play Console에 올리는 파일이에요.

## 5. Play Console에 앱 만들기

**앱 만들기**에서 `store/play/listing.md`의 기본 정보를 입력하고, 같은 파일의 **앱 콘텐츠** 표대로 정책 설문에 답하세요.

## 6. 비공개 테스트 시작

1. **테스트 > 비공개 테스트 > 트랙 만들기**
2. **테스터**: 1단계에서 모은 이메일로 목록을 만들어요.
3. **새 버전 만들기**: `orbit-hop-release-aab`의 `.aab` 파일을 올립니다. Play 앱 서명 사용에 동의하세요.
4. 검토가 끝나면 테스터용 참여 링크가 생겨요. 테스터들에게 보내 주세요.
5. **14일이 지나면** 대시보드에서 **프로덕션 액세스 신청**을 할 수 있어요.

## 7. 스토어 등록정보

`store/play/listing.md`의 문구와 `store/play/`의 그래픽을 올리세요. 스크린샷은 `store/play/screenshots/`의 1080×1920 이미지예요. App Store용 1320×2868은 Google Play 비율 제한(2:1)에 걸려서 따로 만들었어요.

## 8. 프로덕션 출시

프로덕션 액세스가 승인되면 **프로덕션 > 새 버전 만들기**에서 같은 `.aab`를 (또는 더 새 빌드를) 올리고 검토를 요청하세요. 보통 며칠 안에 결과가 나와요.

## 업데이트할 때

게임을 고쳐 `main`에 올리면 GitHub이 새 `.aab`를 만들어요. 버전 코드는 GitHub 실행 번호로 자동으로 올라가요. 화면에 보이는 버전 이름은 `android/app/build.gradle`의 `versionName`이에요. 출시마다 iOS와 같은 값으로 올려 주세요.

## Android에서 달라지는 점

- **Game Center 랭킹 버튼이 없어요.** Game Center는 iPhone 전용이에요. Android용 랭킹(Google Play 게임즈)은 나중에 추가할 수 있어요.
- 휴대폰의 **뒤로 가기**: 플레이 중에는 일시정지, 창이 열려 있으면 닫기, 메인 메뉴에서는 앱 종료예요.
- 상태 표시줄과 내비게이션 바를 숨긴 전체 화면이에요. 화면 가장자리를 쓸어내리면 잠깐 나타나요.
