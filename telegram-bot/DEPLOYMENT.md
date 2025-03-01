# Telegram Bot 部署指南

## 1. 环境准备
- Python 3.8+
- Git
- Telegram Bot Token

## 2. 安装依赖
```bash
pip install -r requirements.txt
```

## 3. 配置设置
1. 创建`.env`文件：
```bash
BOT_TOKEN=你的Telegram Bot Token
SECRET_KEY=随机生成的密钥
ADMIN_USERNAME=后台用户名
ADMIN_PASSWORD=后台密码
```

## 4. 初始化数据库
```bash
python -c "import sqlite3; conn = sqlite3.connect('bot_data.db'); c = conn.cursor(); c.execute('CREATE TABLE IF NOT EXISTS buttons (id INTEGER PRIMARY KEY, text TEXT, response TEXT)'); conn.commit()"
```

## 5. Systemd 服务配置

### 5.1 创建telegram-bot服务
1. 将telegram-bot.service文件复制到/etc/systemd/system/
2. 修改服务文件中的路径和配置：
   - User: 修改为运行服务的系统用户名（建议创建一个专用用户，如`telegram-bot`，创建命令：`sudo adduser telegram-bot`）
   - WorkingDirectory: 修改为项目实际路径，如/home/user/telegram-bot
   - ExecStart: 修改为实际的Python解释器路径和项目路径，如/home/user/telegram-bot/venv/bin/python /home/user/telegram-bot/bot.py
   - Environment: 确保TELEGRAM_BOT_TOKEN和ADMIN_PASSWORD已正确设置
3. 启用并启动服务：
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### 5.2 创建telegram-bot-admin服务
1. 将telegram-bot-admin.service文件复制到/etc/systemd/system/
2. 修改服务文件中的路径和配置：
   - User: 修改为运行服务的系统用户名（建议使用与bot服务相同的用户，如`telegram-bot`）
   - WorkingDirectory: 修改为项目实际路径，如/home/user/telegram-bot
   - ExecStart: 修改为实际的Python解释器路径和项目路径，如/home/user/telegram-bot/venv/bin/python /home/user/telegram-bot/admin.py
   - Environment: 确保TELEGRAM_BOT_TOKEN和ADMIN_PASSWORD已正确设置
3. 启用并启动服务：
```bash
sudo systemctl enable telegram-bot-admin
sudo systemctl start telegram-bot-admin
```

## 6. 访问后台
- 打开浏览器访问：http://your_domain.com
- 使用设置的用户名和密码登录
- 管理按钮和回复内容

## 7. 生产环境部署

### 7.1 安装Nginx
```bash
sudo apt update
sudo apt install nginx
```

### 7.2 配置Nginx反向代理
1. 创建新的Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/telegram-bot
```

2. 添加以下配置内容：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 防止直接访问IP地址
    if ($host !~* ^(your_domain.com|www.your_domain.com)$ ) {
        return 444;
    }

    # 性能优化
    client_max_body_size 10M;
    keepalive_timeout 65;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
}
```

3. 创建符号链接启用配置：
```bash
# 如果文件已存在，先删除旧链接
sudo rm -f /etc/nginx/sites-enabled/telegram-bot
# 创建新的符号链接
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
```

4. 测试Nginx配置：
```bash
sudo nginx -t
```

5. 重启Nginx服务：
```bash
sudo systemctl restart nginx
```

### 7.3 配置防火墙
1. 允许HTTP和HTTPS流量：
```bash
sudo ufw allow 'Nginx Full'
```

2. 查看防火墙状态：
```bash
sudo ufw status
```

### 7.4 配置SSL证书（可选）：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## 8. 常用命令
- 查看服务状态：
```bash
sudo systemctl status telegram-bot
sudo systemctl status telegram-bot-admin
```

- 重启服务：
```bash
sudo systemctl restart telegram-bot
sudo systemctl restart telegram-bot-admin
```

- 查看日志：
```bash
journalctl -u telegram-bot -f
journalctl -u telegram-bot-admin -f
```

## 9. 注意事项
- 确保服务器开放5000端口
- 定期备份bot_data.db文件
