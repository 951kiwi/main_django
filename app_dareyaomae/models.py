from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    s_player = models.IntegerField(default=4)
    s_one_image = models.IntegerField(default=3)
    s_set_image = models.IntegerField(default=10)
    s_dupe = models.IntegerField(default=5)

    def __str__(self):
        return self.name
    
class Player(models.Model):
    name = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Image_Card(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    player= models.ForeignKey(Player, on_delete=models.CASCADE)
    card_name = models.CharField(blank=True,null=True,max_length=255)
    image = models.ImageField(upload_to='dareyaomae/upload/')
    use_to = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Select_Card(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    image_card = models.ForeignKey(Image_Card, on_delete=models.CASCADE)
    get_player = models.ManyToManyField(Player, blank=True,default=None)
    is_drawn = models.BooleanField(default=False)
    def __str__(self):
        return str(self.room.name)+str(" - ")+str(self.image_card.id)+str("     (")+str(self.id)+str(")")
    

    


@receiver(pre_delete, sender=Image_Card)
def image_card_pre_delete(sender, instance, **kwargs):
    # インスタンスに関連する画像を削除
    if instance.image:
        instance.image.delete()