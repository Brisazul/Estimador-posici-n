import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Título de la aplicación
st.title("Estimador de posición para el ascenso 🚓")

# --- Configuración inicial ---
# Simular datos faltantes y combinar con ponderaciones reales

# Cargar datos reales
df_ponderaciones = pd.read_csv("ponderaciones.csv")
puntajes_reales = df_ponderaciones["PUNTAJE FINAL"].values

# Datos del test
no_presentados = 21
no_aprobaron = 3
puntajes_100 = 30
sumarios = 67

# Datos conocidos
total_inscriptos = 1065
total_aptos = total_inscriptos - no_presentados - sumarios
total_vacantes = 500
total_ponderaciones = len(df_ponderaciones)  # Personas que compartieron sus notas
#puntaje_papa = 82.525
#antecedente_papa = 69.75
#test_papa = 88
tolerancia = 1e-3

# Generar datos simulados
faltantes = total_aptos - total_ponderaciones
resto = faltantes - (puntajes_100 + no_aprobaron)

np.random.seed(42)
valores = [60, 64, 68, 72, 76, 80, 84, 88, 92, 96]
p = np.array([0.02, 0.03, 0.05, 0.1, 0.15, 0.2, 0.2, 0.15, 0.07, 0.03])

simulados_resto = np.random.choice(valores, size=(resto), p=p)

# Combinar reales y simulados
puntajes_simulados = np.concatenate((
    np.full(puntajes_100, 100),
    np.full(no_aprobaron, 56),
    simulados_resto
    ))

df_simulado = pd.DataFrame({
    "ANTECEDENTES": [np.nan] * faltantes,
    "PUNTAJE FINAL": puntajes_simulados
})

df_reales = pd.DataFrame({
    "PUNTAJE FINAL": df_ponderaciones["PUNTAJE FINAL"]
})

df_total = pd.concat([df_reales, df_simulado], ignore_index=True)
df_total = df_total.sort_values(by="PUNTAJE FINAL", ascending=False).reset_index(drop=True)
df_total["POSICION"] = df_total.index + 1

# --- Entrada del usuario ---
st.header("¿Cuántos decimales tiene su ponderación?")
decimales = st.number_input("Elija la cantidad de decimales (sin redondear)", min_value=0, max_value=10, step=1, value=3)

def truncar(valor, decimales):
    factor = 10**decimales
    return np.trunc(valor * factor) / factor

# Aplicar truncamiento al DataFrame
df_total["PUNTAJE FINAL"] = df_total["PUNTAJE FINAL"].apply(lambda x: truncar(x, decimales))

# --- Entrada del usuario ---
st.header("Ingrese su puntaje ponderado:")
puntaje_usuario = st.number_input("Puntaje final (ponderado):", min_value=56.0, max_value=100.0, step=0.01)

# Procesar posición estimada
if puntaje_usuario:
    filtro = np.abs(df_total["PUNTAJE FINAL"] - puntaje_usuario) < tolerancia
    if filtro.any():
        posicion = df_total[filtro].iloc[0]["POSICION"]
        st.subheader(f"Posición estimada: {int(posicion)}")
        if posicion <= 500:
            st.success(f"¡Estás dentro de las 500 vacantes! 🚀")
        else:
            st.error(f"Estás fuera de las 500 vacantes. 😟")
    else:
        st.warning("No se encontró una posición exacta, intenta con otro puntaje.")

    # Visualización del puesto
    st.header("Distribución de puntajes y tu posición:")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_total["PUNTAJE FINAL"], kde=True, bins=20, color="#aab1f6", alpha=0.7, label="Distribución de puntajes")
    ax.axvline(puntaje_usuario, color="red", linestyle="--", label=f"Tu puntaje ({puntaje_usuario})")
    ax.axvline(df_total["PUNTAJE FINAL"].iloc[499], color="blue", linestyle="--", label="Último puntaje dentro de 500 vacantes")
    ax.set_title("Distribución de Puntajes Finales")
    ax.set_xlabel("Puntaje Final")
    ax.set_ylabel("Frecuencia")
    ax.legend()
    st.pyplot(fig)
