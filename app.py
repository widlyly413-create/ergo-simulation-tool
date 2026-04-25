import streamlit as st
import streamlit.components.v1 as components
import numpy as np
from shapely.geometry import Polygon

# ==========================================
# 0. 页面配置与 CSS
# ==========================================
st.set_page_config(page_title="大漆工艺人机适配系统 - 微醺集", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Roboto:wght@300;400;700&display=swap');

    .stApp { 
        background-color: #FDFBF7; 
        color: #2C2C2C; 
        font-family: 'Roboto', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Noto Serif SC', serif;
        font-weight: 700 !important;
    }

    .card { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 24px; 
        box-shadow: 0 4px 20px rgba(140, 28, 19, 0.08); 
        margin-bottom: 24px; 
        border: 1px solid #F0E6D2;
        border-top: 5px solid #8C1C13; 
        transition: transform 0.2s ease-in-out;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(140, 28, 19, 0.12);
    }

    .metric-container { 
        display: flex; 
        flex-wrap: wrap; 
        gap: 15px; 
        margin-top: 15px; 
    }
    
    .metric-box { 
        background: #FAF7F2; 
        padding: 18px; 
        border-radius: 10px; 
        flex: 1; 
        min-width: 140px;
        text-align: center; 
        border: 1px solid #EADDC3;
        border-left: 4px solid #8C1C13; 
    }
    
    .metric-title { 
        font-size: 13px; 
        color: #666; 
        margin-bottom: 8px; 
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value { 
        font-size: 24px; 
        font-weight: 700; 
        color: #8C1C13; 
        margin: 0; 
        font-family: 'Georgia', serif;
    }

    /* 优化侧边栏和按钮 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# 统一的高度精确度函数
def round_to_half_cm(value_mm):
    return round(value_mm / 5.0) * 5

# ==========================================
# 2. 页面头部
# ==========================================
st.markdown("""
<div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #1A1A1A 0%, #333333 100%); color: #FDFBF7; border-radius: 12px; margin-bottom: 30px; border-bottom: 6px solid #8C1C13; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
    <h1 style="color: #D4AF37; margin-bottom: 15px; font-size: 2.5rem; letter-spacing: 2px;">传统大漆工艺 · 人机适配数字化系统</h1>
    <div style="width: 60px; height: 3px; background: #8C1C13; margin: 0 auto 20px auto;"></div>
    <p style="color: #E0E0E0; font-size: 1.15rem; max-width: 850px; margin: 0 auto; line-height: 1.6; font-weight: 300;">
        融合 <span style="color: #D4AF37; font-weight: 500;">RULA/REBA</span> 动态评估与 <span style="color: #D4AF37; font-weight: 500;">Squires</span> 作业面算法，<br>
        为您量身定制精确至 0.5cm 的工位尺寸与功能落点布局。
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 3. 参数录入
# ==========================================
st.markdown("### 📐 1. 作业者与场景参数")
st.markdown('<div class="card">', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 2])
with col_a:
    work_type = st.selectbox("🎯 核心工序", ["打磨工序 (侧重施力)", "装饰工序 (侧重视觉)"])
    offset = 200 if "装饰" in work_type else 120
    mode = st.selectbox("⚙️ 设施可调性", ["全自由调节", "仅座椅高度固定", "仅桌面高度固定"])
    h_workpiece = st.slider("📦 工件作业点高度 (mm)", 0, 500, 50, step=5)

with col_b:
    st.info("请输入作业者的身体静态尺寸（单位：mm）")
    c1, c2, c3, c4 = st.columns(4)
    with c1: h_popliteal = st.number_input("坐姿腘高", 300, 600, 400, step=5, help="小腿腘窝至地面的高度")
    with c2: h_elbow = st.number_input("坐姿肘高", 100, 500, 250, step=5, help="坐姿状态下肘部至座面的高度")
    with c3: L_a = st.number_input("上臂长", 200.0, 500.0, 318.0, step=5.0)
    with c4: R_a = st.number_input("前臂长", 150.0, 400.0, 235.0, step=5.0)
    
    c5, c6, c7 = st.columns([1, 1, 2])
    with c5: S_a = st.number_input("肩宽", 300.0, 600.0, 419.0, step=5.0)
    with c6: F_a = st.number_input("手长(1/2)", 50.0, 150.0, 92.0, step=1.0)
    with c7: st.write("") # 占位
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
    st.markdown('<div class="card" style="height: 420px;">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#8C1C13; margin-top:0; border-bottom:1px solid #eee; padding-bottom:10px;'>📊 推荐尺寸 (mm)</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">最佳座椅高度</div><p class="metric-value">{int(h_chair_final)}</p></div>
        <div class="metric-box"><div class="metric-title">最佳作业面高度</div><p class="metric-value">{int(h_desk_final)}</p></div>
    </div>
    <div class="metric-container">
        <div class="metric-box"><div class="metric-title">视线参考高度</div><p class="metric-value">{int(h_eye)}</p></div>
        <div class="metric-box"><div class="metric-title">最小桌下净空</div><p class="metric-value">{int(h_knee_clearance)}</p></div>
    </div>
    <div style="margin-top:20px; padding:12px; background:#F8F9FA; border-radius:8px; font-size:0.85rem; color:#666; border-left:4px solid #D4AF37;">
        💡 <b>建议：</b> 根据计算结果，您的座椅应调整至 {int(h_chair_final)}mm，以确保双脚平放且大腿与地面平行。
    </div>
    </div>
    """, unsafe_allow_html=True)

with col_img:
    scale = 0.28
    gy = 340 
    sy = gy - (h_chair_final * scale)
    dy = gy - (h_desk_final * scale)
    ey = gy - (h_eye * scale)
    ky = gy - (h_knee_clearance * scale)
    wy = dy - (h_workpiece * scale)

    svg_html = f"""
    <div style="background: white; border-radius: 12px; border: 1px solid #F0E6D2; border-top: 5px solid #8C1C13; box-shadow: 0 4px 20px rgba(0,0,0,0.05); width: 100%; height: 420px; display: flex; align-items: center; justify-content: center;">
        <svg width="100%" height="400" viewBox="0 0 450 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="deskGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#8C1C13;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#5A120D;stop-opacity:1" />
                </linearGradient>
            </defs>
            <line x1="30" y1="{gy}" x2="420" y2="{gy}" stroke="#121212" stroke-width="3"/>
            
            <line x1="50" y1="{gy}" x2="50" y2="{sy}" stroke="#999" stroke-width="1" stroke-dasharray="4"/>
            <text x="55" y="{gy - 15}" fill="#666" font-size="11" font-family="sans-serif">椅高 {int(h_chair_final)}</text>
            
            <line x1="400" y1="{gy}" x2="400" y2="{dy}" stroke="#8C1C13" stroke-width="1.5" stroke-dasharray="4"/>
            <text x="325" y="{dy + 20}" fill="#8C1C13" font-size="12" font-family="sans-serif" font-weight="bold">桌高 {int(h_desk_final)}</text>
            
            <line x1="20" y1="{gy}" x2="20" y2="{ey}" stroke="#D4AF37" stroke-width="1" stroke-dasharray="4"/>
            <text x="25" y="{ey - 5}" fill="#B8962D" font-size="11" font-family="sans-serif">视高 {int(h_eye)}</text>
            
            <rect x="250" y="{dy}" width="140" height="12" fill="url(#deskGrad)" rx="2"/>
            <line x1="270" y1="{dy+12}" x2="270" y2="{gy}" stroke="#444" stroke-width="5"/>
            <line x1="370" y1="{dy+12}" x2="370" y2="{gy}" stroke="#444" stroke-width="5"/>
            
            <rect x="90" y="{sy}" width="70" height="10" fill="#333" rx="2"/>
            <line x1="110" y1="{sy+10}" x2="110" y2="{gy}" stroke="#444" stroke-width="4"/>
            <line x1="140" y1="{sy+10}" x2="140" y2="{gy}" stroke="#444" stroke-width="4"/>
            <path d="M 95 {sy} L 85 {sy-70}" stroke="#333" stroke-width="7" stroke-linecap="round"/>
            
            <circle cx="130" cy="{ey}" r="16" fill="#D4AF37"/> 
            <path d="M 130 {ey+16} L 115 {sy}" stroke="#8C1C13" stroke-width="14" stroke-linecap="round" fill="none"/>
            <path d="M 115 {sy} L 200 {sy}" stroke="#121212" stroke-width="12" stroke-linecap="round" fill="none"/> 
            <path d="M 200 {sy} L 195 {gy}" stroke="#121212" stroke-width="10" stroke-linecap="round" fill="none"/>
            <path d="M 130 {ey+20} L 155 {sy-25} L 285 {wy}" stroke="#D4AF37" stroke-width="8" stroke-linecap="round" fill="none" stroke-linejoin="round"/>
            <circle cx="285" cy="{wy}" r="5" fill="#ff7f0e"/>
        </svg>
    </div>
    """
    components.html(svg_html, height=440)

# ==========================================
# 6. 平面布局图生成 (纯 SVG 矢量渲染技术)
# ==========================================
st.markdown("### 🎯 3. XY轴：动态包络面与功能落点布局")
st.markdown('<div class="card">', unsafe_allow_html=True)
st.write("基于 Squires 算法与几何中点法则，系统自动规划出大漆核心工具的最佳摆放区域。采用纯矢量 SVG 渲染。")

if st.button("生成/刷新 布局动线解析图", type="primary", use_container_width=True):
    with st.spinner("正在解算空间几何与矢量节点..."):
        
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
            (X_op, Y_op, '#8C1C13', '操作区'),
            (X_st, Y_st, '#2CA02C', '存放区'),
            (X_tr, Y_tr, '#FF7F0E', '转换区'),
            (X_nu, Y_nu, '#9467BD', '非取用区')
        ]

        svg_w, svg_h = 800, 600
        scale = 0.4
        center_x = svg_w / 2
        base_y = svg_h - 100 

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

        svg_content = f"""
        <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #F0E6D2; border-top: 5px solid #8C1C13; box-shadow: 0 4px 20px rgba(0,0,0,0.05); width: 100%; display: flex; justify-content: center; overflow-x: auto; padding: 20px 0;">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', sans-serif;">
                <defs>
                    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
                        <feOffset dx="2" dy="2" result="offsetblur" />
                        <feComponentTransfer>
                            <feFuncA type="linear" slope="0.3" />
                        </feComponentTransfer>
                        <feMerge>
                            <feMergeNode />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>
                
                {"".join([f'<polygon points="{pts}" fill="#90EE90" fill-opacity="0.2" stroke="#4CAF50" stroke-width="1" stroke-dasharray="5,5" />' for pts in max_paths])}
                
                {"".join([f'<polygon points="{pts}" fill="#ADD8E6" fill-opacity="0.4" stroke="#1f77b4" stroke-width="2" />' for pts in sq_paths])}

        """

        R_zone_svg = 100 * scale
        for X, Y, color, label in zones:
            cx = X * scale + center_x
            cy = base_y - Y * scale
            svg_content += f"""
                <g filter="url(#shadow)">
                    <circle cx="{cx}" cy="{cy}" r="{R_zone_svg}" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-width="2" stroke-dasharray="4,4"/>
                    <circle cx="{cx}" cy="{cy}" r="5" fill="{color}"/>
                    <rect x="{cx - 40}" y="{cy - R_zone_svg - 25}" width="80" height="20" rx="4" fill="white" fill-opacity="0.8" />
                    <text x="{cx}" y="{cy - R_zone_svg - 10}" fill="{color}" font-size="12" font-weight="bold" text-anchor="middle">{label}</text>
                </g>
            """

        chest_y = base_y - (shoulder_y * scale)
        svg_content += f"""
                <line x1="50" y1="{base_y}" x2="{svg_w - 50}" y2="{base_y}" stroke="#8C1C13" stroke-width="3" stroke-linecap="round" />
                <text x="60" y="{base_y + 20}" fill="#8C1C13" font-size="12" font-weight="bold">工作台边缘 (Table Edge)</text>

                <line x1="{center_x - 150}" y1="{chest_y}" x2="{center_x + 150}" y2="{chest_y}" stroke="#999" stroke-width="1" stroke-dasharray="4,4" />
                <circle cx="{center_x}" cy="{chest_y}" r="6" fill="#121212" stroke="white" stroke-width="2" />
                <text x="{center_x + 12}" y="{chest_y + 4}" fill="#121212" font-size="12" font-weight="bold">胸廓中心</text>
            </svg>
        </div>
        """

        components.html(svg_content, height=svg_h + 20)

st.markdown('</div>', unsafe_allow_html=True)
