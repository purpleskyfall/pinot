# Pinot

## Pinot 简介

Pinot（Pinot is not only TEQC） 是一系列使用 Python3 语言开发的脚本，主要用于对 GNSS 静态数据进行批量处理，特别适合处理 CORS 站静态数据。

Pinot 部分脚本依赖于 [TEQC][1] 或 [runpkr00][2] 程序，并且需要 PyYAML 模块的支持。具备以下功能：

- 批量将原始观测数据转化为 RINEX 2.11；
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
- leica2rnx.py
- low2upper.py
- metacheck.py
- orderfiles.py
- qualitycheck.py
- sitecheck.py
- subnet.py
- trimble2rnx.py
- unificate.py
- up2lower.py

## 作者信息

Developer by: Jon Jiang & Maosheng Zhou

First upload: 2017-01-20

[1]: https://www.unavco.org/software/data-processing/teqc/teqc.html
[2]: http://kb.unavco.org/kb/article/trimble-runpkr00-v5-40-latest-version-mac-osx-10-7-windows-xp-7-linux-solaris-744.html
[3]: http://www-gpsg.mit.edu/~simon/gtgk/