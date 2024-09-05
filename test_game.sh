#!/bin/sh

# 游戏设置
typeset -i WIDTH=20 HEIGHT=10
typeset -i SNAKE_X=5 SNAKE_Y=5
typeset -i FOOD_X=$((RANDOM % WIDTH)) FOOD_Y=$((RANDOM % HEIGHT))
typeset -a SNAKE
SNAKE=("$SNAKE_X,$SNAKE_Y")
DIRECTION="RIGHT"
SCORE=0

# 显示游戏画面
draw_board() {
    clear
    for ((y = 0; y < HEIGHT; y++)); do
        for ((x = 0; x < WIDTH; x++)); do
            if [[ "$x,$y" == "$FOOD_X,$FOOD_Y" ]]; then
                echo -n "🍎"  # 食物
                elif [[ " ${SNAKE[@]} " =~ " $x,$y " ]]; then
                echo -n "🟩"  # 蛇
            else
                echo -n "⬛"  # 空白区域
            fi
        done
        echo
    done
    echo "Score: $SCORE"
}

# 更新蛇的方向
update_direction() {
    read -rs -t 0.1 -n 1 key
    case "$key" in
        w) [[ "$DIRECTION" != "DOWN" ]] && DIRECTION="UP" ;;
        s) [[ "$DIRECTION" != "UP" ]] && DIRECTION="DOWN" ;;
        a) [[ "$DIRECTION" != "RIGHT" ]] && DIRECTION="LEFT" ;;
        d) [[ "$DIRECTION" != "LEFT" ]] && DIRECTION="RIGHT" ;;
    esac
}

# 更新蛇的位置
move_snake() {
    case "$DIRECTION" in
        UP) ((SNAKE_Y--)) ;;
        DOWN) ((SNAKE_Y++)) ;;
        LEFT) ((SNAKE_X--)) ;;
        RIGHT) ((SNAKE_X++)) ;;
    esac
    
    # 蛇吃到食物
    if [[ "$SNAKE_X,$SNAKE_Y" == "$FOOD_X,$FOOD_Y" ]]; then
        FOOD_X=$((1+RANDOM % (WIDTH-2)))
        FOOD_Y=$((1+RANDOM % (HEIGHT-2)))
        ((SCORE++))
        SNAKE+=("$SNAKE_X,$SNAKE_Y")  # 增加蛇的长度
    else
        SNAKE=("${SNAKE[@]}" "$SNAKE_X,$SNAKE_Y")
        SNAKE=("${SNAKE[@]:1}")
    fi
}

# 检查游戏状态
check_collision() {
    if (( SNAKE_X < 0 || SNAKE_X >= WIDTH || SNAKE_Y < 0 || SNAKE_Y >= HEIGHT )); then
        echo "Game Over! You hit the wall."
        exit 1
    fi

    for ((i = 0; i < ${#SNAKE[@]}-1; i++)); do
        if [[ "${SNAKE[i]}" == "$SNAKE_X,$SNAKE_Y" ]]; then
            echo "Game Over! You ran into yourself."
            exit 1
        fi
    done
}

# 主循环
while true; do
    draw_board
    update_direction
    move_snake
    check_collision
done
