from pulp import *

VALS = range(1,10)

path = input("Input file path: ")

horizontal = []
vertical = []

# 入力から縦と横の連鎖を決めてそれぞれhorizontalとverticalのリストに格納する
with open(path) as puzzle:
    text_split = [line.split(' ') for line in puzzle.read().split('\n')]
    # 問題の長さを格納する
    global ROW_LENGTH, COL_LENGTH
    ROW_LENGTH, COL_LENGTH = [int(num) for num in text_split.pop(0)]
    
    # 斜めに分けられたマスを探すことに通じて白マスの連鎖を探す
    for rownum, row in enumerate(text_split):
        for colnum, element in enumerate(row):
            if element == '.' or element == 'X':
                continue
            # 斜めに分けられたマスが見つかった場合
            down, right = [int(num) for num in element.split(',')]
            if down != 0:
                # 下に辿る
                i = rownum + 1
                while (i < ROW_LENGTH and text_split[i][colnum] == '.'):
                    i += 1
                i -= 1
                vertical.append((rownum + 2, i + 1, colnum + 1, down))
            if right != 0:
                # 右に辿る
                j = colnum + 1
                while (j < COL_LENGTH and text_split[rownum][j] == '.'):
                    j += 1
                j -= 1
                horizontal.append((colnum + 2, j + 1, rownum + 1, right))

ROWS = range(1, ROW_LENGTH + 1)
COLS = range(1, COL_LENGTH + 1)

# モデルを形成する
prob = LpProblem("Kakuro_Problem")

# 決定変数の行列を作る
choices = LpVariable.dicts("Choice", (VALS, ROWS, COLS), cat="Binary")

# ルール第1項
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[v][r][c] for v in VALS]) == 1

# 横の連鎖の場合
for x_l, x_r, row, c in horizontal:
    
    # ルール第3項
    for v in VALS:
        prob += lpSum([choices[v][row][x] for x in range(x_l, x_r + 1)]) <= 1
        
    # ルール第2項
    prob += lpSum([v * choices[v][row][x] for v in VALS for x in range(x_l, x_r + 1)]) == c

# 縦の連鎖の場合
for y_t, y_b, col, c in vertical:
    
    # ルール第3項
    for v in VALS:
        prob += lpSum([choices[v][y][col] for y in range(y_t, y_b + 1)]) <= 1
    
    # ルール第2項
    prob += lpSum([v * choices[v][y][col] for v in VALS for y in range(y_t, y_b + 1)]) == c

# 問題データを.lpファイルで書く
prob.writeLP("Kakuro.lp")

# 問題を解く
prob.solve()

# 解答ステータスを出力
print("Status:", LpStatus[prob.status])

with open(path) as puzzle:
    with open("kakuroout.txt", "w") as kakuroout:
        text_split = [line.split(' ') for line in puzzle.read().split('\n')]
        text_split.pop(0)
        for r in ROWS:
            row_out = ""
            for c in COLS:
                if text_split[r-1][c-1] != '.':
                    kakuroout.write("- ")
                else:
                    for v in VALS:
                        if value(choices[v][r][c]) == 1:
                            kakuroout.write(str(v) + " ")
            kakuroout.write('\n')