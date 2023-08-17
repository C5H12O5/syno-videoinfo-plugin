# syno-videoinfo-plugin

[![GitHub release](https://img.shields.io/github/v/release/C5H12O5/syno-videoinfo-plugin?logo=github)](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)
![GitHub stars](https://img.shields.io/github/stars/C5H12O5/syno-videoinfo-plugin?logo=github)
![GitHub downloads](https://img.shields.io/github/downloads/C5H12O5/syno-videoinfo-plugin/total?logo=github)
![GitHub top language](https://img.shields.io/github/languages/top/C5H12O5/syno-videoinfo-plugin)
[![GitHub license](https://img.shields.io/github/license/C5H12O5/syno-videoinfo-plugin)](LICENSE)

##### 📖 English | 📖 [简体中文](README.zh-CN.md)

This project is a video information plugin for Synology Video Station. It provides a way to fetch metadata from websites
other than the default ones.

* Implemented in Python without any third-party dependencies.
* Supports multiple sources, and can be easily extended to support more.
* Has a simple configuration page where you can customize your plugin.

## Usage

Install the plugin:

1. Download the latest release from [**here**](https://github.com/C5H12O5/syno-videoinfo-plugin/releases).
2. Open your Video Station, go to ***Settings*** > ***Video Info Plugin***.
3. Click ***Add***, select the downloaded file, and click ***OK***.

Configure the plugin:

1. Open your browser, go to `http://[NAS_IP]:5125` (replace `[NAS_IP]` with your NAS IP address).
2. Change the configuration as you want, and click ***Save Button*** in the upper right corner.
3. Go back to your Video Station, the configuration should be applied automatically.

## Requirements

* Python 3.7+
* DSM 7.0+
* Video Station 3.0.0+

## References

* [The Video Station Metadata](https://kb.synology.com/en-id/DSM/help/VideoStation/metadata?version=7)
* [The Video Station API documentation](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)

> Tips for naming video files:
>
> Movie:
>
> * Naming format: Movie_Name (Release_Year).ext
> * Example: Avatar (2009).avi
>
> TV Show:
> * Naming format: TV_Show_Name.SXX.EYY.ext (***S*** as a shorthand for ***Season*** and ***E*** for ***Episode***)
> * Example: Gossip Girl.S03.E04.avi

## Development

You can develop your own plugin based on this project easily. Here are the steps:

1. Clone this repository to your local machine:

```sh
$ git clone https://github.com/C5H12O5/syno-videoinfo-plugin
```

2. Modify the code as you want, and test it like this:

```sh
$ python main.py --type movie --input "{\"title\":\"{movie_title}\"}" --limit 1 --loglevel debug
```

3. Package the plugin using the following command:

```sh
$ python setup.py sdist --formats=zip
```

## License

[Apache-2.0 license](LICENSE)