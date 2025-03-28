from django.contrib.auth import login
import random
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .form import CustomAuthenticationForm
from .models import Link
# Create your views here.


def main_page(request):
    if request.user.is_authenticated:
        # ログインしているユーザーに関連するリンクを取得
        user_links = Link.objects.filter(users=request.user)
    else:
        # ログインしていない場合、関連なしのリンクだけを表示
        user_links = Link.objects.none()  # 空のクエリセットにする

    # ログインしていないユーザーにも表示されるリンク（usersフィールドに何も設定されていないリンク）
    public_links = Link.objects.filter(users__isnull=True)

    # 全てのリンク（ユーザーに関連するもの、関連しないもの）
    links = user_links | public_links

    links = links.order_by("rank").distinct()  # 重複を排除して並べ替え

    return render(request, 'main.html', {'links': links})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 登録後にログイン
            return redirect('/')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main_page')  # ログイン後のリダイレクト先
            else:
                form.add_error(None, "無効なユーザー名またはパスワードです。")
    else:
        form = CustomAuthenticationForm()  # GETリクエスト時は新しいフォームを表示
    # 静的ファイルのディレクトリパスを取得
    image_folder = os.path.join(settings.BASE_DIR, 'static', 'main', 'backgraundImages')
    # ディレクトリ内の全てのファイルを取得
    images = [img for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    # 画像が存在すればランダムに選択
    if images:
        selected_image = random.choice(images)
        image_path = os.path.join('main', 'backgraundImages', selected_image)  # テンプレートに渡すパス
    else:
        image_path = None  # 画像が無い場合の処理
        
    return render(request, 'accounts/login.html', {'form': form ,'image_path': image_path})