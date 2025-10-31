Windows 目录前缀重命名工具

使用 Python + PySimpleGUI 提供 UI，遍历子目录并按父文件夹在同级中的自然序（1,2,3,10…）给该目录内的文件加上前缀 `N_`。仅重命名“文件”，不改“文件夹”。可选“是否包含根目录文件”。

## 功能规则
- 仅重命名文件；不重命名任何文件夹。
- 每一层独立计算：对当前目录的父目录的同级子目录做“自然排序”，当前目录在这些同级中的 1 基序号 = 给该目录内所有“直接子文件”的前缀 `N_`。
- 递归处理所有层级。
- 不跳过已带 `数字_` 的文件；重复执行会叠加前缀。

## 环境准备（Windows）
```powershell
# 1) 安装依赖
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 2) 运行（开发态）
python main.py
```

## 生成测试用例（Windows）
```powershell
# 使用 Python 脚本（推荐）
python scripts\create_testcase.py --target C:\temp\win_testcase

# 或使用批处理（在未安装 Python 的机器上也可生成基础用例）
scripts\create_testcase.bat C:\temp\win_testcase
```

## 使用步骤
1. 启动程序（`python main.py` 或使用打包后的 exe）。
2. 在 UI 中选择根路径（例如 `C:\temp\win_testcase`）。
3. 可勾选“Include root files”以处理根目录直系文件。
4. 点击 Start，观察日志输出和统计信息。

## 打包为 Windows 可执行文件
```powershell
# 需在已激活的虚拟环境中
pyinstaller --noconfirm --onefile --windowed main.py
# 产物在 dist\main.exe
```

> 如需自定义图标，可添加 `--icon icon.ico`。

## 注意事项
- 权限：如遇只读或无权限文件，程序会记录错误并继续处理。
- 同名冲突：采用两阶段改名（临时名 -> 目标名）规避冲突。
- 路径长度：极端长路径可能报错，请调整目录结构或在更高路径层级运行。
- 可重复执行：不会去重历史前缀，重复执行会叠加 `N_`。

## 结构说明
- `main.py`：程序入口，启动 UI。
- `app/renamer.py`：核心逻辑（自然排序、计算序号、两阶段改名）。
- `app/ui.py`：PySimpleGUI 界面与后台线程。
- `scripts/create_testcase.py`：生成丰富的测例目录树。
- `scripts/create_testcase.bat`：无 Python 场景下的基础测例生成。

## 开发风格
- 代码注释使用英文。
- Python 遵循 Google 风格与类型注解，尽量保持函数职责单一。


