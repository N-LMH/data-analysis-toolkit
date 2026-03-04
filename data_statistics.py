"""
数据统计工具
功能：
1. 描述性统计
2. 假设检验（t检验、卡方检验）
3. 相关性分析
4. 回归分析
5. 分布检验
6. 生成统计报告
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats

class DataStatistics:
    """数据统计分析器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df.copy()
        self.stats_results = {}
    
    def descriptive_stats(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        描述性统计
        
        Args:
            columns: 指定列（None = 所有数值列）
        
        Returns:
            统计结果
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        results = {}
        
        for col in columns:
            if col not in self.df.columns:
                continue
            
            data = self.df[col].dropna()
            
            results[col] = {
                'count': int(len(data)),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'mode': float(data.mode()[0]) if len(data.mode()) > 0 else None,
                'std': float(data.std()),
                'var': float(data.var()),
                'min': float(data.min()),
                'max': float(data.max()),
                'range': float(data.max() - data.min()),
                'q25': float(data.quantile(0.25)),
                'q50': float(data.quantile(0.50)),
                'q75': float(data.quantile(0.75)),
                'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
                'skewness': float(data.skew()),
                'kurtosis': float(data.kurtosis())
            }
        
        self.stats_results['descriptive'] = results
        return results
    
    def t_test(
        self,
        column1: str,
        column2: Optional[str] = None,
        value: Optional[float] = None,
        alternative: str = 'two-sided'
    ) -> Dict[str, Any]:
        """
        t检验
        
        Args:
            column1: 第一列
            column2: 第二列（配对t检验）
            value: 比较值（单样本t检验）
            alternative: 备择假设（'two-sided', 'less', 'greater'）
        
        Returns:
            检验结果
        """
        data1 = self.df[column1].dropna()
        
        if column2:
            # 配对t检验
            data2 = self.df[column2].dropna()
            statistic, pvalue = stats.ttest_rel(data1, data2, alternative=alternative)
            test_type = 'paired'
        elif value is not None:
            # 单样本t检验
            statistic, pvalue = stats.ttest_1samp(data1, value, alternative=alternative)
            test_type = 'one-sample'
        else:
            raise ValueError("必须指定 column2 或 value")
        
        result = {
            'test_type': test_type,
            'statistic': float(statistic),
            'pvalue': float(pvalue),
            'significant': pvalue < 0.05,
            'alternative': alternative
        }
        
        self.stats_results['t_test'] = result
        return result
    
    def chi_square_test(
        self,
        column1: str,
        column2: str
    ) -> Dict[str, Any]:
        """
        卡方检验（独立性检验）
        
        Args:
            column1: 第一列
            column2: 第二列
        
        Returns:
            检验结果
        """
        # 创建列联表
        contingency_table = pd.crosstab(self.df[column1], self.df[column2])
        
        # 卡方检验
        chi2, pvalue, dof, expected = stats.chi2_contingency(contingency_table)
        
        result = {
            'chi2': float(chi2),
            'pvalue': float(pvalue),
            'dof': int(dof),
            'significant': pvalue < 0.05,
            'contingency_table': contingency_table.to_dict()
        }
        
        self.stats_results['chi_square'] = result
        return result
    
    def correlation_analysis(
        self,
        columns: Optional[List[str]] = None,
        method: str = 'pearson'
    ) -> Dict[str, Any]:
        """
        相关性分析
        
        Args:
            columns: 指定列（None = 所有数值列）
            method: 方法（'pearson', 'spearman', 'kendall'）
        
        Returns:
            相关性矩阵和显著性
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        data = self.df[columns].dropna()
        
        # 计算相关系数
        corr_matrix = data.corr(method=method)
        
        # 计算p值
        n = len(data)
        pvalue_matrix = pd.DataFrame(
            np.zeros((len(columns), len(columns))),
            index=columns,
            columns=columns
        )
        
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i != j:
                    if method == 'pearson':
                        _, pvalue = stats.pearsonr(data[col1], data[col2])
                    elif method == 'spearman':
                        _, pvalue = stats.spearmanr(data[col1], data[col2])
                    else:
                        _, pvalue = stats.kendalltau(data[col1], data[col2])
                    pvalue_matrix.iloc[i, j] = pvalue
        
        # 找出显著相关的列对
        significant_pairs = []
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i < j:  # 只取上三角
                    corr = corr_matrix.iloc[i, j]
                    pvalue = pvalue_matrix.iloc[i, j]
                    if pvalue < 0.05:
                        significant_pairs.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': float(corr),
                            'pvalue': float(pvalue)
                        })
        
        result = {
            'method': method,
            'correlation_matrix': corr_matrix.to_dict(),
            'pvalue_matrix': pvalue_matrix.to_dict(),
            'significant_pairs': significant_pairs
        }
        
        self.stats_results['correlation'] = result
        return result
    
    def linear_regression(
        self,
        x_column: str,
        y_column: str
    ) -> Dict[str, Any]:
        """
        线性回归分析
        
        Args:
            x_column: 自变量列
            y_column: 因变量列
        
        Returns:
            回归结果
        """
        # 准备数据
        data = self.df[[x_column, y_column]].dropna()
        X = data[x_column].values
        y = data[y_column].values
        
        # 计算回归系数（使用最小二乘法）
        n = len(X)
        x_mean = np.mean(X)
        y_mean = np.mean(y)
        
        # 计算斜率和截距
        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # 预测
        y_pred = intercept + slope * X
        
        # 计算R²
        ss_total = np.sum((y - y_mean) ** 2)
        ss_residual = np.sum((y - y_pred) ** 2)
        r_squared = 1 - (ss_residual / ss_total)
        
        # 计算标准误差
        mse = ss_residual / (n - 2)
        se = np.sqrt(mse)
        
        result = {
            'intercept': float(intercept),
            'slope': float(slope),
            'r_squared': float(r_squared),
            'standard_error': float(se),
            'equation': f'y = {intercept:.4f} + {slope:.4f}x'
        }
        
        self.stats_results['linear_regression'] = result
        return result
    
    def normality_test(
        self,
        column: str,
        method: str = 'shapiro'
    ) -> Dict[str, Any]:
        """
        正态性检验
        
        Args:
            column: 列名
            method: 方法（'shapiro', 'kstest'）
        
        Returns:
            检验结果
        """
        data = self.df[column].dropna()
        
        if method == 'shapiro':
            # Shapiro-Wilk检验
            statistic, pvalue = stats.shapiro(data)
            test_name = 'Shapiro-Wilk'
        elif method == 'kstest':
            # Kolmogorov-Smirnov检验
            statistic, pvalue = stats.kstest(data, 'norm')
            test_name = 'Kolmogorov-Smirnov'
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        result = {
            'test': test_name,
            'statistic': float(statistic),
            'pvalue': float(pvalue),
            'is_normal': pvalue > 0.05
        }
        
        self.stats_results['normality'] = result
        return result
    
    def anova(
        self,
        value_column: str,
        group_column: str
    ) -> Dict[str, Any]:
        """
        方差分析（ANOVA）
        
        Args:
            value_column: 数值列
            group_column: 分组列
        
        Returns:
            检验结果
        """
        # 按组分割数据
        groups = []
        group_names = []
        
        for name, group in self.df.groupby(group_column):
            groups.append(group[value_column].dropna().values)
            group_names.append(str(name))
        
        # 单因素方差分析
        f_statistic, pvalue = stats.f_oneway(*groups)
        
        # 计算组间和组内统计
        group_stats = []
        for name, data in zip(group_names, groups):
            group_stats.append({
                'group': name,
                'count': len(data),
                'mean': float(np.mean(data)),
                'std': float(np.std(data))
            })
        
        result = {
            'f_statistic': float(f_statistic),
            'pvalue': float(pvalue),
            'significant': pvalue < 0.05,
            'group_stats': group_stats
        }
        
        self.stats_results['anova'] = result
        return result
    
    def print_report(self):
        """打印统计报告"""
        if not self.stats_results:
            print("请先执行统计分析")
            return
        
        print("\n" + "="*60)
        print("统计分析报告")
        print("="*60)
        
        # 描述性统计
        if 'descriptive' in self.stats_results:
            print("\n【描述性统计】")
            for col, stats in self.stats_results['descriptive'].items():
                print(f"\n  {col}:")
                print(f"    样本数: {stats['count']}")
                print(f"    均值: {stats['mean']:.4f}")
                print(f"    中位数: {stats['median']:.4f}")
                print(f"    标准差: {stats['std']:.4f}")
                print(f"    范围: [{stats['min']:.4f}, {stats['max']:.4f}]")
        
        # t检验
        if 't_test' in self.stats_results:
            print("\n【t检验】")
            result = self.stats_results['t_test']
            print(f"  类型: {result['test_type']}")
            print(f"  统计量: {result['statistic']:.4f}")
            print(f"  p值: {result['pvalue']:.4f}")
            print(f"  显著性: {'是' if result['significant'] else '否'} (α=0.05)")
        
        # 卡方检验
        if 'chi_square' in self.stats_results:
            print("\n【卡方检验】")
            result = self.stats_results['chi_square']
            print(f"  卡方值: {result['chi2']:.4f}")
            print(f"  p值: {result['pvalue']:.4f}")
            print(f"  自由度: {result['dof']}")
            print(f"  显著性: {'是' if result['significant'] else '否'} (α=0.05)")
        
        # 相关性分析
        if 'correlation' in self.stats_results:
            print("\n【相关性分析】")
            result = self.stats_results['correlation']
            print(f"  方法: {result['method']}")
            if result['significant_pairs']:
                print(f"  显著相关对数: {len(result['significant_pairs'])}")
                for pair in result['significant_pairs'][:5]:
                    print(f"    - {pair['column1']} <-> {pair['column2']}: r={pair['correlation']:.3f} (p={pair['pvalue']:.4f})")
            else:
                print("  无显著相关")
        
        # 线性回归
        if 'linear_regression' in self.stats_results:
            print("\n【线性回归】")
            result = self.stats_results['linear_regression']
            print(f"  方程: {result['equation']}")
            print(f"  R²: {result['r_squared']:.4f}")
            print(f"  标准误差: {result['standard_error']:.4f}")
        
        # 正态性检验
        if 'normality' in self.stats_results:
            print("\n【正态性检验】")
            result = self.stats_results['normality']
            print(f"  检验: {result['test']}")
            print(f"  统计量: {result['statistic']:.4f}")
            print(f"  p值: {result['pvalue']:.4f}")
            print(f"  正态分布: {'是' if result['is_normal'] else '否'} (α=0.05)")
        
        # 方差分析
        if 'anova' in self.stats_results:
            print("\n【方差分析】")
            result = self.stats_results['anova']
            print(f"  F统计量: {result['f_statistic']:.4f}")
            print(f"  p值: {result['pvalue']:.4f}")
            print(f"  显著性: {'是' if result['significant'] else '否'} (α=0.05)")
        
        print("\n" + "="*60)
    
    def export_report(self, output_path: str):
        """导出统计报告"""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ 报告已导出: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 创建测试数据
    np.random.seed(42)
    df = pd.DataFrame({
        'Group': np.random.choice(['A', 'B', 'C'], 100),
        'Value1': np.random.normal(100, 15, 100),
        'Value2': np.random.normal(105, 20, 100),
        'Score': np.random.normal(75, 10, 100)
    })
    
    # 添加相关性
    df['Value2'] = df['Value1'] * 0.8 + np.random.normal(0, 5, 100)
    
    print("测试数据:")
    print(df.head())
    
    # 创建统计分析器
    stats_analyzer = DataStatistics(df)
    
    # 描述性统计
    print("\n【描述性统计】")
    desc_stats = stats_analyzer.descriptive_stats(['Value1', 'Value2', 'Score'])
    
    # 相关性分析
    print("\n【相关性分析】")
    corr_result = stats_analyzer.correlation_analysis(['Value1', 'Value2', 'Score'])
    
    # 线性回归
    print("\n【线性回归】")
    reg_result = stats_analyzer.linear_regression('Value1', 'Value2')
    
    # 正态性检验
    print("\n【正态性检验】")
    norm_result = stats_analyzer.normality_test('Value1')
    
    # 方差分析
    print("\n【方差分析】")
    anova_result = stats_analyzer.anova('Score', 'Group')
    
    # 打印完整报告
    stats_analyzer.print_report()
    
    # 导出报告
    stats_analyzer.export_report('stats_report.json')
    
    print("\n完成！")
