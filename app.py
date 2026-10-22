import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Comparador Global de Deuda y Carteras Avanzado",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Evaluador Bursátil, Deuda Global y Simulador de Carteras")
st.caption("Yahoo Finance en vivo | Selector de Plazos de Deuda | Simulador con Aportaciones Mensuales")

st.divider()

# NAVEGACIÓN DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "🏢 Buscador & Semáforo Financiero (Yahoo Finance)", 
    "🌍 Comparador Global de Deuda (Por Plazos)", 
    "📊 Simulador Avanzado de Carteras"
])

# =========================================================
# PESTAÑA 1: BUSCADOR LIBRE + SEMÁFORO FINANCIERO
# =========================================================
with tab1:
    st.header("🏢 Analizador de Salud Financiera de Cualquier Empresa")
    st.write("Consulta los datos oficiales extraídos de Yahoo Finance para cualquier compañía del mundo y su semáforo de riesgo.")
    
    modo_busqueda = st.radio("Selecciona el origen de la empresa:", ["Big Tech (Predefinidas)", "Buscador Libre por Ticker (Global)"])
    
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
        ticker_symbol = st.text_input("Introduce el Ticker de Yahoo Finance (ej. TSLA, SAN.MC, VOW.DE, 005930.KS):", "TSLA").upper().strip()
    
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

                # Métricas principales
                m1, m2, m3 = st.columns(3)
                fcf_m = f"${fcf / 1e9:.2f} B" if fcf is not None else "No disponible"
                capex_m = f"${capex / 1e9:.2f} B" if capex is not None else "No disponible"
                debt_m = f"${total_debt / 1e9:.2f} B" if total_debt is not None else "No disponible"
                
                m1.metric("Flujo de Caja Libre (FCF)", fcf_m)
                m2.metric("Gasto de Capital (CapEx)", capex_m)
                m3.metric("Deuda Total", debt_m)
                
                # Sistema de Semáforo
                st.markdown("---")
                st.subheader("🚦 Sistema de Semáforo de Riesgo")
                
                if fcf is not None and capex is not None:
                    if fcf < 0:
                        st.error("🔴 **ROJO (Riesgo Alto):** Caja libre negativa. La empresa quema más efectivo del que ingresa de forma operativa y depende fuertemente de emitir deuda.")
                    elif fcf < capex:
                        st.warning("🟡 **AMARILLO (Precaución):** El flujo de caja es positivo pero insuficiente para cubrir todo el CapEx de inversiones sin apretarse el cinturón.")
                    else:
                        st.success("🟢 **VERDE (Sólido):** Excelente generación de caja libre. Autopista financiera para cubrir inversiones y deuda holgadamente.")
                else:
                    st.info("No se pudieron calcular suficientes métricas detalladas para establecer el semáforo con este ticker.")
                    
            except Exception as e:
                st.error(f"No se pudieron recuperar datos para '{ticker_symbol}'. Comprueba que el ticker sea correcto en Yahoo Finance. Detalle: {e}")

# =========================================================
# PESTAÑA 2: COMPARADOR GLOBAL DE DEUDA CON PLAZOS
# =========================================================
with tab2:
    st.header("🌍 Comparador de Deuda Global por Plazos y Madurez")
    st.write("Consulta y compara los rendimientos de bonos soberanos y corporativos ajustando la temporalidad.")
    
    # Selector de temporalidad / madurez
    maturity = st.selectbox(
        "Selecciona la Temporalidad / Madurez del Bono:", 
        ["2 Años (Corto Plazo)", "5 Años (Medio Plazo)", "10 Años (Referencia Estándar)", "30 Años (Largo Plazo)"]
    )
    
    # Aviso explicativo sobre bonos de EE.UU. y otros países
    st.warning(
        "⚠️ **Aviso Importante sobre Plazos y Deuda:**\n\n"
        "• **Estados Unidos (EE.UU.):** Su referencia principal, más líquida y negociada a nivel mundial es el bono a **10 años** (US 10Y Treasury), aunque emiten letras a 1 mes y bonos de 2, 5 y 30 años.\n"
        "• **Europa / España / Alemania:** Tienen una estructura de emisiones muy diversificada que incluye Letras del Tesoro a Corto Plazo (3, 6, 9 y 12 meses) y Bonos/Obligaciones a 3, 5, 10 y 15+ años. Los plazos cortos en Europa han ofrecido históricamente rentabilidades distintas según los tipos del BCE."
    )
    
    # Base de datos simulada orientativa según el plazo seleccionado
    # (Ajusta la lógica de rendimientos según madurez)
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
        "ASML / Tech Europa (Corporativa)": round(3.80 * mult, 2),
    }
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        emisor_a = st.selectbox("Emisor / País A:", list(yields_db.keys()), index=0)
        yield_a = yields_db[emisor_a]
        st.metric(f"Interés ({maturity}) - {emisor_a}", f"{yield_a:.2f}%")
        
    with col_d2:
        emisor_b = st.selectbox("Emisor / País B:", list(yields_db.keys()), index=1)
        yield_b = yields_db[emisor_b]
        st.metric(f"Interés ({maturity}) - {emisor_b}", f"{yield_b:.2f}%")
        
    st.markdown("---")
    diff = abs(yield_a - yield_b)
    bps = diff * 100
    if yield_a > yield_b:
        st.info(f"💡 **Diferencial:** **{emisor_a}** paga **{diff:.2f}% más** (+{bps:.0f} puntos básicos) que **{emisor_b}** al plazo de {maturity}.")
    elif yield_b > yield_a:
        st.info(f"💡 **Diferencial:** **{emisor_b}** paga **{diff:.2f}% más** (+{bps:.0f} puntos básicos) que **{emisor_a}** al plazo de {maturity}.")
    else:
        st.info("💡 Ambos ofrecen idéntica rentabilidad para este plazo.")

# =========================================================
# PESTAÑA 3: COMPARADOR AVANZADO DE CARTERAS (MENSUAL + ACTIVOS)
# =========================================================
with tab3:
    st.header("📊 Simulador Avanzado de Carteras con Aportaciones Mensuales")
    st.write("Configura dos carteras añadiendo diferentes tipos de activos (S&P 500, MSCI World, Fondos Monetarios, Bonos) con inversión inicial y aportaciones periódicas.")
    
    years = st.slider("Horizonte Temporal (Años):", min_value=1, max_value=10, value=5)
    
    # Rentabilidades estimadas anuales por categoría de activo
    asset_expectations = {
        "S&P 500 (ETF / Fondo Indexado)": 8.0,
        "MSCI World (Renta Variable Global)": 7.5,
        "Fondos Europeos (Stoxx 600)": 5.5,
        "Fondo Monetario (Liquidez / Corto Plazo)": 3.2,
        f"Deuda / Bonos Seleccionados ({emisor_a})": yield_a
    }
    
    col_c1, col_c2 = st.columns(2)
    
    def calcular_cartera_compuesta(inversion_inicial, aportacion_mensual, items_activos, anos):
        # items_activos es una lista de tuplas: (nombre_activo, porcentaje)
        # Aseguramos que los porcentajes sumen 100
        total_p = sum([p for _, p in items_activos])
        if total_p <= 0:
            return 0, 0
        
        # Rentabilidad ponderada anual
        rent_ponderada = sum([ (p / total_p) * asset_expectations[activo] for activo, p in items_activos ])
        r_mensual = (1 + rent_ponderada / 100) ** (1 / 12) - 1
        
        meses = anos * 12
        valor_actual = inversion_inicial
        total_aportado = inversion_inicial
        
        for _ in range(meses):
            valor_actual = (valor_actual + aportacion_mensual) * (1 + r_mensual)
            total_aportado += aportacion_mensual
            
        ganancia = valor_actual - total_aportado
        return valor_actual, total_aportado, ganancia, rent_ponderada

    with col_c1:
        st.subheader("💼 Cartera A")
        inv_ini_a = st.number_input("Inversión Inicial Cartera A (€):", value=10000.0, step=1000.0, key="ini_a")
        apo_mes_a = st.number_input("Aportación Mensual Cartera A (€):", value=200.0, step=50.0, key="apo_a")
        
        st.markdown("**Composición de Activos (Cartera A):**")
        act_1_a = st.selectbox("Activo 1 (Cartera A):", list(asset_expectations.keys()), index=0, key="a1")
        pct_1_a = st.slider("Peso Activo 1 (%):", 0, 100, 50, key="p1_a")
        
        act_2_a = st.selectbox("Activo 2 (Cartera A):", list(asset_expectations.keys()), index=3, key="a2")
        pct_2_a = 100 - pct_1_a
        st.info(f"Asignado automáticamente: {pct_2_a}% para **{act_2_a}** (Suma total: 100%)")
        
        items_a = [(act_1_a, pct_1_a), (act_2_a, pct_2_a)]
        val_fin_a, tot_aport_a, gan_a, rent_p_a = calcular_cartera_compuesta(inv_ini_a, apo_mes_a, items_a, years)

    with col_c2:
        st.subheader("💼 Cartera B")
        inv_ini_b = st.number_input("Inversión Inicial Cartera B (€):", value=10000.0, step=1000.0, key="ini_b")
        apo_mes_b = st.number_input("Aportación Mensual Cartera B (€):", value=200.0, step=50.0, key="apo_b")
        
        st.markdown("**Composición de Activos (Cartera B):**")
        act_1_b = st.selectbox("Activo 1 (Cartera B):", list(asset_expectations.keys()), index=1, key="b1")
        pct_1_b = st.slider("Peso Activo 1 (%):", 0, 100, 20, key="p1_b")
        
        act_2_b = st.selectbox("Activo 2 (Cartera B):", list(asset_expectations.keys()), index=4, key="b2")
        pct_2_b = 100 - pct_1_b
        st.info(f"Asignado automáticamente: {pct_2_b}% para **{act_2_b}** (Suma total: 100%)")
        
        items_b = [(act_1_b, pct_1_b), (act_2_b, pct_2_b)]
        val_fin_b, tot_aport_b, gan_b, rent_p_b = calcular_cartera_compuesta(inv_ini_b, apo_mes_b, items_b, years)

    st.markdown("---")
    st.subheader(f"📈 Resultados Comparativos al Término de {years} Años")
    
    res_a1, res_a2 = st.columns(2)
    
    with res_a1:
        st.markdown("### Cartera A")
        st.metric("Rentabilidad Anual Media Ponderada", f"{rent_p_a:.2f}%")
        st.metric("Capital Total Aportado", f"{tot_aport_a:,.2f} €")
        st.metric(f"Valor Final Estimado", f"{val_fin_a:,.2f} €", delta=f"+{gan_a:,.2f} € de Beneficio Netos")
        
    with res_a2:
        st.markdown("### Cartera B")
        st.metric("Rentabilidad Anual Media Ponderada", f"{rent_p_b:.2f}%")
        st.metric("Capital Total Aportado", f"{tot_aport_b:,.2f} €")
        st.metric(f"Valor Final Estimado", f"{val_fin_b:,.2f} €", delta=f"+{gan_b:,.2f} € de Beneficio Netos")
        
    st.markdown("---")
    diff_final = abs(val_fin_a - val_fin_b)
    if val_fin_a > val_fin_b:
        st.success(py := f"🏆 **La Cartera A** acumula un valor total superior por **{diff_final:,.2f} €** frente a la Cartera B al cabo de {years} años.")
    elif val_fin_b > val_fin_a:
        st.success(py := f"🏆 **La Cartera B** acumula un valor total superior por **{diff_final:,.2f} €** frente a la Cartera A al cabo de {years} años.")
    else:
        st.info("Ambas carteras obtienen exactamente el mismo resultado final.")
