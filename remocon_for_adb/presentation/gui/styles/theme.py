"""
GUI Theme and Styles
Android TV リモコンGUIのテーマとスタイル定義
"""

# カラーパレット
COLORS = {
    'primary': '#007ACC',      # メインブルー
    'primary_dark': '#005A9F', # ダークブルー
    'secondary': '#4A90E2',    # セカンダリブルー
    'accent': '#FFC107',       # アクセントカラー（アンバー）
    'background': '#2D2D30',   # ダークグレー背景
    'surface': '#3E3E42',      # サーフェスグレー
    'text': '#FFFFFF',         # ホワイトテキスト
    'text_secondary': '#CCCCCC', # セカンダリテキスト
    'success': '#4CAF50',      # 成功グリーン
    'error': '#F44336',        # エラーレッド
    'warning': '#FF9800',      # 警告オレンジ
    'button_normal': '#4A4A4F',  # ボタン通常色
    'button_hover': '#5A5A5F',   # ボタンホバー色
    'button_pressed': '#6A6A6F'  # ボタン押下色
}

# フォント設定
FONTS = {
    'default': ('Segoe UI', 10),
    'title': ('Segoe UI', 12, 'bold'),
    'button': ('Segoe UI', 9),
    'status': ('Segoe UI', 8),
    'small': ('Segoe UI', 8)
}

# サイズ設定
SIZES = {
    'window_width': 450,   # タブ分少し幅を拡張
    'window_height': 650,  # 適切な高さに調整
    'button_direction': (60, 40),   # 方向キーボタン
    'button_action': (80, 40),      # アクションボタン
    'button_large': (120, 40),      # 大きなボタン
    'padding': 10,
    'margin': 5
}

# ボタンスタイル
BUTTON_STYLE = {
    'relief': 'raised',
    'borderwidth': 2,
    'font': FONTS['button'],
    'fg': COLORS['text'],
    'bg': COLORS['button_normal'],
    'activebackground': COLORS['button_hover'],
    'activeforeground': COLORS['text']
}

# 方向キーボタンスタイル
DIRECTION_BUTTON_STYLE = {
    **BUTTON_STYLE,
    'width': 8,
    'height': 2,
    'font': FONTS['button']
}

# アクションボタンスタイル
ACTION_BUTTON_STYLE = {
    **BUTTON_STYLE,
    'width': 10,
    'height': 2,
    'font': FONTS['button']
}

# プライマリボタンスタイル
PRIMARY_BUTTON_STYLE = {
    **BUTTON_STYLE,
    'bg': COLORS['primary'],
    'activebackground': COLORS['primary_dark']
}

# ラベルスタイル
LABEL_STYLE = {
    'font': FONTS['default'],
    'fg': COLORS['text'],
    'bg': COLORS['background']
}

# タイトルラベルスタイル
TITLE_LABEL_STYLE = {
    'font': FONTS['title'],
    'fg': COLORS['text'],
    'bg': COLORS['background']
}

# ステータスラベルスタイル
STATUS_LABEL_STYLE = {
    'font': FONTS['status'],
    'fg': COLORS['text_secondary'],
    'bg': COLORS['background']
}

# フレームスタイル
FRAME_STYLE = {
    'bg': COLORS['background'],
    'relief': 'flat',
    'borderwidth': 1
}

# メインフレームスタイル
MAIN_FRAME_STYLE = {
    'bg': COLORS['surface'],
    'relief': 'raised',
    'borderwidth': 2,
    'padx': SIZES['padding'],
    'pady': SIZES['padding']
}

def apply_button_hover_effects(button, normal_bg, hover_bg, pressed_bg):
    """ボタンにホバー効果を適用"""
    def on_enter(event):
        button.config(bg=hover_bg)
    
    def on_leave(event):
        button.config(bg=normal_bg)
    
    def on_press(event):
        button.config(bg=pressed_bg)
    
    def on_release(event):
        button.config(bg=hover_bg)
    
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    button.bind('<Button-1>', on_press)
    button.bind('<ButtonRelease-1>', on_release)
