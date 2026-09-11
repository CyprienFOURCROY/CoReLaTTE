import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Prepare keys and filters
    df_portad["ls_num"] = pd.to_numeric(df_portad["ls"], errors="coerce")
    heads = df_portad[
        (df_portad["ent"] == 20) &  # Oaxaca
        (df_portad["edad"] >= 18) &  # Adults
        (df_portad["ls_num"] == 1)   # Household head (ls == '01')
    ][["folio", "edad", "ls_num"]].copy()

    # Households that answered "No" to having had forced entry since 2005
    hh_no_entry_since_2005 = df_vlh[df_vlh["vlh12a_c"] == 3][["folio"]].drop_duplicates()

    # Merge heads with eligible households
    heads = heads.merge(hh_no_entry_since_2005, on="folio", how="inner")

    # Electronic devices value (positive)
    df_ah["ls_num"] = pd.to_numeric(df_ah["ls"], errors="coerce")
    electronics = df_ah[["folio", "ls_num", "ah04e_2"]].copy()

    group = heads.merge(electronics, on=["folio", "ls_num"], how="inner")
    group = group[(group["ah04e_2"].notna()) & (group["ah04e_2"] > 0)]

    if group.empty:
        return pd.DataFrame({"count_above_avg": [0], "average_age": [float("nan")]})

    overall_avg = group["ah04e_2"].mean()
    above = group[group["ah04e_2"] > overall_avg]

    count_above = int(above.shape[0])
    avg_age = above["edad"].mean() if count_above > 0 else float("nan")

    return pd.DataFrame({"count_above_avg": [count_above], "average_age": [avg_age]})