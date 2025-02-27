from .models import Room, Player,Image_Card,Select_Card
import random

def Set_Game(room):     #ゲームを初期化して、新しく0のゲームデータを作る
    use_quantity = room.s_set_image
    print("startが押されました" + str(use_quantity))
    card_name_reset(room)
    select_card_reset(room)
    card_useto_reset(room)

    room_image_card = Image_Card.objects.filter(room=room)
    room_image_card = list(room_image_card)
    if len(room_image_card) < use_quantity:
        print("エラー、カードの枚数が足りないです。")
    else:
        random_subset = random.sample(room_image_card, use_quantity)
        for card in random_subset:
            card.use_to = True
            card.save()
            for i in range(room.s_dupe):
                Select_Card.objects.create(room=room,image_card=card)
            
            
def card_name_reset(room):
    print("Image_cardの名前をすべてリセットします")
    image_cards = Image_Card.objects.filter(room=room)
    for card in image_cards:
        card.card_name = None
        card.save()  # 保存を忘れずに

def select_card_reset(room):    #選択カードのデータベースをルーム単位ですべて消す
    print("選択カードをresetします")
    select_card = Select_Card.objects.filter(room=room).delete()

def card_name_reset(room):      #カードの名前をデータベースをルーム単位ですべて消す
    print("Image_cardの名前をすべてリセットします")
    image_cards = Image_Card.objects.filter(room=room)
    Image_Card.objects.filter(room=room).update(card_name=None)

def card_useto_reset(room):     #use_toのデータベースをルーム単位ですべて初期化する
    print("Image_cardの使用履歴をすべてfalseにします")
    image_cards = Image_Card.objects.filter(room=room)
    for card in image_cards:
        card.use_to = False
        card.save()  # 保存を忘れずに

def card_drawn_reset(room):
    card_name_reset(room)
    print("Image_cardの使用履歴をすべてfalseにします")
    image_cards = Select_Card.objects.filter(room=room)
    for card in image_cards:
        card.is_drawn = False
        card.save()  # 保存を忘れずに
