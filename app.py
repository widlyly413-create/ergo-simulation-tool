import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon
import os
import matplotlib.font_manager as fm

# ==========================================
# 0. 页面配置与微醺集品牌 CSS
# ==========================================
st.set_page_config(page_title="大漆工艺人机适配系统 - 微醺集", layout="wide", initial_sidebar_state="collapsed")

# 注入中式极简与大漆色彩体系 CSS
st.markdown("""
    <style>
    /* 全局背景与字体 */
    .stApp { background-color: #FDFBF7; color: #121212; }
    h1, h2, h3, h4, h5, h6 { color: #121212; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* 核心品牌色：朱砂红 */
    .brand-text { color: #8C1C13; font-weight: bold; }
    .stButton>button { background-color: #8C1C13; color: #FDFBF7; border: none; border-radius: 4px; padding: 10px 24px; transition: all 0.3s; }
    .stButton>button:hover { background-color: #A62419; box-shadow: 0 4px 8px rgba(140,28,19,0.2); }
    
    /* 模块卡片样式 */
    .card { background-color: #FFFFFF; border-radius: 8px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 24px; border-top: 4px solid #8C1C13; }
    
    /* 关键尺寸数值展示 */
    .metric-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: space-between; margin-top: 15px; }
    .metric-box { background: #F5F5F5; padding: 15px; border-radius: 6px; flex: 1; min-width: 120px; text-align: center; border-left: 3px solid #8C1C13; }
    .metric-title { font-size: 12px; color: #666; margin-bottom: 5px; }
    .metric-value { font-size: 22px; font-weight: 700; color: #8C1C13; margin: 0; }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        .metric-container { flex-direction: column; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 解决 Matplotlib 中文显示问题 (云端防乱码)
# ==========================================
@st.cache_resource
def setup_fonts():
    font_path = "SimHei.ttf" # 需在项目根目录放置该字体文件
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.sans-serif'] = ['SimHei']
    else:
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
setup_fonts()

def round_to_half_cm(value_mm):
    """将毫米精确到 5mm (0.5cm) 的倍数，符合家具制造精度"""
    return round(value_mm / 5.0) * 5

# ==========================================
# 1. 顶部 Hero Section (背景与引言)
# ==========================================
st.markdown("""
<div style="text-align: center; padding: 40px 20px; background-color: #121212; color: #FDFBF7; border-radius: 8px; margin-bottom: 30px;">
    <h1 style="color: #D4AF37; margin-bottom: 10px; font-size: 2.2rem;">传统大漆工艺·人机适配数字化系统</h1>
    <p style="font-size: 1.1rem; max-width: 800px; margin: 0 auto; color: #CCCCCC; line-height: 1.6;">
        传统大漆工序（如打磨、髹漆、描金）极易导致手工艺人遭遇颈椎与腰椎的肌肉骨骼损伤（MSDs）。<br>
        本系统基于 <span style="color: #8C1C13; font-weight: bold;">RULA/REBA 评估模型</span> 与 <span style="color: #8C1C13; font-weight: bold;">Squires 动态作业面算法</span>，
        为工匠量身定制 0.5cm 精度的桌椅高度与桌面工具落点布局，实现从经验到科学的健康转化。
    </p>
    <p style="margin-top: 20px; font-size: 0.9rem; color: #666;">微醺集设计工作室 (Weixunji Design) 研发支持</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. 统一的人体与场景数据录入
# ==========================================
st.markdown("### 📐 1. 作业者与场景参数录入")
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        work_type = st.selectbox("核心工序类别", ["打磨工序 (侧重施力，修正+120mm)", "装饰工序 (侧重精细视觉，修正+200mm)"])
        offset = 200 if "装饰" in work_type else 120
    with col2:
        h_workpiece = st.number_input("工件作业点高度 (mm)", 0, 1000, 50, step=5, help="工件中心距桌面的高度")
    with col3:
        mode = st.selectbox("设施可调性限制", ["全自由调节 (推荐)", "仅座椅高度固定", "仅桌面高度固定"])

    st.markdown("<hr style='margin:15px 0; border-top: 1px dashed #eee;'>", unsafe_allow_html=True)
    st.markdown("<span style='font-size: 14px; color: #666;'>身体关键尺寸 (默认数值基于中国成年男性 P50 标准)</span>", unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: h_popliteal = st.number_input("坐姿腘高", 300, 600, 400, step=5)
    with c2: h_elbow = st.number_input("坐姿肘高", 100, 500, 250, step=5)
    with c3: L_a = st.number_input("上臂长", 200.0, 500.0, 318.0, step=5.0)
    with c4: R_a = st.number_input("前臂长", 150.0, 400.0, 235.0, step=5.0)
    with c5: S_a = st.number_input("肩宽", 300.0, 600.0, 419.0, step=5.0)
    
    # 隐藏变量
    F_a_full = 184.0 
    F_a = F_a_full / 2.0
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. 核心计算：高度推算与动态姿态图
# ==========================================
# 高度逻辑计算
h_chair_final, h_desk_final = 0, 0

if "全自由" in mode:
    h_chair_final = round_to_half_cm(h_popliteal + 20) # 鞋服修正
    h_desk_final = round_to_half_cm(h_chair_final + h_elbow + h_workpiece + offset)
elif "座椅固定" in mode:
    h_chair_fixed = st.number_input("当前座椅高度 (mm)", 300, 600, 450, step=5)
    h_chair_final = round_to_half_cm(h_chair_fixed)
    h_desk_final = round_to_half_cm(h_chair_final + h_elbow + h_workpiece + offset)
else:
    h_desk_fixed = st.number_input("当前桌面高度 (mm)", 500, 1200, 750, step=5)
    h_desk_final = round_to_half_cm(h_desk_fixed)
    h_chair_final = round_to_half_cm(h_desk_final - h_elbow - h_workpiece - offset)

# 推算其他关键尺寸用于展示
h_eye = round_to_half_cm(h_chair_final + 780) # 假设坐姿眼高均值
h_knee_clearance = round_to_half_cm(h_popliteal + 60) # 膝部空间要求

st.markdown("### 🪑 2. Z轴：定制高度与工作姿态")
col_text, col_img = st.columns([1.2, 1])

with col_text:
    st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#8C1C13;'>关键尺寸推荐参数表 (精确至 5mm)</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">❶ 最佳座椅高度</div><p class="metric-value">{int(h_chair_final)} <span style='font-size:14px'>mm</span></p></div>
        <div class="metric-box"><div class="metric-title">❷ 最佳作业面高度</div><p class="metric-value">{int(h_desk_final)} <span style='font-size:14px'>mm</span></p></div>
    </div>
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">❸ 视线参考高度</div><p class="metric-value">{int(h_eye)} <span style='font-size:14px'>mm</span></p></div>
        <div class="metric-box"><div class="metric-title">❹ 最小桌下净空</div><p class="metric-value">{int(h_knee_clearance)} <span style='font-size:14px'>mm</span></p></div>
        <div class="metric-box"><div class="metric-title">❺ 工件中心修正</div><p class="metric-value">+{int(h_workpiece+offset)} <span style='font-size:14px'>mm</span></p></div>
    </div>
    <p style='margin-top: 20px; font-size: 13px; color: #888;'>* 计算逻辑：作业面高度 = 座椅高度 + 坐姿肘高 + 工件高度 + 工序修正值</p>
    </div>
    """, unsafe_allow_html=True)

with col_img:
    # 动态生成 SVG 侧视姿态图
    # 映射比例: 1mm 约等于 0.3 px 绘图单位
    scale = 0.3
    svg_chair_y = 350 - (h_chair_final * scale)
    svg_desk_y = 350 - (h_desk_final * scale)
    
    svg_code = f"""
    <div class="card" style="height: 100%; display: flex; align-items: center; justify-content: center;">
    <svg width="100%" height="320" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg">
        <line x1="10" y1="350" x2="290" y2="350" stroke="#121212" stroke-width="3"/>
        
        <rect x="180" y="{svg_desk_y}" width="80" height="15" fill="#8C1C13" rx="2"/>
        <line x1="200" y1="{svg_desk_y+15}" x2="200" y2="350" stroke="#555" stroke-width="6"/>
        <line x1="240" y1="{svg_desk_y+15}" x2="240" y2="350" stroke="#555" stroke-width="6"/>
        
        <rect x="50" y="{svg_chair_y}" width="60" height="10" fill="#333" rx="2"/>
        <line x1="60" y1="{svg_chair_y+10}" x2="60" y2="350" stroke="#555" stroke-width="5"/>
        <line x1="100" y1="{svg_chair_y+10}" x2="100" y2="350" stroke="#555" stroke-width="5"/>
        <line x1="55" y1="{svg_chair_y}" x2="45" y2="{svg_chair_y - 80}" stroke="#333" stroke-width="8" stroke-linecap="round"/>
        
        <circle cx="85" cy="{svg_chair_y - 180}" r="18" fill="#D4AF37"/>
        <line x1="80" y1="{svg_chair_y - 160}" x2="70" y2="{svg_chair_y - 10}" stroke="#8C1C13" stroke-width="16" stroke-linecap="round"/>
        <line x1="70" y1="{svg_chair_y - 10}" x2="150" y2="{svg_chair_y - 10}" stroke="#121212" stroke-width="14" stroke-linecap="round"/>
        <line x1="150" y1="{svg_chair_y - 10}" x2="140" y2="340" stroke="#121212" stroke-width="12" stroke-linecap="round"/>
        <line x1="80" y1="{svg_chair_y - 140}" x2="110" y2="{svg_chair_y - 50}" stroke="#D4AF37" stroke-width="10" stroke-linecap="round"/>
        <line x1="110" y1="{svg_chair_y - 50}" x2="190" y2="{svg_desk_y - 20}" stroke="#D4AF37" stroke-width="8" stroke-linecap="round"/>
        
        <line x1="20" y1="350" x2="20" y2="{svg_chair_y}" stroke="#666" stroke-width="1" stroke-dasharray="4"/>
        <text x="25" y="{svg_chair_y + (350-svg_chair_y)/2}" fill="#666" font-size="10">❶ {int(h_chair_final)}</text>
        
        <line x1="280" y1="350" x2="280" y2="{svg_desk_y}" stroke="#8C1C13" stroke-width="1" stroke-dasharray="4"/>
        <text x="245" y="{svg_desk_y + (350-svg_desk_y)/2}" fill="#8C1C13" font-size="10">❷ {int(h_desk_final)}</text>
    </svg>
    </div>
    """
    st.markdown(svg_code, unsafe_allow_html=True)

# ==========================================
# 4. 平面计算：XY轴包络面与落点图生成
# ==========================================
st.markdown("### 🎯 3. XY轴：动态包络面与功能落点布局")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.write("基于 Squires 算法与几何中点法则，系统自动规划出大漆核心工具的最佳摆放区域，减少无效跨越与肩部代偿。")

if st.button("生成/刷新 布局动线解析图", type="primary", use_container_width=True):
    with st.spinner("正在解算多边形边界与落点坐标..."):
        # 绘图环境设置
        fig, ax = plt.subplots(figsize=(10, 7))
        title = f"双臂作业包络面及功能落点区综合布局\n(La={L_a:.1f}, Ra={R_a:.1f}, Fa={F_a:.1f}, Sa={S_a:.1f} mm)"
        
        d_offset = 50
        shoulder_y = -d_offset
        B_a = R_a + F_a
        R_max = L_a + B_a
        theta_0 = 65 * np.pi / 180

        # 调整画幅防止遮挡
        ax.set_xlim(-900, 900)
        ax.set_ylim(-200, 1000)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.3, zorder=1)
        ax.set_xlabel("X坐标 (mm) - 原点为工作台边缘中心", fontsize=10)
        ax.set_ylabel("Y坐标 (mm) - 桌面伸展深度", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)

        # 边界计算
        ex, ey = 50, 90
        center_x_R_comp, center_y_R_comp = S_a / 2 - ex, shoulder_y + ey
        center_x_L_comp, center_y_L_comp = -S_a / 2 + ex, shoulder_y + ey
        center_x_R_orig, center_y_R_orig = S_a / 2, shoulder_y
        center_x_L_orig, center_y_L_orig = -S_a / 2, shoulder_y

        theta_semi = np.linspace(0, np.pi, 200)

        # 构造半圆多边形函数
        def create_poly(cx, cy, r):
            arc_x = cx + r * np.cos(theta_semi)
            arc_y = cy + r * np.sin(theta_semi)
            return Polygon(np.column_stack((np.concatenate([arc_x, [arc_x[-1], arc_x[0]]]), 
                                            np.concatenate([arc_y, [shoulder_y, shoulder_y]]))))

        poly_comp_R = create_poly(center_x_R_comp, center_y_R_comp, R_max)
        poly_comp_L = create_poly(center_x_L_comp, center_y_L_comp, R_max)
        poly_orig_R = create_poly(center_x_R_orig, center_y_R_orig, R_max)
        poly_orig_L = create_poly(center_x_L_orig, center_y_L_orig, R_max)

        union_max = poly_comp_R.union(poly_comp_L).union(poly_orig_R).union(poly_orig_L)

        def plot_polygon(geom, color, alpha, zorder):
            if geom.geom_type == 'Polygon':
                x, y = geom.exterior.xy
                ax.fill(x, y, color=color, alpha=alpha, zorder=zorder)
            else:
                for g in geom.geoms:
                    x, y = g.exterior.xy
                    ax.fill(x, y, color=color, alpha=alpha, zorder=zorder)

        # 绘制最大工作区
        plot_polygon(union_max, 'lightgreen', 0.25, 2)
        if union_max.geom_type == 'Polygon':
            ax.plot(*union_max.exterior.xy, color='green', linestyle='-.', alpha=0.5, zorder=3)
        
        # Squires 最佳区
        theta_full = np.linspace(0, 105 * np.pi / 180, 200)
        x_curve_R = S_a / 2 + L_a * np.cos(theta_full) + B_a * np.cos(theta_0 + 73 * theta_full / 90)
        y_curve_R = shoulder_y + L_a * np.sin(theta_full) + B_a * np.sin(theta_0 + 73 * theta_full / 90)
        x_curve_L = -x_curve_R
        y_curve_L = y_curve_R

        poly_sq_R = Polygon(np.column_stack((np.concatenate([[0, S_a / 2, S_a / 2 + L_a], x_curve_R, [0]]), 
                                             np.concatenate([[shoulder_y, shoulder_y, shoulder_y], y_curve_R, [shoulder_y]]))))
        poly_sq_L = Polygon(np.column_stack((np.concatenate([[0, -S_a / 2, -S_a / 2 - L_a], x_curve_L, [0]]),
                                             np.concatenate([[shoulder_y, shoulder_y, shoulder_y], y_curve_L, [shoulder_y]]))))

        union_sq = poly_sq_R.union(poly_sq_L)
        plot_polygon(union_sq, 'lightblue', 0.5, 4)
        ax.plot(x_curve_R, y_curve_R, color='#1f77b4', linestyle='--', alpha=0.8, zorder=5)
        ax.plot(x_curve_L, y_curve_L, color='#1f77b4', linestyle='--', alpha=0.8, zorder=5)

        # --- 功能落点区计算 ---
        # 1. 操作区
        X_op = 0
        Y_op = shoulder_y + R_a + 50
        # 2. 存放区
        theta_abd = np.radians(15)
        gamma = np.radians(25)
        d_ua = L_a * 0.85
        b = S_a / 2
        X_e = b + d_ua * np.sin(theta_abd)
        Y_e = shoulder_y + d_ua * np.cos(theta_abd)
        X_st = X_e + R_a * np.sin(gamma)
        Y_st = Y_e + R_a * np.cos(gamma)
        # 3. 转换区
        X_tr = (X_op + X_st) / 2
        Y_tr = (Y_op + Y_st) / 2
        # 4. 非取用区
        angle_nu = np.radians(-40)
        R_nu_dist = 420
        X_nu = R_nu_dist * np.sin(angle_nu)
        Y_nu = shoulder_y + R_nu_dist * np.cos(angle_nu)

        R_zone = 90 # 缩小圆圈半径避免太挤
        zones = [
            (X_op, Y_op, '#8C1C13', '操作区\n(当前工件)'),
            (X_st, Y_st, '#2CA02C', '存放区\n(常用漆刷/刻刀)'),
            (X_tr, Y_tr, '#FF7F0E', '转换区\n(调色板/砂纸)'),
            (X_nu, Y_nu, '#9467BD', '非取用区\n(水桶/废料)')
        ]
        
        for X, Y, color, label in zones:
            circle = patches.Circle((X, Y), R_zone, color=color, alpha=0.2, edgecolor=color, lw=2, zorder=9)
            ax.add_patch(circle)
            ax.plot(X, Y, marker='P', color=color, markersize=8, zorder=10)
            ax.text(X, Y + R_zone + 15, label, color=color, fontsize=9, fontweight='bold', ha='center', zorder=11)

        # 静态收纳区 (外围)
        minx, miny, maxx, maxy = union_max.bounds
        outer_rect = Polygon([(minx-50, 0), (maxx+50, 0), (maxx+50, maxy+100), (minx-50, maxy+100)])
        inner_poly = union_max.buffer(-50)
        static_storage_poly = outer_rect.difference(inner_poly)
        plot_polygon(static_storage_poly, 'brown', 0.1, 1)

        # 参考线
        ax.axhline(0, color='#8C1C13', linestyle='-', lw=2, alpha=0.8, zorder=6, label='工作台边缘 (Y=0)')
        ax.axhline(shoulder_y, color='#555', linestyle='--', lw=1.5, alpha=0.8, zorder=6, label='胸廓基准线')
        ax.plot([0], [shoulder_y], 'kX', markersize=8, zorder=12)

        # 图例配置
        ax.legend(loc='upper right', fontsize=9, facecolor='#FDFBF7', framealpha=0.9)
        plt.tight_layout(rect=[0, 0, 1, 1])
        
        st.pyplot(fig)
        
        # 提取区域数据输出表格
        st.markdown("<h5 style='color:#8C1C13; margin-top: 20px;'>落点中心坐标推荐 (相对于操作者正中桌边)</h5>", unsafe_allow_html=True)
        point_data = pd.DataFrame({
            "功能分区": ["操作区 (主工件)", "存放区 (高频工具)", "转换区 (中频物料)", "非取用区 (低频物品)"],
            "X坐标(左右偏移/mm)": [round_to_half_cm(X_op), round_to_half_cm(X_st), round_to_half_cm(X_tr), round_to_half_cm(X_nu)],
            "Y坐标(距桌边深度/mm)": [round_to_half_cm(Y_op), round_to_half_cm(Y_st), round_to_half_cm(Y_tr), round_to_half_cm(Y_nu)]
        })
        st.dataframe(point_data, hide_index=True, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
