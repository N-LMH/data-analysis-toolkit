"""
数据转换工具
功能：
1. CSV ↔ Excel ↔ JSON 格式转换
2. 批量转换
3. 自定义转换选项
4. 保留数据类型
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

class DataConverter:
    """数据转换器"""
    
    SUPPORTED_FORMATS = ['csv', 'xlsx', 'xls', 'json', 'parquet', 'feather']
    
    def __init__(self):
        """初始化"""
        self.conversion_log = []
    
    def convert_file(
        self,
        input_path: str,
        output_path: str,
        **kwargs
    ) -> bool:
        """
        转换单个文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            **kwargs: 额外参数
        
        Returns:
            是否成功
        """
        try:
            input_file = Path(input_path)
            output_file = Path(output_path)
            
            # 读取数据
            df = self._read_file(input_file, **kwargs)
            
            # 写入数据
            self._write_file(df, output_file, **kwargs)
            
            log_entry = f"✓ {input_file.name} → {output_file.name}"
            self.conversion_log.append(log_entry)
            print(log_entry)
            
            return True
        
        except Exception as e:
            log_entry = f"✗ {input_path}: {e}"
            self.conversion_log.append(log_entry)
            print(log_entry)
            return False
    
    def _read_file(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """读取文件"""
        suffix = file_path.suffix.lower().lstrip('.')
        
        if suffix == 'csv':
            return pd.read_csv(file_path, **kwargs)
        elif suffix in ['xlsx', 'xls']:
            return pd.read_excel(file_path, **kwargs)
        elif suffix == 'json':
            return pd.read_json(file_path, **kwargs)
        elif suffix == 'parquet':
            return pd.read_parquet(file_path, **kwargs)
        elif suffix == 'feather':
            return pd.read_feather(file_path, **kwargs)
        else:
            raise ValueError(f"不支持的格式: {suffix}")
    
    def _write_file(self, df: pd.DataFrame, file_path: Path, **kwargs):
        """写入文件"""
        suffix = file_path.suffix.lower().lstrip('.')
        
        # 创建目录
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if suffix == 'csv':
            df.to_csv(file_path, index=False, **kwargs)
        elif suffix in ['xlsx', 'xls']:
            df.to_excel(file_path, index=False, **kwargs)
        elif suffix == 'json':
            df.to_json(file_path, orient='records', force_ascii=False, indent=2, **kwargs)
        elif suffix == 'parquet':
            df.to_parquet(file_path, index=False, **kwargs)
        elif suffix == 'feather':
            df.to_feather(file_path, **kwargs)
        else:
            raise ValueError(f"不支持的格式: {suffix}")
    
    def batch_convert(
        self,
        input_dir: str,
        output_dir: str,
        input_format: str,
        output_format: str,
        **kwargs
    ) -> Dict[str, int]:
        """
        批量转换
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            input_format: 输入格式（如 'csv'）
            output_format: 输出格式（如 'xlsx'）
            **kwargs: 额外参数
        
        Returns:
            统计信息
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 查找所有匹配的文件
        pattern = f"*.{input_format}"
        files = list(input_path.glob(pattern))
        
        if not files:
            print(f"未找到 {pattern} 文件")
            return {'total': 0, 'success': 0, 'failed': 0}
        
        print(f"\n找到 {len(files)} 个文件")
        print("="*60)
        
        success = 0
        failed = 0
        
        for file in files:
            output_file = output_path / f"{file.stem}.{output_format}"
            
            if self.convert_file(str(file), str(output_file), **kwargs):
                success += 1
            else:
                failed += 1
        
        print("="*60)
        print(f"\n完成: {success} 成功, {failed} 失败")
        
        return {
            'total': len(files),
            'success': success,
            'failed': failed
        }
    
    def convert_to_multiple_formats(
        self,
        input_path: str,
        output_formats: List[str],
        output_dir: Optional[str] = None,
        **kwargs
    ):
        """
        转换为多种格式
        
        Args:
            input_path: 输入文件路径
            output_formats: 输出格式列表
            output_dir: 输出目录（可选）
            **kwargs: 额外参数
        """
        input_file = Path(input_path)
        
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = input_file.parent
        
        print(f"\n转换 {input_file.name} 为多种格式:")
        print("="*60)
        
        for fmt in output_formats:
            output_file = output_path / f"{input_file.stem}.{fmt}"
            self.convert_file(str(input_file), str(output_file), **kwargs)
        
        print("="*60)
    
    def get_log(self) -> List[str]:
        """获取转换日志"""
        return self.conversion_log
    
    def clear_log(self):
        """清空日志"""
        self.conversion_log = []


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    test_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Tokyo']
    })
    
    # 保存为 CSV
    test_data.to_csv('test_data.csv', index=False)
    print("创建测试文件: test_data.csv")
    
    # 创建转换器
    converter = DataConverter()
    
    # 单文件转换
    print("\n【单文件转换】")
    converter.convert_file('test_data.csv', 'test_data.xlsx')
    converter.convert_file('test_data.csv', 'test_data.json')
    
    # 转换为多种格式
    print("\n【转换为多种格式】")
    converter.convert_to_multiple_formats(
        'test_data.csv',
        ['xlsx', 'json', 'parquet']
    )
    
    # 查看日志
    print("\n【转换日志】")
    for log in converter.get_log():
        print(f"  {log}")
    
    print("\n完成！")
