# TOBOT AI Toolchain · 瞳步机器人官方工具链

面向 Tbot 全系移动底盘的开发者工具集。所有工具基于官方 **ROS over WebSocket (rosbridge)** 协议，无需安装 ROS 即可使用。

> 官网：<https://www.tobotai.com> · SDK 文档：<https://www.tobotai.com/sdk/index.html> · 技术支持：support@tobotai.com

## 工具一览

| 工具 | 目录 | 说明 | 依赖 |
|---|---|---|---|
| 🔧 **Web 调试台** | [debug-console](debug-console/) | 浏览器直连底盘：实时电量/定位/导航可视化 + 一键调用全部 9 个 Service（建图/保存/选图/删图/回充/导航/目标点） | 无（浏览器原生 WebSocket） |
| 🗺 **地图管理 CLI** | [tbot-maps](tbot-maps/) | 列地图、开始建图、保存、选择并启动导航、删除地图、增删目标点 | roslibpy |
| 📊 **状态监控 CLI** | [tbot-status](tbot-status/) | 电量/充电/定位位姿/导航到达/路径点，支持循环与 JSON 输出（可接监控平台） | roslibpy |
| 🤖 **全系 URDF** | [urdf](urdf/) | 12 款底盘 URDF（规格示意），Rviz 可视化与仿真扩展 | 无 |

## 快速开始

```bash
# 1. Web 调试台：浏览器打开 debug-console/index.html，输入机器人 IP 即可
# 2. 命令行（需 Python 3.8+）
pip install roslibpy
python tbot-maps/maps.py --ip 192.168.1.151 list          # 查看地图
python tbot-status/status.py --ip 192.168.1.151 --once    # 查看底盘状态
```

## 协议

所有工具通过 `ws://<robot-ip>:9090` 连接（rosbridge）。接口速览：

- **Topic 订阅（5）**：/fast_lio_localization · /aft_pgo_path · /map_list_kitty · /ebot_goal_status_local_planner · /ebot_work_state
- **Service 调用（9）**：/start_mapping_kitty · /save_map_kitty · /select_map_and_start_kitty · /delete_map_kitty · /docking_kitty · /navigate_to_pose（含取消）· /add_goal_kitty · /delete_goal_kitty

完整字段说明见 [SDK 文档](https://www.tobotai.com/sdk/index.html) 与 [TobotSlam3D_SDK 仓库](../TobotSlam3D_SDK)。

## 目录结构

```
toolchain/
├── debug-console/index.html     # Web 调试台（单文件，零依赖）
├── tbot-maps/maps.py            # 地图管理 CLI
├── tbot-status/status.py        # 状态监控 CLI
├── urdf/generate_urdf.py        # URDF 生成器（可扩展）
└── LICENSE · README.md
```

## 支持

- 技术支持：support@tobotai.com（工作日 1 小时内响应）
- 商务合作 / ODM / 定制：sales@tobotai.com
- 官网选型手册与 3D 模型：<https://www.tobotai.com/downloads.html>

## License

[Apache-2.0](LICENSE) · © 上海瞳步机器人科技有限公司（TOBOT AI）
