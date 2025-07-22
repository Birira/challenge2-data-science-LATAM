import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt

# Leer archivo
with open('data.json', 'r') as f:
    data = json.load(f)

df = pd.json_normalize(data)

#Procesar datos
#print(df.isnull().sum())
df = df[df['Churn'].str.strip() != '']

df["account.Charges.Total"] = pd.to_numeric(df["account.Charges.Total"], errors='coerce')
#print(df['account.Charges.Total'].dtype)

# Función para convertir "si"/"no" a True/False
def convert_si_no_to_bool(series):
    return series.str.lower().map({'yes': True, 'no': False})

# Aplicar conversión a columnas que contengan "si"/"no"
for col in df.columns:
    if df[col].dtype == 'object':  
        unique_vals = df[col].astype(str).str.lower().unique()
        if 'si' in unique_vals or 'no' in unique_vals:
            df[col] = convert_si_no_to_bool(df[col])

try: 
    std_charges = df['account.Charges.Total'].std()
    mean = df['account.Charges.Total'].mean()
    #print(f"\nDesviasion estandar: {std_charges}")
    #print((std_charges/ mean)*100)
except Exception as e:
    print(f"Error: {e}")

#Cuentas diarias
df["account.Charges.Diary"] = df["account.Charges.Monthly"] / 30
#print(df[['account.Charges.Monthly', "account.Charges.Diary"]])

#print(df.describe())

# Contar los valores de Churn
churn = df["Churn"]
churn_counts = churn.value_counts()

# Crear un gráfico circular
plt.figure(figsize=(8, 8))
plt.pie(churn_counts, labels=churn_counts.index, autopct='%1.1f%%')
plt.title('Distribución de evasión')
plt.axis('equal')
plt.show()

# Crear un gráfico de barras para relacionar Churn con Contract
churn_contract = pd.crosstab(df['Churn'], df['account.PaymentMethod'], normalize='columns')
churn_contract.plot(kind='bar', stacked=False)
plt.title('Relación entre la evasión y Tipo de Contrato')
plt.xlabel('Evasión')
plt.ylabel('Porcentaje (%)')
plt.legend(title='Tipo de Contrato')
plt.grid(axis='y', linestyle='--')
plt.show() 

# Calcular correlaciones con Churn con histograma
# Convertir columna Churn a numérica para correlación
df['Churn_numeric'] = df['Churn'].map({True: 1, False: 0})

# Seleccionar columnas numéricas para correlación
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
correlation_data = df[list(numeric_cols) + ['Churn_numeric']]

# Calcular matriz de correlación
correlation_matrix = correlation_data.corr()

# Visualizar correlaciones con Churn
plt.figure(figsize=(10, 8))
churn_correlations = correlation_matrix['Churn_numeric'].sort_values(ascending=False)
sns.barplot(x=churn_correlations.values[1:], y=churn_correlations.index[1:])
plt.title('Correlación de variables numéricas con Churn')
plt.xlabel('Coeficiente de correlación')
plt.tight_layout()
plt.show()
