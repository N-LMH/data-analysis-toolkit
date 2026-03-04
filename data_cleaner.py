"""
数据清洗工具
功能：
1. 处理缺失值
2. 删除重复行
3. 数据类型转换
4. 异常值检测和处理
5. 数据标准化
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.cleaning_log = []
    
    def handle_missing_values(
        self,
        strategy: str = 'drop',
        columns: Optional[List[str]] = None,
        fill_value: Any = None
    ) -> 'DataCleaner':
        """
        处理缺失值
        
        Args:
            strategy: 策略 ('drop', 'fill', 'forward', 'backward')
            columns: 指定列（None = 所有列）
            fill_value: 填充值（strategy='fill'时使用）
        
        Returns:
            self
        """
        cols = columns or self.df.columns
        
        if strategy == 'drop':
            before = len(self.df)
            self.df = self.df.dropna(subset=cols)
            after = len(self.df)
            self.cleaning_log.append(f"删除缺失值: {before - after} 行")
        
        elif strategy == 'fill':
            for col in cols:
                if fill_value is not None:
                    self.df[col].fillna(fill_value, inplace=True)
                else:
                    # 数值列用均值，分类列用众数
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        self.df[col].fillna(self.df[col].mean(), inplace=True)
                    else:
                        self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            self.cleaning_log.append(f"填充缺失值: {len(cols)} 列")
        
        elif strategy == 'forward':
            self.df[cols] = self.df[cols].fillna(method='ffill')
            self.cleaning_log.append(f"前向填充: {len(cols)} 列")
        
        elif strategy == 'backward':
            self.df[cols] = self.df[cols].fillna(method='bfill')
            self.cleaning_log.append(f"后向填充: {len(cols)} 列")
        
        return self
    
    def remove_duplicates(
        self,
        subset: Optional[List[str]] = None,
        keep: str = 'first'
    ) -> 'DataCleaner':
        """
        删除重复行
        
        Args:
            subset: 指定列（None = 所有列）
            keep: 保留哪个 ('first', 'last', False)
        
        Returns:
            self
        """
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        after = len(self.df)
        
        self.cleaning_log.append(f"删除重复行: {before - after} 行")
        return self
    
    def convert_types(
        self,
        conversions: Dict[str, str]
    ) -> 'DataCleaner':
        """
        转换数据类型
        
        Args:
            conversions: {列名: 目标类型}
        
        Returns:
            self
        """
        for col, dtype in conversions.items():
            if col in self.df.columns:
                try:
                    if dtype == 'datetime':
                        self.df[col] = pd.to_datetime(self.df[col])
                    else:
                        self.df[col] = self.df[col].astype(dtype)
                    self.cleaning_log.append(f"转换类型: {col} -> {dtype}")
                except Exception as e:
                    self.cleaning_log.append(f"转换失败: {col} -> {dtype} ({e})")
        
        return self
    
    def detect_outliers(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> Dict[str, List[int]]:
        """
        检测异常值
        
        Args:
            columns: 指定列（None = 所有数值列）
            method: 方法 ('iqr', 'zscore')
            threshold: 阈值（IQR倍数或Z-score阈值）
        
        Returns:
            {列名: [异常值索引]}
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        outliers = {}
        
        for col in columns:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                outlier_mask = z_scores > threshold
            
            outlier_indices = self.df[outlier_mask].index.tolist()
            if outlier_indices:
                outliers[col] = outlier_indices
        
        return outliers
    
    def remove_outliers(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> 'DataCleaner':
        """
        删除异常值
        
        Args:
            columns: 指定列（None = 所有数值列）
            method: 方法 ('iqr', 'zscore')
            threshold: 阈值
        
        Returns:
            self
        """
        outliers = self.detect_outliers(columns, method, threshold)
        
        if outliers:
            all_outlier_indices = set()
            for indices in outliers.values():
                all_outlier_indices.update(indices)
            
            before = len(self.df)
            self.df = self.df.drop(list(all_outlier_indices))
            after = len(self.df)
            
            self.cleaning_log.append(f"删除异常值: {before - after} 行")
        
        return self
    
    def normalize(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'minmax'
    ) -> 'DataCleaner':
        """
        数据标准化
        
        Args:
            columns: 指定列（None = 所有数值列）
            method: 方法 ('minmax', 'zscore')
        
        Returns:
            self
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        for col in columns:
            if method == 'minmax':
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                self.df[col] = (self.df[col] - min_val) / (max_val - min_val)
            
            elif method == 'zscore':
                mean = self.df[col].mean()
                std = self.df[col].std()
                self.df[col] = (self.df[col] - mean) / std
        
        self.cleaning_log.append(f"标准化: {len(columns)} 列 ({method})")
        return self
    
    def get_cleaned_data(self) -> pd.DataFrame:
        """获取清洗后的数据"""
        return self.df
    
    def get_log(self) -> List[str]:
        """获取清洗日志"""
        return self.cleaning_log
    
    def reset(self):
        """重置到原始数据"""
        self.df = self.original_df.copy()
        self.cleaning_log = []
        return self


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5, 100],
        'B': [10, 20, 30, 30, 50, 60],
        'C': ['x', 'y', 'z', 'x', 'y', 'z']
    })
    
    print("原始数据:")
    print(df)
    print()
    
    # 清洗数据
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values(strategy='fill')
    cleaner.remove_duplicates()
    cleaner.remove_outliers(columns=['A'], method='iqr')
    
    print("清洗后数据:")
    print(cleaner.get_cleaned_data())
    print()
    
    print("清洗日志:")
    for log in cleaner.get_log():
        print(f"  - {log}")
