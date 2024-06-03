import os

def play_tts(path):
    os.system(f"ffplay {path} -autoexit")

if __name__ == "__main__":
    play_tts("")