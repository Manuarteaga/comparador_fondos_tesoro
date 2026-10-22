import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Comparador Global de Deuda y Simulador Avanzado",
    page_icon="⚖️",
    layout="wide"
)

# Inicializar Session State para almacenar activos enviados a las carteras
if "custom_assets_a" not in st.session_state:
    st.session_state.custom_assets_a = []
if "custom_assets_b" not in st.session_state:
    st.session_state.custom_assets_b = []

st.title("⚖️ Evaluador Bursátil, Deuda Global y Simulador Avanzado de Carteras")
st.caption("Yahoo Finance en vivo | Estructura de Tarjetas por Categorías | Asignación en €")

st.divider()

# NAVEGACIÓN DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "🏢 Buscador, Semáforo & Alternativas", 
    "🌍 Comparador de Deuda & Monetarios", 
    "📊 Simulador Avanzado de Carteras (en €)"
])

# Base de datos global con ISIN, TER y Puntuación para imitar la interfaz de la foto
market_products = {
    "Vanguard S&P 500 ETF (VOO)": {"tipo": "ETF", "isin": "US9229083632", "ter": "0.03%", "rating": "4.9/5", "return": 8.0, "cat": "ETF"},
    "iShares Core S&P 500 ETF (IVV)": {"tipo": "ETF", "isin": "US4642872000", "ter": "0.03%", "rating": "4.9/5", "return": 8.0, "cat": "ETF"},
    "Vanguard FTSE All-World (Acc)": {"tipo": "Fondo", "isin": "IE00BK5BQT80", "ter": "0.22%", "rating": "4.8/5", "return": 7.5, "cat": "Acc"},
    "Amundi Prime Global UCITS ETF": {"tipo": "ETF", "isin": "LU1931974698", "ter": "0.05%", "rating": "4.7/5", "return": 7.4, "cat": "ETF"},
    "AXA Court Terme AC (Monetario)": {"tipo": "Monetario", "isin": "FR0000447823", "ter": "0.15%", "rating": "4.8/5", "return": 3.2, "cat": "Acc"},
    "Groupama Trésorerie IC (Monetario)": {"tipo": "Monetario", "isin": "FR0000989626", "ter": "0.12%", "rating": "4.8/5", "return": 3.3, "cat": "Acc"},
    "PIMCO Euro Short-Term Institutional": {"tipo": "Bonos", "isin": "IE00B11XZB05", "ter": "0.25%", "rating": "4.7/5", "return": 3.8, "cat": "Acc"},
    "Vanguard Global Bond Index Fund": {"tipo": "Bonos", "isin": "IE00B18GC888", "ter": "0.15%", "rating": "4.6/5", "return": 3.6, "cat": "Acc"}
}

# Extraer solo las rentabilidades para el simulador
asset_expectations = {name: data["return"] for name, data in market_products.items()}
asset_expectations["Invesco QQQ (Nasdaq 100)"] = 9.2

# =========================================================
# PESTAÑA 1: BUSCADOR LIBRE + SEMÁFORO + TARJETAS EN 3 COLUMNAS
# =========================================================
with tab1:
    st.header("🏢 Analizador de Salud Financiera & Alternativas Equivalentes")
    st.write("Busca cualquier empresa y descubre los fondos de acumulación, distribución y ETFs equivalentes organizados en tarjetas.")
    
    modo_busqueda = st.radio("Origen de la empresa:", ["Big Tech (Predefinidas)", "Buscador Libre por Ticker (Global)"], key="mod_b1")
    
    if modo_busqueda == "Big Tech (Predefinidas)":
        ticker_dict = {
            "Microsoft (MSFT)": "MSFT",
            "Alphabet / Google (GOOGL)": "GOOGL",
            "Meta (META)": "META",
            "Amazon (AMZN)": "AMZN",
            "Oracle (ORCL)": "ORCL",
            "Apple (AAPL)": "AAPL",
            "Nvidia (NVDA)": "NVDA"
        }
        selected_name = st.selectbox("Selecciona empresa:", list(ticker_dict.keys()))
        ticker_symbol = ticker_dict[selected_name]
    else:
        ticker_symbol = st.text_input("Introduce el Ticker de Yahoo Finance (ej. TSLA, SAN.MC, VOW.DE):", "TSLA").upper().strip()
    
    if ticker_symbol:
        with st.spinner(f"Consultando datos en tiempo real para {ticker_symbol}..."):
            try:
                ticker = yf.Ticker(ticker_symbol)
                cashflow = ticker.cashflow
                balance = ticker.balance_sheet
                
                fcf, capex, total_debt = None, None, None
                
                if cashflow is not None and not cashflow.empty:
                    if 'Free Cash Flow' in cashflow.index:
                        fcf = cashflow.loc['Free Cash Flow'].iloc[0]
                    if 'Capital Expenditure' in cashflow.index:
                        capex = abs(cashflow.loc['Capital Expenditure'].iloc[0])
                        
                if balance is not None and not balance.empty:
                    if 'Total Debt' in balance.index:
                        total_debt = balance.loc['Total Debt'].iloc[0]

                # Métricas
                m1, m2, m3 = st.columns(3)
                fcf_m = f"${fcf / 1e9:.2f} B" if fcf is not None else "No disponible"
                capex_m = f"${capex / 1e9:.2f} B" if capex is not None else "No disponible"
                debt_m = f"${total_debt / 1e9:.2f} B" if total_debt is not None else "No disponible"
                
                m1.metric("Flujo de Caja Libre (FCF)", fcf_m)
                m2.metric("Gasto de Capital (CapEx)", capex_m)
                m3.metric("Deuda Total", debt_m)
                
                # Semáforo
                st.markdown("---")
                st.subheader("🚦 Sistema de Semáforo de Riesgo")
                
                if fcf is not None and capex is not None:
                    if fcf < 0:
                        st.error("🔴 **ROJO (Riesgo Alto):** Caja libre negativa. Dependencia fuerte de emisión de deuda.")
                    elif fcf < capex:
                        st.warning("🟡 **AMARILLO (Precaución):** Positivo pero ajustado para cubrir todo el CapEx de inversiones.")
                    else:
                        st.success("🟢 **VERDE (Sólido):** Excelente generación de caja libre para autofinanciar crecimiento.")
                else:
                    st.info("Métricas insuficientes para establecer el semáforo automático con este ticker.")
                
                # Estructura de 3 columnas idéntica a tu imagen de referencia
                st.markdown("---")
                st.subheader(f"📦 Alternativas de Inversión Relacionadas con **{ticker_symbol}**")
                
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    st.markdown("### 📊 Fondos (Acumulación)")
                    st.markdown("• **Vanguard FTSE All-World (Acc)**")
                    st.caption("ISIN: `IE00BK5BQT80` | TER: **0.22%** | ⭐ **4.8/5**")
                    if st.button("➕ Añadir a Cartera A", key="btn_acc_a"):
                        st.session_state.custom_assets_a.append(("Vanguard FTSE All-World (MSCI World)", 1000.0))
                        st.success("¡Añadido!")

                    st.markdown("---")
                    st.markdown("• **Amundi Prime Global**")
                    st.caption("ISIN: `LU1931974698` | TER: **0.05%** | ⭐ **4.7/5**")
                    if st.button("➕ Añadir a Cartera B", key="btn_acc_b"):
                        st.session_state.custom_assets_b.append(("Amundi Prime Global UCITS ETF", 1000.0))
                        st.success("¡Añadido!")

                with col_c2:
                    st.markdown("### 💰 Fondos (Distribución)")
                    st.info("No hay fondos de distribución directos destacados en esta categoría para este activo.")

                with col_c3:
                    st.markdown("### 🌐 ETFs Equivalentes (Coste Bajo)")
                    st.markdown("• **Vanguard S&P 500 ETF (VOO)**")
                    st.caption("ISIN: `US9229083632` | TER: **0.03%** | ⭐ **4.9/5**")
                    if st.button("➕ Añadir a Cartera A", key="btn_etf_a"):
                        st.session_state.custom_assets_a.append(("Vanguard S&P 500 ETF (VOO)", 1000.0))
                        st.success("¡Añadido!")

                    st.markdown("---")
                    st.markdown("• **iShares Core S&P 500 (IVV)**")
                    st.caption("ISIN: `US4642872000` | TER: **0.03%** | ⭐ **4.9/5**")
                    if st.button("➕ Añadir a Cartera B", key="btn_etf_b"):
                        st.session_state.custom_assets_b.append(("iShares Core S&P 500 ETF (IVV)", 1000.0))
                        st.success("¡Añadido!")
                        
            except Exception as e:
                st.error(f"Error al recuperar datos para '{ticker_symbol}': {e}")

# =========================================================
# PESTAÑA 2: COMPARADOR DE DEUDA + MONETARIOS (ESTILO TARJETAS)
# =========================================================
with tab2:
    st.header("🌍 Comparador Global de Deuda & Fondos Monetarios / Renta Fija")
    st.write("Compara bonos soberanos y corporativos por plazos y consulta los fondos monetarios asociados en formato de tarjetas.")
    
    maturity = st.selectbox(
        "Selecciona la Temporalidad / Madurez del Bono:", 
        ["2 Años (Corto Plazo)", "5 Años (Medio Plazo)", "10 Años (Referencia Estándar)", "30 Años (Largo Plazo)"]
    )
    
    st.warning(
        "⚠️ **Aviso Importante sobre Plazos y Deuda:**\n\n"
        "• **Estados Unidos (EE.UU.):** Su referencia principal y más líquida es el bono a **10 años** (US 10Y Treasury), aunque emiten plazos de 2, 5 y 30 años.\n"
        "• **Europa / España / Alemania:** Tienen emisiones diversificadas en Letras a corto plazo (3-12 meses) y Bonos a 3, 5 y 10 años."
    )
    
    base_multiplier = {"2 Años (Corto Plazo)": 0.85, "5 Años (Medio Plazo)": 0.95, "10 Años (Referencia Estándar)": 1.0, "30 Años (Largo Plazo)": 1.08}
    mult = base_multiplier[maturity]
    
    yields_db = {
        "EE.UU. (Tesoro Soberano)": round(4.50 * mult, 2),
        "España (Bono Soberano)": round(3.15 * mult, 2),
        "Alemania (Bund Soberano)": round(2.30 * mult, 2),
        "Francia (OAT Soberano)": round(3.00 * mult, 2),
        "Japón (JGB Soberano)": round(0.95 * (mult * 0.8), 2),
        "Microsoft (Deuda Corporativa Grado A)": round(5.20 * mult, 2),
        "Oracle (Deuda Corporativa)": round(5.80 * mult, 2),
    }
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        emisor_a = st.selectbox("Emisor / País A:", list(yields_db.keys()), index=0, key="ema")
        yield_a = yields_db[emisor_a]
        st.metric(f"Interés ({maturity}) - {emisor_a}", f"{yield_a:.2f}%")
    with col_d2:
        emisor_b = st.selectbox("Emisor / País B:", list(yields_db.keys()), index=1, key="emb")
        yield_b = yields_db[emisor_b]
        st.metric(f"Interés ({maturity}) - {emisor_b}", f"{yield_b:.2f}%")
        
    st.markdown("---")
    diff = abs(yield_a - yield_b)
    bps = diff * 100
    if yield_a > yield_b:
        st.info(f"💡 **Diferencial:** **{emisor_a}** paga **{diff:.2f}% más** (+{bps:.0f} bps) que **{emisor_b}** al plazo de {maturity}.")
    elif yield_b > yield_a:
        st.info(f"💡 **Diferencial:** **{emisor_b}** paga **{diff:.2f}% más** (+{bps:.0f} bps) que **{emisor_a}** al plazo de {maturity}.")
    else:
        st.info("💡 Ambos ofrecen idéntica rentabilidad para este plazo.")
        
    # Tarjetas de Fondos Monetarios y de Bonos estilo tu imagen
    st.markdown("### 💰 Fondos Monetarios y de Bonos Recomendados")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.markdown("• **AXA Court Terme AC**")
        st.caption("ISIN: `FR0000447823` | TER: **0.15%** | ⭐ **4.8/5**")
        if st.button("➕ Añadir a Cartera A", key="btn_mon_a"):
            st.session_state.custom_assets_a.append(("Amundi Cash EUR (Fondo Monetario)", 2000.0))
            st.success("¡Añadido!")

    with col_m2:
        st.markdown("• **Groupama Trésorerie IC**")
        st.caption("ISIN: `FR0000989626` | TER: **0.12%** | ⭐ **4.8/5**")
        if st.button("➕ Añadir a Cartera B", key="btn_mon_b"):
            st.session_state.custom_assets_b.append(("Amundi Cash EUR (Fondo Monetario)", 2000.0))
            st.success("¡Añadido!")

    with col_m3:
        st.markdown("• **PIMCO Euro Short-Term**")
        st.caption("ISIN: `IE00B11XZB05` | TER: **0.25%** | ⭐ **4.7/5**")
        if st.button("➕ Añadir a Cartera B", key="btn_bon_b"):
            st.session_state.custom_assets_b.append(("Vanguard Global Bond Index Fund (Hedg)", 2000.0))
            st.success("¡Añadido!")

# =========================================================
# PESTAÑA 3: SIMULADOR AVANZADO DE CARTERAS (EN EUROS)
# =========================================================
with tab3:
    st.header("📊 Simulador Avanzado de Carteras con Importes en Euros (€)")
    st.write("Configura libremente cada cartera añadiendo los activos deseados mediante desplegables encadenados (Tipo de Activo -> Activo específico) e indicando la cantidad exacta en euros.")
    
    years = st.slider("Horizonte Temporal (Años):", min_value=1, max_value=10, value=5, key="slider_years")
    
    col_c1, col_c2 = st.columns(2)
    
    def calcular_cartera_en_euros(inversion_inicial, aportacion_mensual, lista_activos, anos):
        total_capital_inicial = sum([amt for _, amt in lista_activos])
        total_inicial_efectivo = inversion_inicial + total_capital_inicial
        
        if total_inicial_efectivo <= 0 and aportacion_mensual <= 0:
            return 0, 0, 0, 0
            
        if total_capital_inicial > 0:
            rent_ponderada = sum([ (amt / total_capital_inicial) * asset_expectations.get(activo, 5.0) for activo, amt in lista_activos ])
        else:
            rent_ponderada = 5.0
            
        r_mensual = (1 + rent_ponderada / 100) ** (1 / 12) - 1
        meses = anos * 12
        
        valor_actual = inversion_inicial + total_capital_inicial
        total_aportado = inversion_inicial + total_capital_inicial
        
        for _ in range(meses):
            valor_actual = (valor_actual + aportacion_mensual) * (1 + r_mensual)
            total_aportado += aportacion_mensual
            
        ganancia = valor_actual - total_aportado
        return valor_actual, total_aportado, ganancia, rent_ponderada

    with col_c1:
        st.subheader("💼 Cartera A")
        inv_ini_a = st.number_input("Inversión Inicial Base Cartera A (€):", value=5000.0, step=500.0, key="ini_a_n")
        apo_mes_a = st.number_input("Aportación Mensual Cartera A (€):", value=150.0, step=50.0, key="apo_a_n")
        
        st.markdown("**Activos en Cartera A:**")
        if st.session_state.custom_assets_a:
            for idx, (act, amt) in enumerate(st.session_state.custom_assets_a):
                col_item1, col_item2, col_item3 = st.columns([3, 2, 1])
                col_item1.write(f"• {act}")
                new_amt = col_item2.number_input(f"€", value=float(amt), key=f"amt_a_{idx}", label_visibility="collapsed")
                st.session_state.custom_assets_a[idx] = (act, new_amt)
                if col_item3.button("🗑️", key=f"del_a_{idx}"):
                    st.session_state.custom_assets_a.pop(idx)
                    st.rerun()
        else:
            st.info("Sin activos específicos. Añade abajo o desde las pestañas 1 y 2.")
            
        # Desplegables encadenados para añadir activo con botón
        with st.form("form_add_a", clear_on_submit=True):
            st.markdown("➕ **Añadir Activo (Cartera A):**")
            tipo_activo_a = st.selectbox("1. Tipo de Activo", ["Fondo Indexado", "ETF", "Fondo Monetario", "Bonos"], key="tipo_a_sel")
            
            # Filtrar opciones según el tipo seleccionado
            if tipo_activo_a in ["Fondo Indexado", "ETF"]:
                opciones_filtradas = [k for k, v in market_products.items() if v["tipo"] in ["Fondo", "ETF"]]
            elif tipo_activo_a == "Fondo Monetario":
                opciones_filtradas = [k for k, v in market_products.items() if v["tipo"] == "Monetario"]
            else:
                opciones_filtradas = [k for k, v in market_products.items() if v["tipo"] == "Bonos"]
                
            if not opciones_filtradas:
                opciones_filtradas = list(market_products.keys())
                
            activo_sel_a = st.selectbox("2. Seleccionar Activo", opciones_filtradas, key="act_a_sel")
            monto_sel_a = st.number_input("3. Cantidad en Euros (€)", value=1000.0, step=100.0, key="monto_a_in")
            
            submitted_a = st.form_submit_button("Añadir a Cartera A")
            if submitted_a:
                st.session_state.custom_assets_a.append((activo_sel_a, monto_sel_a))
                st.rerun()
                
        val_fin_a, tot_aport_a, gan_a, rent_p_a = calcular_cartera_en_euros(inv_ini_a, apo_mes_a, st.session_state.custom_assets_a, years)

    with col_c2:
        st.subheader("💼 Cartera B")
        inv_ini_b = st.number_input("Inversión Inicial Base Cartera B (€):", value=5000.0, step=500.0, key="ini_b_n")
        apo_mes_b = st.number_input("Aportación Mensual Cartera B (€):", value=150.0, step=50.0, key="apo_b_n")
        
        st.markdown("**Activos en Cartera B:**")
        if st.session_state.custom_assets_b:
            for idx, (act, amt) in enumerate(st.session_state.custom_assets_b):
                col_item1, col_item2, col_item3 = st.columns([3, 2, 1])
                col_item1.write(f"• {act}")
                new_amt = col_item2.number_input(f"€", value=float(amt), key=f"amt_b_{idx}", label_visibility="collapsed")
                st.session_state.custom_assets_b[idx] = (act, new_amt)
                if col_item3.button("🗑️", key=f"del_b_{idx}"):
                    st.session_state.custom_assets_b.pop(idx)
                    st.rerun()
        else:
            st.info("Sin activos específicos. Añade abajo o desde las pestañas 1 y 2.")
            
        with st.form("form_add_b", clear_on_submit=True):
            st.markdown("➕ **Añadir Activo (Cartera B):**")
            tipo_activo_b = st.selectbox("1. Tipo de Activo", ["Fondo Indexado", "ETF", "Fondo Monetario", "Bonos"], key="tipo_b_sel")
            
            if tipo_activo_b in ["Fondo Indexado", "ETF"]:
                opciones_filtradas_b = [k for k, v in market_products.items() if v["tipo"] in ["Fondo", "ETF"]]
            elif tipo_activo_b == "Fondo Monetario":
                opciones_filtradas_b = [k for k, v in market_products.items() if v["tipo"] == "Monetario"]
            else:
                opciones_filtradas_b = [k for k, v in market_products.items() if v["tipo"] == "Bonos"]
                
            if not opciones_filtradas_b:
                opciones_filtradas_b = list(market_products.keys())
                
            activo_sel_b = st.selectbox("2. Seleccionar Activo", opciones_filtradas_b, key="act_b_sel")
            monto_sel_b = st.number_input("3. Cantidad en Euros (€)", value=1000.0, step=100.0, key="monto_b_in")
            
            submitted_b = st.form_submit_button("Añadir a Cartera B")
            if submitted_b:
                st.session_state.custom_assets_b.append((activo_sel_b, monto_sel_b))
                st.rerun()
                
        val_fin_b, tot_aport_b, gan_b, rent_p_b = calcular_cartera_en_euros(inv_ini_b, apo_mes_b, st.session_state.custom_assets_b, years)

    st.markdown("---")
    st.subheader(f"📈 Resultados Comparativos al Término de {years} Años")
    
    res_a1, res_a2 = st.columns(2)
    with res_a1:
        st.markdown("### Cartera A")
        st.metric("Rentabilidad Anual Media Ponderada", f"{rent_p_a:.2f}%")
        st.metric("Capital Total Aportado", f"{tot_aport_a:,.2f} €")
        st.metric("Valor Final Estimado", f"{val_fin_a:,.2f} €", delta=f"+{gan_a:,.2f} € Netos")
        
    with res_a2:
        st.markdown("### Cartera B")
        st.metric("Rentabilidad Anual Media Ponderada", f"{rent_p_b:.2f}%")
        st.metric("Capital Total Aportado", f"{tot_aport_b:,.2f} €")
        st.metric("Valor Final Estimado", f"{val_fin_b:,.2f} €", delta=f"+{gan_b:,.2f} € Netos")
        
    st.markdown("---")
    diff_final = abs(val_fin_a - val_fin_b)
    if val_fin_a > val_fin_b:
        st.success(f"🏆 **La Cartera A** acumula un valor superior por **{diff_final:,.2f} €** frente a la Cartera B tras {years} años.")
    elif val_fin_b > val_fin_a:
        st.success(f"🏆 **La Cartera B** acumula un valor superior por **{diff_final:,.2f} €** frente a la Cartera A tras {years} años.")
    else:
        st.info("Ambas carteras obtienen exactamente el mismo resultado final.")
