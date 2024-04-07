import time
import subprocess
from openai import OpenAI
from pydub import AudioSegment

def generate_voice( script,
                    outpath="output.wav",
                    narrator="Japanese Female 1",
                    speed=100,
                    pitch=0,
                    happy=50,
                    fun=50,
                    angry=0,
                    sad=0 ):
    exepath = "C:/Program Files/VOICEPEAK/voicepeak.exe"
    args = [
        exepath,
        "-s", script,
        "-n", narrator,
        "-o", outpath,
        "-e", f"happy={happy},sad={sad},angry={angry},fun={fun}",
        "--speed", f"{speed}",
        "--pitch", f"{pitch}",
    ]
    process = subprocess.Popen(args)
    process.communicate()

def extract_arguments_from_string(s):
    lines = s.split('\n')
    args_list = []
    for line in lines:
        if line.strip() == "":
            continue
        parts = line.split(':')
        script=parts[1].split('(')[0]
        emotion_info=parts[1].split('(')[1].strip(')')
        emotions = emotion_info.split(',')
        emotions_dict = {}
        for emotion in emotions:
            key_value_pair = emotion.split('=')
            if len(key_value_pair) == 2:
                key = key_value_pair[0].strip()
                value = key_value_pair[1].strip()
                emotions_dict[key] = int(value)
        args = {'script': script}
        args.update(emotions_dict)
        if parts[0].startswith("he"):
            narrator_prefix = "Japanese Male"
            narrator = f"{narrator_prefix} {parts[0].strip('he')}"
        elif parts[0].startswith("she"):
            narrator_prefix = "Japanese Female"
            narrator = f"{narrator_prefix} {parts[0].strip('she')}"
        else:
            narrator_prefix = "Japanese Feale Child"
        args.update({'narrator': narrator})
        args_list.append(args)
    return args_list

def run_gen_voice(args):
    script = args.get('script')
    outpath = args.get('outpath', "output.wav")
    narrator = args.get('narrator', "Japanese Female 1")
    speed = args.get('speed', 100)
    pitch = args.get('pitch', 0)
    happy = args.get('happy', 50)
    fun = args.get('fun', 50)
    angry = args.get('angry', 0)
    sad = args.get('sad', 0)
    generate_voice( script,
                    outpath,
                    narrator,
                    speed,
                    pitch,
                    happy,
                    fun,
                    angry,
                    sad )

def combine_wavfiles(args_list, output_file, silence_duration_ms=200):
    result = None
    silence = AudioSegment.silent(duration=silence_duration_ms)
    for args in args_list:
        file = args['outpath']
        audio = AudioSegment.from_wav(file)
        if result is None:
            result = audio
        else:
            result += silence + audio
    result.export(output_file, format="wav")

client = OpenAI()

if __name__ == "__main__":
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "男女4人くらいの面白い漫才のネタはありますか？"},
            {"role": "assistant", "content": """he1: 最近さ、買い物行ったらさ、なんか面白いことがあったんだよ。(happy=20,fun=20,angry=0,sad=0)
she1:え、なに？(happy=0,fun=50,angry=0,sad=0)
he1:その日、僕、魚屋に行ったんだよ。そしたらさ、店員さんが僕に言ったんだよ、『これが鮮度のいい魚です。』ってさ。(happy=0,fun=20,angry=0,sad=20)
he2:でもさ、ちょっと待ってよ。それって、魚が新しいんじゃなくて、鮮度が新しいってこと？(happy=0,fun=10,angry=10,sad=0)
she2:あはは、確かに！それってちょっと変な表現だよね。(happy=30,fun=20,angry=0,sad=0)
he1:そうそう、それでさ、魚が新しくなかったら、どうするんだろうって思ってたんだ。(happy=20,fun=20,angry=10,sad=10)
he1:魚屋の店員さんが、ポンと僕の頭を叩いて、『買い物帰りにスーパー行け』って言われたんだよ！(happy=10,fun=10,angry=20,sad=20)
she2:あはは、それは面白いエピソードだね！(happy=50,fun=50,angry=0,sad=0)
he1:うん、買い物で思いがけないことが起きるから、面白いよね！(happy=50,fun=50,angry=0,sad=0)"""},
            {"role": "user", "content": "他の面白い漫才のネタはありますか？"},
        ]
    )

    txt = completion.choices[0].message.content
    print(txt)
    args_list = extract_arguments_from_string(txt)
    wavfile_list = []

    for i, args in enumerate(args_list, start=1):
        outpath = f"voice{i:03d}.wav"
        args.update({'outpath': outpath})
        run_gen_voice(args)
        wavfile = {'outpath': outpath}
        wavfile_list.append(wavfile)
        print(outpath)
        time.sleep(1.0)

    output_wav_file = "combined_voice.wav"
    output_txt_file = "combined_voice.txt"
    with open(output_txt_file, "w") as f:
        print(txt, file=f)
    
    print(output_txt_file)
    combine_wavfiles(args_list, output_wav_file)
    print(output_wav_file)
