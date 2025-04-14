#!/bin/bash

# 清理之前的构建文件
rm -rf build dist
rm -rf icon.iconset icon.icns

# 创建图标
mkdir icon.iconset
sips -z 16 16   source.png --out icon.iconset/icon_16x16.png
sips -z 32 32   source.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32   source.png --out icon.iconset/icon_32x32.png
sips -z 64 64   source.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 source.png --out icon.iconset/icon_128x128.png
sips -z 256 256 source.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 source.png --out icon.iconset/icon_256x256.png
sips -z 512 512 source.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 source.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 source.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset

# 使用 PyInstaller 打包应用
pyinstaller build_mac_arm64.spec

# 检查打包是否成功
if [ -d "dist/简历匹配分析工具.app" ]; then
    echo "打包成功！应用程序位于 dist/简历匹配分析工具.app"
    
    # 签名应用程序
    echo "正在签名应用程序..."
    codesign --force --deep --sign - "dist/简历匹配分析工具.app"
    
    # 删除已存在的DMG文件
    rm -f "dist/简历匹配分析工具-arm64.dmg"
    
    # 创建DMG文件
    echo "正在创建DMG文件..."
    create-dmg \
        --volname "简历匹配分析工具" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "简历匹配分析工具.app" 200 190 \
        --hide-extension "简历匹配分析工具.app" \
        --app-drop-link 600 185 \
        "dist/简历匹配分析工具-arm64.dmg" \
        "dist/简历匹配分析工具.app"
    
    if [ -f "dist/简历匹配分析工具-arm64.dmg" ]; then
        echo "DMG文件创建成功！位于 dist/简历匹配分析工具-arm64.dmg"
        # 设置DMG文件权限
        chmod 644 "dist/简历匹配分析工具-arm64.dmg"
    else
        echo "DMG文件创建失败！"
        exit 1
    fi
    
    # 清理临时文件
    rm -rf icon.iconset icon.icns
else
    echo "打包失败！"
    exit 1
fi 