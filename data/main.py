{\rtf1\ansi\ansicpg950\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import sys\
from config import TRANSCRIPTS_DIR\
from llm_summarizer import LLMSummarizer\
\
def main():\
    print("=== ASR + LLM \uc0\u25688 \u35201 \u27969 \u27700 \u32218  ===")\
    print(f"\uc0\u36681 \u37636 \u25991 \u20214 \u30446 \u37636 : \{TRANSCRIPTS_DIR\}")\
    \
    if not os.path.exists(TRANSCRIPTS_DIR):\
        print(f"\uc0\u37679 \u35492 : \u36681 \u37636 \u25991 \u20214 \u30446 \u37636 \u19981 \u23384 \u22312 : \{TRANSCRIPTS_DIR\}")\
        print("\uc0\u35531 \u21109 \u24314 \u30446 \u37636 \u20006 \u25918 \u20837 \u36681 \u37636 \u25991 \u20214 ")\
        return\
    \
    transcript_files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith(('.txt', '.text'))]\
    if not transcript_files:\
        print("\uc0\u37679 \u35492 : \u36681 \u37636 \u25991 \u20214 \u30446 \u37636 \u20013 \u27794 \u26377 \u25214 \u21040 .txt\u25991 \u20214 ")\
        print("\uc0\u35531 \u23559 \u36681 \u37636 \u25991 \u26412 \u25991 \u20214 \u25918 \u20837  data/transcripts/ \u30446 \u37636 ")\
        return\
    \
    print(f"\uc0\u25214 \u21040  \{len(transcript_files)\} \u20491 \u36681 \u37636 \u25991 \u20214 ")\
    \
    summarizer = LLMSummarizer()\
    \
    print("\\n\uc0\u38283 \u22987 \u34389 \u29702 \u36681 \u37636 \u25991 \u20214 ...")\
    success_count, total_count = summarizer.summarize_all_files(TRANSCRIPTS_DIR)\
    \
    print(f"\\n\uc0\u34389 \u29702 \u23436 \u25104 !")\
    print(f"\uc0\u25104 \u21151 : \{success_count\} \u20491 \u25991 \u20214 ")\
    print(f"\uc0\u22833 \u25943 : \{total_count - success_count\} \u20491 \u25991 \u20214 ")\
    print(f"\uc0\u25688 \u35201 \u32080 \u26524 \u20445 \u23384 \u22312 : data/summaries/")\
\
def show_usage():\
    print("\uc0\u20351 \u29992 \u35498 \u26126 :")\
    print("1. \uc0\u23559 \u36681 \u37636 \u25991 \u26412 \u25991 \u20214 (.txt)\u25918 \u20837  data/transcripts/ \u30446 \u37636 ")\
    print("2. \uc0\u35373 \u32622 \u29872 \u22659 \u35722 \u37327  OPENROUTER_API_KEY")\
    print("3. \uc0\u36939 \u34892 : python main.py")\
    print("\\n\uc0\u29872 \u22659 \u35722 \u37327 \u35373 \u32622 \u31034 \u20363 :")\
    print("Windows cmd: set OPENROUTER_API_KEY=your_key_here")\
    print("Windows PowerShell: $env:OPENROUTER_API_KEY='your_key_here'")\
    print("Mac/Linux: export OPENROUTER_API_KEY=your_key_here")\
\
if __name__ == "__main__":\
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:\
        show_usage()\
    else:\
        main()}