[app]
title = Neon Space Defender
package.name = neonspacedefender
package.domain = com.spacegames
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy,android
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png
orientation = portrait
fullscreen = 1

# Android-specific settings
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.arch = armeabi-v7a

# Google Play settings
android.gradle_dependencies = 
android.add_src =

# Это позволит приложению писать логи
android.logcat_filters = *:S python:D

# Gradle версия
p4a.source_dir = 

[buildozer]
log_level = 2
warn_on_root = 1
