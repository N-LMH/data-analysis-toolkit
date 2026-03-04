"""
数据对比工具
功能：
1. 对比两个数据集的差异
2. 识别新增、删除、修改的行
3. 生成差异报告
4. 可视化差异
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from pathlib import Path

class DataComparator:
    """数据对比器"""
    
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, key_columns: List[str] = None):
        """
        初始化
        
        Args:
            df1: 第一个数据框（旧数据）
            df2: 第二个数据框（新数据）
            key_columns: 用于匹配行的关键列
        """
        self.df1 = df1.copy()
        self.df2 = df2.copy()
        self.key_columns = key_columns or []
        self.comparison_results = {}
    
    def compare(self) -> Dict[str, Any]:
        """
        对比两个数据集
        
        Returns:
            对比结果字典
        """
        results = {
            'basic_comparison': self._compare_basic_info(),
            'schema_comparison': self._compare_schema(),
            'data_comparison': self._compare_data()
        }
        
        self.comparison_results = results
        return results
    
    def _compare_basic_info(self) -> Dict[str, Any]:
        """对比基本信息"""
        return {
            'df1': {
                'rows': len(self.df1),
                'columns': len(self.df1.columns),
                'memory': f"{self.df1.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            },
            'df2': {
                'rows': len(self.df2),
                'columns': len(self.df2.columns),
                'memory': f"{self.df2.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            },
            'difference': {
                'rows': len(self.df2) - len(self.df1),
                'columns': len(self.df2.columns) - len(self.df1.columns)
            }
        }
    
    def _compare_schema(self) -> Dict[str, Any]:
        """对比数据结构"""
        cols1 = set(self.df1.columns)
        cols2 = set(self.df2.columns)
        
        return {
            'common_columns': list(cols1 & cols2),
            'added_columns': list(cols2 - cols1),
            'removed_columns': list(cols1 - cols2),
            'dtype_changes': self._compare_dtypes()
        }
    
    def _compare_dtypes(self) -> List[Dict[str, Any]]:
        """对比数据类型变化"""
        changes = []
        common_cols = set(self.df1.columns) & set(self.df2.columns)
        
        for col in common_cols:
            dtype1 = str(self.df1[col].dtype)
            dtype2 = str(self.df2[col].dtype)
            if dtype1 != dtype2:
                changes.append({
                    'column': col,
                    'old_dtype': dtype1,
                    'new_dtype': dtype2
                })
        
        return changes
    
    def _compare_data(self) -> Dict[str, Any]:
        """对比数据内容"""
        if not self.key_columns:
            # 如果没有指定关键列，按索引对比
            return self._compare_by_index()
        else:
            # 按关键列对比
            return self._compare_by_key()
    
    def _compare_by_index(self) -> Dict[str, Any]:
        """按索引对比"""
        common_cols = list(set(self.df1.columns) & set(self.df2.columns))
        
        # 找出共同的索引
        common_idx = self.df1.index.intersection(self.df2.index)
        
        # 对比共同索引的数据
        df1_common = self.df1.loc[common_idx, common_cols]
        df2_common = self.df2.loc[common_idx, common_cols]
        
        # 找出不同的行
        diff_mask = (df1_common != df2_common).any(axis=1)
        modified_rows = df1_common[diff_mask].index.tolist()
        
        return {
            'added_rows': len(self.df2) - len(common_idx),
            'removed_rows': len(self.df1) - len(common_idx),
            'modified_rows': len(modified_rows),
            'unchanged_rows': len(common_idx) - len(modified_rows),
            'modified_indices': modified_rows[:10]  # 只显示前10个
        }
    
    def _compare_by_key(self) -> Dict[str, Any]:
        """按关键列对比"""
        # 合并两个数据框
        merged = self.df1.merge(
            self.df2,
            on=self.key_columns,
            how='outer',
            indicator=True,
            suffixes=('_old', '_new')
        )
        
        # 统计各类行
        added = merged[merged['_merge'] == 'right_only']
        removed = merged[merged['_merge'] == 'left_only']
        both = merged[merged['_merge'] == 'both']
        
        # 找出修改的行
        modified = []
        common_cols = [col for col in self.df1.columns if col not in self.key_columns]
        
        for col in common_cols:
            if f'{col}_old' in both.columns and f'{col}_new' in both.columns:
                diff_mask = both[f'{col}_old'] != both[f'{col}_new']
                modified.extend(both[diff_mask][self.key_columns].to_dict('records'))
        
        # 去重
        modified = [dict(t) for t in {tuple(d.items()) for d in modified}]
        
        return {
            'added_rows': len(added),
            'removed_rows': len(removed),
            'modified_rows': len(modified),
            'unchanged_rows': len(both) - len(modified),
            'added_samples': added[self.key_columns].head(5).to_dict('records'),
            'removed_samples': removed[self.key_columns].head(5).to_dict('records'),
            'modified_samples': modified[:5]
        }
    
    def get_added_rows(self) -> pd.DataFrame:
        """获取新增的行"""
        if not self.key_columns:
            new_idx = self.df2.index.difference(self.df1.index)
            return self.df2.loc[new_idx]
        else:
            merged = self.df1.merge(
                self.df2,
                on=self.key_columns,
                how='outer',
                indicator=True
            )
            return merged[merged['_merge'] == 'right_only'].drop('_merge', axis=1)
    
    def get_removed_rows(self) -> pd.DataFrame:
        """获取删除的行"""
        if not self.key_columns:
            old_idx = self.df1.index.difference(self.df2.index)
            return self.df1.loc[old_idx]
        else:
            merged = self.df1.merge(
                self.df2,
                on=self.key_columns,
                how='outer',
                indicator=True
            )
            return merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
    
    def get_modified_rows(self) -> pd.DataFrame:
        """获取修改的行"""
        if not self.key_columns:
            common_idx = self.df1.index.intersection(self.df2.index)
            common_cols = list(set(self.df1.columns) & set(self.df2.columns))
            
            df1_common = self.df1.loc[common_idx, common_cols]
            df2_common = self.df2.loc[common_idx, common_cols]
            
            diff_mask = (df1_common != df2_common).any(axis=1)
            return df2_common[diff_mask]
        else:
            # 按关键列对比
            merged = self.df1.merge(
                self.df2,
                on=self.key_columns,
                how='inner',
                suffixes=('_old', '_new')
            )
            
            # 找出有变化的行
            common_cols = [col for col in self.df1.columns if col not in self.key_columns]
            diff_mask = pd.Series(False, index=merged.index)
            
            for col in common_cols:
                if f'{col}_old' in merged.columns and f'{col}_new' in merged.columns:
                    diff_mask |= merged[f'{col}_old'] != merged[f'{col}_new']
            
            return merged[diff_mask]
    
    def print_report(self):
        """打印对比报告"""
        if not self.comparison_results:
            print("请先运行 compare()")
            return
        
        results = self.comparison_results
        
        print("\n" + "="*60)
        print("数据对比报告")
        print("="*60)
        
        # 基本信息
        print("\n【基本信息对比】")
        basic = results['basic_comparison']
        print(f"  数据集1: {basic['df1']['rows']} 行, {basic['df1']['columns']} 列")
        print(f"  数据集2: {basic['df2']['rows']} 行, {basic['df2']['columns']} 列")
        print(f"  差异: {basic['difference']['rows']:+d} 行, {basic['difference']['columns']:+d} 列")
        
        # 结构对比
        print("\n【结构对比】")
        schema = results['schema_comparison']
        print(f"  共同列: {len(schema['common_columns'])} 个")
        if schema['added_columns']:
            print(f"  新增列: {', '.join(schema['added_columns'])}")
        if schema['removed_columns']:
            print(f"  删除列: {', '.join(schema['removed_columns'])}")
        if schema['dtype_changes']:
            print(f"  类型变化: {len(schema['dtype_changes'])} 个")
            for change in schema['dtype_changes'][:3]:
                print(f"    - {change['column']}: {change['old_dtype']} → {change['new_dtype']}")
        
        # 数据对比
        print("\n【数据对比】")
        data = results['data_comparison']
        print(f"  新增行: {data['added_rows']}")
        print(f"  删除行: {data['removed_rows']}")
        print(f"  修改行: {data['modified_rows']}")
        print(f"  未变化: {data['unchanged_rows']}")
        
        print("\n" + "="*60)
    
    def export_report(self, output_path: str):
        """导出对比报告"""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.comparison_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ 报告已导出: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    df1 = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        'Name': ['A', 'B', 'C', 'D', 'E'],
        'Value': [10, 20, 30, 40, 50]
    })
    
    df2 = pd.DataFrame({
        'ID': [1, 2, 3, 5, 6],
        'Name': ['A', 'B', 'C_modified', 'E', 'F'],
        'Value': [10, 25, 30, 50, 60],
        'NewColumn': [100, 200, 300, 400, 500]
    })
    
    print("数据集1:")
    print(df1)
    print("\n数据集2:")
    print(df2)
    
    # 对比数据
    comparator = DataComparator(df1, df2, key_columns=['ID'])
    comparator.compare()
    comparator.print_report()
    
    # 获取差异
    print("\n新增的行:")
    print(comparator.get_added_rows())
    
    print("\n删除的行:")
    print(comparator.get_removed_rows())
    
    print("\n修改的行:")
    print(comparator.get_modified_rows())
