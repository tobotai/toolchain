#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tbot-maps · Tbot 地图管理命令行工具

基于 ROS over WebSocket (rosbridge) 管理 Tbot 底盘地图：
列出地图、开始建图、保存地图、选择地图并启动导航、删除地图。

依赖: pip install roslibpy

用法:
  python maps.py --ip 192.168.1.151 list                      # 列出地图与目标点
  python maps.py --ip 192.168.1.151 start-mapping            # 开始建图
  python maps.py --ip 192.168.1.151 save --map office        # 保存当前地图为 office
  python maps.py --ip 192.168.1.151 select --map office      # 选择地图并启动导航
  python maps.py --ip 192.168.1.151 delete --map office      # 删除地图（需先停止导航）
  python maps.py --ip 192.168.1.151 add-goal --map office --name "电梯口" --x 1.0 --y 2.0 --theta 0.5
  python maps.py --ip 192.168.1.151 del-goal  --map office --name "电梯口"
"""
import argparse, json, sys, time

import roslibpy


def build_client(ip, port=9090):
    client = roslibpy.Ros(host=ip, port=port)
    client.run()
    return client


def wait_connected(client, timeout=8):
    t0 = time.time()
    while not client.is_connected:
        if time.time() - t0 > timeout:
            raise RuntimeError(f"无法连接到 {client.host}:{client.port}，请检查 IP/网络/固件")
        time.sleep(0.1)


def call(client, service, srv_type, args=None, timeout=10):
    req = roslibpy.ServiceRequest(args or {})
    result = {}

    def cb(resp, err=None):
        if err:
            result['err'] = err
        else:
            result['data'] = resp

    roslibpy.Service(client, service, srv_type).call(req, callback=cb)
    t0 = time.time()
    while 'data' not in result and 'err' not in result:
        if time.time() - t0 > timeout:
            raise TimeoutError(f"{service} 调用超时")
        time.sleep(0.1)
    if 'err' in result:
        raise RuntimeError(f"{service} 调用失败: {result['err']}")
    return result['data']


def list_maps(client, timeout=10):
    maps = {}

    def cb(msg):
        maps['data'] = msg

    roslibpy.Topic(client, '/map_list_kitty', 'kitty_runtime_manager/MapList').subscribe(cb)
    t0 = time.time()
    while 'data' not in maps:
        if time.time() - t0 > timeout:
            raise TimeoutError("等待 /map_list_kitty 超时（请确认导航系统已启动）")
        time.sleep(0.2)
    return maps['data'].get('maps', [])


def fmt_map(mp):
    goals = mp.get('goals', [])
    g = ', '.join(f"{g['name']}({g['x']:.2f},{g['y']:.2f},θ={g['theta']:.2f})" for g in goals) if goals else '无目标点'
    return f"  ■ {mp['map_name']}  路径: {mp.get('map_path','-')}\n      目标点: {g}"


def main():
    ap = argparse.ArgumentParser(description='Tbot 地图管理 CLI')
    ap.add_argument('--ip', required=True, help='机器人 IP，如 192.168.1.151')
    ap.add_argument('--port', type=int, default=9090)
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('list', help='列出地图与目标点')
    p_start = sub.add_parser('start-mapping', help='开始建图')
    p_save = sub.add_parser('save', help='保存当前地图')
    p_save.add_argument('--map', required=True)
    p_sel = sub.add_parser('select', help='选择地图并启动导航')
    p_sel.add_argument('--map', required=True)
    p_del = sub.add_parser('delete', help='删除地图')
    p_del.add_argument('--map', required=True)
    p_ag = sub.add_parser('add-goal', help='添加目标点')
    p_ag.add_argument('--map', required=True); p_ag.add_argument('--name', required=True)
    p_ag.add_argument('--x', type=float, required=True); p_ag.add_argument('--y', type=float, required=True)
    p_ag.add_argument('--theta', type=float, default=0.0)
    p_dg = sub.add_parser('del-goal', help='删除目标点')
    p_dg.add_argument('--map', required=True); p_dg.add_argument('--name', required=True)

    a = ap.parse_args()
    client = build_client(a.ip, a.port)
    try:
        wait_connected(client)
        print(f"[OK] 已连接 {a.ip}:{a.port}\n")

        if a.cmd == 'list':
            maps = list_maps(client)
            if not maps:
                print("未找到地图。使用 start-mapping 开始建图。")
            else:
                print(f"共 {len(maps)} 张地图：")
                for mp in maps:
                    print(fmt_map(mp))

        elif a.cmd == 'start-mapping':
            r = call(client, '/start_mapping_kitty', 'std_srvs/Trigger')
            print(f"[OK] {r.get('message','开始建图')} (success={r.get('success')})")

        elif a.cmd == 'save':
            r = call(client, '/save_map_kitty', 'kitty_runtime_manager/SaveMap', {'filepath': a.map})
            print(f"[OK] 地图已保存为「{a.map}」: {r.get('message')}")

        elif a.cmd == 'select':
            r = call(client, '/select_map_and_start_kitty', 'kitty_runtime_manager/SaveMap', {'filepath': a.map})
            print(f"[OK] 已选择「{a.map}」并启动导航: {r.get('message')}")

        elif a.cmd == 'delete':
            r = call(client, '/delete_map_kitty', 'kitty_runtime_manager/DeleteMap', {'map_name': a.map})
            print(f"[OK] 已删除地图「{a.map}」: {r.get('message')}")

        elif a.cmd == 'add-goal':
            r = call(client, '/add_goal_kitty', 'kitty_runtime_manager/AddGoal',
                     {'map_name': a.map, 'goal_name': a.name, 'x': a.x, 'y': a.y, 'theta': a.theta})
            print(f"[OK] 目标点「{a.name}」已添加到「{a.map}」: {r.get('message')}")

        elif a.cmd == 'del-goal':
            r = call(client, '/delete_goal_kitty', 'kitty_runtime_manager/DeleteGoal',
                     {'map_name': a.map, 'goal_name': a.name})
            print(f"[OK] 目标点「{a.name}」已从「{a.map}」删除: {r.get('message')}")

    except KeyboardInterrupt:
        print("\n已中断")
    finally:
        client.terminate()


if __name__ == '__main__':
    main()
