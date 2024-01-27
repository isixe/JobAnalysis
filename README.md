<div align=center>
    <img style="text-align:center" src="https://raw.githubusercontent.com/isixe/JobAnalysis/main/static/img/logo/favicon.svg" width=20%  alt="favicon.ico"/>
    <h1>JobAnalysis</h1>
    <p>基于 Flask 的招聘工作数据分析，数据可视化使用 matplotlib，界面基于 <a href="https://github.com/creativetimofficial/material-dashboard">material-dashboard</p>
</div>

# 预览
![主页](https://github.com/isixe/JobAnalysis/blob/main/doc/img/home.png?raw=true)

![数据爬取](https://github.com/isixe/JobAnalysis/blob/main/doc/img/spider.png?raw=true)

![数据分析](https://github.com/isixe/JobAnalysis/blob/main/doc/img/analysis.png?raw=true)

# 环境要求
本项目使用 Edge 执行数据爬取操作，请确保已安装 Edge
```
Edge
attrs==23.1.0
beautifulsoup4==4.12.2
blinker==1.7.0
certifi==2023.11.17
cffi==1.16.0
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
colorlog==6.8.0
contourpy==1.2.0
cycler==0.12.1
et-xmlfile==1.1.0
fake-useragent==1.4.0
Flask==3.0.0
fonttools==4.46.0
greenlet==3.0.2
h11==0.14.0
idna==3.6
itsdangerous==2.1.2
jieba==0.42.1
Jinja2==3.1.2
kiwisolver==1.4.5
MarkupSafe==2.1.3
matplotlib==3.8.2
mypy-extensions==1.0.0
numpy==1.26.2
openpyxl==3.1.2
outcome==1.3.0.post0
packaging==23.2
pandas==2.1.3
Pillow==10.1.0
prettytable==3.9.0
pycparser==2.21
pyecharts==2.0.4
pyparsing==3.1.1
PySocks==1.7.1
python-dateutil==2.8.2
python-dotenv==1.0.0
pytz==2023.3.post1
requests==2.31.0
scipy==1.11.4
selenium==4.15.2
simplejson==3.19.2
six==1.16.0
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
SQLAlchemy==2.0.23
trio==0.23.1
trio-websocket==0.11.1
typing_extensions==4.9.0
tzdata==2023.3
urllib3==2.1.0
wcwidth==0.2.12
webdriver-manager==4.0.1
Werkzeug==3.0.1
wordcloud==1.9.3
wsproto==1.2.0
```
# 运行 (Pycharm)
启动 web/app.py

# 项目结构
```
├─function 
│ ├─clean 
│ │ ├─jobcleaner51.py                       --清洗-工作数据
│ │ └─__init__.py 
│ ├─spider 
│ │ ├─area 
│ │ │ ├─areaspider51.py                     --爬取-地区数据
│ │ │ └─__init__.py 
│ │ ├─jobspider51.py                        --爬取-工作数据
│ │ └─__init__.py 
│ └─_init__.py 
├─LICENSE 
├─log 
│ ├─handler_logger.py                       --日志处理器
│ ├─__init__.py 
├─output                                    --文件输出
│ ├─area 
│ │ ├─51area.csv 
│ │ └─51area.db 
│ ├─clean 
│ │ ├─51job.csv 
│ │ └─51job.db 
│ ├─export 
│ │ ├─51job.csv 
│ │ └─51job.xlsx 
│ └─job 
│   ├─51job.csv 
│   └─51job.db 
├─README.md 
├─requirements.txt 
├─static 
├─templates 
│ ├─index.html                               --主页
│ └─pages 
│   ├─analysis.html                          --可视化页
│   ├─data_clean.html                        --数据清洗页
│   ├─data_show.html                         --数据展示页
│   ├─data_spider.html                       --数据爬取页
│   ├─sign_in.html                           --登录
│   └─sign_up.html                           --注册
├─test                                       --测试
│ ├─cleaner_test.py 
│ └─spider_test.py 
└─web 
  ├─app.py                                   --启动入口
  ├─identifier.sqlite 
  ├─models                                   --实体
  │ ├─result.py 
  │ ├─user.py 
  │ └─___init__.py 
  ├─utils                                    --工具类
  │ ├─database_builder.py 
  │ ├─matplotlib_drawer.py 
  │ └─___init__.py 
  ├─views                                    --视图
  │ ├─analysis.py                            --数据分析
  │ ├─auth.py                                --登录授权
  │ ├─clean.py                               --数据清洗
  │ ├─index.py                               --主页
  │ ├─show.py                                --数据展示
  │ ├─spider.py                              --数据爬取
  │ └─___init__.py 
  ├─__init__.py 
```
