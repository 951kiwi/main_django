import json
from collections import deque
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room

# --- ルール判定関数群 ---
def is_blocked(x1, y1, x2, y2, fences):
    if x1 == x2:  # 上下移動 -> 横壁(H)が遮る
        min_y = min(y1, y2)
        for f in fences:
            if f['orientation'] == 'H' and f['y'] == min_y:
                if f['x'] == x1 or f['x'] == x1 - 1:
                    return True
    elif y1 == y2:  # 左右移動 -> 縦壁(V)が遮る
        min_x = min(x1, x2)
        for f in fences:
            if f['orientation'] == 'V' and f['x'] == min_x:
                if f['y'] == y1 or f['y'] == y1 - 1:
                    return True
    return False

def has_path_to_goal(start_pos, goal_row, board_size, fences):
    start = (start_pos['x'], start_pos['y'])
    queue = deque([start])
    visited = {start}

    while queue:
        cx, cy = queue.popleft()
        if cy == goal_row:
            return True
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                if (nx, ny) not in visited and not is_blocked(cx, cy, nx, ny, fences):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return False

# --- ビュー関数 ---
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '対戦部屋')
        board_size = int(request.POST.get('board_size', 9))
        fences_per_player = int(request.POST.get('fences_per_player', 10))
        room = Room.objects.create(name=name, board_size=board_size, fences_per_player=fences_per_player)
        return redirect('game_room', room_id=room.id)
    return render(request, 'quoridor/index.html')

def game_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'quoridor/game.html', {'room': room})

# views.py の api_move_pawn を以下のように置き換えます

@csrf_exempt
def api_move_pawn(request, room_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POSTメソッドのみ対応しています'}, status=405)

    room = get_object_or_404(Room, id=room_id)
    if room.winner:
        return JsonResponse({'success': False, 'error': 'ゲームは終了しています'}, status=400)

    data = json.loads(request.body)
    tx, ty = data.get('x'), data.get('y')

    current_pos = room.p1_pos if room.current_turn == 1 else room.p2_pos
    enemy_pos = room.p2_pos if room.current_turn == 1 else room.p1_pos

    # 相手がいるマスへの重複配置は禁止
    if tx == enemy_pos['x'] and ty == enemy_pos['y']:
        return JsonResponse({'success': False, 'error': '相手のいるマスには重なれません'}, status=400)

    dx = tx - current_pos['x']
    dy = ty - current_pos['y']
    dist = abs(dx) + abs(dy)

    # 1. 通常の1マス移動 (上下左右)
    if dist == 1:
        if is_blocked(current_pos['x'], current_pos['y'], tx, ty, room.placed_fences):
            return JsonResponse({'success': False, 'error': '壁があって進めません'}, status=400)

    # 2. ★ 相手コマを直線で飛び越える2マスジャンプ移動 ★
    elif (abs(dx) == 2 and dy == 0) or (abs(dy) == 2 and dx == 0):
        mid_x = (current_pos['x'] + tx) // 2
        mid_y = (current_pos['y'] + ty) // 2
        
        # 間に相手コマがいるかチェック
        if not (mid_x == enemy_pos['x'] and mid_y == enemy_pos['y']):
            return JsonResponse({'success': False, 'error': '相手コマがいないため飛び越えられません'}, status=400)

        # 自分から相手、相手から着地点の間に壁がないかチェック
        if is_blocked(current_pos['x'], current_pos['y'], mid_x, mid_y, room.placed_fences) or \
           is_blocked(mid_x, mid_y, tx, ty, room.placed_fences):
            return JsonResponse({'success': False, 'error': '壁があるため飛び越えられません'}, status=400)

    else:
        return JsonResponse({'success': False, 'error': '無効な移動先です'}, status=400)

    # 移動反映
    if room.current_turn == 1:
        room.p1_pos = {'x': tx, 'y': ty}
        if ty == 0:
            room.winner = 1
        room.current_turn = 2
    else:
        room.p2_pos = {'x': tx, 'y': ty}
        if ty == room.board_size - 1:
            room.winner = 2
        room.current_turn = 1

    room.save()
    return JsonResponse({'success': True, 'room': get_room_dict(room)})

# views.py の api_place_fence 関数内の該当箇所

@csrf_exempt
def api_place_fence(request, room_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POSTメソッドのみ対応しています'}, status=405)

    room = get_object_or_404(Room, id=room_id)
    if room.winner:
        return JsonResponse({'success': False, 'error': 'ゲームは終了しています'}, status=400)

    # 壁の残数チェック
    if (room.current_turn == 1 and room.p1_fences_left <= 0) or (room.current_turn == 2 and room.p2_fences_left <= 0):
        return JsonResponse({'success': False, 'error': '壁が残っていません'}, status=400)

    data = json.loads(request.body)
    fx, fy, orient = data.get('x'), data.get('y'), data.get('orientation')

    # 盤面外チェック
    if not (0 <= fx < room.board_size - 1 and 0 <= fy < room.board_size - 1):
        return JsonResponse({'success': False, 'error': '盤面外です'}, status=400)

    # 既存壁との重複/交差チェック
    for f in room.placed_fences:
        if f['x'] == fx and f['y'] == fy:
            return JsonResponse({'success': False, 'error': 'すでに壁が存在します'}, status=400)
        if f['orientation'] == orient:
            if orient == 'H' and f['y'] == fy and abs(f['x'] - fx) < 1:
                return JsonResponse({'success': False, 'error': '横壁が重なっています'}, status=400)
            if orient == 'V' and f['x'] == fx and abs(f['y'] - fy) < 1:
                return JsonResponse({'success': False, 'error': '縦壁が重なっています'}, status=400)

    # 完全封鎖判定（シミュレーション）
    new_fence = {'x': fx, 'y': fy, 'orientation': orient, 'player': room.current_turn}
    sim_fences = room.placed_fences + [new_fence]

    if not has_path_to_goal(room.p1_pos, 0, room.board_size, sim_fences) or \
       not has_path_to_goal(room.p2_pos, room.board_size - 1, room.board_size, sim_fences):
        return JsonResponse({'success': False, 'error': 'ゴールへの道を完全に塞ぐことはできません'}, status=400)

    # プレイヤー情報を含めて壁を追加
    room.placed_fences.append(new_fence)
    if room.current_turn == 1:
        room.p1_fences_left -= 1
        room.current_turn = 2
    else:
        room.p2_fences_left -= 1
        room.current_turn = 1

    room.save()
    return JsonResponse({'success': True, 'room': get_room_dict(room)})
@csrf_exempt
def api_reset_game(request, room_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POSTメソッドのみ対応しています'}, status=405)

    room = get_object_or_404(Room, id=room_id)

    # 盤面とプレイヤー状態を初期化
    mid = room.board_size // 2
    room.p1_pos = {"x": mid, "y": room.board_size - 1}
    room.p2_pos = {"x": mid, "y": 0}
    room.p1_fences_left = room.fences_per_player
    room.p2_fences_left = room.fences_per_player
    room.placed_fences = []
    room.current_turn = 1
    room.winner = None
    room.save()

    return JsonResponse({'success': True, 'room': get_room_dict(room)})

def get_room_dict(room):
    return {
        'board_size': room.board_size,
        'current_turn': room.current_turn,
        'winner': room.winner,
        'p1_pos': room.p1_pos,
        'p2_pos': room.p2_pos,
        'p1_fences_left': room.p1_fences_left,
        'p2_fences_left': room.p2_fences_left,
        'placed_fences': room.placed_fences,
    }