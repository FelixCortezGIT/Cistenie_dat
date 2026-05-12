import pandas as pd
import os

os.makedirs("cleaned_data", exist_ok=True)

report = []
def log(msg):
    print(msg)
    report.append(msg)

def analyzuj(df, nazov):
    log(f"\n{'=' * 50}")
    log(f"analyza: {nazov}")
    log(f"\n{'=' * 50}")

    log(f"rozmery: {df.shape[0]} riadkov, {df.shape[1]} stlpcov")

    log(f"\ndatove typy stlpcov:\n{df.dtypes}")

    null_counts = df.isnull().sum()
    log(f"\nchybajuce hodnoty:\n{null_counts}")
    null_pct = (null_counts / len(df) * 100).round(2)
    log(f"\nchybajuce hodnoty v %\n{null_pct}")

    duplikaty = df[df.duplicated(subset=['full_name'])]
    log(f"\nduplikatnych riadkov: {duplikaty}")

    log(f"\nunikatne hodntoy v textovych stlpcoch:")
    for stlpec in df.select_dtypes(include="string").columns:
        unikatne = df[stlpec].dropna().unique()
        log(f"  {stlpec}: {len(unikatne)}")

    log(f"\nstatistiky numerickych stlpcov:\n{df.describe()}")
    cv_salary = (df['salary'].std() / df['salary'].mean() * 100)
    log(f"\nKoeficient variacie platov (CV - Coefficient of Variation): {cv_salary:.1f} %")
    cv_by_dept = (df.groupby('department')['salary']
                  .agg(['count', 'mean', 'std'])
                  .assign(CV=lambda x: (x['std'] / x['mean'] * 100).round(2))
                  .round(2))
    log(f"\n=== CV platov podla departmentu ===\n{cv_by_dept.to_string()}")

    # print(df["contract_type"].unique())

    return df.shape[0]


log("DATA CLEANING WORKFLOW")
log("=" * 50)

df = pd.read_csv("Cvicne raw data subory CSV a XMLS/hr_employees.csv", dtype={
    "hire_date": str
})

pred_hr = analyzuj(df, "hr_employees.csv")

# === 1. WHITESPACE CLEANING ===
aggressive_cleaning = ['email']
for stlpec in df.select_dtypes(include=['string']).columns:
    if stlpec in aggressive_cleaning:
        df[stlpec]=df[stlpec].str.replace(r'\s+', '', regex=True).str.strip()
    else:
        df[stlpec]=df[stlpec].str.replace(r'\s+', ' ', regex=True).str.strip()

# === 2. DUPLIKATY ===
df = df.drop_duplicates(subset=['full_name']).reset_index(drop=True)
log(f"po odstraneni duplikatov: {df.shape[0]} riadkov")

# === 3. DEPARTMENT ===
df['department'] = df['department'].str.title()
log(f"\nzjednotene hodnoty pre department: {df['department'].unique()}")

# === 4. CONTRACT TYPE ===
df['contract_type'] = df['contract_type'].str.lower().map({
    'full-time': 'Full-Time',
    'part-time': 'Part-Time',
    'contractor': 'Contractor'
})
log(f"unikatne contract_type po cisteni: {df['contract_type'].unique()}")

# === 5. SALARY — informacia o null hodnotach ===
log(f"riadky s chybajucim salary: {df['salary'].isnull().sum()}")

# === 6. ULOZENIE ===
df.to_csv("cleaned_data/hr_employees_clean.csv", index=False)
log("subor ulozeny: cleaned_data/hr_employees_clean.csv")

# === AUDIT CISTYCH DAT ===
po_hr = analyzuj(df, "cleaned_data/hr_employees_clean.csv")

with open("cleaned_data/report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(str(r) for r in report))
log("report ulozeny: cleaned_data/report.txt")
