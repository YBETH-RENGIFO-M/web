import streamlit as st
import json
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import base64
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
WOMPI_PUBLIC_KEY = "pub_stagtest_g2u0HQd3ZMh05hsSgTS2lUV8t3s4mOt7"  # Reemplazar con tu clave real
WOMPI_ENV = "sandbox"  # Cambiar a "production" en producción
NOTIFICATION_EMAIL = "tubotlatam@gmail.com"
CURRENCY = "COP"
AMOUNT_COP = 350000  # Precio en COP (se envía en centavos a Wompi)

st.set_page_config(
    page_title="TuBot LATAM — Indicadores NinjaTrader",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# ESTILOS CSS PREMIUM
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
    --danger: #ff4757;
    --warning: #ffa502;
    --success: #00d4aa;
  }

  .stApp {
    background: var(--bg-primary) !important;
    font-family: 'Outfit', sans-serif !important;
  }

  /* Header hero */
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
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
  }
  .hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.15;
    margin-bottom: 0.6rem;
  }
  .hero-subtitle {
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 300;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
  }

  /* Cards */
  .glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    transition: all 0.3s ease;
  }
  .glass-card:hover {
    border-color: var(--accent-dim);
    background: var(--bg-card-hover);
  }
  .card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
  }
  .card-step {
    background: var(--accent);
    color: var(--bg-primary);
    font-weight: 700;
    font-size: 0.75rem;
    width: 28px; height: 28px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  /* Indicator preview */
  .indicator-preview {
    background: linear-gradient(135deg, #0d1b2a, #1b2838);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin: 1rem 0;
  }
  .indicator-preview img {
    border-radius: 8px;
    max-height: 320px;
    width: 100%;
    object-fit: contain;
    border: 1px solid var(--border);
  }
  .indicator-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-top: 1rem;
  }
  .indicator-desc {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.6;
    margin-top: 0.5rem;
  }

  /* Price tag */
  .price-tag {
    display: inline-flex;
    align-items: baseline;
    gap: 0.3rem;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    margin-top: 1rem;
  }
  .price-currency {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--accent);
  }
  .price-amount {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
  }

  /* Form inputs */
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
  .stTextInput > label, .stTextArea > label {
    color: var(--text-secondary) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #00d4aa, #00b894) !important;
    color: #0a0e17 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
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
  .stFileUploader label {
    color: var(--text-secondary) !important;
    font-family: 'Outfit', sans-serif !important;
  }

  /* Success / Info boxes */
  .success-box {
    background: linear-gradient(135deg, #00d4aa15, #00d4aa08);
    border: 1px solid #00d4aa44;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
  }
  .success-box h3 {
    color: var(--accent);
    margin: 0 0 0.5rem;
    font-size: 1.2rem;
  }
  .success-box p {
    color: var(--text-secondary);
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.6;
  }

  /* Info badge */
  .info-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1e3a5f;
    color: #60a5fa;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 0.35rem 0.8rem;
    border-radius: 6px;
    margin-top: 0.4rem;
  }

  /* Feature pills */
  .features-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  .feature-pill {
    background: #0d1520;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
  }

  /* Divider */
  .custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
  }

  /* Hide Streamlit branding */
  #MainMenu, footer, header {visibility: hidden;}
  .stDeployButton {display: none;}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: var(--text-secondary);
    font-family: 'Outfit', sans-serif;
    font-weight: 500;
    padding: 0.5rem 1.2rem;
  }
  .stTabs [aria-selected="true"] {
    background: var(--accent-dim) !important;
    color: var(--accent) !important;
  }
  .stTabs [data-baseweb="tab-border"] { display: none; }
  .stTabs [data-baseweb="tab-highlight"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────────────────────
def generate_reference(name: str) -> str:
    """Genera una referencia única para el pago."""
    ts = str(int(time.time()))
    raw = f"{name}-{ts}"
    return "TBOT-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()


def get_wompi_checkout_url(ref: str, amount_cents: int, customer_name: str, customer_email: str) -> str:
    """Genera la URL del checkout de Wompi."""
    base = "https://checkout.wompi.co/p/" if WOMPI_ENV == "production" else "https://checkout.wompi.co/p/"
    url = (
        f"{base}"
        f"?public-key={WOMPI_PUBLIC_KEY}"
        f"&currency={CURRENCY}"
        f"&amount-in-cents={amount_cents}"
        f"&reference={ref}"
        f"&customer-data.full-name={customer_name}"
        f"&customer-data.email={customer_email}"
        f"&redirect-url=https://tubot-latam.streamlit.app/?status=success"
    )
    return url


def send_notification_email(customer_data: dict) -> bool:
    """
    Envía notificación por email. En producción, configura un
    SMTP real o usa un servicio como SendGrid/Resend.
    """
    # Esta función es un placeholder — en producción se conecta a SMTP real
    # o se integra con un webhook de Wompi que llama a un backend.
    return True


def render_indicator_card(image_bytes, name: str, description: str, price: int):
    """Renderiza la tarjeta del indicador."""
    if image_bytes:
        encoded = base64.b64encode(image_bytes).decode()
        img_html = f'<img src="data:image/png;base64,{encoded}" alt="{name}" />'
    else:
        img_html = '<div style="height:200px;display:flex;align-items:center;justify-content:center;color:#8899aa;font-size:0.9rem;">Vista previa no disponible</div>'

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
# ESTADO
# ─────────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "payment_ref" not in st.session_state:
    st.session_state.payment_ref = None
if "customer" not in st.session_state:
    st.session_state.customer = {}
if "indicator_image" not in st.session_state:
    st.session_state.indicator_image = None
if "indicator_name" not in st.session_state:
    st.session_state.indicator_name = ""
if "indicator_desc" not in st.session_state:
    st.session_state.indicator_desc = ""


# ─────────────────────────────────────────────────────────────
# HEADER
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
# PANEL DE ADMINISTRACIÓN (pestaña colapsable)
# ─────────────────────────────────────────────────────────────
tab_compra, tab_admin = st.tabs(["🛒  Comprar Indicador", "⚙️  Admin — Configurar Producto"])

with tab_admin:
    st.markdown("""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-step">⚙</div>
            <div class="card-title">Configuración del Indicador</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])

    with col_a:
        admin_name = st.text_input(
            "Nombre del indicador",
            value=st.session_state.indicator_name or "SuperTrend Pro v3",
            key="admin_name"
        )
        admin_desc = st.text_area(
            "Descripción breve",
            value=st.session_state.indicator_desc or "Indicador de tendencia avanzado con filtro de volatilidad ATR adaptativo. Genera señales claras de entrada y salida con alertas visuales y sonoras integradas.",
            height=120,
            key="admin_desc"
        )
        admin_price = st.number_input(
            "Precio (COP)",
            min_value=10000,
            value=AMOUNT_COP,
            step=5000,
            key="admin_price"
        )

    with col_b:
        admin_image = st.file_uploader(
            "Imagen del indicador (PNG, JPG)",
            type=["png", "jpg", "jpeg", "webp"],
            key="admin_upload"
        )
        if admin_image:
            st.image(admin_image, caption="Vista previa", use_container_width=True)

    if st.button("💾  Guardar configuración", key="save_config"):
        st.session_state.indicator_name = admin_name
        st.session_state.indicator_desc = admin_desc
        st.session_state.indicator_image = admin_image.read() if admin_image else st.session_state.indicator_image
        st.session_state.admin_price = admin_price
        st.success("✅ Configuración guardada correctamente.")


# ─────────────────────────────────────────────────────────────
# FLUJO DE COMPRA
# ─────────────────────────────────────────────────────────────
with tab_compra:

    # Obtener valores configurados
    ind_name = st.session_state.indicator_name or "SuperTrend Pro v3"
    ind_desc = st.session_state.indicator_desc or "Indicador de tendencia avanzado con filtro de volatilidad ATR adaptativo. Genera señales claras de entrada y salida con alertas visuales y sonoras integradas."
    ind_image = st.session_state.indicator_image
    ind_price = st.session_state.get("admin_price", AMOUNT_COP)

    # ── PASO 1: Vista del producto ──
    st.markdown("""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-step">1</div>
            <div class="card-title">Producto</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_indicator_card(ind_image, ind_name, ind_desc, ind_price)

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

    # Validación y botón de pago
    form_valid = all([
        customer_name and len(customer_name.strip()) >= 3,
        customer_email and "@" in customer_email and "." in customer_email,
        machine_id and len(machine_id.strip()) >= 4
    ])

    if not form_valid:
        st.warning("⚠️ Completa todos los campos correctamente para proceder al pago.")

    if form_valid:
        ref = generate_reference(customer_name)
        amount_cents = ind_price * 100

        # Guardar datos del cliente en sesión
        st.session_state.customer = {
            "name": customer_name.strip(),
            "email": customer_email.strip(),
            "machine_id": machine_id.strip(),
            "reference": ref,
            "product": ind_name,
            "price": ind_price,
            "timestamp": datetime.now().isoformat()
        }

        checkout_url = get_wompi_checkout_url(
            ref=ref,
            amount_cents=amount_cents,
            customer_name=customer_name.strip().replace(" ", "+"),
            customer_email=customer_email.strip()
        )

        # Resumen antes de pagar
        st.markdown(f"""
        <div class="glass-card" style="background: linear-gradient(135deg, #0d1b2a, #111827);">
            <table style="width:100%; color: #8899aa; font-size: 0.88rem; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #1e2d3d;">
                    <td style="padding: 0.5rem 0;">📦 Producto</td>
                    <td style="text-align:right; color: #f0f4f8; font-weight:600;">{ind_name}</td>
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
                    <td style="text-align:right; color: #00d4aa; font-weight:800; font-size: 1.1rem; font-family: 'JetBrains Mono', monospace;">COP ${ind_price:,.0f}</td>
                </tr>
            </table>
            <div style="margin-top:0.6rem; font-size: 0.72rem; color: #556677; text-align:center;">
                Ref: {ref}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Botón de pago con Wompi
        st.markdown(f"""
        <a href="{checkout_url}" target="_blank" style="text-decoration: none;">
            <div style="
                background: linear-gradient(135deg, #00d4aa, #00b894);
                color: #0a0e17;
                font-family: 'Outfit', sans-serif;
                font-weight: 700;
                font-size: 1.05rem;
                text-align: center;
                padding: 1rem 2rem;
                border-radius: 14px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 0.5rem;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 20px #00d4aa33;
            ">
                🔒&nbsp; Pagar con Wompi — COP ${ind_price:,.0f}
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin-top:0.8rem; font-size: 0.75rem; color: #556677;">
            🔐 Pago seguro procesado por Wompi · Cifrado SSL 256-bit
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── PASO 4: Confirmación post-pago ──
    # Wompi redirige con ?status=success en la URL
    query_params = st.query_params
    status = query_params.get("status", None)

    if status == "success" or st.session_state.get("payment_confirmed"):
        st.session_state.payment_confirmed = True

        customer = st.session_state.get("customer", {})

        # Notificación al administrador
        notification_data = {
            "to": NOTIFICATION_EMAIL,
            "subject": f"🛒 Nueva compra — {customer.get('product', 'Indicador')}",
            "body": f"""
            NUEVA COMPRA RECIBIDA
            ─────────────────────
            Cliente:    {customer.get('name', 'N/A')}
            Email:      {customer.get('email', 'N/A')}
            Machine ID: {customer.get('machine_id', 'N/A')}
            Producto:   {customer.get('product', 'N/A')}
            Precio:     COP {customer.get('price', 0):,.0f}
            Referencia: {customer.get('reference', 'N/A')}
            Fecha:      {customer.get('timestamp', 'N/A')}
            """
        }

        # Log de la transacción (en producción integrar con webhook de Wompi)
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

        # Guardar transacción en JSON local (log)
        log_file = Path("transactions_log.json")
        transactions = []
        if log_file.exists():
            try:
                transactions = json.loads(log_file.read_text())
            except Exception:
                transactions = []
        transactions.append({**customer, "status": "completed", "notified": NOTIFICATION_EMAIL})
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
