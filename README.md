# Python Mastery - Interactive Learning App

## 项目简介
`Python Mastery` 是一个基于 `Python 3`、`pygame-ce` 和 `pygame_gui` 开发的本地交互式学习应用，面向 Python 课程项目展示与课堂演示场景。系统将登录注册、题库测验、结果统计、学习分析、题库管理和算法可视化整合在同一套深色现代化界面中。

本项目不依赖服务器，所有数据均以本地 JSON 文件形式保存，适合课程作业提交、现场演示和后续继续扩展。

## 项目目标
- 为 Python 课程项目提供一个完整、可运行、可演示的桌面学习系统
- 支持学生登录、练习测验、查看结果和分析学习表现
- 支持管理员维护题库内容，方便演示后台管理能力
- 通过数组、链表、树的动画演示满足算法可视化要求
- 使用纯颜色、形状和文字构建现代深色 UI，不依赖图片和声音

## 核心功能
- 用户登录 / 注册
  - 支持 `student` 和 `admin` 两种角色
  - 密码使用 `hashlib.sha256` 哈希保存
  - 默认测试管理员账号自动初始化
- 题库系统
  - 题目保存在 `data/questions.json`
  - 支持题型：`mcq`、`blank`、`output`
  - 支持按题型、难度、分类筛选和随机抽题
- Quiz 测验系统
  - 开始前可选择题目数量、难度、分类
  - 每次显示 1 题
  - 提交后即时显示对错与解析
  - 测验完成后进入结果页
- Result 结果页
  - 显示分数、正确题数、总题数、正确率、用时
  - 自动保存测验结果到历史文件
- Analytics 学习分析
  - 展示平均分、最佳成绩、总测验次数、最近一次结果
  - 绘制成绩趋势图、分类正确率柱状图、难度分布图
  - 显示当前用户的历史测验记录
- Admin 题库管理
  - 仅 `admin` 可进入
  - 支持查看、搜索、筛选、新增、编辑、删除题目
- Algorithm Visualization 算法可视化
  - Arrays：线性查找
  - Lists：链表插入
  - Trees：二叉树中序遍历
  - 支持 `Play / Pause / Next / Reset`
- Lesson 页面
  - 当前为统一风格课程页占位版本
  - 预留后续接入章节内容、知识点讲解和课件展示

## 技术栈
- Python 3.10+
- pygame-ce
- pygame_gui
- 本地 JSON 文件存储
- 纯本地桌面运行，无服务端

## 项目目录结构
```text
python-mastery-app/
├─ main.py
├─ requirements.txt
├─ README.md
├─ DEMO_GUIDE.md
├─ AI_WORK_LOG_TEMPLATE.md
├─ PROJECT_REPORT.md
├─ assets/
│  └─ themes/
│     └─ theme.json
├─ data/
│  ├─ users.json
│  ├─ questions.json
│  ├─ questions_seed.json
│  ├─ quiz_history.json
│  ├─ lessons.json
│  └─ algorithm_steps.json
├─ exercises/
│  └─ exercises.py
└─ src/
   ├─ app.py
   ├─ config.py
   ├─ router.py
   ├─ models/
   ├─ services/
   ├─ storage/
   ├─ ui/
   └─ utils/
```

## 安装依赖方法
建议先创建并激活虚拟环境，再安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

如果本机已经有项目虚拟环境，也可以直接执行：

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

## 运行方法
在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe main.py
```

## 默认测试账号
- 管理员账号
  - 用户名：`admin`
  - 密码：`admin123`

也可以在登录页切换到注册模式，自行创建 `student` 或 `admin` 账号。

## 数据文件说明
- `data/users.json`
  - 保存用户账号信息
  - 包含用户名、密码哈希、角色
- `data/questions.json`
  - 当前运行题库文件
  - 保存测验和管理员后台使用的题目数据
- `data/questions_seed.json`
  - 稳定题库种子文件
  - 当 `questions.json` 缺失、为空或损坏时可作为恢复来源
- `data/quiz_history.json`
  - 保存每次测验结果
  - 与当前登录用户绑定
- `data/lessons.json`
  - 预留课程内容数据文件，目前未接入正式课程页面逻辑
- `data/algorithm_steps.json`
  - 预留算法步骤数据文件，目前算法演示步骤由服务层内置生成

## 支持的题型
- `mcq`：单选题
- `blank`：填空题
- `output`：程序输出题

## exercises.py 题目来源说明
当前仓库中的 [exercises/exercises.py](C:/Users/20375/Desktop/python-mastery-app/exercises/exercises.py:1) 仍是占位文件，尚未包含完整函数实现。

目前题库中与算法/函数相关的题目，是根据课程要求中给出的函数名列表扩展生成，并通过 `source` 字段标记对应函数来源，例如：
- `isLeapYear`
- `isPalindrome`
- `isPrime`
- `binaryToDecimal`
- `insertElement`
- `rotateLeft`

因此，课堂演示时可以展示：
- `questions.json` 中每道题的 `source`
- 题库已按函数名来源分类扩展
- 后续如果补齐 `exercises.py` 真实实现，可以继续把题库与源码更严格地对齐

## 算法可视化内容
- Arrays
  - 线性查找（Linear Search）
  - 高亮当前检查索引
  - 显示目标值与步骤说明
- Lists
  - 链表插入过程演示
  - 显示节点、箭头与插入步骤说明
- Trees
  - 二叉树中序遍历
  - 按访问顺序高亮节点
  - 显示已访问顺序和步骤说明

## 稳定性与容错设计
- `users.json / questions.json / quiz_history.json` 缺失时自动初始化
- JSON 为空或格式异常时自动回落到安全默认结构
- 对非法字段、脏数据、空状态增加保护
- 未登录访问受限页面时自动回到登录页
- `student` 无法进入管理员页面
- 测验筛选为空、分析记录为空、算法步骤为空时均提供友好提示

## 默认演示流程
1. 使用 `admin / admin123` 登录
2. 首页展示系统总览
3. 进入 Quiz，完成一轮简短测验
4. 展示 ResultScreen 的成绩摘要
5. 进入 AnalyticsScreen 展示趋势图和统计卡
6. 返回首页，进入 AlgorithmScreen 展示数组、链表、树动画
7. 返回首页，进入 AdminScreen 演示题库搜索、新增或编辑
8. 最后补充说明 LessonScreen 为课程内容扩展入口

## 后续可扩展方向
- 接入正式课程章节内容，完善 LessonScreen
- 从真实 `exercises.py` 或课程资料自动生成题目
- 增加历史记录详情页与错题回顾页
- 增加更多算法可视化，如排序、二分查找、栈、队列、图
- 支持题库导入导出与批量管理
- 增加更多图表和学习建议模块

## 说明
本项目当前版本重点完成了课程项目提交所需的核心功能闭环、统一 UI、稳定性增强和演示材料准备，适合用于课堂展示、答辩和作业提交。
