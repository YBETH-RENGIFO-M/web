# 📊 TuBot LATAM — Venta de Indicadores NinjaTrader

App profesional de Streamlit para vender indicadores de NinjaTrader con integración de pagos Wompi.

---

## 🚀 Instalación Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ⚙️ Configuración Importante

### 1. Clave de Wompi
Edita `app.py` y reemplaza la variable `WOMPI_PUBLIC_KEY` con tu clave pública real:

```python
WOMPI_PUBLIC_KEY = "pub_prod_TU_CLAVE_REAL_AQUI"
WOMPI_ENV = "production"  # Cambiar de "sandbox" a "production"
```

### 2. Precio del indicador
Modifica `AMOUNT_COP` o usa el panel Admin dentro de la app para cambiar el precio dinámicamente.

### 3. Notificación por email
La app registra cada transacción en `transactions_log.json`. Para notificación automática por email al completar el pago, tienes dos opciones:

**Opción A — Webhook de Wompi (RECOMENDADA):**
Configura un webhook en tu dashboard de Wompi que apunte a un endpoint backend (puede ser una Cloud Function, AWS Lambda, etc.) que envíe el email a `tubotlatam@gmail.com` cuando el evento sea `transaction.updated` con estado `APPROVED`.

**Opción B — SendGrid / Resend:**
Integra un servicio de email transaccional en la función `send_notification_email()` del archivo `app.py`.

### 4. URL de redirección
Cambia la `redirect-url` en la función `get_wompi_checkout_url()` para que apunte a tu dominio real de Streamlit Cloud:

```python
f"&redirect-url=https://TU-APP.streamlit.app/?status=success"
```

---

## 📋 Flujo del Cliente

1. **Ve el producto** — imagen, descripción y precio del indicador
2. **Ingresa sus datos** — nombre, email y Machine ID de NinjaTrader
3. **Paga con Wompi** — checkout seguro con tarjeta, PSE, Nequi, etc.
4. **Recibe confirmación** — mensaje de éxito + notificación al admin
5. **Activación en <24h** — el equipo contacta al cliente para activar la licencia

---

## 🛡️ Seguridad

- Los pagos son procesados directamente por Wompi (PCI DSS compliant)
- La app nunca almacena datos de tarjetas
- Las transacciones se registran localmente en JSON para auditoría
- Se recomienda usar HTTPS en producción (Streamlit Cloud lo incluye)

---

## 📁 Estructura

```
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── transactions_log.json  # Log de transacciones (se crea automáticamente)
└── README.md           # Este archivo
```

---

## 🌐 Deploy en Streamlit Cloud

1. Sube el proyecto a un repo de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo y selecciona `app.py`
4. ¡Listo! Tu tienda estará en línea

---

© 2026 TuBot LATAM
