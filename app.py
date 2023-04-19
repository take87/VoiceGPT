import streamlit as st
import requests
import base64
import time

# APIのそれぞれのURL
CHATBOT_ENDPOINT = 'http://127.0.0.1:8000/chat'
TTS_ENDPOINT = 'http://127.0.0.1:8000/tts'

def get_tts_sound(text:str, url=TTS_ENDPOINT):
    params = {'text': text}
    response = requests.get(url, params=params)
    return response.content

def sound_player(response_content: bytes) -> None:
    audio_placeholder = st.empty()
    audio_html = f"""
        <audio controls autoplay>
            <source src="data:audio/wav;base64,{base64.b64encode(response_content).decode()}"
                type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    """
    audio_placeholder.empty()
    time.sleep(0.5)
    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)


def get_chat_response(text:str, url=CHATBOT_ENDPOINT):
    params = {'text': text}
    response = requests.get(url, params=params)
    return response.text

if __name__ == "__main__":
    st.set_page_config(layout="wide")
    
    query = st.text_input('質問を入力してください')
    button = st.button('実行')

    if button:
        # チャットボットの返信を取得
        response_text = get_chat_response(query)
        st.write(f'回答：{response_text}')
        sound_player(get_tts_sound(response_text))