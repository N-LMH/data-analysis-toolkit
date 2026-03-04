# 数据分析工具套件

一套简单易用的 Python 数据分析工具，帮助你快速分析 CSV/Excel 数据。

## 功能特点

- 📊 **自动数据分析** - 一键生成完整的统计报告
- 🧹 **数据清洗** - 处理缺失值、重复行、异常值
- 📈 **数据可视化** - 自动生成多种图表
- 🔄 **数据对比** - 对比两个数据集的差异
- 🔀 **数据转换** - CSV ↔ Excel ↔ JSON 格式转换
- 🔗 **数据合并** - 合并多个数据文件
- ✅ **质量检查** - 5个维度的数据质量评估
- 🎲 **数据采样** - 多种采样方法（随机、分层、系统）
- 📤 **数据导出** - 导出为多种格式（CSV, Excel, JSON, HTML, SQL）
- 🚀 **简单易用** - 无需复杂配置，开箱即用

## 工具列表

1. **data_analyzer.py** - 数据分析器
2. **data_cleaner.py** - 数据清洗器
3. **data_visualizer.py** - 数据可视化器
4. **data_comparator.py** - 数据对比工具
5. **data_converter.py** - 数据转换工具
6. **data_merger.py** - 数据合并工具
7. **data_quality_checker.py** - 数据质量检查工具
8. **data_sampler.py** - 数据采样工具
9. **data_exporter.py** - 数据导出工具
10. **demo.py** - 完整演示脚本

## 快速开始

### 1. 数据分析器 (data_analyzer.py)

自动分析 CSV/Excel 文件，生成统计报告。

```python
from data_analyzer import DataAnalyzer

# 创建分析器
analyzer = DataAnalyzer()

# 加载文件
analyzer.load_file("your_data.csv")

# 分析数据
analyzer.analyze()

# 打印报告
analyzer.print_report()

# 导出报告
analyzer.export_report("report.json")
analyzer.export_report("report.txt")
```

**功能：**
- 基本信息（行数、列数、内存占用）
- 列分析（类型、缺失值、唯一值）
- 缺失值分析
- 数值列统计（均值、标准差、分位数）
- 分类列统计（唯一值、频数分布）
- 相关性分析（高相关性列对）

### 2. 数据清洗器 (data_cleaner.py)

清洗和预处理数据。

```python
from data_cleaner import DataCleaner
import pandas as pd

# 加载数据
df = pd.read_csv("your_data.csv")

# 创建清洗器
cleaner = DataCleaner(df)

# 处理缺失值
cleaner.handle_missing_values(strategy='fill')

# 删除重复行
cleaner.remove_duplicates()

# 删除异常值
cleaner.remove_outliers(method='iqr')

# 数据标准化
cleaner.normalize(method='minmax')

# 获取清洗后的数据
clean_df = cleaner.get_cleaned_data()

# 查看清洗日志
for log in cleaner.get_log():
    print(log)
```

**功能：**
- 处理缺失值（删除、填充、前向/后向填充）
- 删除重复行
- 数据类型转换
- 异常值检测和删除（IQR、Z-score）
- 数据标准化（Min-Max、Z-score）

### 3. 数据可视化器 (data_visualizer.py)

自动生成多种图表。

```python
from data_visualizer import DataVisualizer
import pandas as pd

# 加载数据
df = pd.read_csv("your_data.csv")

# 创建可视化器
viz = DataVisualizer(df)

# 生成所有图表
viz.plot_all()

# 保存图表
viz.save_all("output_plots")

# 或者单独生成图表
viz.plot_distribution()      # 分布图
viz.plot_correlation()        # 相关性热图
viz.plot_boxplot()            # 箱线图
viz.plot_scatter_matrix()     # 散点矩阵
viz.plot_categorical('column_name')  # 分类统计图
```

**功能：**
- 分布图（直方图）
- 相关性热图
- 箱线图（异常值检测）
- 散点矩阵
- 分类统计图（柱状图 + 饼图）
- 时间序列图

### 4. 数据对比工具 (data_comparator.py)

对比两个数据集的差异。

```python
from data_comparator import DataComparator
import pandas as pd

df1 = pd.read_csv("old_data.csv")
df2 = pd.read_csv("new_data.csv")

comparator = DataComparator(df1, df2, key_columns=['ID'])
comparator.compare()
comparator.print_report()

# 获取差异
added = comparator.get_added_rows()
removed = comparator.get_removed_rows()
modified = comparator.get_modified_rows()
```

**功能：**
- 识别新增、删除、修改的行
- 对比数据结构变化
- 生成详细的差异报告
- 支持按索引或关键列对比

### 5. 数据转换工具 (data_converter.py)

在不同格式之间转换数据。

```python
from data_converter import DataConverter

converter = DataConverter()

# 单文件转换
converter.convert_file('data.csv', 'data.xlsx')

# 批量转换
converter.batch_convert(
    input_dir='csv_files',
    output_dir='excel_files',
    input_format='csv',
    output_format='xlsx'
)

# 转换为多种格式
converter.convert_to_multiple_formats(
    'data.csv',
    ['xlsx', 'json', 'parquet']
)
```

**功能：**
- CSV ↔ Excel ↔ JSON ↔ Parquet 格式转换
- 批量转换
- 转换为多种格式
- 保留数据类型

### 6. 数据合并工具 (data_merger.py)

合并多个数据文件。

```python
from data_merger import DataMerger

merger = DataMerger()

# 纵向拼接（追加行）
merger.merge_files(
    ['file1.csv', 'file2.csv'],
    'merged.csv',
    merge_type='concat'
)

# 关联合并（类似 SQL JOIN）
merger.merge_files(
    ['users.csv', 'orders.csv'],
    'merged.csv',
    merge_type='merge',
    on=['user_id']
)

# 智能合并（自动检测最佳方式）
merger.smart_merge(
    ['file1.csv', 'file2.csv'],
    'merged.csv'
)
```

**功能：**
- 纵向拼接（追加行）
- 横向拼接（追加列）
- 关联合并（类似 SQL JOIN）
- 智能合并（自动检测最佳方式）

### 7. 数据质量检查工具 (data_quality_checker.py)

检查数据质量并生成评分报告。

```python
from data_quality_checker import DataQualityChecker
import pandas as pd

df = pd.read_csv("data.csv")
checker = DataQualityChecker(df)

# 执行所有检查
report = checker.check_all()

# 打印报告
checker.print_report()

# 导出报告
checker.export_report('quality_report.json')
```

**功能：**
- 完整性检查（缺失值、空值）
- 一致性检查（数据类型、格式）
- 准确性检查（范围、逻辑）
- 唯一性检查（重复值、主键）
- 时效性检查（日期范围）
- 生成质量报告和评分（A-F等级）

### 8. 数据采样工具 (data_sampler.py)

从大数据集中提取代表性样本。

```python
from data_sampler import DataSampler
import pandas as pd

df = pd.read_csv("large_data.csv")
sampler = DataSampler(df)

# 随机采样
sample = sampler.random_sample(frac=0.1)

# 分层采样（保持比例）
sample = sampler.stratified_sample('category_column', frac=0.1)

# 时间序列采样
sample = sampler.time_series_sample('date_column', freq='D')

# 自动采样（智能选择方法）
sample = sampler.auto_sample(target_size=1000)

# 打印报告
sampler.print_report()
```

**功能：**
- 随机采样
- 分层采样（保持各层比例）
- 系统采样（等间隔）
- 时间序列采样（按时间聚合）
- 整群采样
- 自动采样（智能选择最佳方法）

### 9. 数据导出工具 (data_exporter.py)

导出数据为多种格式。

```python
from data_exporter import DataExporter
import pandas as pd

df = pd.read_csv("data.csv")
exporter = DataExporter(df)

# 导出为单一格式
exporter.export_csv('output.csv')
exporter.export_excel('output.xlsx')
exporter.export_json('output.json')
exporter.export_html('output.html')
exporter.export_sql('output.sql', table_name='my_table')

# 导出为多种格式
results = exporter.export_multiple(
    output_dir='exports',
    base_name='data',
    formats=['csv', 'excel', 'json', 'html', 'sql'],
    compress=True  # 压缩为 ZIP
)

# 打印摘要
exporter.print_summary()
```

**功能：**
- CSV 导出
- Excel 导出
- JSON 导出
- HTML 导出（带样式）
- SQL 导出（INSERT 语句）
- Markdown 导出
- 批量导出多种格式
- 压缩导出（ZIP）

## 安装依赖

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

## 使用示例

### 完整工作流

```python
import pandas as pd
from data_analyzer import DataAnalyzer
from data_cleaner import DataCleaner
from data_visualizer import DataVisualizer

# 1. 加载和分析数据
analyzer = DataAnalyzer()
analyzer.load_file("sales_data.csv")
analyzer.analyze()
analyzer.print_report()

# 2. 清洗数据
df = pd.read_csv("sales_data.csv")
cleaner = DataCleaner(df)
cleaner.handle_missing_values(strategy='fill')
cleaner.remove_duplicates()
cleaner.remove_outliers()
clean_df = cleaner.get_cleaned_data()

# 3. 可视化
viz = DataVisualizer(clean_df)
viz.plot_all()
viz.save_all("analysis_plots")

# 4. 保存清洗后的数据
clean_df.to_csv("sales_data_clean.csv", index=False)
```

## 支持的文件格式

- CSV (.csv)
- Excel (.xlsx, .xls)

## 输出格式

- 报告：JSON (.json) 或 文本 (.txt)
- 图表：PNG (.png)

## 注意事项

1. **中文显示问题**：如果图表中文显示为方框，需要配置中文字体：
   ```python
   import matplotlib.pyplot as plt
   plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
   plt.rcParams['axes.unicode_minus'] = False
   ```

2. **大文件处理**：对于大文件（>100MB），建议分块处理或使用 Dask。

3. **内存占用**：可视化会占用较多内存，处理完后记得关闭图表：
   ```python
   viz.close_all()
   ```

## 常见问题

**Q: 如何处理特定列的缺失值？**
```python
cleaner.handle_missing_values(strategy='fill', columns=['column1', 'column2'])
```

**Q: 如何只可视化特定列？**
```python
viz.plot_distribution(columns=['column1', 'column2'])
```

**Q: 如何调整异常值检测的敏感度？**
```python
# IQR 方法：threshold 越大越宽松（默认 1.5）
cleaner.remove_outliers(method='iqr', threshold=3.0)

# Z-score 方法：threshold 越大越宽松（默认 3.0）
cleaner.remove_outliers(method='zscore', threshold=4.0)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

凌 (Ling) - AI Assistant

---

**快速上手：**
1. 安装依赖：`pip install pandas numpy matplotlib seaborn openpyxl`
2. 运行示例：`python data_analyzer.py`
3. 查看生成的报告和图表

**需要帮助？** 查看代码中的注释和文档字符串。
