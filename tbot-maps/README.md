# tbot-maps · Tbot 地图管理 CLI

基于 ROS over WebSocket (rosbridge) 管理 Tbot 底盘地图的命令行工具。

## 安装

```bash
pip install roslibpy
```

## 用法

```bash
python maps.py --ip 192.168.1.151 list                      # 列出地图与目标点
python maps.py --ip 192.168.1.151 start-mapping            # 开始建图
python maps.py --ip 192.168.1.151 save --map office        # 保存当前地图为 office
python maps.py --ip 192.168.1.151 select --map office      # 选择地图并启动导航
python maps.py --ip 192.168.1.151 delete --map office      # 删除地图（需先停止导航）
python maps.py --ip 192.168.1.151 add-goal --map office --name "电梯口" --x 1.0 --y 2.0 --theta 0.5
python maps.py --ip 192.168.1.151 del-goal  --map office --name "电梯口"
```

## 示例输出

```bash
$ python maps.py --ip 192.168.1.151 list
[OK] 已连接 192.168.1.151:9090

共 2 张地图：
  ■ Lobby  路径: /maps/floor1
      目标点: Reception(1.00,2.00,θ=0.50), 电梯口(3.00,4.00,θ=1.20)
  ■ Warehouse  路径: /maps/floor2
      目标点: 无目标点
```

## 说明

- 依赖机器人导航系统已启动（`/map_list_kitty` 有输出）；
- `delete` 前请先取消导航，避免正在使用的地图被删除；
- 支持脚本化：`python maps.py --ip ... list` 的输出可直接被自动化任务解析。

## 接口

| 命令 | 调用 Service |
|---|---|
| list | 订阅 /map_list_kitty |
| start-mapping | /start_mapping_kitty (std_srvs/Trigger) |
| save | /save_map_kitty (kitty_runtime_manager/SaveMap) |
| select | /select_map_and_start_kitty (kitty_runtime_manager/SaveMap) |
| delete | /delete_map_kitty (kitty_runtime_manager/DeleteMap) |
| add-goal | /add_goal_kitty (kitty_runtime_manager/AddGoal) |
| del-goal | /delete_goal_kitty (kitty_runtime_manager/DeleteGoal) |

更多协议细节见 [TOBOT AI SDK](https://www.tobotai.com/sdk/index.html)。
