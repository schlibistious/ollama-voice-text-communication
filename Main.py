import speech_recognition as recog
import pvrecorder as recorder
import wave
import array
import os
import ollama
import pyttsx3

engine = pyttsx3.init()

path = os.path.dirname(__file__) + "/"
l = recorder.PvRecorder(512)
r = recog.Recognizer()

systemPrompt = "Your name is Scribble, you exist to be funny and entertaining, your personality is sarcastic and stubborn, and your second purpose is to answer questions."

def say(text): #broken after first try for some reason
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def voice():
    while True:
        canContinue = input('press enter to continue:')
        if canContinue == "":
            memoryAppend = open(path + 'memory.txt', 'a', encoding='utf-8')
            memory = open(path + 'memory.txt', 'r', encoding='utf-8') #memory file will be created if doesn't exist
            audio = []
            recording = True
            l.start()
            print("listening (press [CTRL] + [C] to stop talking):") 
            while recording == True:
                try:
                    frame = l.read()
                    audio.extend(frame)
                except KeyboardInterrupt:
                    print("loading..")
                    l.stop()
                    recording = False
                    filePath = path + "audio.wav"

                    with wave.open(filePath, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(16000)
                        wf.writeframes(array.array('h', audio).tobytes()) #idk how wave works this is stolen code lol
                        with recog.AudioFile(filePath) as source:
                            
                            audio_data = r.record(source)

                            transcription = r.recognize_google(audio_data)
                            print("transcription: " + transcription)
                            print("loading ai response..")
                            response = ollama.chat(
                                model='qwen3:4b',
                                messages=[{'role': 'assistant', 'content': ('heres a recap: ' + memory.read())}, {'role': 'system', 'content': systemPrompt},{'role': 'user', 'content': transcription}]
                            )
            memoryAppend.write('\nuser: ' + transcription + '\nyou: ' + response.message.content)
            memory.close()
            memoryAppend.close()
            print("\nresponse>> " + response.message.content)
            say(response.message.content)

def text():
    while True:
        memoryAppend = open(path + 'memory.txt', 'a', encoding='utf-8')
        memory = open(path + 'memory.txt', 'r', encoding='utf-8')
        message = input("\nSAY SOMETHING!!>>")
        print("loading ai response..")
        response = ollama.chat(
            model='qwen3:4b',
            messages=[{'role': 'assistant', 'content': ('heres a recap: ' + memory.read())}, {'role': 'system', 'content': systemPrompt},{'role': 'user', 'content': message}]
        )
        memoryAppend.write('\nuser: ' + message + '\nyou: ' + str(response.message.content))
        memory.close()
        memoryAppend.close()
        print("\nresponse>> " + response.message.content)
        say(response.message.content)

def record():
    option = input("would you like to use voice or text to communicate?:\n")
    if "voice" in option:
        print("initiating voice control..")
        voice()
    elif "text" in option:
        print("initiating text control..")
        text()
record()
