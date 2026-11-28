# src/game.html（Claudeのページと同じもの）から、公開用の index.html を作る
# 使い方：リポジトリのいちばん上で  python3 src/make_site.py
import os
here = os.path.dirname(os.path.abspath(__file__))
h = open(os.path.join(here, 'game.html'), encoding='utf-8').read()
h = h.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
head = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n<meta name="theme-color" content="#0b0a1a">\n'
        '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">\n<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n<meta name="apple-mobile-web-app-title" content="スフィアライズ">\n'
        '<meta name="description" content="オリジナルの対戦カードゲーム「スフィアライズ」の試作版。">\n')
open(os.path.join(here, '..', 'index.html'), 'w', encoding='utf-8').write(head + h + '\n</html>\n')
print('index.html を作りました')
