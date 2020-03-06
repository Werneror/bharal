# bharal

![logo](resources/bharal.png)

岩羊，一个带访问限制的简单通用反向代理服务器。

## 效果演示

![demonstration](resources/demonstration.gif)

## 使用说明

### 下载源码

```
git clone https://github.com/Werneror/bharal.git
```

### 修改配置

```
cd bharal
vim settings.py
```

配置文件是`settings.py`，建议修改：

- LOG_FILE: 日志文件路径
- DOMAIN: 域名，不正确设置会导致无法登录
- PORT: 监听端口
- USERS: 用户

### 替换证书

证书和私钥在文件夹`ssl`中，为增强安全性，建议替换为自己的、有效的证书和私钥。

### 运行

有两种运行方式。第一种，直接运行：

```
python3 bharal.py
```

更为推荐第二种，在Docker中运行：

```
docker build -t bharal .
docker run -d -p 4430:4430 --name bharal  bharal:latest
```


## 特点

- 访问限制
- 多用户
- 30x跟随


## 使用建议

1. 一般而言一个产品的用户数量越多生命力就越强，但某些特殊情况下用户数量与生命力成反比。所以建议在自己的服务器上部署bharal，并尽量不要分享；
2. 虽然反向代理了POST方法并处理了cookie中的path，但出于账号安全的考虑，尽量不要在使用bharal时登录任何网站；
3. 本项目代码未经安全审计，所以推荐在Docker中运行。


## 下一步

- 编写更加美观的首页和登录页面
