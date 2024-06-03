import os
import json
from gtts import gTTS

CONST_PATH_JSON = "/home/jetson/turtlebot3_ws/src/lbo/lbo/tts_dict.json"
CONST_PATH_OUTPUT = "/home/jetson/turtlebot3_ws/src/lbo/lbo/sounds"

def generate_tts(text, lang='ko', save=None):
    print(text)
    tts = gTTS(text, lang=lang)
    if save:
        if os.path.isdir(save):
            output_path = os.path.join(save, "tts_sample.mp3")
        else:
            output_path = save
        
        print(output_path)
        print(os.path.dirname(output_path))

        if os.path.exists(os.path.dirname(output_path)) == False:
            os.makedirs(os.path.dirname(output_path))

        tts.save(output_path)

def read_json(path, enc='UTF8'):
    with open(path, 'r', encoding=enc) as f:
        return json.load(f)

def main():
    meta_dict = read_json(CONST_PATH_JSON)
    for i in range(16):
        generate_tts(meta_dict[str(i)]["text"], save=os.path.join(CONST_PATH_OUTPUT, meta_dict[str(i)]["file"]))
        
if __name__ == "__main__":
    main()
