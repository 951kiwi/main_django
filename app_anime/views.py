
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404

def folder_list(request):
    static_path = os.path.join(settings.BASE_DIR, 'static/anime')
    folders = []
    
    # フォルダ内のアイコンをチェック
    for folder in os.listdir(static_path):
        folder_path = os.path.join(static_path, folder)
        if os.path.isdir(folder_path):
            icon_path = None
            # listicon画像をチェック
            for ext in ['jpg', 'jpeg', 'png']:
                icon_file = f"listIcon.{ext}"
                if os.path.exists(os.path.join(folder_path, icon_file)):
                    icon_path = f"/static/anime/{folder}/{icon_file}"
                    break
            folders.append({'name': folder, 'icon': icon_path})
    
    return render(request, 'folder_list.html', {'folders': folders})

def video_list(request, playlist_name):
    # フォルダパス
    playlist_path = os.path.join(settings.BASE_DIR, 'static/anime', playlist_name)
    
    if not os.path.isdir(playlist_path):
        raise Http404("プレイリストが見つかりません。")
    
    # フォルダ内の動画ファイルをリストアップ (動画ファイル拡張子でフィルタリング)
    video_files = [f for f in os.listdir(playlist_path) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        raise Http404("動画がありません。")
    
    # 動画ファイルをソートして最初の動画を取得
    video_files.sort()
    first_video = video_files[0]
    
    return redirect('video_play', playlist_name=playlist_name, video_name=first_video)

def video_play(request, playlist_name, video_name):
    # フォルダパス
    playlist_path = os.path.join(settings.BASE_DIR, 'static/anime', playlist_name)
    video_path = os.path.join(playlist_path, video_name)

    if not os.path.exists(video_path):
        raise Http404("動画が見つかりません。")

    # フォルダ内の動画ファイルをリストアップ
    video_files = [f for f in os.listdir(playlist_path) if f.endswith(('.mp4', '.avi', '.mov'))]
    video_files.sort()
    
    # 次の動画と前の動画のインデックスを取得
    current_index = video_files.index(video_name)
    next_video = video_files[current_index + 1] if current_index + 1 < len(video_files) else None
    prev_video = video_files[current_index - 1] if current_index - 1 >= 0 else None
    
    context = {
        'video_path': f"/static/anime/{playlist_name}/{video_name}",
        'playlist_name': playlist_name,
        'video_name': video_name,  # 動画名を追加
        'next_video': next_video,
        'prev_video': prev_video,
        'video_list': video_files,  # 動画一覧を context に追加
    }

    return render(request, 'video_play.html', context)
