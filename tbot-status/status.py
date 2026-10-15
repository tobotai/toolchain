#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tbot-status · Tbot 底盘状态监控命令行工具

基于 ROS over WebSocket (rosbridge) 实时读取底盘状态：
电量、充电状态、定位位姿、导航到达状态、路径点数量。

依赖: pip install roslibpy

用法:
  python status.py --ip 192.168.1.151                  # 实时循环监控（Ctrl+C 退出）
  python status.py --ip 192.168.1.151 --once           # 打印一次后退出
  python status.py --ip 192.168.1.151 --interval 2     # 每 2 秒刷新
  python status.py --ip 192.168.1.151 --once --json    # JSON 输出，供脚本/监控平台集成
"""
import argparse, json, math, sys, time

import roslibpy


class TbotStatus:
    def __init__(self, client):
        self.state = {
            'battery': None, 'charging': None,
            'x': None, 'y': None, 'yaw': None,
            'arrived': None, 'path_pts': None,
            'connected': False,
        }
        self._subs = []
        self._subscribe(client)

    def _subscribe(self, client):
        def on_work(m):
            d = m['data']
            self.state['battery'] = float(d[1])
            self.state['charging'] = int(d[0]) == 1

        def on_odom(m):
            p = m['pose']['pose']['position']
            o = m['pose']['pose']['orientation']
            yaw = math.atan2(2 * (o['w'] * o['z'] + o['x'] * o['y']), 1 - 2 * (o['z'] ** 2 + o['y'] ** 2))
            self.state['x'], self.state['y'], self.state['yaw'] = float(p['x']), float(p['y']), yaw

        def on_nav(m):
            self.state['arrived'] = int(m['data'][0]) == 1

        def on_path(m):
            self.state['path_pts'] = len(m.get('poses', []))

        for topic, mtype, fn in [
            ('/ebot_work_state', 'std_msgs/Float64MultiArray', on_work),
            ('/fast_lio_localization', 'nav_msgs/Odometry', on_odom),
            ('/ebot_goal_status_local_planner', 'std_msgs/Float64MultiArray', on_nav),
            ('/aft_pgo_path', 'nav_msgs/Path', on_path),
        ]:
            self._subs.append(roslibpy.Topic(client, topic, mtype))
            self._subs[-1].subscribe(fn)

    def close(self):
        for s in self._subs:
            s.unsubscribe()

    def snapshot(self):
        return dict(self.state)


def build_client(ip, port=9090):
    client = roslibpy.Ros(host=ip, port=port)
    client.run()
    t0 = time.time()
    while not client.is_connected:
        if time.time() - t0 > 8:
            raise RuntimeError(f"无法连接到 {ip}:{port}，请检查 IP/网络/固件")
        time.sleep(0.1)
    return client


def render(s):
    s['connected'] = True
    s['yaw_deg'] = None if s['yaw'] is None else math.degrees(s['yaw'])
    s['charging_txt'] = {True: '充电中', False: '未充电', None: '--'}[s['charging']]
    s['arrived_txt'] = {True: '✅ 已到达', False: '导航中/未到达', None: '--'}[s['arrived']]
    s['pose_txt'] = (f"x={s['x']:.2f}  y={s['y']:.2f}  yaw={s['yaw_deg']:.1f}°"
                     if s['x'] is not None else '--')
    s['batt_txt'] = f"{s['battery']:.1f}%" if s['battery'] is not None else '--'
    s['path_txt'] = str(s['path_pts']) if s['path_pts'] is not None else '--'
    return s


def print_once(s):
    r = render(s)
    print('┌────────────────────────────────────────')
    print('│  Tbot 底盘状态  (ROS over WebSocket)')
    print('├────────────────────────────────────────')
    print(f'│  电量    {r["batt_txt"]:<8} 状态: {r["charging_txt"]}')
    print(f'│  定位    {r["pose_txt"]}')
    print(f'│  导航    {r["arrived_txt"]}')
    print(f'│  路径点  {r["path_txt"]} 个')
    print('└────────────────────────────────────────')


def main():
    ap = argparse.ArgumentParser(description='Tbot 底盘状态监控 CLI')
    ap.add_argument('--ip', required=True, help='机器人 IP，如 192.168.1.151')
    ap.add_argument('--port', type=int, default=9090)
    ap.add_argument('--once', action='store_true', help='打印一次后退出')
    ap.add_argument('--interval', type=float, default=1.0, help='刷新间隔（秒）')
    ap.add_argument('--json', action='store_true', help='JSON 输出（供脚本集成）')
    a = ap.parse_args()

    client = build_client(a.ip, a.port)
    st = TbotStatus(client)
    try:
        time.sleep(0.5)  # 等待首批消息
        if a.json or a.once:
            snap = st.snapshot()
            print(json.dumps(render(snap), ensure_ascii=False, indent=2) if a.json else '')
            if a.once:
                if not a.json:
                    print_once(snap)
                return
        print(f"[监控中] {a.ip}:{a.port}  Ctrl+C 退出\n")
        while True:
            print_once(st.snapshot())
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print('\n已退出')
    finally:
        st.close()
        client.terminate()


if __name__ == '__main__':
    main()
