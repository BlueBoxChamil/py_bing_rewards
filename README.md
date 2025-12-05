# 如何配置bing-rewards

> [!tip]
>
> ## 网页端的配置
>
> 1. 下载并安装python3.10.13，至少3.10往上，具体可以参考github上bing-rewards的环境要求
>
> 2. 下载google浏览器，把需要刷分的账户都以本地账户的形式登录，并且进入www.bing.com中登入自己的微软bing账号。本地账号任意取名，bing账号是有账号密码的。
>
> 3. 进入路径`C:\Users\28304\AppData\Local\Google\Chrome\User Data`下，查找类似`Profile 1`这样的文件夹，这些文件夹就是你登录的本地谷歌账户，文件夹名字要记住后边要用。
>
> 4. 在控制台终端先确认python是否装好，然后输入`pip install bing-rewards`来下载，下载后输入`bing-rewards -h`来确认是否安装成功。
>
> 5. 打开`C:\Users\28304\AppData\Roaming\bing-rewards\config.json`来把多个谷歌账户配置进去
>
>    ```
>    {
>      "desktop_count": 33,
>      "mobile_count": 0,
>      "load_delay": 1.5,
>      "search_delay": 6.0,
>      "search_url": "https://www.bing.com/search?form=QBRE&q=",
>      "desktop_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edge/126.0.0.0",
>      "mobile_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 6 Build/AP2A.240605.024) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36 Edge/121.0.2277.138",
>      "browser_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
>      "bing": false,
>      "open_rewards": false,
>      "window": true,
>      "exit": true,
>      "ime": false,
>      "profile": [
>       "Profile 1", "Profile 2", "Profile 3", "Profile 5", "Profile 6"
>      ]
>    }
>    ```
>
>    
>
> 6. desktop_count是网页端搜索的个数，browser_path是你谷歌浏览器的位置，profile是之前文件夹名字
>

> [!important]
>
> **在控制台终端中，直接输入`bing-rewards`来测试刚刚的配置是否正常**



> [!tip]
>
> ## app端配置
>
> 1. 下载mumu模拟器，把里边设置中的的快捷键->切换至指定标签打开
>
> 2. 在mumu模拟器中安装bing app，并且应用分身4个，将每个应用都登录微软bing账号
>
> 3. 配置app段的json文件
>
>    ```
>    {
>        "search_bing": {
>            "mumu_start_time": 10,
>            "bing_start_time": 5,
>            "search_delay_time": 6,
>            "search_count": 3,
>            "run_device_id": [
>                2,
>                4
>            ],
>            "mumu_path": "D:\\software\\MuMu\\nx_main\\MuMuNxMain.exe",
>            "mumu_name": "MuMu安卓设备"
>        }
>    }
>    ```
>
>    
>
> 4. 文件描述
>
>    1. mumu_start_time是mumu模拟器启动时间，如果电脑比较旧，调大时间
>    2. bing_start_time是bing app启动时间，如果配置的模拟器比较差，调大时间
>    3. search_delay_time是每次搜索停留时间
>    4. run_device_id是你准备运行哪个bing app，全运行可以改为0,1,2,3,4
>    5. mumu_path是模拟器安装的目录
>    6. mumu_name是模拟器的名字，从任务管理器上确认一下，主要是有中英文的区别
>

> [!important]
>
> **配置好json文件后，双击test6.exe测试一下，这是自己写的，非常脆弱，后续看看怎么改**



> [!tip]
>
> 将bing-rewards和test6.exe都写入bat文件中，在用定时任务触发bat文件来定时运行

