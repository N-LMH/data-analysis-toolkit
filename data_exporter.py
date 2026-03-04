"""
数据导出工具
功能：
1. 导出为多种格式（CSV, Excel, JSON, HTML, SQL, Markdown）
2. 自定义导出选项
3. 批量导出
4. 压缩导出
5. 生成导出报告
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import zipfile
import json

class DataExporter:
    """数据导出器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df.copy()
        self.export_log = []
    
    def export_csv(
        self,
        output_path: str,
        sep: str = ',',
        encoding: str = 'utf-8',
        index: bool = False,
        **kwargs
    ) -> bool:
        """
        导出为 CSV
        
        Args:
            output_path: 输出路径
            sep: 分隔符
            encoding: 编码
            index: 是否包含索引
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        try:
            self.df.to_csv(output_path, sep=sep, encoding=encoding, index=index, **kwargs)
            self._log_export('CSV', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('CSV', output_path, str(e))
            return False
    
    def export_excel(
        self,
        output_path: str,
        sheet_name: str = 'Sheet1',
        index: bool = False,
        **kwargs
    ) -> bool:
        """
        导出为 Excel
        
        Args:
            output_path: 输出路径
            sheet_name: 工作表名称
            index: 是否包含索引
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        try:
            self.df.to_excel(output_path, sheet_name=sheet_name, index=index, **kwargs)
            self._log_export('Excel', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('Excel', output_path, str(e))
            return False
    
    def export_json(
        self,
        output_path: str,
        orient: str = 'records',
        indent: int = 2,
        **kwargs
    ) -> bool:
        """
        导出为 JSON
        
        Args:
            output_path: 输出路径
            orient: 方向（'records', 'index', 'columns', 'values'）
            indent: 缩进
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        try:
            self.df.to_json(
                output_path,
                orient=orient,
                indent=indent,
                force_ascii=False,
                **kwargs
            )
            self._log_export('JSON', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('JSON', output_path, str(e))
            return False
    
    def export_html(
        self,
        output_path: str,
        index: bool = False,
        border: int = 1,
        **kwargs
    ) -> bool:
        """
        导出为 HTML
        
        Args:
            output_path: 输出路径
            index: 是否包含索引
            border: 边框宽度
            **kwargs: 其他参数
        
        Returns:
            是否成功
        """
        try:
            html = self.df.to_html(index=index, border=border, **kwargs)
            
            # 添加样式
            styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Data Export</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
    <h1>Data Export</h1>
    <p>Total rows: {len(self.df)}</p>
    {html}
</body>
</html>
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            
            self._log_export('HTML', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('HTML', output_path, str(e))
            return False
    
    def export_sql(
        self,
        output_path: str,
        table_name: str = 'data',
        if_exists: str = 'replace'
    ) -> bool:
        """
        导出为 SQL 插入语句
        
        Args:
            output_path: 输出路径
            table_name: 表名
            if_exists: 如果表存在（'replace', 'append', 'fail'）
        
        Returns:
            是否成功
        """
        try:
            # 生成 CREATE TABLE 语句
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            
            for col in self.df.columns:
                dtype = self.df[col].dtype
                if dtype == 'int64':
                    sql_type = 'INTEGER'
                elif dtype == 'float64':
                    sql_type = 'REAL'
                else:
                    sql_type = 'TEXT'
                
                create_sql += f"    {col} {sql_type},\n"
            
            create_sql = create_sql.rstrip(',\n') + "\n);\n\n"
            
            # 生成 INSERT 语句
            insert_sql = ""
            for _, row in self.df.iterrows():
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, str):
                        escaped_val = val.replace("'", "''")
                        values.append(f"'{escaped_val}'")
                    else:
                        values.append(str(val))
                
                insert_sql += f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n"
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(create_sql)
                f.write(insert_sql)
            
            self._log_export('SQL', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('SQL', output_path, str(e))
            return False
    
    def export_markdown(
        self,
        output_path: str,
        index: bool = False
    ) -> bool:
        """
        导出为 Markdown
        
        Args:
            output_path: 输出路径
            index: 是否包含索引
        
        Returns:
            是否成功
        """
        try:
            markdown = self.df.to_markdown(index=index)
            
            # 添加标题
            content = f"# Data Export\n\n"
            content += f"Total rows: {len(self.df)}\n\n"
            content += markdown
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_export('Markdown', output_path, len(self.df))
            return True
        except Exception as e:
            self._log_error('Markdown', output_path, str(e))
            return False
    
    def export_multiple(
        self,
        output_dir: str,
        base_name: str,
        formats: List[str],
        compress: bool = False
    ) -> Dict[str, bool]:
        """
        导出为多种格式
        
        Args:
            output_dir: 输出目录
            base_name: 基础文件名
            formats: 格式列表（'csv', 'excel', 'json', 'html', 'sql', 'markdown'）
            compress: 是否压缩
        
        Returns:
            各格式的导出结果
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        files = []
        
        print(f"\n导出为多种格式:")
        print("="*60)
        
        for fmt in formats:
            if fmt == 'csv':
                file_path = output_path / f"{base_name}.csv"
                results['csv'] = self.export_csv(str(file_path))
                files.append(file_path)
            
            elif fmt == 'excel':
                file_path = output_path / f"{base_name}.xlsx"
                results['excel'] = self.export_excel(str(file_path))
                files.append(file_path)
            
            elif fmt == 'json':
                file_path = output_path / f"{base_name}.json"
                results['json'] = self.export_json(str(file_path))
                files.append(file_path)
            
            elif fmt == 'html':
                file_path = output_path / f"{base_name}.html"
                results['html'] = self.export_html(str(file_path))
                files.append(file_path)
            
            elif fmt == 'sql':
                file_path = output_path / f"{base_name}.sql"
                results['sql'] = self.export_sql(str(file_path))
                files.append(file_path)
            
            elif fmt == 'markdown':
                file_path = output_path / f"{base_name}.md"
                results['markdown'] = self.export_markdown(str(file_path))
                files.append(file_path)
        
        print("="*60)
        
        # 压缩
        if compress and files:
            zip_path = output_path / f"{base_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    if file.exists():
                        zipf.write(file, file.name)
                        file.unlink()  # 删除原文件
            
            print(f"\n✓ 已压缩为: {zip_path}")
        
        return results
    
    def _log_export(self, format_type: str, path: str, rows: int):
        """记录导出成功"""
        log_entry = f"✓ {format_type}: {Path(path).name} ({rows} 行)"
        self.export_log.append(log_entry)
        print(log_entry)
    
    def _log_error(self, format_type: str, path: str, error: str):
        """记录导出错误"""
        log_entry = f"✗ {format_type}: {Path(path).name} - {error}"
        self.export_log.append(log_entry)
        print(log_entry)
    
    def get_log(self) -> List[str]:
        """获取导出日志"""
        return self.export_log
    
    def print_summary(self):
        """打印导出摘要"""
        print("\n" + "="*60)
        print("导出摘要")
        print("="*60)
        
        success = sum(1 for log in self.export_log if log.startswith('✓'))
        failed = sum(1 for log in self.export_log if log.startswith('✗'))
        
        print(f"\n总计: {len(self.export_log)} 次导出")
        print(f"成功: {success}")
        print(f"失败: {failed}")
        
        if self.export_log:
            print("\n详细日志:")
            for log in self.export_log:
                print(f"  {log}")
        
        print("\n" + "="*60)


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'City': ['New York', 'London', 'Tokyo', 'Paris', 'Berlin'],
        'Salary': [50000, 60000, 70000, 80000, 90000]
    })
    
    print("测试数据:")
    print(df)
    
    # 创建导出器
    exporter = DataExporter(df)
    
    # 导出为多种格式
    results = exporter.export_multiple(
        output_dir='exports',
        base_name='test_data',
        formats=['csv', 'excel', 'json', 'html', 'sql', 'markdown'],
        compress=False
    )
    
    # 打印摘要
    exporter.print_summary()
    
    print("\n完成！")
