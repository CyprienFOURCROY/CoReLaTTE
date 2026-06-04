import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_inr = tables["ii_inr"]

    hh_dairy = df_inr.loc[df_inr["inr02a"] == 1, ["folio"]].dropna(subset=["folio"]).drop_duplicates()
    hh_no_plot = df_su.loc[df_su["su01"] == 3, ["folio"]].dropna(subset=["folio"]).drop_duplicates()

    eligible_hh = pd.merge(hh_dairy, hh_no_plot, on="folio", how="inner")

    people = df_portad[df_portad["folio"].isin(eligible_hh["folio"])]

    result = (
        people.groupby("ent", dropna=True)
        .agg(n_individuals=("folio", "size"), average_age=("edad", "mean"))
        .reset_index()
        .sort_values(["n_individuals", "ent"], ascending=[False, True])
        .reset_index(drop=True)
    )

    return result