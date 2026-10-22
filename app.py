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

# Inicializar Session State para almacenar activos enviados desde Tab 1 y Tab 2
if "custom_assets_a" not in st.session_state:
    st.session_state.custom_assets_a = []
if "custom_assets_b" not in st.session_state:
    st.session_state.custom_assets_b = []

st.title("⚖️ Evaluador Bursátil, Deuda Global y Simulador Avanzado de Carteras")
st.caption("Yahoo Finance en vivo | Explorador de Fondos/ETFs/Bonos | Asignación en €")

st.divider()

# NAVEGACIÓN DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "🏢 Buscador, Semáforo & Fondos Asociados", 
    "🌍 Comparador de Deuda & Fondos Monetarios", 
    "📊 Simulador Avanzado de Carteras (en €)"
])

# Base de datos de rentabilidades estimadas anuales por activo
asset_expectations = {
    "Vanguard S&P 500 ETF (VOO)": 8.0,
    "iShares Core S&P 500 ETF (IVV)": 8.0,
    "Vanguard FTSE All-World (MSCI World)": 7.5,
    "Invesco QQQ (Nasdaq 100 - Tech)": 9.2,
    "Amundi Cash EUR (Fondo Monetario)": 3.2,
    "Vanguard Global Short-Term Corporate Bond": 4.1,
    "Vanguard Global Bond Index Fund (Hedg)": 3.8,
    "iShares Euro Government Bond ETF": 3.1,
    "Fondo Monetario Lyxor / Amundi EUR": 3.3
}

# =========================================================
# PESTAÑA 1: BUSCADOR LIBRE + SEMÁFORO + FONDOS ASOCIADOS
# =========================================================
with tab1:
    st.header("🏢 Analizador de Salud Financiera & Fondos Asociados")
    st.write("Busca cualquier empresa y descubre en qué grandes fondos e índices principales aparece para llevarlos al simulador.")
    
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
                
                # Relación de Fondos / ETFs donde suele aparecer
                st.markdown("---")
                st.subheader(f"📦 Fondos Indexados y ETFs donde aparece **{ticker_symbol}**")
                st.write("Añade estos vehículos directamente a tu simulador avanzado de carteras:")
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    if st.button("➕ Añadir 'Vanguard S&P 500 ETF (VOO)' a Cartera A"):
                        st.session_state.custom_assets_a.append(("Vanguard S&P 500 ETF (VOO)", 1000.0))
                        st.success("¡Añadido a Cartera A!")
                    if st.button("➕ Añadir 'Vanguard FTSE All-World' a Cartera A"):
                        st.session_state.custom_assets_a.append(("Vanguard FTSE All-World (MSCI World)", 1000.0))
                        st.success("¡Añadido a Cartera A!")
                with col_f2:
                    if st.button("➕ Añadir 'Invesco QQQ (Nasdaq)' a Cartera B"):
                        st.session_state.custom_assets_b.append(("Invesco QQQ (Nasdaq 100 - Tech)", 1000.0))
                        st.success("¡Añadido a Cartera B!")
                    if st.button("➕ Añadir 'iShares Core S&P 500' a Cartera B"):
                        st.session_state.custom_assets_b.append(("iShares Core S&P 500 ETF (IVV)", 1000.0))
                        st.success("¡Añadido a Cartera B!")
                        
            except Exception as e:
                st.error(f"Error al recuperar datos para '{ticker_symbol}': {e}")

# =========================================================
# PESTAÑA 2: COMPARADOR DE DEUDA + FONDOS MONETARIOS / BONOS
# =========================================================
with tab2:
    st.header("🌍 Comparador Global de Deuda & Selección de Fondos Monetarios")
    st.write("Compara bonos soberanos y corporativos por plazos y encuentra los fondos monetarios o de renta fija asociados.")
    
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
        
    # Relación de fondos monetarios y bonos para añadir al simulador
    st.markdown("### 💰 Fondos Monetarios y de Bonos donde encontrar estos rendimientos")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("➕ Añadir 'Amundi Cash EUR (Monetario)' a Cartera A"):
            st.session_state.custom_assets_a.append(("Amundi Cash EUR (Fondo Monetario)", 2000.0))
            st.success("¡Monetario añadido a Cartera A!")
    with col_b2:
        if st.button("➕ Añadir 'Vanguard Global Bond Index' a Cartera B"):
            st.session_state.custom_assets_b.append(("Vanguard Global Bond Index Fund (Hedg)", 2000.0))
            st.success("¡Fondo de bonos añadido a Cartera B!")

# =========================================================
# PESTAÑA 3: SIMULADOR AVANZADO DE CARTERAS (EN EUROS)
# =========================================================
with tab3:
    st.header("📊 Simulador Avanzado de Carteras con Importes en Euros (€)")
    st.write("Configura libremente cada cartera añadiendo los activos que desees, indicando la cantidad exacta en euros y tus aportaciones periódicas.")
    
    years = st.slider("Horizonte Temporal (Años):", min_value=1, max_value=10, value=5, key="slider_years")
    
    col_c1, col_c2 = st.columns(2)
    
    def calcular_cartera_en_euros(inversion_inicial, aportacion_mensual, lista_activos, anos):
        # lista_activos es una lista de tuplas/diccionarios: (nombre_activo, cantidad_euros)
        total_capital_inicial = sum([amt for _, amt in lista_activos])
        total_inicial_efectivo = inversion_inicial + total_capital_inicial
        
        if total_inicial_efectivo <= 0 and aportacion_mensual <= 0:
            return 0, 0, 0, 0
            
        # Rentabilidad ponderada basada en los euros asignados a cada activo
        if total_capital_inicial > 0:
            rent_ponderada = sum([ (amt / total_capital_inicial) * asset_expectations.get(activo, 5.0) for activo, amt in lista_activos ])
        else:
            rent_ponderada = 5.0 # Valor por defecto si no hay activos definidos
            
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
        
        st.markdown("**Activos añadidos en Cartera A:**")
        # Mostrar los que vienen de session_state o permitir añadir nuevos
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
            st.info("No hay activos específicos añadidos todavía. Usa el botón inferior o ven de las pestañas 1 y 2.")
            
        # Botón para añadir un nuevo activo manualmente en Cartera A
        with st.form("form_add_a", clear_on_submit=True):
            st.markdown("➕ **Añadir nuevo activo a Cartera A:**")
            tipo_sel_a = st.selectbox("Tipo de Activo", ["Fondo Indexado", "ETF", "Fondo Monetario", "Bono"], key="tipo_a")
            activo_sel_a = st.selectbox("Seleccionar Activo Específico", list(asset_expectations.keys()), key="act_sel_a")
            monto_sel_a = st.number_input("Cantidad en Euros (€)", value=1000.0, step=100.0, key="monto_a")
            submitted_a = st.form_submit_button("Añadir Activo")
            if submitted_a:
                st.session_state.custom_assets_a.append((activo_sel_a, monto_sel_a))
                st.rerun()
                
        val_fin_a, tot_aport_a, gan_a, rent_p_a = calcular_cartera_en_euros(inv_ini_a, apo_mes_a, st.session_state.custom_assets_a, years)

    with col_c2:
        st.subheader("💼 Cartera B")
        inv_ini_b = st.number_input("Inversión Inicial Base Cartera B (€):", value=5000.0, step=500.0, key="ini_b_n")
        apo_mes_b = st.number_input("Aportación Mensual Cartera B (€):", value=150.0, step=50.0, key="apo_b_n")
        
        st.markdown("**Activos añadidos en Cartera B:**")
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
            st.info("No hay activos específicos añadidos todavía. Usa el botón inferior o ven de las pestañas 1 y 2.")
            
        with st.form("form_add_b", clear_on_submit=True):
            st.markdown("➕ **Añadir nuevo activo a Cartera B:**")
            tipo_sel_b = st.selectbox("Tipo de Activo", ["Fondo Indexado", "ETF", "Fondo Monetario", "Bono"], key="tipo_b")
            activo_sel_b = st.selectbox("Seleccionar Activo Específico", list(asset_expectations.keys()), key="act_sel_b")
            monto_sel_b = st.number_input("Cantidad en Euros (€)", value=1000.0, step=100.0, key="monto_b")
            submitted_b = st.form_submit_button("Añadir Activo")
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
