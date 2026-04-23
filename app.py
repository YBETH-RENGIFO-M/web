import streamlit as st
import json
import hashlib
import time
from datetime import datetime
import base64
from pathlib import Path
from urllib.parse import quote

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
WOMPI_PUBLIC_KEY = "pub_stagtest_g2u0HQd3ZMh05hsSgTS2lUV8t3s4mOt7"  # ← Reemplaza con tu clave real
WOMPI_ENV = "sandbox"  # ← Cambiar a "production" en producción
NOTIFICATION_EMAIL = "tubotlatam@gmail.com"
CURRENCY = "COP"
DEFAULT_PRICE = 150000
DEFAULT_NAME = "SuperTrend Pro v3"
DEFAULT_DESC = (
    "Indicador de tendencia avanzado con filtro de volatilidad ATR adaptativo. "
    "Genera señales claras de entrada y salida con alertas visuales y sonoras integradas."
)
ADMIN_PASSWORD = "TuBot2026!"  # ← Cambia esta contraseña

st.set_page_config(
    page_title="TuBot LATAM — Indicadores NinjaTrader",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# ESTADO INICIAL
# ─────────────────────────────────────────────────────────────
if "product_name" not in st.session_state:
    st.session_state.product_name = DEFAULT_NAME
if "product_desc" not in st.session_state:
    st.session_state.product_desc = DEFAULT_DESC
if "product_price" not in st.session_state:
    st.session_state.product_price = DEFAULT_PRICE
if "product_image_b64" not in st.session_state:
    st.session_state.product_image_b64 = None
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ─────────────────────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg-primary: #0a0e17;
    --bg-card: #111827;
    --bg-card-hover: #1a2332;
    --accent: #00d4aa;
    --accent-dim: #00d4aa33;
    --accent-glow: #00d4aa55;
    --text-primary: #f0f4f8;
    --text-secondary: #8899aa;
    --border: #1e2d3d;
  }

  .stApp {
    background: var(--bg-primary) !important;
    font-family: 'Outfit', sans-serif !important;
  }

  /* Hero */
  .hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
  }
  .hero-container::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 400px; height: 400px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
    opacity: 0.15;
    pointer-events: none;
  }
  .hero-brand {
    font-size: 0.85rem; font-weight: 600;
    letter-spacing: 4px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.5rem;
  }
  .hero-title {
    font-size: 2.2rem; font-weight: 800;
    color: var(--text-primary); line-height: 1.15;
    margin-bottom: 0.6rem;
  }
  .hero-subtitle {
    font-size: 1rem; color: var(--text-secondary);
    font-weight: 300; max-width: 520px;
    margin: 0 auto; line-height: 1.6;
  }

  /* Cards */
  .glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 1.8rem;
    margin-bottom: 1.2rem;
    transition: all 0.3s ease;
  }
  .glass-card:hover {
    border-color: var(--accent-dim);
    background: var(--bg-card-hover);
  }
  .card-header {
    display: flex; align-items: center;
    gap: 0.6rem; margin-bottom: 1rem;
  }
  .card-step {
    background: var(--accent); color: var(--bg-primary);
    font-weight: 700; font-size: 0.75rem;
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .card-title {
    font-size: 1.1rem; font-weight: 600;
    color: var(--text-primary);
  }

  /* Indicator preview */
  .indicator-preview {
    background: linear-gradient(135deg, #0d1b2a, #1b2838);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1.5rem;
    text-align: center; margin: 1rem 0;
  }
  .indicator-preview img {
    border-radius: 8px; max-height: 320px;
    width: 100%; object-fit: contain;
    border: 1px solid var(--border);
  }
  .indicator-name {
    font-size: 1.3rem; font-weight: 700;
    color: var(--text-primary); margin-top: 1rem;
  }
  .indicator-desc {
    color: var(--text-secondary); font-size: 0.9rem;
    line-height: 1.6; margin-top: 0.5rem;
  }

  /* Price */
  .price-tag {
    display: inline-flex; align-items: baseline; gap: 0.3rem;
    background: var(--accent-dim); border: 1px solid var(--accent);
    border-radius: 10px; padding: 0.6rem 1.4rem; margin-top: 1rem;
  }
  .price-currency { font-size: 0.85rem; font-weight: 500; color: var(--accent); }
  .price-amount {
    font-size: 1.8rem; font-weight: 800;
    color: var(--accent); font-family: 'JetBrains Mono', monospace;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    background: #0d1520 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.7rem 1rem !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
  }
  .stTextInput > label, .stTextArea > label,
  .stNumberInput > label, .stFileUploader > label {
    color: var(--text-secondary) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important; font-size: 0.85rem !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #00d4aa, #00b894) !important;
    color: #0a0e17 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.8rem 2rem !important; width: 100% !important;
    transition: all 0.3s ease !important; letter-spacing: 0.5px;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px var(--accent-glow) !important;
  }

  /* File uploader */
  .stFileUploader > div {
    background: #0d1520 !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
  }

  /* Success box */
  .success-box {
    background: linear-gradient(135deg, #00d4aa15, #00d4aa08);
    border: 1px solid #00d4aa44; border-radius: 12px;
    padding: 1.5rem; text-align: center;
  }
  .success-box h3 { color: var(--accent); margin: 0 0 0.5rem; font-size: 1.2rem; }
  .success-box p { color: var(--text-secondary); margin: 0; font-size: 0.9rem; line-height: 1.6; }

  .info-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: #1e3a5f; color: #60a5fa;
    font-size: 0.78rem; font-weight: 500;
    padding: 0.35rem 0.8rem; border-radius: 6px; margin-top: 0.4rem;
  }

  .features-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
  .feature-pill {
    background: #0d1520; border: 1px solid var(--border);
    border-radius: 20px; padding: 0.35rem 0.9rem;
    font-size: 0.78rem; color: var(--text-secondary); font-weight: 500;
  }

  .custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
  }

  /* Sidebar dark theme */
  section[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid var(--border) !important;
  }
  section[data-testid="stSidebar"] .stTextInput > div > div > input,
  section[data-testid="stSidebar"] .stTextArea > div > div > textarea {
    background: #111827 !important;
    border: 1px solid #1e2d3d !important;
    color: #f0f4f8 !important;
  }
  section[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background: #111827 !important;
    border: 1px solid #1e2d3d !important;
    color: #f0f4f8 !important;
  }

  /* Hide Streamlit defaults */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────────────────────
def generate_reference(name: str) -> str:
    ts = str(int(time.time()))
    raw = f"{name}-{ts}"
    return "TBOT-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()


def get_wompi_checkout_url(ref: str, amount_cents: int, name: str, email: str) -> str:
    return (
        f"https://checkout.wompi.co/p/"
        f"?public-key={WOMPI_PUBLIC_KEY}"
        f"&currency={CURRENCY}"
        f"&amount-in-cents={amount_cents}"
        f"&reference={ref}"
        f"&customer-data.full-name={quote(name)}"
        f"&customer-data.email={quote(email)}"
        f"&redirect-url={quote('https://tubot-latam.streamlit.app/?status=success')}"
    )


def render_indicator_card(image_b64, name: str, description: str, price: int):
    if image_b64:
        img_html = f'<img src="data:image/png;base64,{image_b64}" alt="{name}" />'
    else:
        img_html = (
            '<div style="height:200px;display:flex;align-items:center;'
            'justify-content:center;color:#8899aa;font-size:0.9rem;'
            'border:1px dashed #1e2d3d;border-radius:8px;">'
            '📊 Vista previa del indicador</div>'
        )

    st.markdown(f"""
    <div class="indicator-preview">
        {img_html}
        <div class="indicator-name">{name}</div>
        <div class="indicator-desc">{description}</div>
        <div class="price-tag">
            <span class="price-currency">COP</span>
            <span class="price-amount">${price:,.0f}</span>
        </div>
        <div class="features-row">
            <span class="feature-pill">📊 NinjaTrader 8</span>
            <span class="feature-pill">🔑 Licencia por Machine ID</span>
            <span class="feature-pill">⚡ Activación en 24h</span>
            <span class="feature-pill">💬 Soporte incluido</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR — PANEL ADMIN CON CONTRASEÑA
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #f0f4f8;">
            🔐 Panel Admin
        </div>
        <div style="font-size: 0.75rem; color: #556677; margin-top: 0.3rem;">
            Configuración del producto
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if not st.session_state.admin_logged_in:
        # ── LOGIN ──
        admin_pass_input = st.text_input(
            "Contraseña de administrador",
            type="password",
            key="admin_pass_field",
            placeholder="Ingresa la contraseña..."
        )
        if st.button("🔓  Ingresar", key="admin_login_btn"):
            if admin_pass_input == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
    else:
        # ── PANEL ADMIN ACTIVO ──
        st.markdown("""
        <div style="background:#00d4aa22; border:1px solid #00d4aa44;
                    border-radius:8px; padding:0.5rem 0.8rem; text-align:center;
                    font-size:0.8rem; color:#00d4aa; font-weight:600; margin-bottom:1rem;">
            ✅ Sesión de admin activa
        </div>
        """, unsafe_allow_html=True)

        new_name = st.text_input(
            "Nombre del indicador",
            value=st.session_state.product_name,
            key="field_product_name"
        )
        new_desc = st.text_area(
            "Descripción breve",
            value=st.session_state.product_desc,
            height=120,
            key="field_product_desc"
        )
        new_price = st.number_input(
            "Precio (COP)",
            min_value=10000,
            value=st.session_state.product_price,
            step=5000,
            key="field_product_price"
        )

        uploaded_img = st.file_uploader(
            "Imagen del indicador",
            type=["png", "jpg", "jpeg", "webp"],
            key="field_product_image"
        )
        if uploaded_img:
            st.image(uploaded_img, caption="Vista previa", use_container_width=True)

        st.markdown("")

        if st.button("💾  Guardar configuración", key="admin_save_btn"):
            st.session_state.product_name = new_name
            st.session_state.product_desc = new_desc
            st.session_state.product_price = int(new_price)
            if uploaded_img:
                st.session_state.product_image_b64 = base64.b64encode(
                    uploaded_img.read()
                ).decode()
            st.success("✅ Producto actualizado.")
            st.rerun()

        st.markdown("---")

        # ── LOG DE TRANSACCIONES ──
        log_file = Path("transactions_log.json")
        if log_file.exists():
            try:
                txns = json.loads(log_file.read_text())
                if txns:
                    st.markdown(f"""
                    <div style="font-size:0.85rem; color:#f0f4f8; font-weight:600;
                                margin-bottom:0.5rem;">
                        📋 Últimas transacciones ({len(txns)})
                    </div>
                    """, unsafe_allow_html=True)
                    for t in reversed(txns[-5:]):
                        st.markdown(f"""
                        <div style="background:#111827; border:1px solid #1e2d3d;
                                    border-radius:8px; padding:0.6rem; margin-bottom:0.5rem;
                                    font-size:0.75rem; color:#8899aa;">
                            <strong style="color:#f0f4f8;">{t.get('name','?')}</strong><br>
                            📧 {t.get('email','?')}<br>
                            🖥️ <code style="color:#00d4aa;">{t.get('machine_id','?')}</code><br>
                            💰 COP ${t.get('price',0):,.0f} · {t.get('reference','?')}
                        </div>
                        """, unsafe_allow_html=True)
            except Exception:
                pass

        if st.button("🚪  Cerrar sesión admin", key="admin_logout_btn"):
            st.session_state.admin_logged_in = False
            st.rerun()


# ─────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-brand">⚡ TUBOT LATAM</div>
    <div class="hero-title">Indicadores Premium<br>para NinjaTrader</div>
    <div class="hero-subtitle">
        Herramientas de análisis técnico profesional.
        Configura, paga y recibe tu licencia en menos de 24 horas.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FLUJO DE COMPRA
# ─────────────────────────────────────────────────────────────
p_name = st.session_state.product_name
p_desc = st.session_state.product_desc
p_price = st.session_state.product_price
p_img = st.session_state.product_image_b64

# ── PASO 1: Producto ──
st.markdown("""
<div class="glass-card">
    <div class="card-header">
        <div class="card-step">1</div>
        <div class="card-title">Producto</div>
    </div>
</div>
""", unsafe_allow_html=True)

render_indicator_card(p_img, p_name, p_desc, p_price)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ── PASO 2: Datos del cliente ──
st.markdown("""
<div class="glass-card">
    <div class="card-header">
        <div class="card-step">2</div>
        <div class="card-title">Tus Datos</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input(
        "Nombre completo",
        placeholder="Ej: Juan Pérez",
        key="cust_name"
    )
with col2:
    customer_email = st.text_input(
        "Correo electrónico",
        placeholder="tu@email.com",
        key="cust_email"
    )

machine_id = st.text_input(
    "Machine ID (NinjaTrader)",
    placeholder="Ej: A1B2C3D4E5F6...",
    key="cust_machine"
)

st.markdown("""
<div class="info-badge">
    ℹ️&nbsp; Obtén tu Machine ID en NinjaTrader → Help → License Key → Machine ID
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ── PASO 3: Pago ──
st.markdown("""
<div class="glass-card">
    <div class="card-header">
        <div class="card-step">3</div>
        <div class="card-title">Pago Seguro con Wompi</div>
    </div>
</div>
""", unsafe_allow_html=True)

form_valid = all([
    customer_name and len(customer_name.strip()) >= 3,
    customer_email and "@" in customer_email and "." in customer_email,
    machine_id and len(machine_id.strip()) >= 4
])

if not form_valid:
    st.warning("⚠️ Completa todos los campos correctamente para proceder al pago.")

if form_valid:
    ref = generate_reference(customer_name)
    amount_cents = p_price * 100

    st.session_state.customer = {
        "name": customer_name.strip(),
        "email": customer_email.strip(),
        "machine_id": machine_id.strip(),
        "reference": ref,
        "product": p_name,
        "price": p_price,
        "timestamp": datetime.now().isoformat()
    }

    checkout_url = get_wompi_checkout_url(
        ref=ref,
        amount_cents=amount_cents,
        name=customer_name.strip(),
        email=customer_email.strip()
    )

    # Resumen
    st.markdown(f"""
    <div class="glass-card" style="background: linear-gradient(135deg, #0d1b2a, #111827);">
        <table style="width:100%; color: #8899aa; font-size: 0.88rem; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #1e2d3d;">
                <td style="padding: 0.5rem 0;">📦 Producto</td>
                <td style="text-align:right; color: #f0f4f8; font-weight:600;">{p_name}</td>
            </tr>
            <tr style="border-bottom: 1px solid #1e2d3d;">
                <td style="padding: 0.5rem 0;">👤 Cliente</td>
                <td style="text-align:right; color: #f0f4f8;">{customer_name}</td>
            </tr>
            <tr style="border-bottom: 1px solid #1e2d3d;">
                <td style="padding: 0.5rem 0;">📧 Email</td>
                <td style="text-align:right; color: #f0f4f8;">{customer_email}</td>
            </tr>
            <tr style="border-bottom: 1px solid #1e2d3d;">
                <td style="padding: 0.5rem 0;">🖥️ Machine ID</td>
                <td style="text-align:right; color: #f0f4f8; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;">{machine_id}</td>
            </tr>
            <tr>
                <td style="padding: 0.6rem 0; font-weight:600; color: #00d4aa;">💰 Total</td>
                <td style="text-align:right; color: #00d4aa; font-weight:800; font-size: 1.1rem; font-family: 'JetBrains Mono', monospace;">COP ${p_price:,.0f}</td>
            </tr>
        </table>
        <div style="margin-top:0.6rem; font-size: 0.72rem; color: #556677; text-align:center;">
            Ref: {ref}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón de pago Wompi
    st.markdown(f"""
    <a href="{checkout_url}" target="_blank" style="text-decoration: none; display:block;">
        <div style="
            background: linear-gradient(135deg, #00d4aa, #00b894);
            color: #0a0e17; font-family: 'Outfit', sans-serif;
            font-weight: 700; font-size: 1.05rem;
            text-align: center; padding: 1rem 2rem;
            border-radius: 14px; cursor: pointer;
            transition: all 0.3s ease; margin-top: 0.5rem;
            letter-spacing: 0.5px; box-shadow: 0 4px 20px #00d4aa33;
        ">
            🔒&nbsp; Pagar con Wompi — COP ${p_price:,.0f}
        </div>
    </a>
    <div style="text-align:center; margin-top:0.8rem; font-size: 0.75rem; color: #556677;">
        🔐 Pago seguro procesado por Wompi · Cifrado SSL 256-bit
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CONFIRMACIÓN POST-PAGO
# ─────────────────────────────────────────────────────────────
query_params = st.query_params
status = query_params.get("status", None)

if status == "success" or st.session_state.get("payment_confirmed"):
    st.session_state.payment_confirmed = True
    customer = st.session_state.get("customer", {})

    st.markdown(f"""
    <div class="success-box">
        <h3>✅ ¡Pago procesado exitosamente!</h3>
        <p>
            Gracias <strong>{customer.get('name', 'Cliente')}</strong>.<br>
            Hemos notificado al equipo de <strong>TuBot LATAM</strong>.<br><br>
            📧 Recibirás un correo en <strong>{customer.get('email', 'tu correo')}</strong><br>
            con las instrucciones de instalación.<br><br>
            ⏱️ <strong>En menos de 24 horas</strong> nos contactaremos contigo<br>
            para la activación de tu licencia.<br><br>
            <span style="font-size: 0.78rem; color: #556677;">
                Referencia de pago: {customer.get('reference', 'N/A')}
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Guardar transacción en log local
    log_file = Path("transactions_log.json")
    transactions = []
    if log_file.exists():
        try:
            transactions = json.loads(log_file.read_text())
        except Exception:
            transactions = []

    existing_refs = {t.get("reference") for t in transactions}
    if customer.get("reference") and customer["reference"] not in existing_refs:
        transactions.append({
            **customer,
            "status": "completed",
            "notified_to": NOTIFICATION_EMAIL
        })
        log_file.write_text(json.dumps(transactions, indent=2, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; color: #334455; font-size: 0.72rem;">
    <div style="margin-bottom: 0.3rem;">
        © 2026 TuBot LATAM · Todos los derechos reservados
    </div>
    <div>
        Indicadores profesionales para NinjaTrader 8 · Soporte: tubotlatam@gmail.com
    </div>
</div>
""", unsafe_allow_html=True)
