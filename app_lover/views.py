from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import Selection,Video
from django.conf import settings
import requests
import re
from django.core.paginator import Paginator
from django.http import JsonResponse
import os
from bs4 import BeautifulSoup
import random
#ハーゲンダッツのjancodeリスト
urls = ['https://www.jancode.xyz/corp/?c=29119','https://www.jancode.xyz/corp/?c=29119&p=2',
       'https://www.jancode.xyz/corp/?c=29119&p=3','https://www.jancode.xyz/corp/?c=29119&p=4'
       ,'https://www.jancode.xyz/corp/?c=29119&p=5','https://www.jancode.xyz/corp/?c=29119&p=6'
       ,'https://www.jancode.xyz/corp/?c=29119&p=7']
base_url = "https://www.jancode.xyz" 
# ヘッダー情報（アクセスブロックを回避するため）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def parse_line_talk(file_path):
    messages = []
    current_date = ""
    current_message = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if re.match(r'^R\d+/\d{2}/\d{2}', line):
                current_date = line
            elif re.match(r'^\d{2}:\d{2}\t', line):
                if current_message:
                    messages.append(current_message)
                parts = line.split('\t')
                if len(parts) >= 3:
                    time, name, content = parts[0], parts[1], '\t'.join(parts[2:])
                    current_message = {
                        'name': name,
                        'time': f"{current_date} {time}",
                        'content': content
                    }
            else:
                if current_message:
                    current_message['content'] += '\n' + line

    if current_message:
        messages.append(current_message)

    return messages

# 初期表示用
def talk_list_view(request):
    return render(request, 'lover/talk_list.html')

def get_page_date(request):
    file_path = os.path.join(settings.BASE_DIR, 'static', 'lover', 'Line', '[LINE]トーク.txt')
    all_messages = parse_line_talk(file_path)

    # 時系列順に並べ替える（すでに並んでいるなら不要）
    all_messages.reverse()

    # R7/05/01 を含む「最後の」メッセージを探す
    target_date = request.GET.get('date')
    index = next((len(all_messages) - 1 - i for i, msg in enumerate(reversed(all_messages)) if target_date in msg["time"]), None)


    if index is None:
        return JsonResponse({'error': 'R7/05/01 の投稿が見つかりませんでした'}, status=404)

    # 100件ごとのページ番号
    page = index // 100 + 1
    return JsonResponse({'page': page})

# Ajaxでページごと取得
def talk_api(request):
    page = int(request.GET.get('page', 1))
    direction = request.GET.get('direction', 'past')  # 'past' または 'future'

    file_path = os.path.join(settings.BASE_DIR, 'static', 'lover', 'Line', '[LINE]トーク.txt')
    all_messages = parse_line_talk(file_path)
    all_messages.reverse()  # 最新が後ろ
    # future のときはそのまま（新しい順）

    paginator = Paginator(all_messages, 100)
    page_obj = paginator.get_page(page)
    data = list(page_obj.object_list)
    return JsonResponse({'messages': data, 'has_next': page_obj.has_next()})

def phone_view(request):
    # 最初のSelectionオブジェクトを取得
    selection = Selection.objects.first()
    if selection.game06:
        return redirect("kiwitok")
    if request.method == "POST":
        data = request.POST.get("message")
        if(data == "Q01=True"):
            selection.game01 = True
            selection.save()
        if(data == "Q02=True"):
            selection.game02 = True
            selection.save()
        ##if(data == "Q03=True"): 使わない
        ##    selection.game03 = True
        ##    selection.save()
        if(data == "Q04=True"):
            selection.game04 = True
            selection.save()
        if(data == "Q05=True"):
            selection.game05 = True
            selection.save()
        if(data == "Q06=True"):
            selection.game06 = True
            selection.save()
        if(data == "Q04=Jan"):
            jancode = request.POST.get("jancode")
            # ページの取得
            print(jancode)
            # ページの取得
            for url in urls:
                response = requests.get(url, headers=headers)
                response.encoding = 'utf-8'  # 文字エンコーディングの設定
                # BeautifulSoupでHTMLを解析
                soup = BeautifulSoup(response.text, 'html.parser')
                # 商品情報を取得
                results = soup.find_all("div", class_="result-box-out m15-b")
                for result in results:
                    # JANコードの取得
                    jan_element = result.find("h4", class_="title")
                    if jan_element:
                        jan_code = jan_element.text.replace("JANコード:", "").strip()
                    else:
                        jan_code = "不明"
                    # 商品名の取得
                    description = result.find("p", class_="description")
                    if description:
                        text_content = description.get_text(strip=True)
                        img_tag = description.find("img")
                        if img_tag and img_tag.has_attr('src'):
                            img_url = base_url + img_tag['src']
                        else:
                            img_url = None 
                    else:
                        text_content = "不明"
                    if(jan_code == jancode):
                        return JsonResponse({"status": "success", "name": text_content , "image_url": img_url})
                    print(f"JANコード: {jan_code}, 商品名: {text_content}")
        else:
            return JsonResponse({"status": "error"})  # JSONレスポンスを返す
        return JsonResponse({"status": "success"})  # JSONレスポンスを返す
        

    if(selection.login == True):
        if(selection.gamestart == True):
            return render(request, 'lover/phone_Q.html',context={"data":selection})
        return render(request, 'lover/phone_sucsess.html',context={"data":selection})
    return render(request, 'lover/phone.html')

def Q3_QR(request):
    selection = Selection.objects.first()
    selection.game03 = True
    selection.save()
    return render(request, 'lover/Q3_QRload.html',context={"data":selection})

def PC_view(request):
    selection = Selection.objects.first()
    if request.method == "POST":
        data = request.POST.get("message")
        print(data)
        if(data == "gamestart"):
            selection.gamestart = True
            selection.save()
        return JsonResponse({"status": "success"})  # JSONレスポンスを返す

    if(selection.login == True):
        if(selection.gamestart == True):
            return render(request, 'lover/PC_startgame.html',context={"data":selection})
        return render(request, 'lover/PC_main01.html')
    return render(request, 'lover/PC_main.html')



def kiwitok(request):
    selection = Selection.objects.first()
    if selection.game06 == False or selection.game05 == False or selection.game04 == False :
        return render(request, 'lover/kiwitok_pre.html')
    
    if request.method == "POST":
        data = request.POST.get("message")
        video = request.POST.get("video")
        if(data == "like"):
            video = Video.objects.get(id=int(video)) 
            video.likes = video.likes + 1
            video.save()
            return JsonResponse({"status": "success", "likes": video.likes})
    videos = list(Video.objects.all())
    random.shuffle(videos)  # ランダムに並び替え
    return render(request, 'lover/tiktok.html', {'videos': videos})

def phone_name_birthday(request):
    if request.method == 'POST':
        # フォームからデータを取得
        name = request.POST.get('name')
        birth_date = request.POST.get('birth_date')
        # 最初のSelectionオブジェクトを取得
        selection = Selection.objects.first()

        if selection:
            selection.name = name
            selection.birth_date = birth_date
            selection.login = True
            selection.save()
    return redirect('phone')

def phone_data_save(request):
    if request.method == 'POST':
        # フォームからデータを取得
        gamestart = request.POST.get('gamestart')
        game01 = request.POST.get('game01')
        game02 = request.POST.get('game02')
        game03 = request.POST.get('game03')
        game04 = request.POST.get('game04')
        game05 = request.POST.get('game05')
        game06 = request.POST.get('game06')
        # 最初のSelectionオブジェクトを取得
        selection = Selection.objects.first()

        if selection:
            if(gamestart):
                selection.gamestart = gamestart
            if(game01):
                selection.game01 = game01
            if(game02):
                selection.game02 = game02
            if(game03):
                selection.game03 = game03
            if(game04):
                selection.game04 = game04
            if(game05):
                selection.game05 = game05
            if(game06):
                selection.game06 = game06
            
            selection.save()
    return redirect('phone')


def get_data(request):
    data = Selection.objects.first()
    response_data = {
        "id": data.id,
        "name": data.name,
        "login": data.login,
        "gamestart":data.gamestart,
        "game01": data.game01,
        "game02": data.game02,
        "game03": data.game03,
        "game04": data.game04,
        "game05": data.game05,
        "game06": data.game06,
    }
    return JsonResponse(response_data)
