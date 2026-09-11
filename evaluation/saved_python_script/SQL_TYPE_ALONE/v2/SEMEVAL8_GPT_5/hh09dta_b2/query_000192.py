import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_su = tables["ii_su"].copy()
    df_inr = tables["ii_inr"].copy()

    # Households in Oaxaca
    oax_folios = (
        df_portad.loc[df_portad["ent"] == 20, ["folio"]]
        .dropna()
        .drop_duplicates()
    )

    # Households that use a plot of land for farming
    su_plot = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    # National average eggs sold last month among those reporting producing/selling eggs in last 12 months
    inr_eggs = df_inr[["folio", "inr02d", "inr04d"]].copy()
    national_avg = inr_eggs.loc[
        (inr_eggs["inr02d"] == 1) & (inr_eggs["inr04d"].notna()), "inr04d"
    ].mean()

    # Eligible Oaxaca households: use plot, reported producing/selling eggs in last 12 months
    eligible = (
        inr_eggs.merge(su_plot, on="folio", how="inner")
        .merge(oax_folios, on="folio", how="inner")
    )
    eligible = eligible[eligible["inr02d"] == 1]

    # Those that sold at least the national average last month
    result = eligible.loc[
        eligible["inr04d"].notna() & (eligible["inr04d"] >= national_avg),
        ["folio", "inr04d"]
    ].drop_duplicates()

    result = result.rename(columns={"folio": "household_id", "inr04d": "eggs_sold_last_month"}).reset_index(drop=True)

    return result