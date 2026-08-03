[README.md](https://github.com/user-attachments/files/30677724/README.md)
[README.zh.md](https://github.com/user-attachments/files/30677730/README.zh.md)# 打砖块 —— 我的游戏（Arkanoid）

一款用 Python 编写、基于 **OpenGL**（通过 Pygame 调用）渲染的经典 **打砖块（Arkanoid / Breakout）** 风格游戏。击碎砖块、收集道具，并在 20 个关卡中与боss战斗。

🌍 [English README](README.md)

## 功能特色

- 🎮 流畅的 OpenGL 硬件加速 2D 渲染（分辨率 1260×800，60 FPS）
- 🧱 20 个可玩关卡，砖块布局各不相同
- 👾 第 5、10、15、20 关设有 Boss 战，每个 Boss 会发射不同类型的弹幕（普通、减速、爆炸）
- ⭐ 特殊道具砖块：
  - **金色** —— 获得一条额外生命
  - **银色** —— 挡板变宽
  - **青色** —— 增加一个球
  - **红色** —— 激活挡板炮台
- 💥 碰撞、爆炸和子弹拖尾的粒子特效
- ❤️ 以心形图标显示剩余生命
- 🔊 程序化生成的音效（挡板反弹、砖块破碎、道具获取、Boss 受击等）
- 🎵 可选背景音乐 —— 只需在脚本同目录下放置一个 MP3 文件（`music.mp3`、`background.mp3`、`game_music.mp3`、`soundtrack.mp3` 或 `arkanoid_music.mp3`）即可
- ⏸️ 暂停菜单与关卡选择

## 环境要求

- Python 3.8 及以上
- [Pygame](https://www.pygame.org/)
- [PyOpenGL](http://pyopengl.sourceforge.net/)
- [NumPy](https://numpy.org/)
- [OpenCV (opencv-python)](https://pypi.org/project/opencv-python/)

安装依赖：

```bash
pip install pygame PyOpenGL PyOpenGL_accelerate numpy opencv-python
```

## 运行游戏

```bash
python ark9k.py
```

## 操作说明

| 按键 | 功能 |
|------|------|
| ← / → | 游戏中移动挡板 / 菜单中导航 |
| ↑ / ↓ | 菜单导航 |
| Enter | 确认菜单选项 |
| Esc | 暂停 / 打开菜单 |
| M | 开启或关闭背景音乐 |
| R | 游戏结束或通关后重新开始 |
| N | 通关当前关卡后进入下一关 |

挡板炮台一旦被红色砖块激活，会自动开火。

## 添加背景音乐

游戏会在运行目录中查找以下任意一个文件，若找到则循环播放：

```
music.mp3
background.mp3
game_music.mp3
soundtrack.mp3
arkanoid_music.mp3
```

如果没有找到这些文件，游戏将没有背景音乐（音效仍会正常播放，因为音效是程序实时生成的）。

## 项目结构

```
ark9k.py    # 单文件游戏：引擎、实体、关卡、Boss 逻辑、UI 与主循环
```

## 许可证

目前尚未指定许可证 —— 如果计划分享代码或接受他人贡献，建议添加一个（例如 MIT 许可证）。
