基于 [musicdl](https://github.com/CharlesPikachu/musicdl) 和 [streamlit](https://github.com/streamlit/streamlit) 构建的音乐下载web网页

![web page](https://github.com/HelloZCB/musicdl-streamlit/blob/245496b92691552f994e6db9aaa923b8ec963555/web%20page.png)

# 本地运行模式
本地web页面，搜索结果勾选后自动下载对应的文件到本地

1、安装依赖
```shell
pip3 install -r requirements.txt
```
2、本地运行
```shell
streamlit run musicdl-streamlit-local.py
```
3、访问网址 http://127.0.0.1:8501

# 服务器运行模式
部署到云主机，配合nginx反向代理，提供公共下载服务

1、安装依赖
```shell
pip3 install -r requirements.txt
```
2、启动服务
```shell
nohup streamlit run musicdl-streamlit-web.py --server.address=127.0.0.1 &
```
3、配置nginx
```
server {
	listen 82;

	location / {
        	auth_basic "login auth";
        	auth_basic_user_file /etc/nginx/conf.d/pass.htpasswd;
        	proxy_pass http://127.0.0.1:8501;
		    error_page 401 =208 /empty.gif;
        	proxy_http_version 1.1;
        	proxy_set_header Upgrade $http_upgrade;
        	proxy_set_header Connection "upgrade";
        	proxy_set_header Host $http_host;
    	}
}
```
4、访问网址 http://[server-ip]:82
