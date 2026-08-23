from django.contrib import admin
from .models import Device, Command, Card
from django.utils.safestring import mark_safe
from django import forms

# =========================================
# Deviceごとのコマンド定義
# =========================================

COMMANDS = {

    "tv": [
        ("電源ON", "turnOn", "default"),
        ("電源OFF", "turnOff", "default"),
        ("1", "SetChannel", "1"),
        ("2", "SetChannel", "2"),
        ("3", "SetChannel", "3"),
        ("4", "SetChannel", "4"),
        ("5", "SetChannel", "5"),
        ("6", "SetChannel", "6"),
        ("7", "SetChannel", "7"),
        ("8", "SetChannel", "8"),
        ("9", "SetChannel", "9"),
        ("0", "SetChannel", "0"),
        ("音量＋", "volumeAdd", "default"),
        ("音量－", "volumeSub", "default"),
    ],

    "light": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
    ],

    "light_detail": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
        ("明るく", "brightnessUp", "default"),
        ("暗く", "brightnessDown", "default"),
    ],

    "aircon": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
        ("温度＋", "setAll", "default"),
        ("温度－", "setAll", "default"),
    ],

    "concent": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
    ],

    "PC": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
    ],

    "remote": [
        ("ON", "turnOn", "default"),
        ("OFF", "turnOff", "default"),
    ],
}

# デバイスタイプごとのコマンド設定ガイド
COMMAND_GUIDES = {
    "light": """
        <strong>💡 ライト向け推奨コマンド設定:</strong><br>
        ・<code>ON</code> (command_type: command, command: turnOn, param: default)<br>
        ・<code>OFF</code> (command_type: command, command: turnOff, param: default)<br>
        ・<code>bright-up</code> (command_type: command, command: brightnessUp), <code>brightnessDown</code> (command_type: command, command: brightnessDown)<br>
        ・<code>other</code> (command_type: customize, command: name, param: default)<br>
        ・<code>other\\worm</code> (command_type: customize, command: name, param: default)<br>
        ・<code>other\\cold</code> (command_type: customize, command: name, param: default)<br>
        ・<code>other\\scene</code> (command_type: customize, command: name, param: default)<br>
        ・<code>other\\night-loght</code> (command_type: customize, command: name, param: default)<br>
        ・<code>other\\timer-30</code> (command_type: customize, command: name, param: default)<br>
    """,
    "light_detail": """
        <strong>✨ 詳細ライト向け推奨コマンド設定:</strong><br>
        ・<code>turnOn</code>, <code>turnOff</code><br>
        ・<code>setBrightness</code> (param: 1~100)<br>
        ・<code>setColorTemp</code> (param: 2700~6500)<br>
        ・<code>setColor</code> (param: #HEXカラー)
    """,
    "aircon": """
        <strong>❄️ エアコン向け推奨コマンド設定:</strong><br>
        ・<code>ON</code>, <code>OFF</code><br>
        ・<code>setAll</code> (param: 25,2,1,on -> 温度,モード,風量,電源)
    """,
    "tv": """
        <strong>📺 テレビ向け推奨コマンド設定:</strong><br>
        ・<code>power</code>, <code>vol_up</code>, <code>vol_down</code>, <code>ch_up</code>, <code>ch_down</code><br>
        ・<code>ch_1</code> ~ <code>ch_12</code>
    """,
    "PC": """
        <strong>💻 パソコン向け推奨設定:</strong><br>
        ・<code>boot</code> (WoLパケット), <code>shutdown</code> (RPC / SSH)
    """,
    "concent": """
        <strong>🔌 コンセントプラグ向け推奨設定:</strong><br>
        ・<code>turnOn</code>, <code>turnOff</code>
    """,
    "remote": """
        <strong>📡 汎用リモコン向け設定:</strong><br>
        ・任意の登録名とSwitchBotコマンドキーを設定してください。
    """
}
# =========================================
# Command Inline
# =========================================

class CommandInline(admin.TabularInline):

    model = Command

    extra = 0

    fields = (
        "name",
        "command_type",
        "command",
        "parameter",
    )


# =========================================
# Device
# =========================================
# 1. 編集画面用のフォーム（チェックボックス化）
class DeviceAdminForm(forms.ModelForm):
    features = forms.MultipleChoiceField(
        choices=Device.FEATURE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="対応機能"
    )

    class Meta:
        model = Device
        fields = '__all__'


# 2. 管理画面の登録
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm

    list_display = (
        "name",
        "device_type",
        "device_id",
        "display_features",  # 一覧に表示
        "show_commands",
    )
    readonly_fields = ("command_guide_box",)

    fieldsets = (
        ("基本情報", {
            "fields": ("name", "device_type", "device_id", "features")
        }),
        ("コマンド設定ガイド", {
            "fields": ("command_guide_box",),
            "description": "選択したデバイス種別に応じて、必要なコマンドの登録ルールが表示されます。"
        }),
    )

    inlines = [
        CommandInline,
    ]
    def command_guide_box(self, obj=None):
        """デバイス種別に応じた説明HTMLを出力"""
        current_type = obj.device_type if obj else "light"
        guide_text = COMMAND_GUIDES.get(current_type, "コマンド一覧を設定してください。")

        return mark_safe(f"""
            <div id="type-guide-display" style="
                padding: 12px 16px;
                background: #f8fafc;
                border-left: 4px solid #008cff;
                border-radius: 4px;
                color: #334155;
                font-size: 13px;
                line-height: 1.6;
            ">
                {guide_text}
            </div>
        """)

    command_guide_box.short_description = "登録のヒント"

    def display_features(self, obj):
        # 機能キーと表示名の対応マップ
        feature_dict = dict(Device.FEATURE_CHOICES)
        
        # 選択された機能ラベルのリストを作成
        selected_labels = [feature_dict.get(k, k) for k in (obj.features or [])]
        
        if not selected_labels:
            return "未設定"

        # デバイスタイプ別の表示名（例: 'ライト'）
        type_label = obj.get_device_type_display()

        # 「ライトの場合：常夜灯、シーン切り替え」の形式で出力
        return f"{type_label}の場合：{', '.join(selected_labels)}"
    
    display_features.short_description = "対応機能"

    def show_commands(self, obj):
        return ", ".join(
            command.name
            for command in obj.commands.all()
        )

    show_commands.short_description = "コマンド"


# =========================================
# Command
# =========================================

@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "device",
        "command_type",
        "command",
    )

    list_filter = (
        "device",
    )


# =========================================
# Card
# =========================================

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "device",
        "x",
        "y",
        "width",
        "height",
    )