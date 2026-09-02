def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge on folio (household ID)
    df = df_portad.merge(df_vlh[["folio", "vlh10a", "vlh18a"]], on="folio", how="inner")

    # Only keep rows where vlh18a == 0 (zero break-ins since 2005)
    df_zero_incident = df[df["vlh18a"] == 0]

    # Only keep rows where vlh10a == 1 (knows family/friend robbed in last 12 months)
    df_zero_incident = df_zero_incident[df_zero_incident["vlh10a"] == 1]

    # Compute overall average age among these people
    avg_age = df_zero_incident["edad"].mean()

    # Select individuals older than this average
    df_result = df_zero_incident[df_zero_incident["edad"] > avg_age]

    # Select and sort required columns
    df_result = df_result[["folio", "ent", "edad", "vlh18a"]].sort_values(by="edad", ascending=False).reset_index(drop=True)

    return df_result