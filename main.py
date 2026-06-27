import turtle
import random
import math
import time

# ---------- 游戏设置 ----------
WIDTH, HEIGHT = 600, 400
BALL_RADIUS = 12
BALL_COUNT = 10
TARGET_COUNT = 2
MARKED_DURATION = 3         # 标记显示秒数
TRACKING_DURATION = 20      # 追踪阶段秒数
PAUSE_DURATION = 5          # 停止后思考秒数
MIN_SPEED = 2.5
MAX_SPEED = 10

# 颜色
COLOR_TARGET = "gold"
COLOR_NONTARGET = "gray"
COLOR_ALL = "white"
COLOR_REVEAL_TARGET = "gold"
COLOR_REVEAL_NONTARGET = "gray"

# ---------- 初始化窗口 ----------
screen = turtle.Screen()
screen.setup(width=WIDTH + 100, height=HEIGHT + 100)
screen.title("多目标追踪 - 视觉记忆训练（点击窗口重新开始）")
screen.bgcolor("black")
screen.tracer(0)

# ---------- 绘制矩形边界 ----------
border = turtle.Turtle()
border.hideturtle()
border.color("white")
border.penup()
border.goto(-WIDTH/2, -HEIGHT/2)
border.pendown()
border.pensize(2)
for _ in range(2):
    border.forward(WIDTH)
    border.left(90)
    border.forward(HEIGHT)
    border.left(90)

# ---------- 提示文字 ----------
writer = turtle.Turtle()
writer.hideturtle()
writer.penup()
writer.color("white")
writer.goto(0, HEIGHT/2 + 20)

# ---------- 小球数据 ----------
balls = []          # 海龟列表
ball_data = []      # 每球字典：dx, dy, is_target

def create_balls():
    """生成不重叠的小球，随机标记目标"""
    positions = []
    for _ in range(BALL_COUNT):
        b = turtle.Turtle()
        b.shape("circle")
        b.shapesize(stretch_wid=BALL_RADIUS/10, stretch_len=BALL_RADIUS/10)
        b.penup()
        b.speed(0)

        # 寻找不重叠位置
        for _ in range(100):
            x = random.uniform(-WIDTH/2 + BALL_RADIUS*2, WIDTH/2 - BALL_RADIUS*2)
            y = random.uniform(-HEIGHT/2 + BALL_RADIUS*2, HEIGHT/2 - BALL_RADIUS*2)
            overlap = any(math.hypot(x - px, y - py) < BALL_RADIUS * 2.5 for px, py in positions)
            if not overlap:
                positions.append((x, y))
                b.goto(x, y)
                break
        else:
            # 防万一：直接随机
            x = random.uniform(-WIDTH/2 + BALL_RADIUS, WIDTH/2 - BALL_RADIUS)
            y = random.uniform(-HEIGHT/2 + BALL_RADIUS, HEIGHT/2 - BALL_RADIUS)
            b.goto(x, y)

        # 随机速度
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed

        balls.append(b)
        ball_data.append({"dx": dx, "dy": dy, "is_target": False})

    # 随机标记目标
    target_indices = random.sample(range(BALL_COUNT), TARGET_COUNT)
    for idx in target_indices:
        ball_data[idx]["is_target"] = True

# ---------- 游戏阶段控制 ----------
phase = "marked"
phase_start_time = time.time()

def update_phase():
    """根据时间自动切换阶段"""
    global phase, phase_start_time
    now = time.time()
    elapsed = now - phase_start_time

    if phase == "marked" and elapsed >= MARKED_DURATION:
        phase = "tracking"
        phase_start_time = now
        for b in balls:
            b.color(COLOR_ALL)
    elif phase == "tracking" and elapsed >= TRACKING_DURATION:
        phase = "pause"
        phase_start_time = now
        for data in ball_data:
            data["dx"] = 0
            data["dy"] = 0
    elif phase == "pause" and elapsed >= PAUSE_DURATION:
        phase = "reveal"
        phase_start_time = now
        for i, data in enumerate(ball_data):
            if data["is_target"]:
                balls[i].color(COLOR_REVEAL_TARGET)
            else:
                balls[i].color(COLOR_REVEAL_NONTARGET)

def draw_ui():
    """更新屏幕提示"""
    writer.clear()
    now = time.time()
    elapsed = now - phase_start_time

    if phase == "marked":
        remain = max(0, int(MARKED_DURATION - elapsed) + 1)
        writer.write(f"盯住这 {TARGET_COUNT} 个金色小球！ {remain} 秒后隐藏...",
                     align="center", font=("Arial", 16, "bold"))
    elif phase == "tracking":
        remain = max(0, int(TRACKING_DURATION - elapsed) + 1)
        writer.write(f"追踪目标！剩余 {remain} 秒",
                     align="center", font=("Arial", 16, "bold"))
    elif phase == "pause":
        remain = max(0, int(PAUSE_DURATION - elapsed) + 1)
        writer.write(f"时间到！{remain} 秒后揭晓答案...",
                     align="center", font=("Arial", 16, "bold"))
    elif phase == "reveal":
        writer.write("目标就是这 3 个金色小球！点击窗口重新开始",
                     align="center", font=("Arial", 16, "bold"))

def move_balls():
    """移动所有小球并处理边界反弹"""
    for b, data in zip(balls, ball_data):
        if data["dx"] == 0 and data["dy"] == 0:
            continue
        new_x = b.xcor() + data["dx"]
        new_y = b.ycor() + data["dy"]

        # 左右反弹
        if new_x - BALL_RADIUS <= -WIDTH/2:
            new_x = -WIDTH/2 + BALL_RADIUS
            data["dx"] = -data["dx"]
        elif new_x + BALL_RADIUS >= WIDTH/2:
            new_x = WIDTH/2 - BALL_RADIUS
            data["dx"] = -data["dx"]

        # 上下反弹
        if new_y - BALL_RADIUS <= -HEIGHT/2:
            new_y = -HEIGHT/2 + BALL_RADIUS
            data["dy"] = -data["dy"]
        elif new_y + BALL_RADIUS >= HEIGHT/2:
            new_y = HEIGHT/2 - BALL_RADIUS
            data["dy"] = -data["dy"]

        b.goto(new_x, new_y)

# ---------- 重置游戏（再来一局） ----------
def reset_game():
    """清除旧小球，重新初始化并开始新游戏"""
    global phase, phase_start_time, balls, ball_data

    # 隐藏并清除所有小球
    for b in balls:
        b.hideturtle()
        b.clear()
    balls.clear()
    ball_data.clear()

    # 创建新小球
    create_balls()

    # 重置阶段
    phase = "marked"
    phase_start_time = time.time()

    # 初始颜色
    for i, b in enumerate(balls):
        if ball_data[i]["is_target"]:
            b.color(COLOR_TARGET)
        else:
            b.color(COLOR_NONTARGET)

    # 移除之前绑定的点击事件，避免误触
    screen.onclick(None)

    # 重新启动游戏循环
    game_loop()

# ---------- 游戏主循环 ----------
def game_loop():
    update_phase()

    if phase != "reveal":
        move_balls()
        draw_ui()
        screen.update()
        screen.ontimer(game_loop, 20)  # 约50fps继续
    else:
        # 揭示阶段：小球静止，只刷新UI，绑定点击重启
        draw_ui()
        screen.update()
        screen.onclick(lambda x, y: reset_game())

# ---------- 首次创建小球并开始 ----------
create_balls()
for i, b in enumerate(balls):
    if ball_data[i]["is_target"]:
        b.color(COLOR_TARGET)
    else:
        b.color(COLOR_NONTARGET)

game_loop()
screen.mainloop()