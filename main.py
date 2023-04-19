from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import requests
import json
from ttslearn.dnntts import DNNTTS
import soundfile as sf
import os
import uuid
import torch

engine = DNNTTS()

TEMPLATE_PATH = "./data/template.txt"
SYSTEM_TEMPLATE_PATH = "./data/system_template.txt"
API_KEY = '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'

app = FastAPI()

def load_template(path:str):
    with open(path, 'r') as f:
        template = f.read()
    return template

template = load_template(TEMPLATE_PATH)
system_prompt = load_template(SYSTEM_TEMPLATE_PATH)

def edit_prompt(template:str, text:str, token="{query}"):
    prompt = template.replace(token, text)
    return prompt

def prompt_response(prompt:str, system_prompt:str):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + API_KEY,
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}, {"role": "system", "content": system_prompt}],
        "max_tokens": 200,
        "temperature": 1,
        "top_p": 1,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
    return response.json()

def foreprocessing(res):
    text = res['choices'][0]['message']['content']
    return text

@app.get("/chat")
async def get_chat_response(text:str = Query(...)):
    prompt = edit_prompt(template, text)
    res = prompt_response(prompt, system_prompt)
    res_text = foreprocessing(res)
    return res_text

#####################################################################

def TTS_streamer(text: str):
    with torch.no_grad():
        wav,sr = engine.tts(text)
        filename = str(uuid.uuid4())
        sf.write(f"{filename}.wav", torch.from_numpy(wav), sr)
        with open(f"{filename}.wav", mode="rb") as wav_file:
            yield from wav_file
    os.remove(f"{filename}.wav")

@app.get("/tts")
async def tts_streamer(text: str = Query(...)):
    return StreamingResponse(TTS_streamer(text), media_type="audio/wav")