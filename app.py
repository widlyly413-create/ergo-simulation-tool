import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import os
from shapely.geometry import Polygon

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 0. 页面配置与 CSS 加载
# ==========================================
st.set_page_config(
    page_title="大漆工艺人机适配系统 - 微醺集",
    layout="wide",
    initial_sidebar_state="collapsed"
)

css_path = os.path.join(BASE_DIR, "static", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def round_to_half_cm(value_mm):
    return round(value_mm / 5.0) * 5

# ==========================================
# 2. 页面头部 (翻新版)
# ==========================================
st.markdown("""
<div class="header-container">
    <h1 class="header-title">大漆工艺人机适配系统</h1>
    <p class="header-subtitle">
        融合 <span class="highlight">RULA/REBA</span> 动态评估与 <span class="highlight">Squires</span> 空间包络算法，<br>
        数字化赋能传统大漆工艺，为手工艺者量身定制精准工位尺寸。
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. 参数录入 (布局优化)
# ==========================================
st.markdown('<div class="section-title">📐 参数录入</div>', unsafe_allow_html=True)

main_col_1, main_col_2 = st.columns([1.2, 2.5], gap="large")

with main_col_1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎯 核心工序")
    work_type = st.selectbox("核心工序选择", ["打磨工序 (侧重施力)", "装饰工序 (侧重视觉)"])
    offset = 200 if "装饰" in work_type else 120
    
    st.subheader("⚙️ 设施可调性")
    mode = st.selectbox("可调性模式", ["全自由调节", "仅座椅高度固定", "仅桌面高度固定"])
    
    st.subheader("📦 工件高度")
    h_workpiece = st.slider("工件作业点高度 (mm)", 0, 500, 50, step=5)
    st.markdown('</div>', unsafe_allow_html=True)

with main_col_2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 身体静态尺寸 (mm)")
    
    # 采用网格化布局
    g_col_1, g_col_2 = st.columns(2)
    with g_col_1:
        h_popliteal = st.number_input("坐姿腘高 (h_p)", 300, 600, 400, step=5)
        h_elbow = st.number_input("坐姿肘高 (h_e)", 100, 500, 250, step=5)
        S_a = st.number_input("肩宽 (S_a)", 300.0, 600.0, 419.0, step=5.0)
    with g_col_2:
        L_a = st.number_input("上臂长 (L_a)", 200.0, 500.0, 318.0, step=5.0)
        R_a = st.number_input("前臂长 (R_a)", 150.0, 400.0, 235.0, step=5.0)
        F_a = st.number_input("手长 1/2 (F_a)", 50.0, 150.0, 92.0, step=1.0)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 计算逻辑
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
# 5. 结果显示 (Z轴与实时 SVG)
# ==========================================
st.markdown('<div class="section-title">🪑 空间适配结果</div>', unsafe_allow_html=True)

res_col_1, res_col_2 = st.columns([1, 1.2], gap="large")

with res_col_1:
    st.markdown('<div class="card" style="height: 100%;">', unsafe_allow_html=True)
    st.subheader("📊 推荐尺寸 (mm)")
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-title">座椅高度</div>
            <div class="metric-value">{int(h_chair_final)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">桌面高度</div>
            <div class="metric-value">{int(h_desk_final)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">视线参考</div>
            <div class="metric-value">{int(h_eye)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">膝盖净空</div>
            <div class="metric-value">{int(h_knee_clearance)}</div>
        </div>
    </div>
    <div class="footer-hint">
        💡 <b>专家建议：</b> 基于您的身体数据，座椅应设定为 {int(h_chair_final)}mm。这能确保您的双脚自然平放，减少下背部压力。
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with res_col_2:
    scale_z = 0.28
    gy = 340 
    sy = gy - (h_chair_final * scale_z)
    dy = gy - (h_desk_final * scale_z)
    ey = gy - (h_eye * scale_z)
    ky = gy - (h_knee_clearance * scale_z)
    wy = dy - (h_workpiece * scale_z)

    svg_html_z = f"""
    <div style="background: white; border-radius: 16px; border: 1px solid rgba(140,28,19,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.05); width: 100%; height: 420px; display: flex; align-items: center; justify-content: center;">
        <svg width="100%" height="400" viewBox="0 0 450 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="deskGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#8C1C13;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#5A120D;stop-opacity:1" />
                </linearGradient>
            </defs>
            <line x1="30" y1="{gy}" x2="420" y2="{gy}" stroke="#333" stroke-width="4"/>
            <line x1="50" y1="{gy}" x2="50" y2="{sy}" stroke="#999" stroke-width="2" stroke-dasharray="6,4"/>
            <text x="55" y="{gy - 15}" fill="#666" font-size="12" font-family="sans-serif">椅高 {int(h_chair_final)}</text>
            <line x1="400" y1="{gy}" x2="400" y2="{dy}" stroke="#8C1C13" stroke-width="2" stroke-dasharray="6,4"/>
            <text x="325" y="{dy + 25}" fill="#8C1C13" font-size="13" font-family="sans-serif" font-weight="bold">桌高 {int(h_desk_final)}</text>
            <line x1="20" y1="{gy}" x2="20" y2="{ey}" stroke="#D4AF37" stroke-width="2" stroke-dasharray="6,4"/>
            <text x="25" y="{ey - 8}" fill="#B8962D" font-size="12" font-family="sans-serif">视高 {int(h_eye)}</text>
            <rect x="250" y="{dy}" width="140" height="12" fill="url(#deskGrad)" rx="3"/>
            <line x1="270" y1="{dy+12}" x2="270" y2="{gy}" stroke="#444" stroke-width="6"/>
            <line x1="370" y1="{dy+12}" x2="370" y2="{gy}" stroke="#444" stroke-width="6"/>
            <rect x="90" y="{sy}" width="70" height="10" fill="#333" rx="3"/>
            <line x1="110" y1="{sy+10}" x2="110" y2="{gy}" stroke="#444" stroke-width="5"/>
            <line x1="140" y1="{sy+10}" x2="140" y2="{gy}" stroke="#444" stroke-width="5"/>
            <path d="M 95 {sy} L 85 {sy-70}" stroke="#333" stroke-width="8" stroke-linecap="round"/>
            <circle cx="130" cy="{ey}" r="18" fill="#D4AF37" stroke="white" stroke-width="2"/> 
            <path d="M 130 {ey+18} L 115 {sy}" stroke="#8C1C13" stroke-width="16" stroke-linecap="round" fill="none"/>
            <path d="M 115 {sy} L 200 {sy}" stroke="#121212" stroke-width="14" stroke-linecap="round" fill="none"/> 
            <path d="M 200 {sy} L 195 {gy}" stroke="#121212" stroke-width="12" stroke-linecap="round" fill="none"/>
            <path d="M 130 {ey+22} L 155 {sy-25} L 285 {wy}" stroke="#D4AF37" stroke-width="10" stroke-linecap="round" fill="none" stroke-linejoin="round"/>
            <circle cx="285" cy="{wy}" r="6" fill="#ff7f0e" stroke="white" stroke-width="2"/>
        </svg>
    </div>
    """
    components.html(svg_html_z, height=440)

# ==========================================
# 6. 平面布局图 (XY轴)
# ==========================================
st.markdown('<div class="section-title">🎯 动态包络面与落点布局</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.write("点击下方按钮，根据您的身体尺寸实时解算工作台的功能区布局（CAD 工程级标注）。")

if st.button("生成/刷新 布局动线解析图 (带工程尺码)", type="primary"):
    with st.spinner("正在解算空间几何..."):
        shoulder_y = -50
        B_a = R_a + F_a
        R_max = L_a + B_a
        theta_0 = 65 * np.pi / 180
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

        theta_full = np.linspace(0, 105 * np.pi / 180, 200)
        x_cR = S_a / 2 + L_a * np.cos(theta_full) + B_a * np.cos(theta_0 + 73 * theta_full / 90)
        y_cR = shoulder_y + L_a * np.sin(theta_full) + B_a * np.sin(theta_0 + 73 * theta_full / 90)
        x_cL, y_cL = -x_cR, y_cR

        sq_R = Polygon(np.column_stack((np.concatenate([[0, S_a/2, S_a/2+L_a], x_cR, [0]]), 
                                        np.concatenate([[shoulder_y]*3, y_cR, [shoulder_y]]))))
        sq_L = Polygon(np.column_stack((np.concatenate([[0, -S_a/2, -S_a/2-L_a], x_cL, [0]]),
                                        np.concatenate([[shoulder_y]*3, y_cL, [shoulder_y]]))))
        union_sq = sq_R.union(sq_L)

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
            (X_op, Y_op, '#8C1C13', '核心操作区'),
            (X_st, Y_st, '#2CA02C', '辅助存放区'),
            (X_tr, Y_tr, '#FF7F0E', '工具转换区'),
            (X_nu, Y_nu, '#9467BD', '非频繁区')
        ]

        minx_max, miny_max, maxx_max, maxy_max = union_max.bounds
        minx_sq, miny_sq, maxx_sq, maxy_sq = union_sq.bounds

        svg_w, svg_h = 960, 750
        scale = 0.35
        center_x = svg_w / 2
        base_y = svg_h - 150 

        def geom_to_svg_path(geom):
            paths = []
            if geom.geom_type == 'Polygon':
                geoms = [geom]
            else:
                geoms = geom.geoms
            for g in geoms:
                x, y = g.exterior.xy
                pts = [f"{xi * scale + center_x},{base_y - yi * scale}" for xi, yi in zip(x, y)]
                paths.append(" ".join(pts))
            return paths

        max_paths = geom_to_svg_path(union_max)
        sq_paths = geom_to_svg_path(union_sq)

        def draw_dim_h(x1, x2, y, label, color="#666"):
            sx1 = center_x + x1 * scale
            sx2 = center_x + x2 * scale
            sy = base_y - y * scale
            return f"""
                <g stroke="{color}" stroke-width="2">
                    <line x1="{sx1}" y1="{sy}" x2="{sx2}" y2="{sy}" />
                    <line x1="{sx1}" y1="{sy-10}" x2="{sx1}" y2="{sy+10}" />
                    <line x1="{sx2}" y1="{sy-10}" x2="{sx2}" y2="{sy+10}" />
                    <text x="{(sx1+sx2)/2}" y="{sy-15}" fill="{color}" font-size="14" font-weight="bold" text-anchor="middle" stroke="none">{label} {x2-x1:.0f} mm</text>
                </g>
            """

        def draw_dim_v(x, y1, y2, label, color="#666", align="left"):
            sx = center_x + x * scale
            sy1 = base_y - y1 * scale
            sy2 = base_y - y2 * scale
            text_x = sx - 15 if align == "left" else sx + 15
            anchor = "end" if align == "left" else "start"
            return f"""
                <g stroke="{color}" stroke-width="2">
                    <line x1="{sx}" y1="{sy1}" x2="{sx}" y2="{sy2}" />
                    <line x1="{sx-8}" y1="{sy1}" x2="{sx+8}" y2="{sy1}" />
                    <line x1="{sx-8}" y1="{sy2}" x2="{sx+8}" y2="{sy2}" />
                    <text x="{text_x}" y="{(sy1+sy2)/2 + 5}" fill="{color}" font-size="14" font-weight="bold" text-anchor="{anchor}" stroke="none">{label} {y2-y1:.0f} mm</text>
                </g>
            """

        svg_content = f"""
        <div style="background: #FFFFFF; border-radius: 16px; border: 1px solid rgba(140,28,19,0.1); width: 100%; display: flex; justify-content: center; overflow-x: auto; padding: 20px 0;">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur in="SourceAlpha" stdDeviation="4" />
                        <feOffset dx="3" dy="3" />
                        <feComponentTransfer><feFuncA type="linear" slope="0.2" /></feComponentTransfer>
                        <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
                    </filter>
                </defs>
                {"".join([f'<polygon points="{pts}" fill="#90EE90" fill-opacity="0.08" stroke="#4CAF50" stroke-width="2" stroke-dasharray="8,4" />' for pts in max_paths])}
                {"".join([f'<polygon points="{pts}" fill="#ADD8E6" fill-opacity="0.3" stroke="#1f77b4" stroke-width="2.5" />' for pts in sq_paths])}
                {draw_dim_h(minx_max, maxx_max, maxy_max + 140, "最大动态包络宽", "#2E7D32")}
                {draw_dim_v(maxx_max + 150, 0, maxy_max, "最大可及深度", "#2E7D32", "right")}
                {draw_dim_h(minx_sq, maxx_sq, maxy_sq + 80, "舒适作业区宽", "#1565C0")}
                {draw_dim_v(minx_sq - 150, 0, maxy_sq, "最佳视距深度", "#1565C0", "left")}
        """

        for X, Y, color, label in zones:
            cx, cy = X * scale + center_x, base_y - Y * scale
            svg_content += f"""
                <g filter="url(#shadow)">
                    <circle cx="{cx}" cy="{cy}" r="{100 * scale}" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-width="2.5" stroke-dasharray="6,4"/>
                    <circle cx="{cx}" cy="{cy}" r="6" fill="{color}" stroke="white" stroke-width="2"/>
                    <rect x="{cx - 60}" y="{cy - 100 * scale - 45}" width="120" height="42" rx="6" fill="white" fill-opacity="0.95" stroke="{color}" stroke-width="1.5"/>
                    <text x="{cx}" y="{cy - 100 * scale - 26}" fill="{color}" font-size="13" font-weight="bold" text-anchor="middle">{label}</text>
                    <text x="{cx}" y="{cy - 100 * scale - 10}" fill="#555" font-size="11" text-anchor="middle">({X:.0f}, {Y:.0f})</text>
                </g>
            """

        chest_y = base_y - (shoulder_y * scale)
        svg_content += f"""
                <line x1="50" y1="{base_y}" x2="{svg_w - 50}" y2="{base_y}" stroke="#8C1C13" stroke-width="5" stroke-linecap="round" />
                <text x="60" y="{base_y + 30}" fill="#8C1C13" font-size="14" font-weight="bold">工作台边缘 (Table Edge / Y=0)</text>
                <line x1="{center_x - 200}" y1="{chest_y}" x2="{center_x + 200}" y2="{chest_y}" stroke="#999" stroke-width="2" stroke-dasharray="10,5" />
                <circle cx="{center_x}" cy="{chest_y}" r="10" fill="#121212" stroke="white" stroke-width="3" />
                <text x="{center_x + 20}" y="{chest_y + 5}" fill="#121212" font-size="14" font-weight="bold">胸廓中心原点</text>
            </svg>
        </div>
        """
        components.html(svg_content, height=svg_h + 30)

st.markdown('</div>', unsafe_allow_html=True)
