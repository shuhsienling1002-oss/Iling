import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="O Lisin - 部落祭儀", 
    page_icon="🔥", 
    layout="centered"
)

# --- 1. 資料庫 (第 11 課：O Lisin no Niyaro') ---
VOCAB_MAP = {
    "ilisin": "豐年祭", "ma'araw": "被看見", "niyam": "我們(排除式)", 
    "'icel": "力量", "kapah": "青年/勇士", "lotok": "山", 
    "riyar": "海", "palemed": "祝福", "kawas": "神靈/靈", 
    "mana": "為何", "tayni": "來這裡", "haca": "竟然/還", 
    "foting": "魚", "nawhani": "因為", "awaay": "沒有", 
    "milifetay": "挑戰/勝過", "riting": "海神祭儀/禁忌", "mato'asay": "長老/老人", 
    "mihomon": "敬重/祭拜", "to'as": "祖靈/祖先", "si'enaw": "冷", 
    "romi'ad": "日子/天氣", "kawra": "但是", "fa'inayan": "男人/男性", 
    "pangcah": "阿美族(自稱)", "caay": "不", "katalaw": "害怕", 
    "saheto": "全部/都是", "mila'dis": "捕魚祭/儀式捕魚", "lekakawa": "傳統/規範"
}

VOCABULARY = [
    {"amis": "Ilisin", "zh": "豐年祭", "emoji": "🔥", "root": "lisin", "root_zh": "祭儀"},
    {"amis": "kapah", "zh": "青年/年齡階級", "emoji": "💪", "root": "kapah", "root_zh": "年輕"},
    {"amis": "kawas", "zh": "神靈/靈", "emoji": "✨", "root": "kawas", "root_zh": "靈"},
    {"amis": "riting", "zh": "祭儀規範/海神禁忌", "emoji": "🌊", "root": "riting", "root_zh": "神力"},
    {"amis": "mila'dis", "zh": "舉行捕魚祭", "emoji": "🐟", "root": "la'dis", "root_zh": "捕魚儀式"},
    {"amis": "mato'asay", "zh": "長老/老人", "emoji": "👴", "root": "to'as", "root_zh": "老/祖先"},
    {"amis": "lekakawa", "zh": "傳統/規範", "emoji": "📜", "root": "kawa", "root_zh": "規矩"},
    {"amis": "palemed", "zh": "祝福", "emoji": "🙏", "root": "lemed", "root_zh": "福氣"},
    {"amis": "fa'inayan", "zh": "男人", "emoji": "👨", "root": "fa'inay", "root_zh": "男"},
    {"amis": "si'enaw", "zh": "寒冷", "emoji": "❄️", "root": "si'enaw", "root_zh": "冷"},
]

SENTENCES = [
    {
        "amis": "I Ilisin i, ma'araw niyam ko 'icel no kapah.", 
        "zh": "在豐年祭時，我們看見了青年的力量。", 
        "note": """
        <br><b>Ilisin</b>：豐年祭 (年度最重要的祭典)。
        <br><b>kapah</b>：青年階級。阿美族是年齡階級社會，<i>kapah</i> 是部落的中堅力量，負責護衛與勞動。"""
    },
    {
        "amis": "I lotok, i riyar, maemin o palemed no kawas.", 
        "zh": "在山裡、在海裡，全部都是神靈的祝福。", 
        "note": """
        <br><b>maemin</b>：全部/所有。
        <br><b>palemed</b>：祝福 (來自詞根 <i>lemed</i> 好運)。
        <br><b>kawas</b>：泛指神、鬼、靈。阿美族相信萬物有靈。"""
    },
    {
        "amis": "Nawhani awaay ko milifetay to riting no mato'asay.", 
        "zh": "因為沒有人敢挑戰長老的規範(禁忌)。", 
        "note": """
        <br><b>Nawhani</b>：因為 (連接詞)。
        <br><b>milifetay</b>：挑戰者/勝過者。
        <br><b>riting</b>：特指與海神、捕魚相關的嚴格禁忌或神力。"""
    },
    {
        "amis": "Saheto o fa'inayan ko tayni-ay a mila'dis.", 
        "zh": "來這裡進行捕魚祭的，全都是男人。", 
        "note": """
        <br><b>Saheto</b>：全部都是 (強調一致性)。
        <br><b>mila'dis</b>：捕魚祭。這不是普通的捕魚，而是祭典結束後的儀式性捕魚，通常女性不能參加。"""
    },
    {
        "amis": "Tada fangcal ko nini a lekakawa.", 
        "zh": "這傳統規範是非常美好的。", 
        "note": """
        <br><b>lekakawa</b>：指成套的規矩、傳統、制度。
        <br><b>fangcal</b>：這裡指文化上的「美好/崇高」。"""
    }
]

STORY_DATA = [
    {"amis": "I Ilisin i, ma'araw niyam ko 'icel no kapah.", "zh": "在豐年祭時，我們看見了青年的力量。"},
    {"amis": "I lotok, i riyar, maemin o palemed no kawas.", "zh": "在山裡、在海裡，全部都是神靈的祝福。"},
    {"amis": "Mana tayni haca ko foting i riyar?", "zh": "為何魚群竟然會來到海裡？"},
    {"amis": "Nawhani awaay ko milifetay to riting no mato'asay.", "zh": "因為沒有人敢挑戰長老的規範(禁忌)。"},
    {"amis": "Mihomon kita to riting, mihomon kita to to'as.", "zh": "我們敬重禁忌，我們祭拜祖靈。"},
    {"amis": "Tada si'enaw-ay ko romi'ad i lotok.", "zh": "山裡的日子非常寒冷。"},
    {"amis": "Kawra o fa'inayan no Pangcah i, caay katalaw to si'enaw.", "zh": "但是阿美族的男人，是不怕冷的。"},
    {"amis": "Saheto o fa'inayan ko tayni-ay a mila'dis.", "zh": "來這裡進行捕魚祭的，全都是男人。"},
    {"amis": "Tada fangcal ko nini a lekakawa.", "zh": "這傳統規範是非常美好的。"}
]

# --- 2. 視覺系統 (CSS 注入 - 祭儀紅主題) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
.stApp { background-color: #FFEBEE; color: #B71C1C; font-family: 'Noto Sans TC', sans-serif; }
.stTabs [data-baseweb="tab"] { color: #D32F2F !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-size: 18px; font-weight: 700; }
.stTabs [aria-selected="true"] { border-bottom: 4px solid #B71C1C !important; color: #B71C1C !important; }
.stButton>button { border: 2px solid #B71C1C !important; background: #FFFFFF !important; color: #B71C1C !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif !important; font-size: 18px !important; font-weight: 700 !important; width: 100%; border-radius: 12px; }
.stButton>button:hover { background: #B71C1C !important; color: #FFFFFF !important; }
.quiz-card { background: #FFFFFF; border: 2px solid #EF9A9A; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
.quiz-tag { background: #880E4F; color: #FFF; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 14px; margin-right: 10px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }
.zh-translation-block { background: #FFCDD2; border-left: 5px solid #B71C1C; padding: 20px; color: #880E4F; font-size: 16px; line-height: 2.0; font-family: 'Noto Sans TC', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #B71C1C; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 2px solid #D32F2F; cursor: pointer; margin: 0 3px; color: #B71C1C; transition: 0.3s; font-size: 19px; font-weight: 600; }}
        .interactive-word:hover {{ color: #FF5252; border-bottom-color: #FF5252; }}
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #B71C1C; color: #FFF; text-align: center; border-radius: 8px; padding: 8px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-weight: 700; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        .play-btn-inline {{ background: #D32F2F; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #B71C1C; transform: scale(1.1); }}
        .word-card-static {{ background: #FFFFFF; border: 1px solid #EF9A9A; border-left: 6px solid #B71C1C; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; box-shadow: 0 3px 6px rgba(0,0,0,0.05); }}
        .wc-root-tag {{ font-size: 12px; background: #FFEBEE; color: #B71C1C; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }}
        .wc-amis {{ color: #B71C1C; font-size: 26px; font-weight: 900; margin: 2px 0; font-family: 'Nunito', sans-serif; }}
        .wc-zh {{ color: #880E4F; font-size: 16px; font-weight: 500; }}
        .play-btn-large {{ background: #FFEBEE; border: 2px solid #B71C1C; color: #B71C1C; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #B71C1C; color: #FFF; }}
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#757575;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#B71C1C; border:none; color:#FFF; padding:6px 15px; border-radius:8px; cursor:pointer; font-family:Nunito; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#B71C1C'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#B71C1C'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["lisin", "kapah", "kawas"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#B71C1C'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#B71C1C'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#B71C1C; font-size:18px;'>{q_text}</span><br><span style='color:#5D4037; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 主題：祭儀紅 (Ritual Red) - 莊嚴、傳統、熱情
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@900&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; }
        .container {
            background: linear-gradient(180deg, #B71C1C 0%, #880E4F 100%);
            border-bottom: 6px solid #5D4037;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            color: #FFFFFF; /* 強制白色 */
        }
        h1 {
            font-family: 'Nunito', sans-serif;
            color: #FFFFFF !important; /* 強制白色 */
            font-size: 48px;
            margin: 0 0 10px 0;
            text-shadow: 3px 3px 0 #000000;
            letter-spacing: 2px;
        }
        .subtitle {
            color: #FFCDD2; /* 亮粉紅/淺紅 */
            border: 1px solid #FFCDD2;
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            padding: 5px 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 18px;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #FFEBEE;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>O Lisin</h1>
        <div class="subtitle">第 11 課：部落祭儀</div>
        <div class="footer">Code-CRF v6.5 | Theme: Ritual Red (Culture)</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=220)

tab1, tab2, tab3, tab4 = st.tabs([
    "🔥 互動課文", 
    "📜 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#FFFFFF; padding:10px; border: 2px solid #EF9A9A; border-radius:12px;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:15px; border:1px dashed #B71C1C; border-radius: 12px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#B71C1C; font-size:16px; margin-bottom:10px; border-top:1px solid #EF9A9A; padding-top:10px;">{s['zh']}</div>
        <div style="color:#D32F2F; font-size:14px; line-height:1.8; border-top:1px dashed #EF9A9A; padding-top:5px;"><span style="color:#B71C1C; font-family:Nunito; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#5D4037;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#B71C1C; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #B71C1C; border-radius:15px; background:#FFFFFF;"><h2 style="color:#B71C1C; font-family:Nunito;">MISSION COMPLETE</h2><p style="font-size:20px; color:#D32F2F;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.5 | Architecture: Chief Architect")
