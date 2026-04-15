import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# ==========================================
# 0. 页面与全局样式配置
# ==========================================
st.set_page_config(page_title="大漆工位优化系统", layout="wide")

# 解决云端部署时 Matplotlib 中文显示的问题（若云端无字体，可替换为英文标签或上传字体）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

st.markdown("""
    <style>
    .result-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border-top: 5px solid #8C1C13; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .metric-value { color: #8C1C13; font-size: 24px; font-weight: bold; margin: 0; }
    .metric-label { color: #666; font-size: 14px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 传统工艺人机适配数字化系统")
st.caption("微醺集设计工作室 (Weixunji Design) | 工业设计人机工程研究支持")

# 创建双标签页
tab1, tab2 = st.tabs(["📏 垂直高度适配 (侧视)", "📐 平面作业包络面 (俯视)"])

# ==========================================
# 标签页 1：垂直高度适配
# ==========================================
with tab1:
    st.header("工位高度推算")
    work_type = st.selectbox(
        "选择当前作业工序：",
        ["打磨工序 (侧重下压力，修正+120mm)", "装饰工序 (侧重精细视觉，修正+200mm)"],
        key="height_work_type"
    )
    offset = 200 if "装饰" in work_type else 120

    col1, col2 = st.columns(2)
    with col1:
        h_elbow = st.number_input("坐姿肘高 (mm)", 100, 500, 250)
    with col2:
        h_workpiece = st.number_input("工件作业点高度 (mm)", 0, 1000, 50)

    mode = st.radio("您的设施可调性：", ["全自由调节", "座椅高度固定", "桌面高度固定"])

    h_chair_final, h_desk_final = 0, 0
    if mode == "全自由调节":
        h_popliteal = st.number_input("坐姿腘高 (mm)", 300, 600, 400)
        h_chair_final = h_popliteal + 20
        h_desk_final = h_chair_final + h_elbow + h_workpiece + offset
    elif mode == "座椅高度固定":
        h_chair_fixed = st.number_input("当前座椅高度 (mm)", 300, 600, 450)
        h_chair_final = h_chair_fixed
        h_desk_final = h_chair_final + h_elbow + h_workpiece + offset
    else:
        h_desk_fixed = st.number_input("当前桌面高度 (mm)", 500, 1200, 750)
        h_desk_final = h_desk_fixed
        h_chair_final = h_desk_final - h_elbow - h_workpiece - offset

    st.markdown(f"""
        <div class="result-box">
            <h4 style='color: #8C1C13; margin-top: 0;'>高度建议结果</h4>
            <div style='display: flex; justify-content: space-around;'>
                <div style='text-align: center;'>
                    <p class='metric-label'>推荐座椅高度</p>
                    <p class='metric-value'>{int(h_chair_final)} mm</p>
                </div>
                <div style='text-align: center;'>
                    <p class='metric-label'>推荐作业面高度</p>
                    <p class='metric-value'>{int(h_desk_final)} mm</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 标签页 2：平面作业包络面
# ==========================================
with tab2:
    st.header("平面布局推荐尺寸推导")
    st.write("基于 Squires 最佳动态作业面与躯干代偿模型，推导桌面物品摆放的极限与最佳区域。")
    
    # 将原本的 Excel 读取改为前端交互输入，预设 P50 的大致数据
    st.subheader("1. 录入人体尺寸参数 (mm)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        L_a = st.number_input("上臂长 ($L_a$)", value=300.0, step=5.0)
    with c2:
        R_a = st.number_input("前臂长 ($R_a$)", value=240.0, step=5.0)
    with c3:
        F_a_full = st.number_input("手长", value=180.0, step=5.0, help="系统将自动取半作为功能性抓握偏移量")
        F_a = F_a_full / 2.0
    with c4:
        S_a = st.number_input("肩宽 ($S_a$)", value=380.0, step=5.0)

    if st.button("生成二维作业包络面解析图", type="primary"):
        # --- 绘图逻辑开始 ---
        fig, ax = plt.subplots(figsize=(8, 8))
        
        d_offset = 50
        shoulder_y = -d_offset
        B_a = R_a + F_a
        R_max = L_a + B_a
        theta_0 = 65 * np.pi / 180

        ax.set_xlim(-800, 800)
        ax.set_ylim(-100, 800)
        ax.set_aspect('equal')
        ax.grid(True, linestyle='--', alpha=0.6, zorder=1)
        ax.set_xlabel("X坐标 (mm) - 原点为桌边中心")
        ax.set_ylabel("Y坐标 (mm) - 向正前方伸展为正方向")

        ex, ey = 50, 90

        center_x_R_comp, center_y_R_comp = S_a / 2 - ex, shoulder_y + ey
        center_x_L_comp, center_y_L_comp = -S_a / 2 + ex, shoulder_y + ey
        center_x_R_orig, center_y_R_orig = S_a / 2, shoulder_y
        center_x_L_orig, center_y_L_orig = -S_a / 2, shoulder_y

        theta_semi = np.linspace(0, np.pi, 500)

        # 辅助多边形构建函数
        def make_poly(cx, cy, r):
            arc_x = cx + r * np.cos(theta_semi)
            arc_y = cy + r * np.sin(theta_semi)
            return Polygon(np.column_stack((
                np.concatenate([arc_x, [arc_x[-1], arc_x[0]]]),
                np.concatenate([arc_y, [shoulder_y, shoulder_y]])
            )))

        poly_comp_R = make_poly(center_x_R_comp, center_y_R_comp, R_max)
        poly_comp_L = make_poly(center_x_L_comp, center_y_L_comp, R_max)
        poly_orig_R = make_poly(center_x_R_orig, center_y_R_orig, R_max)
        poly_orig_L = make_poly(center_x_L_orig, center_y_L_orig, R_max)

        union_max = poly_comp_R.union(poly_comp_L).union(poly_orig_R).union(poly_orig_L)

        if union_max.geom_type == 'Polygon':
            x, y = union_max.exterior.xy
            ax.fill(x, y, color='lightgreen', alpha=0.4, zorder=2, label="最大作业范围")
            ax.plot(x, y, color='gray', linestyle='-.', alpha=0.7, zorder=3)
        else:
            for geom in union_max.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, color='lightgreen', alpha=0.4, zorder=2)
                ax.plot(x, y, color='gray', linestyle='-.', alpha=0.7, zorder=3)

        theta_full = np.linspace(0, 105 * np.pi / 180, 500)
        x_curve_R = S_a / 2 + L_a * np.cos(theta_full) + B_a * np.cos(theta_0 + 73 * theta_full / 90)
        y_curve_R = shoulder_y + L_a * np.sin(theta_full) + B_a * np.sin(theta_0 + 73 * theta_full / 90)
        x_curve_L, y_curve_L = -x_curve_R, y_curve_R

        poly_sq_R = Polygon(np.column_stack((
            np.concatenate([[0, S_a / 2, S_a / 2 + L_a], x_curve_R, [0]]),
            np.concatenate([[shoulder_y, shoulder_y, shoulder_y], y_curve_R, [shoulder_y]])
        )))
        poly_sq_L = Polygon(np.column_stack((
            np.concatenate([[0, -S_a / 2, -S_a / 2 - L_a], x_curve_L, [0]]),
            np.concatenate([[shoulder_y, shoulder_y, shoulder_y], y_curve_L, [shoulder_y]])
        )))

        union_sq = poly_sq_R.union(poly_sq_L)

        if union_sq.geom_type == 'Polygon':
            x, y = union_sq.exterior.xy
            ax.fill(x, y, color='lightblue', alpha=0.7, zorder=4, label="Squires 最佳动态范围")
        else:
            for geom in union_sq.geoms:
                x, y = geom.exterior.xy
                ax.fill(x, y, color='lightblue', alpha=0.7, zorder=4)

        ax.plot(x_curve_R, y_curve_R, color='#1f77b4', linestyle='--', alpha=0.8, zorder=5)
        ax.plot(x_curve_L, y_curve_L, color='#1f77b4', linestyle='--', alpha=0.8, zorder=5)

        # 尺寸计算
        minx_max, miny_max, maxx_max, maxy_max = union_max.bounds
        max_width = maxx_max - minx_max
        max_depth = maxy_max if maxy_max > 0 else 0

        minx_sq, miny_sq, maxx_sq, maxy_sq = union_sq.bounds
        sq_width = maxx_sq - minx_sq
        sq_depth = maxy_sq if maxy_sq > 0 else 0

        # 基准线
        ax.axhline(0, color='red', linestyle='-', lw=2, alpha=0.8, zorder=6, label='工作台边缘 (Y=0)')
        ax.axhline(shoulder_y, color='gray', linestyle='--', lw=1.5, alpha=0.8, zorder=6, label='胸廓基准线')
        ax.plot([0], [shoulder_y], 'rX', markersize=8, zorder=7)

        ax.legend(loc='upper right', fontsize=9)
        
        # --- 绘图逻辑结束，开始在网页上渲染 ---
        
        st.subheader("📊 桌面布局关键尺寸推荐")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.markdown(f"""
            <div class="result-box">
                <p class='metric-label'>最佳作业区 (核心工具摆放)</p>
                <p>距桌边深度：<span class='metric-value'>{sq_depth:.1f}</span> mm</p>
                <p>左右总宽度：<span class='metric-value'>{sq_width:.1f}</span> mm</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.markdown(f"""
            <div class="result-box">
                <p class='metric-label'>最大触及区 (辅料及备件区)</p>
                <p>距桌边深度：<span class='metric-value'>{max_depth:.1f}</span> mm</p>
                <p>左右总宽度：<span class='metric-value'>{max_width:.1f}</span> mm</p>
            </div>
            """, unsafe_allow_html=True)

        st.pyplot(fig)