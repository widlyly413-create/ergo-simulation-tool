import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon
import os
import matplotlib.font_manager as fm

# ==========================================
# 0. 页面配置与 CSS
# ==========================================
st.set_page_config(page_title="大漆工艺人机适配系统 - 微醺集", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; color: #121212; }
    .card { background-color: #FFFFFF; border-radius: 8px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.05); margin-bottom: 24px; border-top: 4px solid #8C1C13; }
    .metric-container { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
    .metric-box { background: #F5F5F5; padding: 15px; border-radius: 6px; flex: 1; text-align: center; border-left: 3px solid #8C1C13; }
    .metric-title { font-size: 12px; color: #666; margin-bottom: 5px; }
    .metric-value { font-size: 20px; font-weight: 700; color: #8C1C13; margin: 0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 终极防乱码：动态读取字体内部名称
# ==========================================
@st.cache_resource
def setup_fonts():
    font_path = "SimHei.ttf" # 必须确保此文件在 GitHub 仓库根目录
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        # 获取字体的内部真实注册名并设置
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.sans-serif'] = [font_prop.get_name(), 'sans-serif']
    else:
        # 如果云端找不到文件，使用默认回退字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False
setup_fonts()

def round_to_half_cm(value_mm):
    return round(value_mm / 5.0) * 5

# ==========================================
# 2. 页面头部
# ==========================================
st.markdown("""
<div style="text-align: center; padding: 30px 20px; background-color: #121212; color: #FDFBF7; border-radius: 8px; margin-bottom: 20px;">
    <h1 style="color: #D4AF37; margin-bottom: 10px;">传统大漆工艺·人机适配数字化系统</h1>
    <p style="color: #CCC; font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
        结合 RULA/REBA 评估与 Squires 动态作业面算法，输出精确至 0.5cm 的工位定制尺寸与功能落点布局。
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. 参数录入
# ==========================================
st.markdown("### 📐 1. 作业者与场景参数")
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    work_type = st.selectbox("核心工序", ["打磨工序 (侧重施力，修正+120mm)", "装饰工序 (侧重视觉，修正+200mm)"])
    offset = 200 if "装饰" in work_type else 120
with col2:
    h_workpiece = st.number_input("工件作业点高度 (mm)", 0, 1000, 50, step=5)
with col3:
    mode = st.selectbox("设施可调性", ["全自由调节", "仅座椅高度固定", "仅桌面高度固定"])

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: h_popliteal = st.number_input("坐姿腘高", 300, 600, 400, step=5)
with c2: h_elbow = st.number_input("坐姿肘高", 100, 500, 250, step=5)
with c3: L_a = st.number_input("上臂长", 200.0, 500.0, 318.0, step=5.0)
with c4: R_a = st.number_input("前臂长", 150.0, 400.0, 235.0, step=5.0)
with c5: S_a = st.number_input("肩宽", 300.0, 600.0, 419.0, step=5.0)
F_a = 184.0 / 2.0
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 高度推算逻辑
# ==========================================
if "全自由" in mode:
    h_chair_final = round_to_half_cm(h_popliteal + 20)
    h_desk_final = round_to_half_cm(h_chair_final + h_elbow + h_workpiece + offset)
elif "座椅固定" in mode:
    h_chair_fixed = st.number_input("当前座椅高度 (mm)", 300, 600, 450, step=5)
    h_chair_final = round_to_half_cm(h_chair_fixed)
    h_desk_final = round_to_half_cm(h_chair_final + h_elbow + h_workpiece + offset)
else:
    h_desk_fixed = st.number_input("当前桌面高度 (mm)", 500, 1200, 750, step=5)
    h_desk_final = round_to_half_cm(h_desk_fixed)
    h_chair_final = round_to_half_cm(h_desk_final - h_elbow - h_workpiece - offset)

h_eye = round_to_half_cm(h_chair_final + 780) 
h_knee_clearance = round_to_half_cm(h_popliteal + 60)

# ==========================================
# 5. Z轴与实时 SVG 渲染
# ==========================================
st.markdown("### 🪑 2. 空间适配：关键尺寸与姿态参考")
col_text, col_img = st.columns([1, 1.2])

with col_text:
    st.markdown('<div class="card" style="height: 380px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#8C1C13; margin-top:0;'>推荐尺寸 (mm)</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">❶ 最佳座椅高度</div><p class="metric-value">{int(h_chair_final)}</p></div>
        <div class="metric-box"><div class="metric-title">❷ 最佳作业面高度</div><p class="metric-value">{int(h_desk_final)}</p></div>
    </div>
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">❸ 视线参考高度</div><p class="metric-value">{int(h_eye)}</p></div>
        <div class="metric-box"><div class="metric-title">❹ 最小桌下净空</div><p class="metric-value">{int(h_knee_clearance)}</p></div>
    </div>
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">❺ 工件中心偏移量</div><p class="metric-value">+{int(h_workpiece+offset)}</p></div>
    </div>
    </div>
    """, unsafe_allow_html=True)

with col_img:
    # 动态映射比例
    scale = 0.25
    gy = 350 # ground y
    sy = gy - (h_chair_final * scale)
    dy = gy - (h_desk_final * scale)
    ey = gy - (h_eye * scale)
    ky = gy - (h_knee_clearance * scale)
    wy = dy - (h_workpiece * scale)

    # 使用专门的组件渲染 HTML，彻底避免 Markdown 格式错乱
    svg_html = f"""
    <div style="background: white; border-radius: 8px; border-top: 4px solid #8C1C13; box-shadow: 0 2px 12px rgba(0,0,0,0.05); width: 100%; height: 380px; display: flex; align-items: center; justify-content: center;">
        <svg width="100%" height="360" viewBox="0 0 450 360" xmlns="http://www.w3.org/2000/svg">
            <line x1="40" y1="{gy}" x2="410" y2="{gy}" stroke="#121212" stroke-width="4"/>
            
            <line x1="50" y1="{gy}" x2="50" y2="{sy}" stroke="#666" stroke-width="1" stroke-dasharray="4"/>
            <text x="55" y="{gy - 20}" fill="#666" font-size="12" font-family="sans-serif">❶ 椅高 {int(h_chair_final)}</text>
            
            <line x1="400" y1="{gy}" x2="400" y2="{dy}" stroke="#8C1C13" stroke-width="1.5" stroke-dasharray="4"/>
            <text x="315" y="{dy + 20}" fill="#8C1C13" font-size="12" font-family="sans-serif" font-weight="bold">❷ 桌高 {int(h_desk_final)}</text>
            
            <line x1="20" y1="{gy}" x2="20" y2="{ey}" stroke="#D4AF37" stroke-width="1" stroke-dasharray="4"/>
            <line x1="20" y1="{ey}" x2="130" y2="{ey}" stroke="#D4AF37" stroke-width="1" stroke-dasharray="4"/>
            <text x="25" y="{ey - 5}" fill="#D4AF37" font-size="12" font-family="sans-serif">❸ 视高 {int(h_eye)}</text>
            
            <line x1="250" y1="{gy}" x2="250" y2="{ky}" stroke="#1f77b4" stroke-width="1" stroke-dasharray="4"/>
            <line x1="240" y1="{ky}" x2="260" y2="{ky}" stroke="#1f77b4" stroke-width="2"/>
            <text x="255" y="{ky + 15}" fill="#1f77b4" font-size="11" font-family="sans-serif">❹ 净空 {int(h_knee_clearance)}</text>

            <line x1="290" y1="{dy}" x2="290" y2="{wy}" stroke="#ff7f0e" stroke-width="1" stroke-dasharray="4"/>
            <circle cx="290" cy="{wy}" r="4" fill="#ff7f0e"/>
            <text x="300" y="{wy + 5}" fill="#ff7f0e" font-size="11" font-family="sans-serif">❺ 工件 {int(h_workpiece)}</text>

            <rect x="250" y="{dy}" width="140" height="15" fill="#8C1C13" rx="2"/>
            <line x1="270" y1="{dy+15}" x2="270" y2="{gy}" stroke="#555" stroke-width="6"/>
            <line x1="370" y1="{dy+15}" x2="370" y2="{gy}" stroke="#555" stroke-width="6"/>
            
            <rect x="90" y="{sy}" width="70" height="10" fill="#333" rx="2"/>
            <line x1="100" y1="{sy+10}" x2="100" y2="{gy}" stroke="#555" stroke-width="5"/>
            <line x1="140" y1="{sy+10}" x2="140" y2="{gy}" stroke="#555" stroke-width="5"/>
            <line x1="95" y1="{sy}" x2="85" y2="{sy - 80}" stroke="#333" stroke-width="8" stroke-linecap="round"/>
            
            <circle cx="130" cy="{ey}" r="18" fill="#D4AF37"/> <line x1="125" y1="{ey+18}" x2="110" y2="{sy}" stroke="#8C1C13" stroke-width="16" stroke-linecap="round"/> <line x1="110" y1="{sy-5}" x2="200" y2="{sy-5}" stroke="#121212" stroke-width="14" stroke-linecap="round"/> <line x1="200" y1="{sy-5}" x2="190" y2="{gy}" stroke="#121212" stroke-width="12" stroke-linecap="round"/> <line x1="125" y1="{ey+25}" x2="150" y2="{sy-30}" stroke="#D4AF37" stroke-width="10" stroke-linecap="round"/> <line x1="150" y1="{sy-30}" x2="280" y2="{wy}" stroke="#D4AF37" stroke-width="8" stroke-linecap="round"/> </svg>
    </div>
    """
    components.html(svg_html, height=400) # 这里高度稍微留一点余量

# ==========================================
# 6. 平面布局图生成
# ==========================================
st.markdown("### 🎯 3. XY轴：动态包络面与功能落点布局")
st.markdown('<div class="card">', unsafe_allow_html=True)
if st.button("生成/刷新 布局动线解析图", type="primary", use_container_width=True):
    with st.spinner("正在解算多边形边界与落点坐标..."):
        fig, ax = plt.subplots(figsize=(10, 7))
        title = f"双臂作业包络面及功能落点区\n(La={L_a:.1f}, Ra={R_a:.1f}, Fa={F_a:.1f}, Sa={S_a:.1f})"
        
        shoulder_y = -50
        B_a = R_a + F_a
        R_max = L_a + B_a
        theta_0 = 65 * np.pi / 180

        ax.set_xlim(-900, 900)
        ax.set_ylim(-200, 1000)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.3, zorder=1)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)

        ex, ey = 50, 90
        theta_semi = np.linspace(0, np.pi, 200)

        def create_poly(cx, cy, r):
            arc_x = cx + r * np.cos(theta_semi)
            arc_y = cy + r * np.sin(theta_semi)
            return Polygon(np.column_stack((np.concatenate([arc_x, [arc_x[-1], arc_x[0]]]), 
                                            np.concatenate([arc_y, [shoulder_y, shoulder_y]]))))

        p1 = create_poly(S_a / 2 - ex, shoulder_y + ey, R_max)
        p2 = create_poly(-S_a / 2 + ex, shoulder_y + ey, R_max)
        p3 = create_poly(S_a / 2, shoulder_y, R_max)
        p4 = create_poly(-S_a / 2, shoulder_y, R_max)
        union_max = p1.union(p2).union(p3).union(p4)

        if union_max.geom_type == 'Polygon':
            x, y = union_max.exterior.xy
            ax.fill(x, y, color='lightgreen', alpha=0.25, zorder=2)
            ax.plot(x, y, color='green', linestyle='-.', alpha=0.5, zorder=3)
        else:
            for g in union_max.geoms:
                x, y = g.exterior.xy
                ax.fill(x, y, color='lightgreen', alpha=0.25, zorder=2)

        theta_full = np.linspace(0, 105 * np.pi / 180, 200)
        x_cR = S_a / 2 + L_a * np.cos(theta_full) + B_a * np.cos(theta_0 + 73 * theta_full / 90)
        y_cR = shoulder_y + L_a * np.sin(theta_full) + B_a * np.sin(theta_0 + 73 * theta_full / 90)
        x_cL, y_cL = -x_cR, y_cR

        sq_R = Polygon(np.column_stack((np.concatenate([[0, S_a/2, S_a/2+L_a], x_cR, [0]]), 
                                        np.concatenate([[shoulder_y]*3, y_cR, [shoulder_y]]))))
        sq_L = Polygon(np.column_stack((np.concatenate([[0, -S_a/2, -S_a/2-L_a], x_cL, [0]]),
                                        np.concatenate([[shoulder_y]*3, y_cL, [shoulder_y]]))))
        union_sq = sq_R.union(sq_L)

        if union_sq.geom_type == 'Polygon':
            x, y = union_sq.exterior.xy
            ax.fill(x, y, color='lightblue', alpha=0.5, zorder=4)
        else:
            for g in union_sq.geoms:
                ax.fill(*g.exterior.xy, color='lightblue', alpha=0.5, zorder=4)

        # 核心落点区
        X_op, Y_op = 0, shoulder_y + R_a + 50
        theta_abd = np.radians(15)
        gamma = np.radians(25)
        d_ua = L_a * 0.85
        X_e = S_a / 2 + d_ua * np.sin(theta_abd)
        Y_e = shoulder_y + d_ua * np.cos(theta_abd)
        X_st, Y_st = X_e + R_a * np.sin(gamma), Y_e + R_a * np.cos(gamma)
        X_tr, Y_tr = (X_op + X_st) / 2, (Y_op + Y_st) / 2
        
        angle_nu = np.radians(-40)
        X_nu, Y_nu = 420 * np.sin(angle_nu), shoulder_y + 420 * np.cos(angle_nu)

        zones = [
            (X_op, Y_op, '#8C1C13', '操作区'),
            (X_st, Y_st, '#2CA02C', '存放区'),
            (X_tr, Y_tr, '#FF7F0E', '转换区'),
            (X_nu, Y_nu, '#9467BD', '非取用区')
        ]
        for X, Y, color, label in zones:
            ax.add_patch(patches.Circle((X, Y), 90, color=color, alpha=0.2, zorder=9))
            ax.plot(X, Y, marker='P', color=color, markersize=8, zorder=10)
            ax.text(X, Y + 105, label, color=color, fontsize=10, fontweight='bold', ha='center', zorder=11)

        ax.axhline(0, color='#8C1C13', linestyle='-', lw=2, zorder=6, label='工作台边缘')
        ax.plot([0], [shoulder_y], 'kX', markersize=8, zorder=12, label='胸廓原点')
        ax.legend(loc='upper right')
        
        st.pyplot(fig)
st.markdown('</div>', unsafe_allow_html=True)
