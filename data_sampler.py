"""
数据采样工具
功能：
1. 随机采样
2. 分层采样（保持比例）
3. 系统采样（等间隔）
4. 时间序列采样
5. 自动确定最佳采样率
6. 生成采样报告
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class DataSampler:
    """数据采样器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df.copy()
        self.sample_df = None
        self.sampling_report = {}
    
    def random_sample(
        self,
        n: Optional[int] = None,
        frac: Optional[float] = None,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """
        随机采样
        
        Args:
            n: 采样数量
            frac: 采样比例（0-1）
            random_state: 随机种子
        
        Returns:
            采样后的数据框
        """
        if n is None and frac is None:
            frac = 0.1  # 默认10%
        
        self.sample_df = self.df.sample(n=n, frac=frac, random_state=random_state)
        
        self.sampling_report = {
            'method': 'random',
            'original_size': len(self.df),
            'sample_size': len(self.sample_df),
            'sampling_rate': len(self.sample_df) / len(self.df) * 100
        }
        
        return self.sample_df
    
    def stratified_sample(
        self,
        stratify_column: str,
        n: Optional[int] = None,
        frac: Optional[float] = None,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """
        分层采样（保持各层比例）
        
        Args:
            stratify_column: 分层列
            n: 总采样数量
            frac: 采样比例
            random_state: 随机种子
        
        Returns:
            采样后的数据框
        """
        if stratify_column not in self.df.columns:
            raise ValueError(f"列不存在: {stratify_column}")
        
        if frac is None:
            frac = n / len(self.df) if n else 0.1
        
        # 按层采样
        samples = []
        strata_info = []
        
        for stratum, group in self.df.groupby(stratify_column):
            stratum_size = len(group)
            sample_size = int(stratum_size * frac)
            
            if sample_size > 0:
                stratum_sample = group.sample(
                    n=min(sample_size, stratum_size),
                    random_state=random_state
                )
                samples.append(stratum_sample)
                
                strata_info.append({
                    'stratum': str(stratum),
                    'original_size': stratum_size,
                    'sample_size': len(stratum_sample),
                    'proportion': stratum_size / len(self.df) * 100
                })
        
        self.sample_df = pd.concat(samples, ignore_index=True)
        
        self.sampling_report = {
            'method': 'stratified',
            'stratify_column': stratify_column,
            'original_size': len(self.df),
            'sample_size': len(self.sample_df),
            'sampling_rate': len(self.sample_df) / len(self.df) * 100,
            'strata': strata_info
        }
        
        return self.sample_df
    
    def systematic_sample(
        self,
        k: Optional[int] = None,
        start: int = 0
    ) -> pd.DataFrame:
        """
        系统采样（等间隔采样）
        
        Args:
            k: 采样间隔（每k个取1个）
            start: 起始位置
        
        Returns:
            采样后的数据框
        """
        if k is None:
            k = 10  # 默认每10个取1个
        
        indices = range(start, len(self.df), k)
        self.sample_df = self.df.iloc[list(indices)]
        
        self.sampling_report = {
            'method': 'systematic',
            'interval': k,
            'start': start,
            'original_size': len(self.df),
            'sample_size': len(self.sample_df),
            'sampling_rate': len(self.sample_df) / len(self.df) * 100
        }
        
        return self.sample_df
    
    def time_series_sample(
        self,
        date_column: str,
        freq: str = 'D',
        agg_func: str = 'mean'
    ) -> pd.DataFrame:
        """
        时间序列采样（按时间频率聚合）
        
        Args:
            date_column: 日期列
            freq: 频率（'D'=天, 'W'=周, 'M'=月, 'Q'=季度, 'Y'=年）
            agg_func: 聚合函数（'mean', 'sum', 'first', 'last'）
        
        Returns:
            采样后的数据框
        """
        if date_column not in self.df.columns:
            raise ValueError(f"列不存在: {date_column}")
        
        # 转换为日期类型
        df_temp = self.df.copy()
        df_temp[date_column] = pd.to_datetime(df_temp[date_column])
        df_temp = df_temp.set_index(date_column)
        
        # 按频率重采样（只对数值列）
        numeric_cols = df_temp.select_dtypes(include=['number']).columns
        
        if agg_func == 'mean':
            self.sample_df = df_temp[numeric_cols].resample(freq).mean()
        elif agg_func == 'sum':
            self.sample_df = df_temp[numeric_cols].resample(freq).sum()
        elif agg_func == 'first':
            self.sample_df = df_temp.resample(freq).first()
        elif agg_func == 'last':
            self.sample_df = df_temp.resample(freq).last()
        else:
            raise ValueError(f"不支持的聚合函数: {agg_func}")
        
        self.sample_df = self.sample_df.reset_index()
        
        self.sampling_report = {
            'method': 'time_series',
            'date_column': date_column,
            'frequency': freq,
            'aggregation': agg_func,
            'original_size': len(self.df),
            'sample_size': len(self.sample_df),
            'sampling_rate': len(self.sample_df) / len(self.df) * 100
        }
        
        return self.sample_df
    
    def auto_sample(
        self,
        target_size: Optional[int] = None,
        max_size: int = 10000,
        stratify_column: Optional[str] = None
    ) -> pd.DataFrame:
        """
        自动采样（智能确定最佳采样方法和比例）
        
        Args:
            target_size: 目标大小
            max_size: 最大大小
            stratify_column: 分层列（可选）
        
        Returns:
            采样后的数据框
        """
        original_size = len(self.df)
        
        # 如果数据集小于最大大小，不需要采样
        if original_size <= max_size:
            self.sample_df = self.df.copy()
            self.sampling_report = {
                'method': 'none',
                'reason': '数据集小于最大大小，无需采样',
                'original_size': original_size,
                'sample_size': original_size
            }
            return self.sample_df
        
        # 确定目标大小
        if target_size is None:
            target_size = min(max_size, int(original_size * 0.1))
        
        # 选择采样方法
        if stratify_column and stratify_column in self.df.columns:
            # 如果指定了分层列，使用分层采样
            frac = target_size / original_size
            return self.stratified_sample(stratify_column, frac=frac)
        else:
            # 否则使用随机采样
            return self.random_sample(n=target_size)
    
    def cluster_sample(
        self,
        cluster_column: str,
        n_clusters: Optional[int] = None,
        frac_clusters: Optional[float] = None,
        random_state: Optional[int] = None
    ) -> pd.DataFrame:
        """
        整群采样（随机选择若干群，取出所有样本）
        
        Args:
            cluster_column: 群组列
            n_clusters: 选择的群数
            frac_clusters: 选择的群比例
            random_state: 随机种子
        
        Returns:
            采样后的数据框
        """
        if cluster_column not in self.df.columns:
            raise ValueError(f"列不存在: {cluster_column}")
        
        # 获取所有群
        all_clusters = self.df[cluster_column].unique()
        
        # 确定选择多少个群
        if n_clusters is None and frac_clusters is None:
            frac_clusters = 0.3  # 默认30%的群
        
        if frac_clusters:
            n_clusters = int(len(all_clusters) * frac_clusters)
        
        # 随机选择群
        np.random.seed(random_state)
        selected_clusters = np.random.choice(
            all_clusters,
            size=min(n_clusters, len(all_clusters)),
            replace=False
        )
        
        # 提取选中群的所有数据
        self.sample_df = self.df[self.df[cluster_column].isin(selected_clusters)]
        
        self.sampling_report = {
            'method': 'cluster',
            'cluster_column': cluster_column,
            'total_clusters': len(all_clusters),
            'selected_clusters': len(selected_clusters),
            'original_size': len(self.df),
            'sample_size': len(self.sample_df),
            'sampling_rate': len(self.sample_df) / len(self.df) * 100
        }
        
        return self.sample_df
    
    def print_report(self):
        """打印采样报告"""
        if not self.sampling_report:
            print("请先执行采样")
            return
        
        report = self.sampling_report
        
        print("\n" + "="*60)
        print("采样报告")
        print("="*60)
        
        print(f"\n【采样方法】 {report['method']}")
        print(f"  原始大小: {report['original_size']} 行")
        print(f"  采样大小: {report['sample_size']} 行")
        if 'sampling_rate' in report:
            print(f"  采样率: {report['sampling_rate']:.2f}%")
        if 'reason' in report:
            print(f"  说明: {report['reason']}")
        
        # 方法特定信息
        if report['method'] == 'stratified':
            print(f"\n【分层信息】")
            print(f"  分层列: {report['stratify_column']}")
            print(f"  层数: {len(report['strata'])}")
            for stratum in report['strata']:
                print(f"    - {stratum['stratum']}: {stratum['sample_size']}/{stratum['original_size']} ({stratum['proportion']:.1f}%)")
        
        elif report['method'] == 'systematic':
            print(f"\n【系统采样】")
            print(f"  采样间隔: {report['interval']}")
            print(f"  起始位置: {report['start']}")
        
        elif report['method'] == 'time_series':
            print(f"\n【时间序列】")
            print(f"  日期列: {report['date_column']}")
            print(f"  频率: {report['frequency']}")
            print(f"  聚合方式: {report['aggregation']}")
        
        elif report['method'] == 'cluster':
            print(f"\n【整群采样】")
            print(f"  群组列: {report['cluster_column']}")
            print(f"  总群数: {report['total_clusters']}")
            print(f"  选中群数: {report['selected_clusters']}")
        
        print("\n" + "="*60)
    
    def get_sample(self) -> pd.DataFrame:
        """获取采样结果"""
        if self.sample_df is None:
            raise ValueError("请先执行采样")
        return self.sample_df
    
    def save_sample(self, output_path: str):
        """保存采样结果"""
        if self.sample_df is None:
            raise ValueError("请先执行采样")
        
        self.sample_df.to_csv(output_path, index=False)
        print(f"✓ 采样结果已保存: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    np.random.seed(42)
    df = pd.DataFrame({
        'ID': range(1, 1001),
        'Category': np.random.choice(['A', 'B', 'C'], 1000),
        'Value': np.random.randn(1000) * 100 + 500,
        'Date': pd.date_range('2024-01-01', periods=1000, freq='h')
    })
    
    print("原始数据:")
    print(f"  大小: {len(df)} 行")
    print(f"  列: {list(df.columns)}")
    
    # 创建采样器
    sampler = DataSampler(df)
    
    # 示例1：随机采样
    print("\n【示例1：随机采样 10%】")
    sample1 = sampler.random_sample(frac=0.1)
    sampler.print_report()
    
    # 示例2：分层采样
    print("\n【示例2：分层采样（按类别）】")
    sample2 = sampler.stratified_sample('Category', frac=0.1)
    sampler.print_report()
    
    # 示例3：系统采样
    print("\n【示例3：系统采样（每10个取1个）】")
    sample3 = sampler.systematic_sample(k=10)
    sampler.print_report()
    
    # 示例4：时间序列采样
    print("\n【示例4：时间序列采样（按天聚合）】")
    sample4 = sampler.time_series_sample('Date', freq='D', agg_func='mean')
    sampler.print_report()
    
    # 示例5：自动采样
    print("\n【示例5：自动采样】")
    sample5 = sampler.auto_sample(target_size=100, stratify_column='Category')
    sampler.print_report()
    
    print("\n完成！")
