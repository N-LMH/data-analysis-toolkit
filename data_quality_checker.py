"""
数据质量检查工具
功能：
1. 完整性检查（缺失值、空值）
2. 一致性检查（数据类型、格式）
3. 准确性检查（范围、逻辑）
4. 唯一性检查（重复值、主键）
5. 时效性检查（日期范围）
6. 生成质量报告和评分
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df.copy()
        self.quality_report = {}
        self.quality_score = 0
    
    def check_all(self) -> Dict[str, Any]:
        """
        执行所有质量检查
        
        Returns:
            质量报告
        """
        report = {
            'completeness': self.check_completeness(),
            'consistency': self.check_consistency(),
            'accuracy': self.check_accuracy(),
            'uniqueness': self.check_uniqueness(),
            'timeliness': self.check_timeliness(),
            'overall_score': 0
        }
        
        # 计算总体质量分数
        scores = []
        for key, value in report.items():
            if key != 'overall_score' and isinstance(value, dict) and 'score' in value:
                scores.append(value['score'])
        
        report['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        self.quality_report = report
        self.quality_score = report['overall_score']
        
        return report
    
    def check_completeness(self) -> Dict[str, Any]:
        """
        完整性检查
        检查缺失值、空值
        """
        total_cells = self.df.size
        missing_cells = self.df.isnull().sum().sum()
        
        # 检查空字符串
        empty_strings = 0
        for col in self.df.select_dtypes(include=['object']).columns:
            empty_strings += (self.df[col] == '').sum()
        
        completeness_rate = (total_cells - missing_cells - empty_strings) / total_cells * 100
        
        # 按列统计
        column_stats = []
        for col in self.df.columns:
            missing = self.df[col].isnull().sum()
            empty = (self.df[col] == '').sum() if self.df[col].dtype == 'object' else 0
            total = len(self.df)
            
            column_stats.append({
                'column': col,
                'missing': int(missing),
                'empty': int(empty),
                'total': total,
                'completeness_rate': (total - missing - empty) / total * 100
            })
        
        return {
            'score': completeness_rate,
            'total_cells': total_cells,
            'missing_cells': int(missing_cells),
            'empty_strings': int(empty_strings),
            'completeness_rate': completeness_rate,
            'column_stats': column_stats,
            'issues': [stat for stat in column_stats if stat['completeness_rate'] < 95]
        }
    
    def check_consistency(self) -> Dict[str, Any]:
        """
        一致性检查
        检查数据类型、格式
        """
        issues = []
        
        # 检查数值列中的非数值
        for col in self.df.select_dtypes(include=['number']).columns:
            # 已经是数值类型，跳过
            pass
        
        # 检查日期列格式
        date_columns = []
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.df[col], errors='coerce')
                    date_columns.append(col)
                except:
                    issues.append({
                        'column': col,
                        'issue': '日期格式不一致',
                        'severity': 'medium'
                    })
        
        # 检查分类列的值分布
        for col in self.df.select_dtypes(include=['object']).columns:
            unique_count = self.df[col].nunique()
            total_count = len(self.df)
            
            # 如果唯一值太多，可能不是分类列
            if unique_count > total_count * 0.5:
                issues.append({
                    'column': col,
                    'issue': f'唯一值过多 ({unique_count}/{total_count})',
                    'severity': 'low'
                })
        
        # 计算一致性分数
        consistency_score = max(0, 100 - len(issues) * 10)
        
        return {
            'score': consistency_score,
            'date_columns': date_columns,
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def check_accuracy(self) -> Dict[str, Any]:
        """
        准确性检查
        检查数值范围、逻辑关系
        """
        issues = []
        
        # 检查数值列的范围
        for col in self.df.select_dtypes(include=['number']).columns:
            # 检查负数（如果不应该有负数）
            if col.lower() in ['age', 'price', 'quantity', 'amount']:
                negative_count = (self.df[col] < 0).sum()
                if negative_count > 0:
                    issues.append({
                        'column': col,
                        'issue': f'包含 {negative_count} 个负数',
                        'severity': 'high'
                    })
            
            # 检查异常值（使用 IQR 方法）
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR
            upper = Q3 + 3 * IQR
            
            outliers = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
            if outliers > len(self.df) * 0.05:  # 超过5%
                issues.append({
                    'column': col,
                    'issue': f'包含 {outliers} 个异常值 ({outliers/len(self.df)*100:.1f}%)',
                    'severity': 'medium'
                })
        
        # 检查逻辑关系
        # 例如：开始日期应该早于结束日期
        date_cols = [col for col in self.df.columns if 'date' in col.lower()]
        if len(date_cols) >= 2:
            for i in range(len(date_cols) - 1):
                col1, col2 = date_cols[i], date_cols[i+1]
                try:
                    df_dates = self.df[[col1, col2]].copy()
                    df_dates[col1] = pd.to_datetime(df_dates[col1], errors='coerce')
                    df_dates[col2] = pd.to_datetime(df_dates[col2], errors='coerce')
                    
                    invalid = (df_dates[col1] > df_dates[col2]).sum()
                    if invalid > 0:
                        issues.append({
                            'column': f'{col1} vs {col2}',
                            'issue': f'{invalid} 行的日期顺序错误',
                            'severity': 'high'
                        })
                except:
                    pass
        
        # 计算准确性分数
        accuracy_score = max(0, 100 - len(issues) * 15)
        
        return {
            'score': accuracy_score,
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def check_uniqueness(self) -> Dict[str, Any]:
        """
        唯一性检查
        检查重复值、主键
        """
        # 检查完全重复的行
        duplicate_rows = self.df.duplicated().sum()
        
        # 检查每列的重复情况
        column_stats = []
        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            total_count = len(self.df)
            duplicate_count = total_count - unique_count
            
            column_stats.append({
                'column': col,
                'unique': int(unique_count),
                'duplicates': int(duplicate_count),
                'uniqueness_rate': unique_count / total_count * 100
            })
        
        # 识别可能的主键列
        potential_keys = [
            stat['column'] for stat in column_stats 
            if stat['uniqueness_rate'] == 100
        ]
        
        # 计算唯一性分数
        uniqueness_score = 100 - (duplicate_rows / len(self.df) * 100)
        
        return {
            'score': uniqueness_score,
            'duplicate_rows': int(duplicate_rows),
            'potential_keys': potential_keys,
            'column_stats': column_stats,
            'issues': [stat for stat in column_stats if stat['duplicates'] > len(self.df) * 0.1]
        }
    
    def check_timeliness(self) -> Dict[str, Any]:
        """
        时效性检查
        检查日期范围、数据新鲜度
        """
        issues = []
        date_ranges = []
        
        # 查找日期列
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    dates = pd.to_datetime(self.df[col], errors='coerce')
                    valid_dates = dates.dropna()
                    
                    if len(valid_dates) > 0:
                        min_date = valid_dates.min()
                        max_date = valid_dates.max()
                        
                        date_ranges.append({
                            'column': col,
                            'min_date': str(min_date),
                            'max_date': str(max_date),
                            'span_days': (max_date - min_date).days
                        })
                        
                        # 检查是否有未来日期
                        future_dates = (dates > pd.Timestamp.now()).sum()
                        if future_dates > 0:
                            issues.append({
                                'column': col,
                                'issue': f'包含 {future_dates} 个未来日期',
                                'severity': 'high'
                            })
                        
                        # 检查数据新鲜度（最新数据是否在最近30天内）
                        days_old = (pd.Timestamp.now() - max_date).days
                        if days_old > 30:
                            issues.append({
                                'column': col,
                                'issue': f'数据已过时 {days_old} 天',
                                'severity': 'medium'
                            })
                
                except:
                    pass
        
        # 计算时效性分数
        timeliness_score = max(0, 100 - len(issues) * 20)
        
        return {
            'score': timeliness_score,
            'date_ranges': date_ranges,
            'issues': issues,
            'issue_count': len(issues)
        }
    
    def print_report(self):
        """打印质量报告"""
        if not self.quality_report:
            print("请先运行 check_all()")
            return
        
        report = self.quality_report
        
        print("\n" + "="*60)
        print("数据质量报告")
        print("="*60)
        
        # 总体评分
        score = report['overall_score']
        grade = self._get_grade(score)
        print(f"\n【总体质量评分】")
        print(f"  分数: {score:.1f}/100")
        print(f"  等级: {grade}")
        
        # 完整性
        print(f"\n【完整性】 {report['completeness']['score']:.1f}/100")
        comp = report['completeness']
        print(f"  缺失单元格: {comp['missing_cells']}/{comp['total_cells']}")
        print(f"  空字符串: {comp['empty_strings']}")
        if comp['issues']:
            print(f"  问题列: {len(comp['issues'])} 个")
            for issue in comp['issues'][:3]:
                print(f"    - {issue['column']}: {issue['completeness_rate']:.1f}% 完整")
        
        # 一致性
        print(f"\n【一致性】 {report['consistency']['score']:.1f}/100")
        cons = report['consistency']
        if cons['issues']:
            print(f"  发现 {len(cons['issues'])} 个问题:")
            for issue in cons['issues'][:3]:
                print(f"    - {issue['column']}: {issue['issue']}")
        else:
            print("  无问题")
        
        # 准确性
        print(f"\n【准确性】 {report['accuracy']['score']:.1f}/100")
        acc = report['accuracy']
        if acc['issues']:
            print(f"  发现 {len(acc['issues'])} 个问题:")
            for issue in acc['issues'][:3]:
                print(f"    - {issue['column']}: {issue['issue']}")
        else:
            print("  无问题")
        
        # 唯一性
        print(f"\n【唯一性】 {report['uniqueness']['score']:.1f}/100")
        uniq = report['uniqueness']
        print(f"  重复行: {uniq['duplicate_rows']}")
        if uniq['potential_keys']:
            print(f"  可能的主键: {', '.join(uniq['potential_keys'])}")
        
        # 时效性
        print(f"\n【时效性】 {report['timeliness']['score']:.1f}/100")
        time = report['timeliness']
        if time['date_ranges']:
            print(f"  日期范围:")
            for dr in time['date_ranges']:
                print(f"    - {dr['column']}: {dr['min_date']} 至 {dr['max_date']}")
        if time['issues']:
            print(f"  发现 {len(time['issues'])} 个问题")
        
        print("\n" + "="*60)
    
    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "优秀 (A)"
        elif score >= 80:
            return "良好 (B)"
        elif score >= 70:
            return "中等 (C)"
        elif score >= 60:
            return "及格 (D)"
        else:
            return "不及格 (F)"
    
    def export_report(self, output_path: str):
        """导出质量报告"""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.quality_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ 报告已导出: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 创建测试数据（包含各种质量问题）
    df = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5, 5],  # 重复
        'Name': ['Alice', 'Bob', '', 'David', np.nan, 'Frank'],  # 缺失和空值
        'Age': [25, 30, -5, 35, 200, 28],  # 负数和异常值
        'Salary': [50000, 60000, 55000, np.nan, 70000, 65000],  # 缺失值
        'StartDate': ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01'],
        'EndDate': ['2021-01-01', '2019-12-01', '2021-03-01', '2021-04-01', '2021-05-01', '2021-06-01']  # 日期顺序错误
    })
    
    print("测试数据:")
    print(df)
    
    # 创建质量检查器
    checker = DataQualityChecker(df)
    
    # 执行所有检查
    report = checker.check_all()
    
    # 打印报告
    checker.print_report()
    
    # 导出报告
    checker.export_report('quality_report.json')
