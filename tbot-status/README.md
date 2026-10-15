# tbot-status · Tbot 底盘状态监控 CLI

基于 ROS over WebSocket (rosbridge) 实时读取 Tbot 底盘状态的命令行工具：电量、充电状态、定位位姿、导航到达状态、路径点数量。

## 安装

```bash
pip install roslibpy
```

## 用法

```bash
python status.py --ip 192.168.1.151                  # 实时循环监控（Ctrl+C 退出）
python status.py --ip 192.168.1.151 --once           # 打印一次后退出
python status.py --ip 192.168.1.151 --interval 2     # 每 2 秒刷新
python status.py --ip 192.168.1.151 --once --json    # JSON 输出，供监控平台/Zabbix 集成
```

## 示例输出

```bash
$ python status.py --ip 192.168.1.151 --once
┌────────────────────────────────────────
│  Tbot 底盘状态  (ROS over WebSocket)
├────────────────────────────────────────
│  电量    75.5%      状态: 未充电
│  定位    x=1.23  y=4.56  yaw=52.3°
│  导航    导航中/未到达
│  路径点  5 个
└────────────────────────────────────────
```

## JSON 集成

```bash
$ python status.py --ip 192.168.1.151 --once --json
{
  "battery": 75.5,
  "charging": false,
  "x": 1.23,
  "y": 4.56,
  "yaw": 0.913,
  "yaw_deg": 52.3,
  "arrived": false,
  "path_pts": 5,
  "connected": true
}
```

可用于定时巡检（配合 cron）：`*/5 * * * * python status.py --ip 192.168.1.151 --once --json >> /var/log/tbot-status.log`

## 接口

| 数据 | Topic | 类型 |
|---|---|---|
| 电量/充电 | /ebot_work_state | std_msgs/Float64MultiArray |
| 定位位姿 | /fast_lio_localization | nav_msgs/Odometry |
| 导航到达 | /ebot_goal_status_local_planner | std_msgs/Float64MultiArray |
| 路径点 | /aft_pgo_path | nav_msgs/Path |

更多协议细节见 [TOBOT AI SDK](https://www.tobotai.com/sdk/index.html)。
