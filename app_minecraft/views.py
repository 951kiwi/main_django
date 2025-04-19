from django.shortcuts import render
from .models import PlayerData
from datetime import datetime, timezone
import os
import re

log_file_path = '/opt/minecraft_be_server/logs/logfile.log'  # ログファイルのパスを指定

def show_log(request):
    try:
        with open(log_file_path, 'r',encoding='utf-8') as file:
            log_content = file.readlines()  # ログファイルの内容を全て読み込む
            log_content = [line for line in log_content if line.strip()]  # 空行を削除

            log_data = []
            for line in log_content:
                if(line.find("[Scripting]") != -1):
                    line = line.split('[Scripting]')[-1].strip()
                    log_data.append(line)

            
    except FileNotFoundError:
        log_content = 'ログファイルが見つかりません。'  # ファイルが見つからなかった場合のエラーメッセージ

    return render(request, 'minecraft/show_log.html', {'log_content': log_data})




def players_list(request):
    set_status()
    # 全てのプレイヤーデータを取得
    players = PlayerData.objects.all()
    
    player_statuses = []
    def format_time_difference(delta):
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m"
    
    for player in players:
        now = datetime.now(timezone.utc)  # 現在の時間（UTC）
        if(player.leave_time == None):
            status = "オンライン"
            border_color = "green"  # オンラインの場合、緑
            loadTIme = now - player.join_time
        # 参加時間と退場時間を比較してオンライン/オフラインを判定
        elif player.leave_time < player.join_time: 
            status = "オンライン"
            border_color = "green"  # オンラインの場合、緑
            loadTIme = now - player.join_time
        else:
            status = "オフライン"
            border_color = "red"  # オフラインの場合、赤
            loadTIme = now - player.leave_time
            player.update_play_time()
        
        player_statuses.append({
            'player': player,
            'status': status,
            'border_color': border_color,
            'loadTIme' : format_time_difference(loadTIme)
        })
    player_statuses.sort(key=lambda player: player["loadTIme"])
    # オンラインプレイヤーを優先的に並べ替え
    player_statuses.sort(key=lambda status: status['border_color'] == "red")
    
    context = {
        'player_statuses': player_statuses,
    }

    return render(request, 'minecraft/players_list.html', context)


def set_status():
    try:
        with open(log_file_path, 'r',encoding='utf-8') as file:
            log_content = file.readlines()  # ログファイルの内容を全て読み込む
            log_data = []
            for line in log_content:
                if(line.find("[Scripting]") != -1):
                    line = line.split('[Scripting]')[-1].strip()    #[scripting]より前のデータを削除 例:[log/????/????]
                    line = line[1:-1]                               #最初と最後を削除 log/????/????
                    command = line.split("/")
                    print(command)
                    if(command[0] == "log"):
                        match command[1]:
                            case "join":
                                save_player_data(playername=command[2],join=command[3])
                                pass
                            case "leave":
                                save_player_data(playername=command[2],leave=command[3])
                                pass
                            case "demantion":
                                save_player_data(playername=command[2],current_world=command[3])
                                pass
                            case "death":
                                save_player_data(playername=command[2],death_World=command[3],dx=command[4],dy=command[5],dz=command[6])
        # ログファイルを空にする
        with open(log_file_path, 'w', encoding='utf-8') as file:
            file.truncate(0)  # ファイルを空にする
        print("ログファイルを空にしました。")
    except FileNotFoundError:
        print('ログファイルが見つかりません。')  # ファイルが見つからなかった場合のエラーメッセージ


def save_player_data(playername,join=None,leave=None,current_world=None,death_World=None,dx=None,dy=None,dz=None):
    # playername が既に存在するか確認
    try:
        player_data = PlayerData.objects.get(player_name=playername)
        # 存在する場合、名前以外を更新
        # None ではないデータのみ更新
        if join is not None:
            player_data.join_time = join
        if leave is not None:
            player_data.leave_time = leave
        if current_world is not None:
            player_data.current_world = current_world
        if death_World is not None:
            player_data.last_death_world = death_World
        if dx is not None:
            player_data.last_death_x = dx
        if dy is not None:
            player_data.last_death_y = dy
        if dz is not None:
            player_data.last_death_z = dz
        player_data.save()
        created = False
        
    except PlayerData.DoesNotExist:
        # 存在しない場合、新規作成
        player_data = PlayerData(
            player_name=playername,
            join_time=join,
            leave_time=leave,
            current_world=current_world,
            last_death_world=death_World,
            last_death_x=dx,
            last_death_y=dy,
            last_death_z=dz
        )
        player_data.save()
        created = True
