import pandas as pd
import unicodedata
import re

INPUT_CSV = "customer_dump.csv"
INPUT_XLSX = "system_audit_logs.xlsx"

def clean_text_basic(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = unicodedata.normalize('NFKC', text)
    zero_width_chars = ['\u200b', '\u200c', '\u200d', '\uFEFF']
    for char in zero_width_chars:
        text = text.replace(char, '')
        
    return text.strip()

def extract_valid_phone(phone_str, whitelist_prefixes):
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) == 13 and digits.startswith('86'):
        digits = digits[2:]
    if len(digits) != 11:
        return None
    prefix = digits[:3]
    if prefix in whitelist_prefixes:
        return digits
    
    return None

def check_id_card(id_card):
    if len(id_card) != 18:
        return False
    if not re.match(r'^\d{17}[\dX]$', id_card):
        return False
    factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_map = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    try:
        total_sum = 0
        for i in range(17):
            total_sum += int(id_card[i]) * factors[i]
        
        remainder = total_sum % 11
        expected_code = check_map[remainder]
        
        return expected_code == id_card[-1].upper()
    except:
        return False

def parse_balance(balance_str):
    clean_num = re.sub(r'[^\d.-]', '', balance_str)
    try:
        return float(clean_num)
    except ValueError:
        return 0.0

def is_surname_li(name):
    if not name: return False
    if name.startswith('李'):
        return True
    if name.lower().startswith('li'):
        return True
    return False

def main():
    print("[-] 正在加载数据与规则...")
    try:
        rules_df = pd.read_excel(INPUT_XLSX, sheet_name='Sheet1')
        # 提取 Allow_Prefix，通常是字符串 "135,136..."
        prefix_rule = rules_df.loc[rules_df['Config_Item'] == 'Allow_Prefix', 'Value'].values[0]
        valid_prefixes = [x.strip() for x in str(prefix_rule).split(',')]
        print(f"[-] 加载白名单号段: {len(valid_prefixes)} 个")
    except Exception as e:
        print(f"[!] 读取Excel规则失败: {e}")
        return
    df = pd.read_csv(INPUT_CSV)
    original_count = len(df)
    print("[-] 执行全角转半角、去除零宽字符...")
    for col in df.columns:
        df[col] = df[col].apply(clean_text_basic)
    print("[-] 执行数据去重...")
    df.drop_duplicates(inplace=True)
    dedup_count = len(df)
    print(f"[-] 数据量变化: {original_count} -> {dedup_count} (剔除重复: {original_count - dedup_count})")
    df['clean_phone'] = df['Phone'].apply(lambda x: extract_valid_phone(x, valid_prefixes))
    df['is_valid_phone'] = df['clean_phone'].notna()
    q1_ans = df['is_valid_phone'].sum()
    df['is_valid_id'] = df['ID_Card'].apply(check_id_card)
    q2_ans = df['is_valid_id'].sum()
    df['is_valid_both'] = df['is_valid_phone'] & df['is_valid_id']
    q3_ans = df['is_valid_both'].sum()
    target_users = df[df['is_valid_both']].copy()
    target_users['clean_balance'] = target_users['Balance'].apply(parse_balance)
    q4_ans = target_users[target_users['clean_balance'] > 0]['clean_balance'].sum()
    q5_ans = target_users['Name'].apply(is_surname_li).sum()
    print("\n" + "="*30)
    print("       分析结果报告       ")
    print("="*30)
    print(f"Q1. 符合白名单的有效手机号数量:  {q1_ans}")
    print(f"Q2. 身份证校验位正确的记录数:    {q2_ans}")
    print(f"Q3. 同时满足Q1和Q2的记录数:      {q3_ans}")
    print(f"Q4. Q3用户的正资产余额总和:      {q4_ans:,.2f}")
    print(f"Q5. Q3用户中'李'姓(含Li)人数:    {q5_ans}")
    print("="*30)

if __name__ == "__main__":
    main()