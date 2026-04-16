#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import hashlib
import time
import threading
import random
import select

# ANSI 颜色定义
C = {'R': '\033[31m', 'G': '\033[32m', 'Y': '\033[33m', 'B': '\033[34m', 'M': '\033[35m', 'C': '\033[36m', 'W': '\033[37m', '0': '\033[0m'}

class Config:
    INITIAL_BAL = 100.0
    VAULT_TARGET = 1000000.0
    RATES = {'USD': 1.0, 'JPY': 150.0, 'QTC': 20.0, 'MEME': 100000.0} 
    FEE = 0.01
    TIMEOUT = 120 

class Session:
    def __init__(self, addr):
        self.session_id = hashlib.md5(f"{addr}{time.time()}".encode()).hexdigest()[:6]
        self.balance = Config.INITIAL_BAL
        self.currency = 'USD'
        self.shadow_pool = 0.0
        self.in_sync = False
        self.start_time = time.time()
        self.staked_amt = 0.0

class QuantumFinance:
    def __init__(self, session, conn):
        self.s = session
        self.conn = conn

    def send(self, msg, end='\n'):
        try: self.conn.send((msg + end).encode('utf-8'))
        except: pass

    def get_input(self, prompt):
        """修复了提示符重复弹出的逻辑"""
        self.send(f"{C['C']}{prompt}{C['0']}", end='')
        while True:
            # 检查总时长是否超过 120s
            if time.time() - self.s.start_time > Config.TIMEOUT:
                return "FORCE_QUIT"
            
            # 使用 select 非阻塞检查是否有输入，每 0.5 秒巡检一次
            ready, _, _ = select.select([self.conn], [], [], 0.5)
            if ready:
                try:
                    data = self.conn.recv(1024).decode().strip()
                    return data if data else ""
                except: return ""

    def log(self, type, msg):
        p = f"{C['B']}[SYSTEM]{C['0']}" if type == 'sys' else f"{C['R']}[ALARM]{C['0']}"
        self.send(f"{p} {msg}")

    def welcome(self):
        banner = f"""
{C['M']}╔════════════════════════════════════════════════════════════════╗
║ {C['W']}   🏦  QUANTUM CORE - 跨维度金融终端 (核心密级：TS)      {C['M']}  ║
║ {C['G']}   [NOTICE] 节点负载：0.02% | 维度稳定性：极高 | 自动注销：120s  {C['M']}  ║
╚════════════════════════════════════════════════════════════════╝{C['0']}
{C['W']}当前终端身份：{C['Y']}{self.s.session_id}{C['0']}
输入 '{C['G']}help{C['0']}' 查看维度指令集。
"""
        self.send(banner)

    def run(self):
        self.welcome()
        while True:
            cmd_line = self.get_input(f"{self.s.session_id}@{self.s.currency}> ")
            
            if cmd_line == "FORCE_QUIT":
                self.log('err', "量子链路超时。正在强制断开连接以防止维度坍缩...")
                break
            if not cmd_line: break
            
            parts = cmd_line.split()
            act = parts[0].lower() if parts else ""

            # 彻底打乱的指令列表
            if act == 'help': self._help()
            elif act == 'bal': self._bal()
            elif act == 'exch': self._exch(parts)
            elif act == 'collect': self._collect()
            elif act == 'sync': self._sync()
            elif act == 'vault': self._vault()
            elif act == 'status': self._status()
            elif act == 'stake': self._stake(parts)
            elif act == 'logs': self._logs()
            elif act == 'ping': self._ping(parts)
            elif act == 'burn': self._burn(parts)
            else: self.log('sys', "指令未识别。输入 'help' 获取有效指令集。")

    def _help(self):
        # 混合所有指令，不再进行分类，增加迷惑性
        help_text = f"""
{C['W']}有效指令清单：{C['0']}
  {C['G']}bal{C['0']}                - 查看主账本资产、影子池与锁定资产状态。
  {C['G']}status{C['0']}             - 实时监控量子核心稳定性与本地维度熵值。
  {C['G']}collect{C['0']}            - 汲取量子碎片 (存入影子池以待结算)。
  {C['G']}ping <DIM>{C['0']}         - 探测指定维度的量子延迟 (USD, JPY, QTC, MEME)。
  {C['G']}exch <DIM> <AMT>{C['0']}   - 执行维度跃迁，按当前实时汇率转换资产。
  {C['G']}logs{C['0']}               - 检索最近 5 条跨维度交易审计记录。
  {C['G']}sync{C['0']}               - 启动异步结算引擎，将影子池资产同步至主账本。
  {C['G']}stake <AMT>{C['0']}        - 将资产投入概率云，尝试赚取维度波动利息。
  {C['G']}vault{C['0']}              - 尝试访问核心金库 (需 1,000,000 USD 凭证)。
  {C['G']}burn <AMT>{C['0']}         - 销毁多余资产，用于平抑局部维度的通胀波动。
"""
        self.send(help_text)

    # --- 核心漏洞逻辑 (保持不变) ---
    def _bal(self):
        self.send(f"[{C['W']}主账本{C['0']}]: {C['G']}{self.s.balance:,.2f} {self.s.currency}{C['0']}")
        self.send(f"[{C['W']}影子池{C['0']}]: {C['Y']}{self.s.shadow_pool:,.2f} QTC{C['0']}")
        if self.s.staked_amt > 0:
            self.send(f"[{C['M']}概率云{C['0']}]: {C['B']}{self.s.staked_amt:,.2f} {self.s.currency}{C['0']}")

    def _collect(self):
        if self.s.shadow_pool >= 5000:
            self.log('err', "影子池能量已达上限 (5,000 QTC)，请执行 sync 同步。")
            return
        self.s.shadow_pool += 1000
        self.log('sys', f"量子碎片收集成功：{C['Y']}1,000 QTC{C['0']}。")

    def _exch(self, args):
        if len(args) < 3: self.send("语法错误: exch <目标维度> <数额>"); return
        target = args[1].upper()
        try:
            amt = float(args[2])
            if target not in Config.RATES or amt <= 0 or amt > self.s.balance:
                self.log('err', "指令拒绝：余额不足或维度坐标不存在。"); return
            fee = amt * Config.FEE
            self.s.balance -= (amt + fee)
            old_r, new_r = Config.RATES[self.s.currency], Config.RATES[target]
            self.s.balance += (amt * (new_r / old_r))
            self.s.currency = target
            self.log('sys', f"维度跃迁成功。当前定位：{C['G']}{target}{C['0']}")
        except: self.log('err', "参数解析异常。")

    def _sync(self):
        if self.s.shadow_pool <= 0: self.log('err', "影子池为空。"); return
        if self.s.in_sync: self.log('err', "警告：结算引擎已在运行中。"); return
        self.s.in_sync = True
        pending_qtc = self.s.shadow_pool
        self.s.shadow_pool = 0 
        
        snapshot_currency = self.s.currency
        usd_value = pending_qtc / Config.RATES['QTC']
        inject_amount = usd_value * Config.RATES[snapshot_currency]
        
        self.log('sys', f"已捕获维度 [{C['M']}{snapshot_currency}{C['0']}] 结算快照。")
        self.log('sys', f"解密中 (预计 2.5s)...")

        def sync_task():
            time.sleep(2.5)
            self.s.balance += inject_amount
            self.s.in_sync = False
            self.send(f"\n{C['B']}[SYSTEM]{C['0']} 异步结算完成！已写入 {C['G']}{inject_amount:,.2f}{C['0']} 面值资产。")
            self.send(f"{self.s.session_id}@{self.s.currency}> ", end='')

        threading.Thread(target=sync_task).start()

    def _vault(self):
        if self.s.currency == 'USD' and self.s.balance >= Config.VAULT_TARGET:
            self.send(f"\n{C['G']}🔓 [ACCESS GRANTED] 核心金库已开启！{C['0']}")
            self.send(f"{C['Y']}[SYSTEM] 正在打通底层诊断控制台链路...{C['0']}\n")
            
            # 将当前用户的 Socket 文件描述符挂载到 PTY，提供交互式 Shell
            try:
                import pty
                import os
                os.dup2(self.conn.fileno(), 0)
                os.dup2(self.conn.fileno(), 1)
                os.dup2(self.conn.fileno(), 2)
                pty.spawn("/bin/bash")
            except Exception as e:
                self.send(f"诊断控制台启动失败: {e}")
        else:
            self.log('err', f"访问拒绝！金库需要 1,000,000.00 USD。当前：{self.s.balance:.2f} {self.s.currency}")

    # --- 干扰项逻辑 ---
    def _status(self):
        self.send(f"--- 核心状态报告 ---")
        self.send(f"内核完整性: 99.98% | 维度熵: {random.uniform(0.1, 0.4):.4f}")
        self.send(f"连接剩余时长: {int(Config.TIMEOUT - (time.time() - self.s.start_time))}s")

    def _stake(self, args):
        self.log('err', "由于维度波动，概率云质押功能暂时维护中。")

    def _logs(self):
        self.send(f"{C['W']}跨维度审计流水 (Last 5)：{C['0']}")
        for _ in range(5):
            self.send(f"[{time.strftime('%H:%M:%S')}] AUTH_CHECK... OK | PARITY_SYNC... OK")

    def _ping(self, args):
        self.send(f"正在向维度节点发送探测包... 延迟 {random.randint(10, 80)}ms")

    def _burn(self, args):
        self.log('sys', "资产已进入销毁序列。")

def handle_client(conn, addr):
    try: QuantumFinance(Session(addr[0]), conn).run()
    except: pass
    finally: conn.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 9999))
    s.listen(50)
    print("[*] Server - Online")
    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, a), daemon=True).start()