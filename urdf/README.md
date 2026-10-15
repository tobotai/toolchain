# Tbot URDF · 全系底盘 3D 模型（规格示意）

根据官网 [全系规格总表](https://www.tobotai.com/specs.html) 生成的 Tbot 全系底盘 URDF，用于 **Rviz 可视化、初步碰撞检查、仿真环境扩展**。

## 覆盖型号（12 款）

| 文件 | 型号 | 驱动方式 | 官网尺寸 | 自重 |
|---|---|---|---|---|
| tbot-n5-3d.urdf | Tbot-N5-3D | 六轮中驱差速 | 500mm 圆形 | 30kg |
| tbot-ow.urdf | Tbot-OW | 全向轮 ×4 | 500mm 方形 | 50kg |
| tbot-s5.urdf / tbot-s8.urdf | Tbot-S5 / S8 | 中驱差速六轮 | 500×200 / 800×200mm | 30 / 45kg |
| tbot-x4.urdf / tbot-x100.urdf | Tbot-X4 / X100 | 四驱差速 | 600×500 / 1000×600mm | 45 / 55kg |
| tbot-x2.urdf | Tbot-X2 | 前驱差速 | 600×500mm | 25kg |
| tbot-ack.urdf | Tbot-ACK | 阿克曼转向 | 1500×800mm | 100kg |
| tbot-mw.urdf | Tbot-MW | 四驱麦克纳姆 | 600×500mm | 45kg |
| tbot-n.urdf | Tbot-N | 六轮中驱差速 | 500mm 圆形 | 30kg |
| tbot-l.urdf | Tbot-L | 双驱差速 | 350×330×136mm | ≈10kg |
| tbot-h.urdf | Tbot-H | 双驱差速 | 官网未公开 | 官网未公开 |

## 使用

```bash
# Rviz 查看（任选一款）
rviz -d <(echo '---')   # 或直接加载 urdf 后 Add RobotModel
# 命令检查
check_urdf tbot-x4.urdf

# 重新生成 / 只生成某一款
python generate_urdf.py
python generate_urdf.py --model Tbot-X4
```

## 重要说明

- **模型为规格示意**：官网未公开的高度统一采用示意值 0.35m（Tbot-L 使用官网 136mm），精确几何请从官网下载中心获取官方 3D 模型（STEP/CAD）；
- **Tbot-H 官网未公开尺寸**，生成的为占位模型，正式几何请联系 sales@tobotai.com；
- 惯性张量按均匀密度长方体/圆柱近似，如需动力学仿真请按实际结构校核；
- 轮子为示意（半径/宽度为行业典型值），数量按驱动方式配置（差速 2、四驱/全向/麦克纳姆/阿克曼 4、六轮 6）；
- 每款 URDF 头部注释包含官方参数（载重/自重/爬坡/越障），可直接读文件确认。
