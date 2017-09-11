# Pinot

## Pinot 简介
Pinot（Pinot is not only TEQC） 是一系列使用 Python3 语言开发的脚本，主要用于对 GNSS 静态数据进行批量处理，特别适合处理 CORS 站静态数据。

Pinot 部分脚本依赖于 [TEQC][1] 、[RNXCMP][2] 或 [runpkr00][3] 程序，并且需要 PyYAML 模块的支持。具备以下功能：

- 批量将原始观测数据转化为 RINEX 2.11；
- 批量将数据在 RINEX 与 Compact RINEX 之间转化；
- 批量检查站点的缺失情况；
- 批量对站点数据进行重命名；
- 批量检查站点观测信息；
- 批量对数据做观测质量分析；
- 批量进行数据标准化；
- 批量将数据整理为 IGS 站的组织方式；
- 批量进行用于数据解算前的子网划分；
- 批量拷贝 GAMIT/GLOBK 程序的数据解算成果。

Pinot 程序包目前包含以下脚本：

- copyresult.py
- crnx2rnx.py
- leica2rnx.py
- low2upper.py
- metacheck.py
- orderfiles.py
- qualitycheck.py
- renamesite.py
- rnx2crnx.py
- sitecheck.py
- subnet.py
- trimble2rnx.py
- unificate.py
- up2lower.py

## 依赖模块
部分脚本依赖于 [PyYAML][4] 或 [tqdm][5] 模块，PyYAML 是一个解析 YAML 数据的程序包，而 tqdm 是一个在命令行界面显示进度条的软件包。使用以下命令安装 tqdm 模块：

```
$ pip install tqdm
```

PyYAML 程序包安装，请参考博文：[PyYAML 安装与使用演示][6]。

## 文档索引
Pinot 脚本文档请移步：[Pinot 脚本文档索引目录][7]。

## 作者信息
Develop by: Jon Jiang & Maosheng Zhou

First upload: 2017-01-20

## 使用授权
基于 GPLv2 协议，详情请参考 LICENSE。

[1]: https://www.unavco.org/software/data-processing/teqc/teqc.html
[2]: http://terras.gsi.go.jp/ja/crx2rnx.html
[3]: http://kb.unavco.org/kb/article/trimble-runpkr00-v5-40-latest-version-mac-osx-10-7-windows-xp-7-linux-solaris-744.html
[4]: http://pyyaml.org/
[5]: https://pypi.python.org/pypi/tqdm
[6]: http://gnss.help/2016/12/01/install-pyyaml/
[7]: http://gnss.help/2017/02/16/pinot-content/