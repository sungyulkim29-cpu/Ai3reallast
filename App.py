import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import base64

st.set_page_config(
    page_title="자비스",
    page_icon="🤖"
)

st.title("🤖 자비스 - AI 음성 비서")

# ── 사이드바 ──────────────────────────────────────────
with st.sidebar:
    st.header("설정")

    voice_lang = st.selectbox(
        "음성 언어",
        ["ko", "en"],
        index=0
    )

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()


# ── 대화 기록 ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── 음성 → 텍스트 ─────────────────────────────────────
def speech_to_text(audio_bytes):

    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        return recognizer.recognize_google(
            audio_data,
            language="ko-KR"
        )

    except sr.UnknownValueError:
        return None

    except sr.RequestError as e:
        st.error(f"음성 인식 서비스 오류: {e}")
        return None

    except Exception as e:
        st.error(f"오디오 처리 오류: {e}")
        return None


# ── 테스트용 자비스 응답 ───────────────────────────────
def get_ai_response(user_input):

    text = user_input.lower()

    if "안녕" in text:
        return "안녕하세요. 저는 자비스입니다."

    if "이름" in text:
        return "제 이름은 자비스입니다."

    if "누구" in text:
        return "저는 음성으로 대화할 수 있는 AI 비서 테스트 프로그램입니다."

    if "날씨" in text:
        return "현재 날씨 정보를 연결하지 않은 테스트 버전입니다."

    if "고마워" in text:
        return "천만에요. 도움이 되어서 기쁩니다."

    return f"말씀하신 내용을 확인했습니다: {user_input}"


# ── 텍스트 → 음성 ─────────────────────────────────────
def text_to_speech(text, lang="ko"):

    tts = gTTS(
        text=text,
        lang=lang
    )

    audio_fp = io.BytesIO()

    tts.write_to_fp(audio_fp)

    audio_fp.seek(0)

    return audio_fp.read()


# ── 자동 재생 ─────────────────────────────────────────
def autoplay_audio(audio_bytes):

    b64 = base64.b64encode(audio_bytes).decode()

    st.markdown(
        f"""
        <audio autoplay>
            <source
                src="data:audio/mp3;base64,{b64}"
                type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )


# ── 기존 대화 표시 ────────────────────────────────────
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ── 음성 입력 ─────────────────────────────────────────
st.write("🎤 아래 버튼을 눌러 말해보세요.")

audio_value = st.audio_input(
    "음성으로 말하기"
)

user_input = None


if audio_value is not None:

    with st.spinner("음성 인식 중..."):

        recognized_text = speech_to_text(
            audio_value.read()
        )

    if recognized_text:

        st.success(
            f"인식된 텍스트: {recognized_text}"
        )

        user_input = recognized_text

    else:

        st.warning(
            "음성을 인식하지 못했습니다. 다시 말씀해 주세요."
        )


# ── 텍스트 입력 ───────────────────────────────────────
text_input = st.chat_input(
    "메시지를 입력하세요"
)

if text_input:
    user_input = text_input


# ── 자비스 응답 ───────────────────────────────────────
if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.write(user_input)


    # 테스트용 응답
    with st.spinner("자비스가 생각 중..."):

        ai_response = get_ai_response(
            user_input
        )


    # 응답 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )


    # 화면 출력
    with st.chat_message("assistant"):

        st.write(ai_response)


        # 음성 생성
        with st.spinner("음성 생성 중..."):

            speech_bytes = text_to_speech(
                ai_response,
                lang=voice_lang
            )


        autoplay_audio(
            speech_bytes
        )

        st.audio(
            speech_bytes,
            format="audio/mp3"
        )
