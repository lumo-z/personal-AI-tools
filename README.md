# 本地AI对话模型客户端
## 项目简介本项目为基于 Vue 2 和 Element UI 的前端管理系统示例，包含用户登录、个人信息管理、对话功能、个人仓库等模块。后端采用 Python Flask（见 backed 目录），支持基础的用户认证和数据存储。
## 主要功能
主要功能
用户注册与登录
首页展示
对话功能
个人仓库管理
个人中心信息维护
目录结构
e:\vue2_demo
├── backed/ # 后端 Flask 相关代码
│ ├── app.py # 后端主程序入口
│ ├── models.py # 数据库模型
│ ├── utils/ # 工具函数
│ └──... # 其他后端相关文件
├── src/ # 前端 Vue 2 源码
│ ├── App.vue # 根组件
│ ├── main.js # 前端入口
│ ├── assets/ # 静态资源
│ ├── components/ # 公共组件
│ ├── views/ # 页面组件
│ ├── api/ # 前端接口请求
│ ├── router/ # 路由配置
│ └── store/ # Vuex 状态管理
├── public/ # 公共静态文件
├── package.json # 前端依赖配置
├── README.md # 项目说明文档
└──... # 其他配置文件
## 安装与启动
### 前端1. 安装依赖   

```bash   
npm install
```
2. 启动开发服务器
```bash
npm run serve
```
### 后端
1. 进入 backed 目录，确保已安装 Python 3 和相关依赖
```bash
cd backed
pip install -r requirements.txt
```
2. 启动后端服务
```bash
python app.py
```
## 其他说明
前端默认端口为 8080，后端端口请参考 backed/app.py 配置。
如需自定义接口或页面，请在 src/api 和 src/views 目录下进行扩展。
样式文件位于 src/assets/base.css，可根据需求自定义主题。
