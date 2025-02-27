from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Player,Image_Card,Select_Card
from .forms import PlayerForm
from . import game
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


IpAddress = "http://127.0.0.1:8000/"
# Create your views here.

def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        password = request.POST.get('password')
    # ボタンが create の場合
        if 'create' in request.POST:
            if room_name:
                #部屋を探す
                existing_room = Room.objects.filter(name=room_name,password=password).first()
                if existing_room:#部屋が見つかったら
                    return render(request, 'create_room.html', {'existing_room': existing_room})
                else: #見つからなかったら
                    room = Room.objects.create(name=room_name,password=password)
                    return redirect('host_room', room_id=room.id)
                    
        
        # ボタンが join の場合
        elif 'join' in request.POST:
            if room_name:
                existing_room = Room.objects.filter(name=room_name).first()
                print(existing_room)
                return redirect('join_room', room_id=existing_room.id)

    return render(request, 'create_room.html')

def joinSerch_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        password = request.POST.get('password')
    # ボタンが create の場合
        if 'serch' in request.POST:
            if room_name:
                #部屋を探す
                existing_room = Room.objects.filter(name=room_name,password=password).first()
                if existing_room:#部屋が見つかったら
                    return render(request, 'joinSerch_room.html', {'existing_room': existing_room})
                else: #見つからなかったら
                    room = Room.objects.create(name=room_name,password=password)
                    return render(request, 'joinSerch_room.html', {'notfound': "true"})
                    
        
        # ボタンが join の場合
        elif 'join' in request.POST:
            if room_name:
                existing_room = Room.objects.filter(name=room_name).first()
                print(existing_room)
                return redirect('join_room', room_id=existing_room.id)

    return render(request, 'joinSerch_room.html')




def host_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    players = Player.objects.filter(room=room)
    card_in_room = Image_Card.objects.filter(room=room)
    print(card_in_room)
    print(card_in_room.count())
    num_players = players.count()
    if request.method == 'POST':
        print(request.POST)
        if 'oneImage' in request.POST:
            oneImage = request.POST.get('oneImage')
            room.s_one_image = oneImage
        if 'useImage' in request.POST:
            useImage = request.POST.get('useImage')
            room.s_set_image = useImage
        if 'dupeImage' in request.POST:
            dupeImage = request.POST.get('dupeImage')
            room.s_dupe = dupeImage
            room.save()
            return JsonResponse({'result': "sucsess"})

        if 'create_player' in request.POST:
            print("aaaa")
            player_name = request.POST.get('player_name')
            if player_name:
                Player.objects.create(name=player_name,room=room)
                return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})
            else:
                Player.objects.create(name="",room=room)
                return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})
        elif 'delete_player' in request.POST:
            delete_player = request.POST.get("delete_player")
            if delete_player:
                try:
                    player = Player.objects.get(id=delete_player, room=room)
                    player.delete()
                    return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})
                except:
                    print("エラー")
        elif 'delete_player_all' in request.POST:
            try:
                player = Player.objects.filter(room=room)
                print(player)
                player.delete()
                return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})
            except:
                print("エラー")
        elif 'save' in request.POST:
            try:
                s_one_image = request.POST.get('s_one_image')
                s_set_image = request.POST.get('s_set_image')
                s_dupe = request.POST.get('s_dupe')
                room.s_one_image = s_one_image
                room.s_set_image = s_set_image
                room.s_dupe = s_dupe
                room.save()
                return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})
            except :
                print("エラー")
        elif 'game_start' in request.POST:
            getText = request.POST.get('game_start')
            if getText == 'new':
                try:
                    game.Set_Game(room)
                    return JsonResponse({'set_result': "sucsess"})
                except Exception as e:
                    print("エラー", e)
                    return JsonResponse({'set_result': str(e)})
            elif getText == 'data_reset':
                try:
                    game.card_drawn_reset(room)
                    return JsonResponse({'set_result': "sucsess"})
                except Exception as e:
                    print("エラー", e)
                    return JsonResponse({'set_result': str(e)})
            elif getText == 'continue':
                try:
                    return JsonResponse({'set_result': "sucsess"})
                except Exception as e:
                    print("エラー", e)
                    return JsonResponse({'set_result': str(e)})
            else:
                return JsonResponse({'set_result': "not_jsons[text data not send or not programmings not use button]"})


    players = Player.objects.filter(room=room)
    return render(request, 'host_room.html', {'room': room, 'players': players , 'card_in_room':card_in_room})

def join_room(request , room_id):
    your = 0
    room = get_object_or_404(Room, pk=room_id )
    print(str(room_id)+"---")
    content_length = request.META.get('CONTENT_LENGTH', 0)
    print("Request content length:", content_length)
    print(request.POST)
    players = Player.objects.filter(room=room)
    if request.method == 'POST':
        if 'delete' in request.POST:
            delete_ID = request.POST.get('delete')
            your = request.POST.get('your_id')
            your = Player.objects.get(room=room,id=your)
            print(your)
            images = Image_Card.objects.filter(room=room,player=your)
            deleteimage = Image_Card.objects.get(room=room,player=your,id=delete_ID)
            if deleteimage:
                default_storage.delete(deleteimage.image.path)
                # 画像カードの削除
                deleteimage.delete()
            return render(request, 'join_room.html',{'room':room , 'your' :your , 'images_':images})

        if 'select' in request.POST:
            your = request.POST.get('select')
            print(your)
            your = Player.objects.get(room=room,id=your)
            images = Image_Card.objects.filter(room=room,player=your)
            print(images)
            return render(request, 'join_room.html',{'room':room , 'your' :your , 'images_':images})
        if 'save' in request.POST:
            your = request.POST.get('your_id')
            your = Player.objects.filter(id=your).first()
            images = Image_Card.objects.filter(room=room,player=your)
            print(request.POST)
            print(request.FILES)
            database_image = Image_Card.objects.filter(room=room,player=your)
            for i in range(3):
                P_image = request.FILES.get('images'+str(i)) 
                if P_image:                 #imageをwebから受信したら
                    print(i)
                    try:    
                        if database_image[i]: #データベース番号にすでにあるか確認   ある場合の処理
                            db = database_image[i]  
                            # 古い画像を削除
                            if db.image:
                                default_storage.delete(db.image.path)       #既存の画像データは先に削除
                            db.image = P_image
                            db.save()
                    except:     #なかった場合の処理
                        Image_Card.objects.create(room=room,player=your,image=P_image)
            return render(request, 'join_room.html',{'room':room , 'your' :your , 'images_':images})
    your = request.GET.get('your', 0)
    if your != 0:
        your = Player.objects.get(room=room,id=your)
        images = Image_Card.objects.filter(room=room,player=your)
        return render(request, 'join_room.html',{'room':room , 'your':your, 'images_' :images })
    return render(request, 'join_room.html',{'room':room , 'players':players, 'your' :your })

def finish_room(request , room_id):
    your = 0
    room = get_object_or_404(Room, pk=room_id )
    print(str(room_id)+"---")
    content_length = request.META.get('CONTENT_LENGTH', 0)
    print("Request content length:", content_length)
    print(request.POST)
    players = Player.objects.filter(room=room)
    if request.method == 'POST':
        if 'delete' in request.POST:
            delete_ID = request.POST.get('delete')
            your = request.POST.get('your_id')
            your = Player.objects.get(room=room,id=your)
            print(your)
            images = Image_Card.objects.filter(room=room,player=your)
            deleteimage = Image_Card.objects.get(room=room,player=your,id=delete_ID)
    your = request.GET.get('your', 0)
    if your != 0:
        your = Player.objects.get(room=room,id=your)
        images = Image_Card.objects.filter(room=room,player=your)
    return render(request, 'finish.html',{'room':room , 'players':players})

def useto_card_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id )
    select_card = Select_Card.objects.filter(room=room,image_card__use_to = True)
    print(select_card)
    return render(request, 'use_card.html',{'room':room , "select_card":select_card })

def play_game(request,room_id):
    print("受信")
    
def game_room(request,room_id):
    room = get_object_or_404(Room, pk=room_id )
    select_cards = Select_Card.objects.filter(room=room,is_drawn=False)
    drawn_cards = Select_Card.objects.filter(room=room,is_drawn=True) #すでに出たカード
    players = Player.objects.filter(room=room)
    return render(request, 'game_room.html',{'room':room ,'select_cards':select_cards,'players':players,"drawn_cards":drawn_cards})

def startmenu(request):
    return render(request, 'startmenu.html')

def uploadImage(request,room_id):
    room = get_object_or_404(Room, pk=room_id )
    players = Player.objects.filter(room=room)
    your = request.POST.get('your')
    your = Player.objects.filter(id=your).first()

    form_data = request.POST  # フォームデータ
    files = request.FILES.getlist("image")  # アップロードされたファイル
    print(form_data)
    print(files)
    images = Image_Card.objects.filter(room=room,player=your)
    for file in files:
        if file:                 #imageをwebから受信したら
            print(file)
            Image_Card.objects.create(room=room,player=your,image=file)
    # 応答を返す（任意の応答）
    return JsonResponse({'message': 'Upload successful'})


def test(request):
    import sqlite3

    conn = sqlite3.connect("db.sqlite3")  # SQLiteデータベースに接続
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()

    if errors:
        print("Foreign Key Constraint Errors:")
        for error in errors:
            print(error)
    else:
        print("No Foreign Key Constraint Errors Found.")

    conn.close()
    

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def set_drawn(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')

        # データベースの更新
        obj = Select_Card.objects.get(id=card_id)
        obj.is_drawn = True
        obj.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def set_name(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        new_name = request.POST.get('new_name')

        # データベースの更新
        obj = Select_Card.objects.get(id=card_id)
        print(obj)
        obj.image_card.card_name = new_name
        obj.image_card.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def get_card(request):
    if request.method == 'POST':
        # POSTリクエストからJSON形式のデータを取得
        data = json.loads(request.body)
        # data内の必要な情報を取得
        player_ids = data.get('player_id', [])
        card_id = data.get('card_id', None)
        print(player_ids,card_id)

        # データを処理する
        card = Select_Card.objects.get(id=card_id)
        for playerId in player_ids:
            player = Player.objects.get(id=playerId)
            card.get_player.add(player)
        card.save()

        # データベースの更新
        #obj = Select_Card.objects.get(id=card_id)
        #player = Player.objects.get(id=player_id)
        #obj.get_player = player
        #obj.save()#

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})