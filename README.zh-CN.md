# syno-videoinfo-plugin

[![GitHub release](https://img.shields.io/github/v/release/C5H12O5/syno-videoinfo-plugin?logo=github)](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)
![GitHub stars](https://img.shields.io/github/stars/C5H12O5/syno-videoinfo-plugin?logo=github)
![GitHub downloads](https://img.shields.io/github/downloads/C5H12O5/syno-videoinfo-plugin/total?logo=github)
![GitHub top language](https://img.shields.io/github/languages/top/C5H12O5/syno-videoinfo-plugin)
[![GitHub license](https://img.shields.io/github/license/C5H12O5/syno-videoinfo-plugin)](LICENSE)

##### 📖 [English](README.md) | 📖 简体中文

本项目是群晖 Video Station 的第三方视频信息插件，它提供了一种从各大影视数据库平台获取视频元数据的方法。

* 使用Python标准库实现，无需安装任何依赖。
* 支持多个数据来源，并且可以轻松扩展。

## 使用说明

1. 从[此处](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)下载最新版本。
2. 打开 Video Station，进入“设置” > “视频信息插件”。
3. 点击“新增”，选择第一步下载的压缩包，然后点击“确定”。

## 版本要求

* Python 3.7+
* DSM 7.0+
* Video Station 3.0.0+

## 相关文档

* [视频元数据](https://kb.synology.cn/zh-cn/DSM/help/VideoStation/metadata?version=7)
* [Video Station API 文档](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)

> 视频文件命名提示：
>
> 电影：
>
> * 命名格式：电影_名称 (发行_年份).ext
> * 例如：Avatar (2009).avi
>
> 电视节目：
> * 命名格式：电视_节目_名称.SXX.EYY.ext（“S”是“季数”的缩写，“E”是“集数”的缩写）
> * 例如：Gossip Girl.S03.E04.avi

## 如何开发

您可以基于本项目并按以下步骤来开发自己的插件：

1. 将本项目克隆到本地：

```sh
$ git clone https://github.com/C5H12O5/syno-videoinfo-plugin
```

2. 根据需要修改代码，并可以使用以下命令进行测试：

```sh
$ python main.py --type movie --input "{\"title\":\"{movie title}\"}" --limit 1 --loglevel debug
```

3. 然后可以使用以下命令进行打包并上传使用：

```sh
$ python setup.py sdist --formats=zip
```

## 使用许可

[Apache-2.0 license](LICENSE)