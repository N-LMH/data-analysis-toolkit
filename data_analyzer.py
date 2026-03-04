"""
CSV 数据分析工具
功能：
1. 读取 CSV/Excel 文件
2. 自动分析数据
3. 生成统计报告
4. 数据可视化
5. 导出报告
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import json

class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self):
        """初始化"""
        self.df = None
        self.file_path = None
        self.analysis_results = {}
    
    def load_file(self, file_path: str) -> bool:
        """
        加载文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        try:
            path = Path(file_path)
            
            if path.suffix.lower() == '.csv':
                self.df = pd.read_csv(file_path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {path.suffix}")
            
            self.file_path = file_path
            print(f"✓ 成功加载文件: {path.name}")
            print(f"  行数: {len(self.df)}")
            print(f"  列数: {len(self.df.columns)}")
            
            return True
        
        except Exception as e:
            print(f"✗ 加载失败: {e}")
            return False
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析数据
        
        Returns:
            分析结果
        """
        if self.df is None:
            raise ValueError("请先加载文件")
        
        results = {
            'basic_info': self._analyze_basic_info(),
            'columns': self._analyze_columns(),
            'missing_values': self._analyze_missing_values(),
            'numeric_stats': self._analyze_numeric_stats(),
            'categorical_stats': self._analyze_categorical_stats(),
            'correlations': self._analyze_correlations()
        }
        
        self.analysis_results = results
        return results
    
    def _analyze_basic_info(self) -> Dict[str, Any]:
        """基本信息"""
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_names': list(self.df.columns)
        }
    
    def _analyze_columns(self) -> List[Dict[str, Any]]:
        """列分析"""
        columns = []
        
        for col in self.df.columns:
            col_info = {
                'name': col,
                'dtype': str(self.df[col].dtype),
                'non_null': int(self.df[col].count()),
                'null': int(self.df[col].isnull().sum()),
                'unique': int(self.df[col].nunique())
            }
            
            # 数值列
            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_info['type'] = 'numeric'
                col_info['min'] = float(self.df[col].min())
                col_info['max'] = float(self.df[col].max())
                col_info['mean'] = float(self.df[col].mean())
                col_info['median'] = float(self.df[col].median())
            else:
                col_info['type'] = 'categorical'
                col_info['top_values'] = self.df[col].value_counts().head(5).to_dict()
            
            columns.append(col_info)
        
        return columns
    
    def _analyze_missing_values(self) -> Dict[str, Any]:
        """缺失值分析"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        
        return {
            'total_missing': int(missing.sum()),
            'columns_with_missing': [
                {
                    'column': col,
                    'count': int(missing[col]),
                    'percentage': float(missing_pct[col])
                }
                for col in missing[missing > 0].index
            ]
        }
    
    def _analyze_numeric_stats(self) -> Dict[str, Dict[str, float]]:
        """数值列统计"""
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'count': int(self.df[col].count()),
                'mean': float(self.df[col].mean()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                '25%': float(self.df[col].quantile(0.25)),
                '50%': float(self.df[col].quantile(0.50)),
                '75%': float(self.df[col].quantile(0.75)),
                'max': float(self.df[col].max())
            }
        
        return stats
    
    def _analyze_categorical_stats(self) -> Dict[str, Dict[str, Any]]:
        """分类列统计"""
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        stats = {}
        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            stats[col] = {
                'unique': int(self.df[col].nunique()),
                'top': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'freq': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'distribution': value_counts.head(10).to_dict()
            }
        
        return stats
    
    def _analyze_correlations(self) -> Dict[str, Any]:
        """相关性分析"""
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {'message': '数值列不足，无法计算相关性'}
        
        corr_matrix = self.df[numeric_cols].corr()
        
        # 找出高相关性的列对
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'matrix': corr_matrix.to_dict(),
            'high_correlations': high_corr
        }
    
    def print_report(self):
        """打印分析报告"""
        if not self.analysis_results:
            print("请先运行 analyze()")
            return
        
        results = self.analysis_results
        
        print("\n" + "="*60)
        print("数据分析报告")
        print("="*60)
        
        # 基本信息
        print("\n【基本信息】")
        info = results['basic_info']
        print(f"  行数: {info['rows']}")
        print(f"  列数: {info['columns']}")
        print(f"  内存占用: {info['memory_usage']}")
        
        # 缺失值
        print("\n【缺失值】")
        missing = results['missing_values']
        if missing['total_missing'] == 0:
            print("  无缺失值")
        else:
            print(f"  总缺失值: {missing['total_missing']}")
            for col_info in missing['columns_with_missing']:
                print(f"  - {col_info['column']}: {col_info['count']} ({col_info['percentage']:.2f}%)")
        
        # 数值列统计
        print("\n【数值列统计】")
        numeric_stats = results['numeric_stats']
        if not numeric_stats:
            print("  无数值列")
        else:
            for col, stats in numeric_stats.items():
                print(f"\n  {col}:")
                print(f"    均值: {stats['mean']:.2f}")
                print(f"    标准差: {stats['std']:.2f}")
                print(f"    最小值: {stats['min']:.2f}")
                print(f"    最大值: {stats['max']:.2f}")
        
        # 分类列统计
        print("\n【分类列统计】")
        categorical_stats = results['categorical_stats']
        if not categorical_stats:
            print("  无分类列")
        else:
            for col, stats in categorical_stats.items():
                print(f"\n  {col}:")
                print(f"    唯一值: {stats['unique']}")
                print(f"    最常见: {stats['top']} (出现 {stats['freq']} 次)")
        
        # 相关性
        print("\n【高相关性列对】")
        corr = results['correlations']
        if 'message' in corr:
            print(f"  {corr['message']}")
        elif not corr['high_correlations']:
            print("  无高相关性列对 (|r| > 0.7)")
        else:
            for pair in corr['high_correlations']:
                print(f"  - {pair['col1']} <-> {pair['col2']}: {pair['correlation']:.3f}")
        
        print("\n" + "="*60)
    
    def export_report(self, output_path: str):
        """
        导出报告
        
        Args:
            output_path: 输出路径 (.json 或 .txt)
        """
        if not self.analysis_results:
            print("请先运行 analyze()")
            return
        
        path = Path(output_path)
        
        if path.suffix == '.json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            print(f"✓ 报告已导出: {output_path}")
        
        elif path.suffix == '.txt':
            # 重定向 print 到文件
            import sys
            original_stdout = sys.stdout
            with open(output_path, 'w', encoding='utf-8') as f:
                sys.stdout = f
                self.print_report()
                sys.stdout = original_stdout
            print(f"✓ 报告已导出: {output_path}")
        
        else:
            print(f"不支持的格式: {path.suffix}")


# 使用示例
if __name__ == "__main__":
    # 创建分析器
    analyzer = DataAnalyzer()
    
    # 加载文件
    if analyzer.load_file("test_data.csv"):
        # 分析数据
        analyzer.analyze()
        
        # 打印报告
        analyzer.print_report()
        
        # 导出报告
        analyzer.export_report("analysis_report.json")
        analyzer.export_report("analysis_report.txt")
