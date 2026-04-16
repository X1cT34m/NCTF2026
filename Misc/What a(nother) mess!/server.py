import os
import re
import time
import random
import unicodedata
import pandas as pd
from flask import Flask, render_template_string, request, send_from_directory, jsonify, session
from faker import Faker

# ================= 配置区域 ==================
PORT = 8888
DATA_DIR = "./static"
FLAG = os.environ.get("GZCTF_FLAG", "nctf{D4ta_Aud1t_M4st3r_2026}")
NUM_RECORDS = 50000
SUBMIT_DELAY = 2 

app = Flask(__name__)
app.secret_key = os.urandom(24)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ================= 数据生成逻辑 (保持不变) ==================
fake = Faker('zh_CN')

def to_full_width(text):
    s = str(text)
    res = []
    for char in s:
        code = ord(char)
        if 33 <= code <= 126: res.append(chr(code + 65248))
        else: res.append(char)
    return "".join(res)

def inject_noise(text):
    s = str(text)
    if not s or random.random() > 0.4: return s
    idx = random.randint(0, len(s))
    noise = random.choice(['\u200b', '\u200c', '\u200d', '\uFEFF']) 
    return s[:idx] + noise + s[idx:]

def mess_phone(phone):
    style = random.choice(['clean', 'dash', 'space', 'prefix', 'prefix_dash', 'bracket'])
    if style == 'clean': return phone
    if style == 'dash': return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    if style == 'space': return f"{phone[:3]} {phone[3:7]} {phone[7:]}"
    if style == 'prefix': return f"+86{phone}"
    if style == 'prefix_dash': return f"(+86){phone[:3]}-{phone[3:]}"
    if style == 'bracket': return f"{phone[:3]}({phone[3:7]}){phone[7:]}"
    return phone

def generate_challenge_data():
    valid_prefixes = ["135", "136", "137", "138", "139", "150", "151", "152", "158", "159", "186", "188"]
    raw_data = []
    used_phones = set() 
    while len(raw_data) < NUM_RECORDS:
        if random.random() < 0.6:
            base_phone = random.choice(valid_prefixes) + "".join([str(random.randint(0,9)) for _ in range(8)])
        else:
            base_phone = re.sub(r'\D', '', fake.phone_number())
            if len(base_phone) != 11: continue
        if base_phone in used_phones: continue
        used_phones.add(base_phone)
        name = fake.name()
        if random.random() < 0.1: name = name.replace("王", "Wang").replace("李", "Li")
        real_id = fake.ssn()
        r = random.random()
        if r < 0.7: id_card = real_id
        elif r < 0.85: id_card = real_id[:-1] + ('X' if real_id[-1] != 'X' else '1')
        else: id_card = real_id + str(random.randint(0,9))
        amount = random.randint(-5000, 500000)
        amount_str = f"{amount:,}"
        if random.random() < 0.2: amount_str = f"¥{amount_str}"
        elif random.random() < 0.4: amount_str = f"{amount_str}CNY"
        final_phone = mess_phone(base_phone)
        if random.random() < 0.3: final_phone = to_full_width(final_phone)
        if random.random() < 0.3: final_phone = inject_noise(final_phone)
        if random.random() < 0.3: id_card = inject_noise(id_card)
        raw_data.append([name, id_card, final_phone, amount_str])
    df = pd.DataFrame(raw_data, columns=["Name", "ID_Card", "Phone", "Balance"])
    duplicates = df.sample(n=int(NUM_RECORDS * 0.05))
    df = pd.concat([df, duplicates]).sample(frac=1).reset_index(drop=True)
    df.to_csv(os.path.join(DATA_DIR, "customer_dump.csv"), index=False, encoding='utf-8-sig')
    rule_df = pd.DataFrame({
        "Config_Item": ["Allow_Prefix", "Min_Balance_Threshold", "ID_Standard"],
        "Value": [",".join(valid_prefixes), "0", "GB 11643-1999"]
    })
    rule_df.to_excel(os.path.join(DATA_DIR, "system_audit_logs.xlsx"), index=False)
    return df, valid_prefixes

def calculate_standards(df, valid_prefixes):
    def clean_txt(t):
        if pd.isna(t): return ""
        t = unicodedata.normalize('NFKC', str(t))
        for c in ['\u200b', '\u200c', '\u200d', '\uFEFF']: t = t.replace(c, '')
        return t.strip()
    for col in df.columns: df[col] = df[col].apply(clean_txt)
    df = df.drop_duplicates()
    def is_valid_p(p):
        d = re.sub(r'\D', '', p)
        if len(d) == 13 and d.startswith('86'): d = d[2:]
        return d if len(d) == 11 and d[:3] in valid_prefixes else None
    df['cp'] = df['Phone'].apply(is_valid_p)
    q1 = int(df['cp'].notna().sum())
    def is_valid_id(id_val):
        if len(id_val) != 18 or not re.match(r'^\d{17}[\dX]$', id_val): return False
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        maps = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        try:
            s = sum(int(id_val[i]) * factors[i] for i in range(17))
            return maps[s % 11] == id_val[-1]
        except: return False
    df['cid'] = df['ID_Card'].apply(is_valid_id)
    q2 = int(df['cid'].sum())
    df['both'] = df['cp'].notna() & df['cid']
    q3 = int(df['both'].sum())
    target = df[df['both']].copy()
    def parse_bal(b):
        try: return float(re.sub(r'[^\d.-]', '', b))
        except: return 0.0
    target['cb'] = target['Balance'].apply(parse_bal)
    q4 = round(target[target['cb'] > 0]['cb'].sum(), 2)
    q5 = int(target['Name'].apply(lambda n: n.startswith('李') or n.lower().startswith('li')).sum())
    return [str(q1), str(q2), str(q3), f"{q4:.2f}", str(q5)]

dirty_df, prefixes = generate_challenge_data()
ANSWERS = calculate_standards(dirty_df.copy(), prefixes)

# ================= Web 界面美化版 ==================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audit Challenge - Data Cleaner</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background-color: #0d1117; 
            color: #c9d1d9; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; 
        }
        .challenge-container { 
            max-width: 900px; 
            margin: 40px auto; 
            background: #161b22; 
            padding: 40px; 
            border-radius: 12px; 
            border: 1px solid #30363d; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.4); 
        }
        .header-title { 
            color: #58a6ff; 
            font-weight: 800; 
            border-bottom: 1px solid #30363d; 
            padding-bottom: 15px; 
            margin-bottom: 30px; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .card { 
            background: #0d1117; 
            border: 1px solid #30363d; 
            border-left: 4px solid #1f6feb; /* 蓝色左边框增强辨识度 */
            margin-bottom: 20px; 
            transition: transform 0.2s;
        }
        .card:hover { border-color: #58a6ff; }
        
        /* 关键修改：增强问题文字的可读性 */
        .question-text { 
            color: #ffffff; /* 纯白文字 */
            font-size: 1.1rem; 
            font-weight: 600; 
            margin-bottom: 12px;
            display: block;
            line-height: 1.5;
        }
        
        .download-zone { 
            background: #161b22; 
            border: 1px dashed #30363d;
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
        }
        .btn-primary { background-color: #238636; border: none; font-weight: 600; }
        .btn-primary:hover { background-color: #2ea043; }
        .btn-outline-info { color: #58a6ff; border-color: #58a6ff; }
        
        .flag-box { 
            background: rgba(35, 134, 54, 0.1); 
            border: 2px solid #238636; 
            color: #3fb950; 
            padding: 20px; 
            border-radius: 8px; 
            display: none; 
            margin-top: 30px; 
            font-family: 'Courier New', Courier, monospace;
            font-size: 1.2rem;
        }
        input.form-control { 
            background: #0d1117; 
            border: 1px solid #30363d; 
            color: #f0f6fc; 
        }
        input.form-control:focus { 
            background: #0d1117; 
            color: #fff; 
            border-color: #58a6ff; 
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.3); 
        }
        .loading { display: none; color: #8b949e; }
    </style>
</head>
<body>

<div class="container">
    <div class="challenge-container">
        <h2 class="header-title">🛡️ 内部审计数据校验系统</h2>
        
        <div class="download-zone">
            <h5 class="text-info mb-3">STEP 1: 获取审计数据包</h5>
            <p class="small text-secondary">系统已自动导出 50,000 条加噪记录，请下载并进行合规性清理：</p>
            <div class="d-flex gap-2">
                <a href="/download/customer_dump.csv" class="btn btn-sm btn-outline-info">💾 下载数据明细 (CSV)</a>
                <a href="/download/system_audit_logs.xlsx" class="btn btn-sm btn-outline-info">📜 查看审计规则 (XLSX)</a>
            </div>
        </div>

        <h5 class="mb-4">STEP 2: 提交校验结果</h5>
        <div id="questions">
            {% for i in range(5) %}
            <div class="card p-3 shadow-sm" id="card-{{ i }}">
                <span class="question-text">{{ titles[i] }}</span>
                <div class="input-group">
                    <input type="text" class="form-control" id="ans-{{ i }}" placeholder="等待输入数值...">
                    <button class="btn btn-primary" onclick="submitAnswer({{ i }})">验证</button>
                </div>
                <div id="msg-{{ i }}" class="mt-2 small"></div>
            </div>
            {% endfor %}
        </div>

        <div id="flag-container" class="flag-box text-center">
            <strong>✅ 审计任务完成！</strong><br>
            <span class="small">系统授权码：</span><br>
            <span id="flag-text" style="word-break: break-all;"></span>
        </div>
        
        <p class="text-center mt-4 loading" id="global-loader">⏳ 正在比对哈希值，请稍候...</p>
    </div>
</div>

<script>
    let solved = [false, false, false, false, false];

    async function submitAnswer(index) {
        const val = document.getElementById(`ans-${index}`).value.trim();
        const msgDiv = document.getElementById(`msg-${index}`);
        const loader = document.getElementById('global-loader');
        
        if(!val) return;
        loader.style.display = 'block';
        msgDiv.innerHTML = "";

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ index: index, answer: val })
            });
            const data = await response.json();
            loader.style.display = 'none';

            if (data.status === 'correct') {
                msgDiv.innerHTML = '<span class="text-success">✔ 校验通过</span>';
                document.getElementById(`ans-${index}`).disabled = true;
                document.getElementById(`card-${index}`).style.borderLeftColor = '#238636';
                solved[index] = true;
                checkAllSolved(data.flag);
            } else if (data.status === 'too_fast') {
                msgDiv.innerHTML = `<span class="text-warning">⚠ 访问受限，请等待 ${data.wait}s</span>`;
            } else {
                msgDiv.innerHTML = '<span class="text-danger">✘ 校验失败，请重新检查清洗逻辑</span>';
            }
        } catch (e) {
            loader.style.display = 'none';
            alert("通信异常，请检查网络");
        }
    }

    function checkAllSolved(flag) {
        if (solved.every(v => v === true)) {
            const flagBox = document.getElementById('flag-container');
            document.getElementById('flag-text').innerText = flag;
            flagBox.style.display = 'block';
            flagBox.scrollIntoView({ behavior: 'smooth' });
        }
    }
</script>

</body>
</html>
"""

TITLES = [
    "Q1. 经过清洗去重后，剩余多少个符合白名单号段的有效手机号？",
    "Q2. 数据集中共有多少个身份证校验位（第18位）计算正确的记录？",
    "Q3. 同时满足Q1和Q2的记录有多少条？",
    "Q4. 针对上述Q3的用户，统计其账户余额的总和（忽略负数，保留两位小数）。",
    "Q5. 在Q3的用户中，姓名为“李”姓（含汉字“李”和拼音“Li/li”）的人数是多少？"
]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, titles=TITLES)

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(DATA_DIR, filename)

@app.route('/submit', methods=['POST'])
def submit():
    last_time = session.get('last_submit', 0)
    current_time = time.time()
    if current_time - last_time < SUBMIT_DELAY:
        return jsonify({'status': 'too_fast', 'wait': round(SUBMIT_DELAY - (current_time - last_time), 1)})
    session['last_submit'] = current_time
    time.sleep(1) 
    
    data = request.json
    try:
        idx = int(data.get('index'))
    except (TypeError, ValueError):
        return jsonify({'status': 'wrong', 'flag': ""})
        
    user_ans = str(data.get('answer', '')).strip()
    correct = False
    
    if idx == 3:
        try: correct = abs(float(user_ans) - float(ANSWERS[3])) < 0.1
        except: pass
    elif 0 <= idx < len(ANSWERS):
        correct = (user_ans == ANSWERS[idx])
    if 'solved_indices' not in session:
        session['solved_indices'] = []   
    solved_list = session['solved_indices']
    if correct and idx not in solved_list:
        solved_list.append(idx)
        session['solved_indices'] = solved_list 
    is_all_solved = (len(session['solved_indices']) == len(ANSWERS))
    return jsonify({
        'status': 'correct' if correct else 'wrong', 
        'flag': FLAG if is_all_solved else "" 
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)