"""
数据可视化工具
功能：
1. 自动生成常见图表
2. 分布图
3. 相关性热图
4. 时间序列图
5. 分类统计图
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List

class DataVisualizer:
    """数据可视化器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化
        
        Args:
            df: 数据框
        """
        self.df = df
        self.figures = []
        
        # 设置样式
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def plot_distribution(
        self,
        columns: Optional[List[str]] = None,
        bins: int = 30
    ):
        """
        绘制分布图
        
        Args:
            columns: 指定列（None = 所有数值列）
            bins: 直方图箱数
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        n_cols = min(3, len(columns))
        n_rows = (len(columns) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(columns):
            if i < len(axes):
                self.df[col].hist(bins=bins, ax=axes[i], edgecolor='black')
                axes[i].set_title(f'{col} 分布')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('频数')
        
        # 隐藏多余的子图
        for i in range(len(columns), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        self.figures.append(('distribution', fig))
        print(f"✓ 生成分布图: {len(columns)} 列")
    
    def plot_correlation(self):
        """绘制相关性热图"""
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            print("✗ 数值列不足，无法绘制相关性图")
            return
        
        corr = self.df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            ax=ax
        )
        ax.set_title('相关性热图')
        
        plt.tight_layout()
        self.figures.append(('correlation', fig))
        print("✓ 生成相关性热图")
    
    def plot_boxplot(
        self,
        columns: Optional[List[str]] = None
    ):
        """
        绘制箱线图
        
        Args:
            columns: 指定列（None = 所有数值列）
        """
        if columns is None:
            columns = self.df.select_dtypes(include=['number']).columns.tolist()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        self.df[columns].boxplot(ax=ax)
        ax.set_title('箱线图（异常值检测）')
        ax.set_ylabel('值')
        ax.set_xticklabels(columns, rotation=45, ha='right')
        
        plt.tight_layout()
        self.figures.append(('boxplot', fig))
        print(f"✓ 生成箱线图: {len(columns)} 列")
    
    def plot_scatter_matrix(
        self,
        columns: Optional[List[str]] = None
    ):
        """
        绘制散点矩阵
        
        Args:
            columns: 指定列（None = 所有数值列，最多5列）
        """
        if columns is None:
            numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
            columns = numeric_cols[:5]  # 最多5列
        
        if len(columns) < 2:
            print("✗ 列数不足，无法绘制散点矩阵")
            return
        
        fig = pd.plotting.scatter_matrix(
            self.df[columns],
            figsize=(15, 15),
            diagonal='hist',
            alpha=0.5
        )
        
        plt.suptitle('散点矩阵', y=1.0)
        plt.tight_layout()
        self.figures.append(('scatter_matrix', fig[0][0].get_figure()))
        print(f"✓ 生成散点矩阵: {len(columns)} 列")
    
    def plot_categorical(
        self,
        column: str,
        top_n: int = 10
    ):
        """
        绘制分类统计图
        
        Args:
            column: 列名
            top_n: 显示前N个类别
        """
        if column not in self.df.columns:
            print(f"✗ 列不存在: {column}")
            return
        
        value_counts = self.df[column].value_counts().head(top_n)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 柱状图
        value_counts.plot(kind='bar', ax=ax1)
        ax1.set_title(f'{column} - 柱状图')
        ax1.set_xlabel(column)
        ax1.set_ylabel('频数')
        ax1.tick_params(axis='x', rotation=45)
        
        # 饼图
        value_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
        ax2.set_title(f'{column} - 饼图')
        ax2.set_ylabel('')
        
        plt.tight_layout()
        self.figures.append(('categorical', fig))
        print(f"✓ 生成分类统计图: {column}")
    
    def plot_time_series(
        self,
        date_column: str,
        value_columns: List[str]
    ):
        """
        绘制时间序列图
        
        Args:
            date_column: 日期列
            value_columns: 数值列
        """
        if date_column not in self.df.columns:
            print(f"✗ 日期列不存在: {date_column}")
            return
        
        # 转换为日期类型
        df_temp = self.df.copy()
        df_temp[date_column] = pd.to_datetime(df_temp[date_column])
        df_temp = df_temp.sort_values(date_column)
        
        fig, ax = plt.subplots(figsize=(15, 6))
        
        for col in value_columns:
            if col in df_temp.columns:
                ax.plot(df_temp[date_column], df_temp[col], label=col, marker='o')
        
        ax.set_title('时间序列图')
        ax.set_xlabel('日期')
        ax.set_ylabel('值')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        self.figures.append(('time_series', fig))
        print(f"✓ 生成时间序列图: {len(value_columns)} 列")
    
    def plot_all(self):
        """生成所有常见图表"""
        print("\n生成所有图表...")
        
        # 分布图
        self.plot_distribution()
        
        # 相关性热图
        self.plot_correlation()
        
        # 箱线图
        self.plot_boxplot()
        
        # 散点矩阵
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) >= 2:
            self.plot_scatter_matrix()
        
        # 分类统计图
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols[:3]:  # 最多3个分类列
            self.plot_categorical(col)
        
        print(f"\n✓ 共生成 {len(self.figures)} 个图表")
    
    def save_all(self, output_dir: str = "plots"):
        """
        保存所有图表
        
        Args:
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, (name, fig) in enumerate(self.figures):
            filename = output_path / f"{i+1:02d}_{name}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ 保存: {filename}")
        
        print(f"\n✓ 所有图表已保存到: {output_dir}")
    
    def show_all(self):
        """显示所有图表"""
        plt.show()
    
    def close_all(self):
        """关闭所有图表"""
        plt.close('all')
        self.figures = []


# 使用示例
if __name__ == "__main__":
    import numpy as np
    
    # 创建测试数据
    df = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100) * 2 + 5,
        'C': np.random.randn(100) * 0.5 + 10,
        'Category': np.random.choice(['X', 'Y', 'Z'], 100),
        'Date': pd.date_range('2024-01-01', periods=100)
    })
    
    # 创建可视化器
    viz = DataVisualizer(df)
    
    # 生成所有图表
    viz.plot_all()
    
    # 保存图表
    viz.save_all("output_plots")
    
    # 显示图表
    # viz.show_all()
