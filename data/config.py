{\rtf1\ansi\ansicpg950\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww12760\viewh13560\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
\
BASE_DIR = os.path.dirname(os.path.abspath(__file__))\
\
DATA_DIR = os.path.join(BASE_DIR, "data")\
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")\
SUMMARIES_DIR = os.path.join(DATA_DIR, "summaries")\
\
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")\
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"\
\
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"\
\
for directory in [TRANSCRIPTS_DIR, SUMMARIES_DIR]:\
    os.makedirs(directory, exist_ok=True)}