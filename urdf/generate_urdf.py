#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_urdf.py · Tbot 全系底盘 URDF 生成器

根据官网规格表（https://www.tobotai.com/specs.html）生成各型号示意 URDF，
用于 Rviz 可视化、初步碰撞检查与仿真扩展。

运行:
  python generate_urdf.py            # 生成 urdf/ 下全部型号
  python generate_urdf.py --model Tbot-X4   # 只生成指定型号

说明:
  - 尺寸以官网公开值为准；官网未公开的高度用示意值(0.35m)，注释中已标注；
    Tbot-H 官网未公开尺寸，生成占位模型，正式几何请联系官方获取 3D 模型。
  - URDF 为规格示意，精确几何与材质请使用官网下载中心 3D 模型 (STEP/CAD)。
"""
import argparse
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# (id, 型号, 驱动, 长mm, 宽mm, 高mm, 圆直径mm, 自重kg, 爬坡, 越障cm, 载重kg, 轮数, 轮径m, 轮宽m)
MODELS = [
    ('Tbot-N5-3D',  'Tbot-N5-3D', '六轮中驱差速',   0, 0, 350, 500, 30, '15°', '2cm', '100~500kg', 6, 0.12, 0.05),
    ('Tbot-OW',     'Tbot-OW',    '全向轮 ×4',       0, 0, 350, 500, 50, '30°', '5cm', '100~500kg', 4, 0.12, 0.05),
    ('Tbot-S5',     'Tbot-S5',    '中驱差速六轮',  500, 200, 350, 0, 30, '15°', '2cm', '100~500kg', 6, 0.12, 0.05),
    ('Tbot-S8',     'Tbot-S8',    '中驱差速六轮',  800, 200, 350, 0, 45, '15°', '2cm', '100~500kg', 6, 0.12, 0.05),
    ('Tbot-X4',     'Tbot-X4',    '四驱差速',       600, 500, 350, 0, 45, '30°', '5cm', '100~500kg', 4, 0.12, 0.05),
    ('Tbot-X100',   'Tbot-X100',  '四驱差速',      1000, 600, 350, 0, 55, '30°', '5cm', '100~500kg', 4, 0.12, 0.05),
    ('Tbot-X2',     'Tbot-X2',    '前驱差速',       600, 500, 350, 0, 25, '30°', '5cm', '100~500kg', 2, 0.12, 0.05),
    ('Tbot-ACK',    'Tbot-ACK',   '阿克曼转向',     1500, 800, 350, 0, 100, '30°', '5cm', '300~500kg', 4, 0.16, 0.06),
    ('Tbot-MW',     'Tbot-MW',    '四驱麦克纳姆',   600, 500, 350, 0, 45, '15°', '2cm', '50kg',      4, 0.12, 0.05),
    ('Tbot-N',      'Tbot-N',     '六轮中驱差速',     0, 0, 350, 500, 30, '15°', '2cm', '100kg',     6, 0.12, 0.05),
    ('Tbot-L',      'Tbot-L',     '双驱差速',       350, 330, 136, 0, 10, '15°', '2cm', '10kg',      2, 0.08, 0.04),
    ('Tbot-H',      'Tbot-H',     '双驱差速',         0, 0, 0, 0, 0, '15°', '2cm', '询价确认',      2, 0.12, 0.05),
]


def urdf(m):
    mid, name, drive, lw, wd, ht, dia, mass, climb, step, load, wheels, rw, tw = m
    body_h = ht / 1000.0 if ht else 0.35
    if dia:
        geo_v = f'<cylinder radius="{dia/2000.0}" length="{body_h}"/>'
        geo_c = f'<cylinder radius="{dia/2000.0}" length="{body_h}"/>'
    else:
        geo_v = f'<box size="{lw/1000.0} {wd/1000.0} {body_h}"/>'
        geo_c = f'<box size="{lw/1000.0} {wd/1000.0} {body_h}"/>'
    ixx = (mass * (max(lw, wd) / 1000.0) ** 2) / 12.0 if not dia else (mass * (dia/1000.0) ** 2) / 8.0
    izz = ixx
    iyy = mass * body_h ** 2 / 12.0

    c = []
    c.append('<?xml version="1.0"?>')
    c.append(f'<robot name="{mid.lower()}">')
    c.append(f'  <!-- {name} · {drive} · 载重 {load} · 自重 {mass}kg · 爬坡 {climb} · 越障 {step}')
    if ht == 0 and not dia:
        c.append(f'       ⚠ 官网未公开整机尺寸，本模型为占位示意；正式几何请联系 sales@tobotai.com 获取 3D 模型')
    c.append(f'       官网规格: https://www.tobotai.com/specs.html -->')
    c.append(f'  <link name="base_link">')
    c.append(f'    <inertial><mass value="{mass}"/>')
    c.append(f'      <inertia ixx="{ixx:.3f}" ixy="0.0" ixz="0.0" iyy="{iyy:.3f}" iyz="0.0" izz="{izz:.3f}"/>')
    c.append(f'    </inertial>')
    c.append(f'    <visual><geometry>{geo_v}</geometry>')
    c.append(f'      <material name="gray"><color rgba="0.55 0.58 0.62 1.0"/></material></visual>')
    c.append(f'    <collision><geometry>{geo_c}</geometry></collision>')
    c.append(f'  </link>')
    # 雷达
    c.append(f'  <link name="laser_link"><visual><geometry><cylinder radius="0.08" length="0.10"/></geometry>')
    c.append(f'    <material name="black"><color rgba="0.1 0.1 0.12 1.0"/></material></visual></link>')
    c.append(f'  <joint name="laser_joint" type="fixed">')
    c.append(f'    <parent link="base_link"/><child link="laser_link"/>')
    c.append(f'    <origin xyz="0 0 {body_h/2.0+0.10}"/></joint>')
    # 轮子
    for i in range(wheels):
        wl = f'wheel_{i+1}'
        c.append(f'  <link name="{wl}"><visual><geometry><cylinder radius="{rw}" length="{tw}"/></geometry>')
        c.append(f'    <material name="dark"><color rgba="0.15 0.15 0.17 1.0"/></material></visual>')
        c.append(f'    <collision><geometry><cylinder radius="{rw}" length="{tw}"/></geometry></collision></link>')
        c.append(f'  <joint name="{wl}_joint" type="continuous">')
        c.append(f'    <parent link="base_link"/><child link="{wl}"/>')
        if dia:
            c.append(f'    <origin xyz="{0 if i%2 else 0.05} {0.22 if i<2 else -0.22} {-body_h/2.0+rw/2.0+0.02}" rpy="0 0 0"/>')
        else:
            c.append(f'    <origin xyz="{0 if i%2 else 0.05} {(wd/1000.0/2.0+0.02) if i<2 else -(wd/1000.0/2.0+0.02)} {-body_h/2.0+rw/2.0+0.02}" rpy="0 0 0"/>')
        c.append(f'  </joint>')
    c.append(f'  <gazebo reference="base_link"><material>Gazebo/Gray</material></gazebo>')
    c.append(f'</robot>')
    return '\n'.join(c) + '\n'


def main():
    ap = argparse.ArgumentParser(description='生成 Tbot 全系底盘 URDF')
    ap.add_argument('--model', help='只生成指定型号（如 Tbot-X4）')
    a = ap.parse_args()
    n = 0
    for m in MODELS:
        if a.model and m[0] != a.model:
            continue
        p = os.path.join(OUT, m[0].lower() + '.urdf')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(urdf(m))
        n += 1
        print('written', p)
    print(f'\n共生成 {n} 个 URDF → {OUT}')


if __name__ == '__main__':
    main()
