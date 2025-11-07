{\rtf1\ansi\ansicpg950\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import requests\
import json\
import os\
from datetime import datetime\
from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, SUMMARIES_DIR\
\
class LLMSummarizer:\
    def __init__(self, model_name="gpt-3.5-turbo"):\
        self.model_name = model_name\
        self.api_key = OPENROUTER_API_KEY\
        \
    def read_transcript_file(self, file_path):\
        try:\
            with open(file_path, 'r', encoding='utf-8') as f:\
                return f.read().strip()\
        except Exception as e:\
            print(f"\uc0\u35712 \u21462 \u25991 \u20214 \u37679 \u35492  \{file_path\}: \{e\}")\
            return None\
    \
    def create_summary_prompt(self, transcript_text):\
        prompt = f"""\uc0\u35531 \u23565 \u20197 \u19979 \u23565 \u35441 \u25110 \u35486 \u38899 \u20839 \u23481 \u36914 \u34892 \u23560 \u26989 \u25688 \u35201 \u65306 \
\
\{transcript_text\}\
\
\uc0\u35531 \u25353 \u29031 \u20197 \u19979 \u35201 \u27714 \u25552 \u20379 \u25688 \u35201 \u65306 \
1. \uc0\u25552 \u21462 \u20027 \u35201 \u35264 \u40670 \u21644 \u38364 \u37749 \u20449 \u24687 \
2. \uc0\u20445 \u25345 \u23458 \u35264 \u20013 \u31435 \
3. \uc0\u29992 \u20013 \u25991 \u22238 \u25033 \
4. \uc0\u31777 \u28500 \u26126 \u20102 \u65292 \u25511 \u21046 \u22312 200\u23383 \u20197 \u20869 \
\
\uc0\u25688 \u35201 \u65306 """\
        return prompt\
    \
    def call_llm_api(self, prompt):\
        if not self.api_key:\
            return "\uc0\u37679 \u35492 \u65306 \u35531 \u35373 \u32622 OPENROUTER_API_KEY\u29872 \u22659 \u35722 \u37327 "\
        \
        headers = \{\
            "Authorization": f"Bearer \{self.api_key\}",\
            "Content-Type": "application/json"\
        \}\
        \
        data = \{\
            "model": self.model_name,\
            "messages": [\
                \{\
                    "role": "user",\
                    "content": prompt\
                \}\
            ],\
            "temperature": 0.3\
        \}\
        \
        try:\
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=60)\
            if response.status_code == 200:\
                result = response.json()\
                return result['choices'][0]['message']['content']\
            else:\
                return f"API\uc0\u35531 \u27714 \u22833 \u25943 : \{response.status_code\} - \{response.text\}"\
        except Exception as e:\
            return f"\uc0\u30332 \u29983 \u37679 \u35492 : \{str(e)\}"\
    \
    def summarize_single_file(self, input_file_path, output_filename=None):\
        print(f"\uc0\u27491 \u22312 \u34389 \u29702 \u25991 \u20214 : \{input_file_path\}")\
        \
        transcript = self.read_transcript_file(input_file_path)\
        if not transcript:\
            return False\
        \
        if len(transcript) < 10:\
            print("\uc0\u35686 \u21578 \u65306 \u36681 \u37636 \u20839 \u23481 \u22826 \u30701 \u65292 \u21487 \u33021 \u19981 \u23436 \u25972 ")\
        \
        prompt = self.create_summary_prompt(transcript)\
        \
        print("\uc0\u27491 \u22312 \u35519 \u29992 LLM\u29983 \u25104 \u25688 \u35201 ...")\
        summary = self.call_llm_api(prompt)\
        \
        if not output_filename:\
            original_name = os.path.basename(input_file_path)\
            name_without_ext = os.path.splitext(original_name)[0]\
            output_filename = f"summary_\{name_without_ext\}.txt"\
        \
        output_path = os.path.join(SUMMARIES_DIR, output_filename)\
        \
        with open(output_path, 'w', encoding='utf-8') as f:\
            f.write(f"\uc0\u21407 \u22987 \u25991 \u20214 : \{os.path.basename(input_file_path)\}\\n")\
            f.write(f"\uc0\u29983 \u25104 \u26178 \u38291 : \{datetime.now().strftime('%Y-%m-%d %H:%M:%S')\}\\n")\
            f.write(f"\uc0\u20351 \u29992 \u27169 \u22411 : \{self.model_name\}\\n")\
            f.write("=" * 50 + "\\n")\
            f.write("\uc0\u25688 \u35201 \u32080 \u26524 :\\n")\
            f.write(summary)\
            f.write("\\n" + "=" * 50 + "\\n")\
            f.write("\\n\uc0\u21407 \u22987 \u36681 \u37636 \u20839 \u23481 :\\n")\
            f.write(transcript)\
        \
        print(f"\uc0\u25688 \u35201 \u24050 \u20445 \u23384 : \{output_path\}")\
        return True\
    \
    def summarize_all_files(self, transcripts_dir):\
        success_count = 0\
        total_count = 0\
        \
        for filename in os.listdir(transcripts_dir):\
            if filename.endswith(('.txt', '.text')):\
                total_count += 1\
                file_path = os.path.join(transcripts_dir, filename)\
                \
                if self.summarize_single_file(file_path):\
                    success_count += 1\
                else:\
                    print(f"\uc0\u34389 \u29702 \u22833 \u25943 : \{filename\}")\
        \
        print(f"\\n\uc0\u34389 \u29702 \u23436 \u25104 : \{success_count\}/\{total_count\} \u20491 \u25991 \u20214 \u25104 \u21151 ")\
        return success_count, total_count\
\
if __name__ == "__main__":\
    summarizer = LLMSummarizer()\
    success, total = summarizer.summarize_all_files("data/transcripts")\
    print(f"\uc0\u28204 \u35430 \u23436 \u25104 : \{success\}/\{total\} \u25104 \u21151 ")}