[app]
title = UNO Счетчик
package.name = unocounter
package.domain = com.yourname
source.dir = .

presplash.filename = %(source.dir)s/assets/textures/icon.png
icon.filename = %(source.dir)s/assets/textures/icon.png

source.include_exts = py,png,jpg,kv,atlas,wav,mp3,ogg,ttf
source.exclude_exts = spec

version = 1.0.5

requirements = python3,kivy

android.icon = icon.png
android.orientation = user
android.manifest_orientation = unspecified
android.permissions = INTERNET, VIBRATE

# Использовать последнюю версию python-for-android
android.p4a_branch = master
android.ndk = 25c
android.api = 31
android.minapi = 21

# Использовать старую версию p4a (совместимую с Python 3.12)
android.p4a_commit = v2023.10.10

android.add_src = assets

[buildozer]
log_level = 2
warn_on_root = 1