import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import pytz
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
import os
import sys
from ml_payouts_analyzer_integrado import (
    DataProcessor,
    PressureGauge,
    FeatureEngineer,
    PrevisaoHistorico
)

# Configuração da página
st.set_page_config(
    page_title="Crazy Time A - Monitor de Grandes Payouts",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
    }
    .css-18e3th9 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .css-1d391kg {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .verde {
        color: #4CAF50;
    }
    .amarelo {
        color: #FFC107;
    }
    .vermelho {
        color: #F44336;
    }
    .azul {
        color: #2196F3;
    }
    .roxo {
        color: #9C27B0;
    }
    .card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .gauge-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
    }
    /* Estilo para o sidebar moderno */
    .css-1lcbmhc {
        background-color: #1E1E1E;
    }
    .css-1v3fvcr {
        background-color: #1E1E1E;
    }
    .css-1adrfps {
        background-color: #1E1E1E;
    }
    /* Separador fino para o sidebar */
    .css-hxt7ib {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Estilo para o slider - REMOVIDO FUNDO VERDE */
    .stSlider > div > div > div {
        background-color: #555555 !important;
    }
    .stSlider > div > div > div > div {
        background-color: #888888 !important;
    }
    /* Título do sidebar */
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        color: white;
        border-bottom: 1px solid #555555;
        padding-bottom: 10px;
    }
    /* Subtítulo do sidebar */
    .sidebar-subtitle {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #cccccc;
    }
    /* Container para o botão */
    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    /* Estilo para botões no sidebar */
    .sidebar-button {
        background-color: #333333;
        color: white;
        border: 1px solid #555555;
        border-radius: 8px;
        padding: 10px 15px;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 10px;
    }
    .sidebar-button:hover {
        background-color: #444444;
        border-color: #777777;
    }
    .sidebar-button-primary {
        background-color: #333333;
        border-color: #555555;
    }
    .sidebar-button-secondary {
        background-color: #333333;
        border-color: #555555;
    }
    /* Ajuste para valores do slider */
    .stSlider label {
        color: #cccccc !important;
    }
    /* Ajuste para texto do sidebar */
    .css-1adrfps label {
        color: #cccccc !important;
    }
    /* Estilo para o último resultado */
    .ultimo-resultado {
        font-weight: bold;
        color: #FFC107;
    }
    /* Estilo para recomendação */
    .recomendacao-apostar {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .recomendacao-nao-apostar {
        background-color: #F44336;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    .recomendacao-aguardar {
        background-color: #FFC107;
        color: black;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Função para criar o gauge chart
def criar_gauge_chart(valor, titulo):
    # Garantir que o valor não ultrapasse 100 para exibição no gauge
    valor_exibicao = min(100, valor)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor_exibicao,
        title={'text': titulo},
        number={'suffix': '%', 'valueformat': '.1f'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#888888"},  # Ponteiro cinza conforme solicitado
            'bgcolor': "gray",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 30], 'color': '#F44336'},
                {'range': [30, 60], 'color': '#FFC107'},
                {'range': [60, 80], 'color': '#4CAF50'},
                {'range': [80, 100], 'color': '#9C27B0'}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="#1E1E1E",
        font=dict(color="white", family="Arial")
    )
    
    return fig

# Função para obter cor baseada no valor
def obter_cor_gauge(valor):
    if valor < 30:
        return '#F44336'  # Vermelho
    elif valor < 60:
        return '#FFC107'  # Amarelo
    elif valor < 80:
        return '#4CAF50'  # Verde
    else:
        return '#9C27B0'  # Roxo

# Função para obter cor baseada no nível
def obter_cor_nivel(nivel):
    if nivel == "BAIXA" or nivel == "FRACA":
        return "vermelho"
    elif nivel == "MÉDIA" or nivel == "MODERADA":
        return "amarelo"
    elif nivel == "ALTA" or nivel == "FORTE":
        return "verde"
    else:  # MUITO ALTA ou MUITO FORTE
        return "roxo"

# Função para carregar histórico de previsões
def carregar_historico_previsoes():
    try:
        historico_manager = PrevisaoHistorico()
        historico = []
        
        for entrada in historico_manager.historico:
            historico.append({
                "data": entrada.get("timestamp", ""),
                "pressao": entrada.get("previsao", {}).get("pressao", 0),
                "probabilidade": entrada.get("previsao", {}).get("probabilidade_30min", 0) * 100,
                "confluencia": (entrada.get("previsao", {}).get("pressao", 0) + 
                               entrada.get("previsao", {}).get("probabilidade_30min", 0) * 100) / 2,
                "recomendacao": entrada.get("previsao", {}).get("recomendacao", "NÃO APOSTAR")
            })
        
        return historico
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {str(e)}")
    
    # Retornar histórico vazio em caso de erro
    return []

# Função para executar análise
def executar_analise():
    with st.spinner('Analisando dados do Crazy Time A...'):
        try:
            # Inicializar objetos
            data_processor = DataProcessor()
            pressure_gauge = PressureGauge()
            feature_engineer = FeatureEngineer()
            
            # Extrair e processar dados
            dados_brutos = data_processor.extrair_dados(limite=10000)
            df = data_processor.processar_dados(dados_brutos)
            
            # Calcular taxa de giros
            taxa_giros = 1.05  # Valor padrão
            
            # Calcular pressão do sistema
            pressao, detalhes_pressao = pressure_gauge.calcular_pressao(df)
            
            # Interpretar nível de pressão
            interpretacao = pressure_gauge.interpretar_pressao(pressao)
            nivel_pressao = interpretacao["nivel"]
            
            # Preparar dados para previsão ML
            X, y = feature_engineer.preparar_dados_ml(df)
            
            # Extrair últimos resultados e payouts
            ultimos_resultados = df.iloc[-5:]['resultado'].tolist()
            ultimos_payouts = df.iloc[-5:]['payout'].tolist()
            
            # Extrair último grande payout
            grandes_payouts = df[df['grande_payout'] == True]
            if not grandes_payouts.empty:
                ultimo_gp = grandes_payouts.iloc[-1]
                ultimo_gp_resultado = ultimo_gp['resultado']
                ultimo_gp_valor = ultimo_gp['payout']
                ultimo_gp_idx = df[df['data'] == ultimo_gp['data']].index[0]
                
                # Calcular tempo e giros desde o último grande payout
                tempo_desde_ultimo_gp = (df.iloc[-1]['data'] - ultimo_gp['data']).total_seconds() / 60
                giros_desde_ultimo_gp = len(df) - 1 - ultimo_gp_idx
            else:
                ultimo_gp_resultado = "Nenhum"
                ultimo_gp_valor = 0
                tempo_desde_ultimo_gp = 999
                giros_desde_ultimo_gp = 999
            
            # Verificar se houve pagamentos recentes significativos
            # Lógica corrigida: pagamentos pequenos não devem aumentar o gauge para 100%
            # Apenas pagamentos acima de 35.000 devem aumentar proporcionalmente
            pagamentos_recentes = df.iloc[-10:]['payout'].tolist()
            
            # Ajustar pressão com base nos pagamentos recentes
            pressao_ajustada = pressao
            for pagamento in pagamentos_recentes:
                if pagamento > 35000:
                    # Pagamentos grandes aumentam a pressão proporcionalmente
                    # Quanto maior o pagamento, maior o aumento
                    fator_aumento = (pagamento - 35000) / 10000  # Cada 10.000 acima de 35.000 aumenta o fator
                    pressao_ajustada += fator_aumento * 10  # Aumenta a pressão proporcionalmente
                elif pagamento > 10000 and pagamento <= 35000:
                    # Pagamentos médios têm efeito moderado
                    pressao_ajustada += 5
                else:
                    # Pagamentos pequenos têm efeito mínimo ou podem até reduzir a pressão
                    pressao_ajustada -= 1
            
            # Garantir que a pressão não fique negativa, mas pode ultrapassar 100%
            pressao_ajustada = max(0, pressao_ajustada)
            
            # Calcular probabilidade com base na pressão ajustada e outros fatores
            # Garantir que grandes pagamentos como 89.441,00 sejam refletidos corretamente
            probabilidade_base = 0
            
            # Verificar pagamentos grandes recentes (últimos 20 giros)
            pagamentos_recentes_20 = df.iloc[-20:]['payout'].tolist()
            for pagamento in pagamentos_recentes_20:
                if pagamento > 80000:  # Pagamentos muito grandes
                    probabilidade_base += 50
                elif pagamento > 50000:  # Pagamentos grandes
                    probabilidade_base += 30
                elif pagamento > 35000:  # Pagamentos significativos
                    probabilidade_base += 20
            
            # Ajuste baseado no tempo desde o último grande payout
            if tempo_desde_ultimo_gp and tempo_desde_ultimo_gp < 999:
                # Tempo ideal entre 30 e 60 minutos
                if 30 <= tempo_desde_ultimo_gp <= 60:
                    probabilidade_base += 15
                elif tempo_desde_ultimo_gp > 60:
                    probabilidade_base += 25
                elif tempo_desde_ultimo_gp < 15:
                    probabilidade_base -= 10  # Reduz se for muito recente
            
            # Ajuste baseado nos giros desde o último grande payout
            if giros_desde_ultimo_gp and giros_desde_ultimo_gp < 999:
                # Giros ideais entre 30 e 50
                if 30 <= giros_desde_ultimo_gp <= 50:
                    probabilidade_base += 15
                elif giros_desde_ultimo_gp > 50:
                    probabilidade_base += 25
                elif giros_desde_ultimo_gp < 15:
                    probabilidade_base -= 10  # Reduz se for muito recente
            
            # Adicionar componente da pressão ajustada
            probabilidade_base += pressao_ajustada * 0.3
            
            # Limitar a probabilidade entre 0 e 100
            probabilidade = max(0, min(100, probabilidade_base))
            
            # Calcular confluência dos indicadores
            confluencia = (pressao_ajustada + probabilidade) / 2
            
            # Interpretar nível de confluência
            if confluencia < 30:
                nivel_confluencia = "FRACA"
            elif confluencia < 60:
                nivel_confluencia = "MODERADA"
            elif confluencia < 80:
                nivel_confluencia = "FORTE"
            else:
                nivel_confluencia = "MUITO FORTE"
            
            # Verificar alinhamento entre indicadores
            diferenca = abs(pressao_ajustada - probabilidade)
            if diferenca < 10:
                alinhamento = "ALTO"
            elif diferenca < 20:
                alinhamento = "MÉDIO"
            else:
                alinhamento = "BAIXO"
            
            # Gerar recomendação final
            if confluencia >= 60 and alinhamento != "BAIXO":
                recomendacao_final = "APOSTAR"
                motivo = "Indicadores fortes e alinhados."
            else:
                recomendacao_final = "NÃO APOSTAR"
                motivo = "Indicadores fracos ou divergentes."
            
            # Calcular tempo estimado até próximo grande payout
            if probabilidade < 10:
                tempo_estimado = 30.0  # Valor padrão para probabilidade baixa
            else:
                # Quanto maior a probabilidade, menor o tempo estimado
                tempo_estimado = max(5, 30 * (1 - (probabilidade / 100)))
            
            # Calcular número estimado de giros
            giros_estimados = tempo_estimado * taxa_giros
            
            # Retornar resultados
            return {
                "ultimos_resultados": ultimos_resultados,
                "ultimos_payouts": ultimos_payouts,
                "ultimo_gp_resultado": ultimo_gp_resultado,
                "ultimo_gp_valor": ultimo_gp_valor,
                "tempo_desde_ultimo_gp": tempo_desde_ultimo_gp,
                "giros_desde_ultimo_gp": giros_desde_ultimo_gp,
                "pressao": pressao_ajustada,  # Usando a pressão ajustada
                "nivel_pressao": nivel_pressao,
                "probabilidade": probabilidade,
                "confluencia": confluencia,
                "nivel_confluencia": nivel_confluencia,
                "alinhamento": alinhamento,
                "recomendacao_final": recomendacao_final,
                "motivo": motivo,
                "tempo_estimado": tempo_estimado,
                "giros_estimados": giros_estimados,
                "taxa_giros": taxa_giros
            }
        except Exception as e:
            st.error(f"Erro na análise: {str(e)}")
            # Retornar valores padrão em caso de erro
            return {
                "ultimos_resultados": ["1", "1", "1", "1", "1"],
                "ultimos_payouts": [0, 0, 0, 0, 0],
                "ultimo_gp_resultado": "Erro",
                "ultimo_gp_valor": 0,
                "tempo_desde_ultimo_gp": 0,
                "giros_desde_ultimo_gp": 0,
                "pressao": 0,
                "nivel_pressao": "BAIXA",
                "probabilidade": 0,
                "confluencia": 0,
                "nivel_confluencia": "FRACA",
                "alinhamento": "BAIXO",
                "recomendacao_final": "NÃO APOSTAR",
                "motivo": "Erro na análise",
                "tempo_estimado": 30,
                "giros_estimados": 30,
                "taxa_giros": 1.0
            }

# Função para exibir resultados
def exibir_resultados(resultados):
    # Cabeçalho
    st.title("🎰 Monitor de Grandes Payouts - Crazy Time A")
    
    # Converter para horário local brasileiro
    fuso_brasil = pytz.timezone('America/Sao_Paulo')
    hora_utc = datetime.datetime.now(pytz.UTC)
    hora_brasil = hora_utc.astimezone(fuso_brasil)
    
    st.write(f"Atualizado em: {hora_brasil.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    # Coluna 1: Gauge Chart e Últimos Resultados
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pressão do Sistema")
        
        # Gauge Chart
        fig = criar_gauge_chart(resultados["pressao"], "Nível de Pressão")
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretação do nível de pressão
        cor_nivel = obter_cor_nivel(resultados["nivel_pressao"])
        st.markdown(f'<p>Nível de pressão: <span class="{cor_nivel}">{resultados["nivel_pressao"]}</span></p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Layout em subcolunas para Últimos Resultados e Recomendação Final
        subcol1, subcol2 = st.columns(2)
        
        # Subcol1: Últimos Resultados
        with subcol1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Últimos Resultados")
            
            # Exibir últimos resultados com destaque para o último
            ultimos_resultados_formatados = []
            for i, resultado in enumerate(resultados["ultimos_resultados"]):
                if i == len(resultados["ultimos_resultados"]) - 1:
                    # Último resultado com destaque
                    ultimos_resultados_formatados.append(f'<span class="ultimo-resultado">{resultado}</span>')
                else:
                    ultimos_resultados_formatados.append(f'{resultado}')
            
            st.markdown("Últimos 5 resultados: " + " → ".join(ultimos_resultados_formatados), unsafe_allow_html=True)
            
            # Exibir último grande payout
            st.write(f"Último grande payout: {resultados['ultimo_gp_valor']:.2f} ({resultados['ultimo_gp_resultado']})")
            st.write(f"Tempo passado: {resultados['tempo_desde_ultimo_gp']:.2f} minutos")
            st.write(f"Giros passados: {resultados['giros_desde_ultimo_gp']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Subcol2: Recomendação Final
        with subcol2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Recomendação Final")
            
            # Classe CSS baseada na recomendação
            if resultados["recomendacao_final"] == "APOSTAR":
                classe_recomendacao = "recomendacao-apostar"
            elif resultados["recomendacao_final"] == "NÃO APOSTAR":
                classe_recomendacao = "recomendacao-nao-apostar"
            else:
                classe_recomendacao = "recomendacao-aguardar"
            
            # Exibir recomendação com estilo
            st.markdown(f'<div class="{classe_recomendacao}">{resultados["recomendacao_final"]}</div>', unsafe_allow_html=True)
            st.write(f"Motivo: {resultados['motivo']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Coluna 2: Previsão e Recomendação
    with col2:
        # Previsão
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Previsão para os Próximos 30 Minutos")
        
        # Probabilidade
        cor_prob = obter_cor_gauge(resultados["probabilidade"])
        st.markdown(f'<p>Probabilidade: <span style="color:{cor_prob};">{resultados["probabilidade"]:.1f}%</span></p>', unsafe_allow_html=True)
        
        # Tempo estimado
        st.write(f"Tempo estimado: {resultados['tempo_estimado']:.1f} minutos")
        
        # Giros estimados
        st.write(f"Número estimado de giros: {resultados['giros_estimados']:.1f}")
        
        # Taxa atual
        st.write(f"Taxa atual: {resultados['taxa_giros']:.2f} giros por minuto")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Confluência
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Confluência dos Indicadores")
        
        # Score de confluência
        cor_conf = obter_cor_gauge(resultados["confluencia"])
        st.markdown(f'<p>Score de confluência: <span style="color:{cor_conf};">{resultados["confluencia"]:.1f}%</span></p>', unsafe_allow_html=True)
        
        # Nível de confluência
        cor_nivel_conf = obter_cor_nivel(resultados["nivel_confluencia"])
        st.markdown(f'<p>Nível de confluência: <span class="{cor_nivel_conf}">{resultados["nivel_confluencia"]}</span></p>', unsafe_allow_html=True)
        
        # Alinhamento
        st.write(f"Alinhamento entre indicadores: {resultados['alinhamento']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Aviso
    st.markdown("""
    <div style="font-size: 0.8em; color: gray; text-align: center; margin-top: 20px;">
        Esta previsão é baseada em análise estatística e não garante resultados futuros.<br>
        Jogue com responsabilidade e dentro dos seus limites financeiros.
    </div>
    """, unsafe_allow_html=True)

# Função principal
def main():
    # Sidebar moderno
    st.sidebar.markdown('<div class="sidebar-title">🎮 Configurações</div>', unsafe_allow_html=True)
    
    # Intervalo de atualização
    st.sidebar.markdown('<div class="sidebar-subtitle">Intervalo de Atualização</div>', unsafe_allow_html=True)
    refresh_interval = st.sidebar.slider(
        "Segundos",
        min_value=30,
        max_value=300,
        value=60,
        step=10
    )
    
    # Botão para atualizar manualmente
    st.sidebar.markdown('<div class="button-container">', unsafe_allow_html=True)
    
    # Botão estilizado com HTML/CSS em vez do botão padrão do Streamlit
    atualizar_clicked = st.sidebar.button("🔄 Atualizar Agora", key="atualizar")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Histórico de previsões
    st.sidebar.markdown('<div class="sidebar-subtitle">Histórico de Previsões</div>', unsafe_allow_html=True)
    historico = carregar_historico_previsoes()
    
    if historico:
        # Criar DataFrame do histórico
        df_historico = pd.DataFrame(historico)
        
        # Exibir gráfico de histórico
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(range(len(df_historico)), df_historico['pressao'], 'r-', label='Pressão')
        ax.plot(range(len(df_historico)), df_historico['probabilidade'], 'g-', label='Probabilidade')
        ax.plot(range(len(df_historico)), df_historico['confluencia'], 'b-', label='Confluência')
        ax.set_xlabel('Análises')
        ax.set_ylabel('Percentual (%)')
        ax.set_title('Histórico de Indicadores')
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        
        # Ajustar cores para tema escuro
        ax.set_facecolor('#1E1E1E')
        fig.patch.set_facecolor('#1E1E1E')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        st.sidebar.pyplot(fig)
    
    # Botão para parar atualização automática
    parar_atualizacao = st.sidebar.button("⏹️ Parar Atualização Automática", key="parar")
    if parar_atualizacao:
        st.session_state.auto_refresh = False
        st.sidebar.info("Atualização automática desativada.")
    
    # Executar análise
    if atualizar_clicked:
        resultados = executar_analise()
        exibir_resultados(resultados)
        st.sidebar.success("Dados atualizados com sucesso!")
    else:
        resultados = executar_analise()
        exibir_resultados(resultados)
        
        # Configurar atualização automática usando st.session_state
        if "auto_refresh" not in st.session_state:
            st.session_state.auto_refresh = True
            
        # Adicionar um placeholder para mensagem de atualização
        placeholder = st.empty()
        
        # Usar st.rerun() para atualização automática
        if st.session_state.auto_refresh:
            placeholder.info(f"Próxima atualização em {refresh_interval} segundos...")
            time.sleep(refresh_interval)
            st.rerun()

# Executar aplicativo
if __name__ == "__main__":
    main()
