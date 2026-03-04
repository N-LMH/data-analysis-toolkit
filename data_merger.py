"""
数据合并工具
功能：
1. 合并多个数据文件
2. 支持多种合并方式（纵向、横向、关联）
3. 自动处理列名冲突
4. 生成合并报告
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any, Literal
import glob

class DataMerger:
    """数据合并器"""
    
    def __init__(self):
        """初始化"""
        self.merge_log = []
    
    def merge_files(
        self,
        file_paths: List[str],
        output_path: str,
        merge_type: Literal['concat', 'join', 'merge'] = 'concat',
        **kwargs
    ) -> pd.DataFrame:
        """
        合并多个文件
        
        Args:
            file_paths: 文件路径列表
            output_path: 输出文件路径
            merge_type: 合并类型
                - 'concat': 纵向拼接（追加行）
                - 'join': 横向拼接（追加列）
                - 'merge': 关联合并（类似 SQL JOIN）
            **kwargs: 额外参数
        
        Returns:
            合并后的数据框
        """
        print(f"\n合并 {len(file_paths)} 个文件...")
        print("="*60)
        
        # 读取所有文件
        dfs = []
        for path in file_paths:
            try:
                df = self._read_file(path)
                dfs.append(df)
                print(f"✓ 读取: {Path(path).name} ({len(df)} 行, {len(df.columns)} 列)")
            except Exception as e:
                print(f"✗ 读取失败: {Path(path).name} - {e}")
        
        if not dfs:
            raise ValueError("没有成功读取任何文件")
        
        # 合并数据
        print(f"\n使用 {merge_type} 方式合并...")
        
        if merge_type == 'concat':
            result = self._concat_dataframes(dfs, **kwargs)
        elif merge_type == 'join':
            result = self._join_dataframes(dfs, **kwargs)
        elif merge_type == 'merge':
            result = self._merge_dataframes(dfs, **kwargs)
        else:
            raise ValueError(f"不支持的合并类型: {merge_type}")
        
        # 保存结果
        self._write_file(result, output_path)
        print(f"\n✓ 合并完成: {len(result)} 行, {len(result.columns)} 列")
        print(f"✓ 保存到: {output_path}")
        print("="*60)
        
        return result
    
    def _read_file(self, file_path: str) -> pd.DataFrame:
        """读取文件"""
        path = Path(file_path)
        suffix = path.suffix.lower().lstrip('.')
        
        if suffix == 'csv':
            return pd.read_csv(file_path)
        elif suffix in ['xlsx', 'xls']:
            return pd.read_excel(file_path)
        elif suffix == 'json':
            return pd.read_json(file_path)
        elif suffix == 'parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"不支持的格式: {suffix}")
    
    def _write_file(self, df: pd.DataFrame, file_path: str):
        """写入文件"""
        path = Path(file_path)
        suffix = path.suffix.lower().lstrip('.')
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if suffix == 'csv':
            df.to_csv(file_path, index=False)
        elif suffix in ['xlsx', 'xls']:
            df.to_excel(file_path, index=False)
        elif suffix == 'json':
            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
        elif suffix == 'parquet':
            df.to_parquet(file_path, index=False)
        else:
            raise ValueError(f"不支持的格式: {suffix}")
    
    def _concat_dataframes(
        self,
        dfs: List[pd.DataFrame],
        ignore_index: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """纵向拼接（追加行）"""
        return pd.concat(dfs, ignore_index=ignore_index, **kwargs)
    
    def _join_dataframes(
        self,
        dfs: List[pd.DataFrame],
        how: str = 'outer',
        **kwargs
    ) -> pd.DataFrame:
        """横向拼接（追加列）"""
        result = dfs[0]
        for df in dfs[1:]:
            result = result.join(df, how=how, rsuffix='_dup', **kwargs)
        return result
    
    def _merge_dataframes(
        self,
        dfs: List[pd.DataFrame],
        on: Optional[List[str]] = None,
        how: str = 'inner',
        **kwargs
    ) -> pd.DataFrame:
        """关联合并（类似 SQL JOIN）"""
        result = dfs[0]
        for df in dfs[1:]:
            result = result.merge(df, on=on, how=how, **kwargs)
        return result
    
    def merge_directory(
        self,
        input_dir: str,
        output_path: str,
        pattern: str = "*.csv",
        merge_type: str = 'concat',
        **kwargs
    ) -> pd.DataFrame:
        """
        合并目录中的所有文件
        
        Args:
            input_dir: 输入目录
            output_path: 输出文件路径
            pattern: 文件匹配模式（如 '*.csv'）
            merge_type: 合并类型
            **kwargs: 额外参数
        
        Returns:
            合并后的数据框
        """
        # 查找所有匹配的文件
        file_paths = glob.glob(str(Path(input_dir) / pattern))
        
        if not file_paths:
            raise ValueError(f"未找到匹配 {pattern} 的文件")
        
        return self.merge_files(file_paths, output_path, merge_type, **kwargs)
    
    def smart_merge(
        self,
        file_paths: List[str],
        output_path: str,
        key_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        智能合并（自动检测最佳合并方式）
        
        Args:
            file_paths: 文件路径列表
            output_path: 输出文件路径
            key_columns: 关键列（用于关联合并）
        
        Returns:
            合并后的数据框
        """
        # 读取所有文件
        dfs = [self._read_file(path) for path in file_paths]
        
        # 检查列结构
        all_columns = [set(df.columns) for df in dfs]
        common_columns = set.intersection(*all_columns)
        
        print(f"\n智能合并分析:")
        print(f"  文件数: {len(dfs)}")
        print(f"  共同列: {len(common_columns)} 个")
        
        # 决定合并方式
        if key_columns:
            # 如果指定了关键列，使用关联合并
            print(f"  合并方式: 关联合并（基于 {key_columns}）")
            return self.merge_files(file_paths, output_path, 'merge', on=key_columns)
        
        elif len(common_columns) == len(dfs[0].columns):
            # 如果所有列都相同，使用纵向拼接
            print(f"  合并方式: 纵向拼接（列结构相同）")
            return self.merge_files(file_paths, output_path, 'concat')
        
        elif len(common_columns) > 0:
            # 如果有部分共同列，使用关联合并
            print(f"  合并方式: 关联合并（基于共同列）")
            return self.merge_files(file_paths, output_path, 'merge', on=list(common_columns))
        
        else:
            # 如果没有共同列，使用横向拼接
            print(f"  合并方式: 横向拼接（无共同列）")
            return self.merge_files(file_paths, output_path, 'join')


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    df1 = pd.DataFrame({
        'ID': [1, 2, 3],
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Score': [85, 90, 88]
    })
    
    df2 = pd.DataFrame({
        'ID': [4, 5, 6],
        'Name': ['David', 'Eve', 'Frank'],
        'Score': [92, 87, 91]
    })
    
    df3 = pd.DataFrame({
        'ID': [1, 2, 3],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Tokyo']
    })
    
    # 保存测试文件
    df1.to_csv('test1.csv', index=False)
    df2.to_csv('test2.csv', index=False)
    df3.to_csv('test3.csv', index=False)
    
    print("创建测试文件:")
    print("  test1.csv (3行)")
    print("  test2.csv (3行)")
    print("  test3.csv (3行)")
    
    # 创建合并器
    merger = DataMerger()
    
    # 示例1：纵向拼接（追加行）
    print("\n【示例1：纵向拼接】")
    result1 = merger.merge_files(
        ['test1.csv', 'test2.csv'],
        'merged_concat.csv',
        merge_type='concat'
    )
    print(result1)
    
    # 示例2：关联合并（基于ID）
    print("\n【示例2：关联合并】")
    result2 = merger.merge_files(
        ['test1.csv', 'test3.csv'],
        'merged_join.csv',
        merge_type='merge',
        on=['ID']
    )
    print(result2)
    
    # 示例3：智能合并
    print("\n【示例3：智能合并】")
    result3 = merger.smart_merge(
        ['test1.csv', 'test3.csv'],
        'merged_smart.csv'
    )
    print(result3)
    
    print("\n完成！")
