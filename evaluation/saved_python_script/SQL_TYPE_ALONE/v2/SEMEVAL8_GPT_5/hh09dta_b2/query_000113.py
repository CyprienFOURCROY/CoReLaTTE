import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Adults 18+ in Oaxaca (ent == 20)
    adults_oax = df_portad[(df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18.0)].copy()

    # Households that use a plot of land for cultivation (su01 == 1)
    adults_plot = adults_oax.merge(df_su, on="folio", how="left")
    adults_plot = adults_plot[adults_plot["su01"] == 1.0].copy()

    # Merge household-level safety question
    adults_plot = adults_plot.merge(df_vlh, on="folio", how="left")

    # Valid answers: 1=Very safe, 2=Safe, 3=Unsafe, 4=Very unsafe
    valid_mask = adults_plot["vlh04"].isin([1.0, 2.0, 3.0, 4.0])
    total_valid = int(valid_mask.sum())

    # Unsafe or Very unsafe
    unsafe_mask = adults_plot["vlh04"].isin([3.0, 4.0])
    unsafe_or_very_unsafe = int((valid_mask & unsafe_mask).sum())

    return pd.DataFrame({
        "valid_answers": [total_valid],
        "unsafe_or_very_unsafe": [unsafe_or_very_unsafe]
    })