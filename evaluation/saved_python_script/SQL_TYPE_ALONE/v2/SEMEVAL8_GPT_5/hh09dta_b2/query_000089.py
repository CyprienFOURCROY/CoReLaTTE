import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_crh = tables["ii_crh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households that own a motor vehicle
    mv = (
        df_ah[["folio", "ah03d"]]
        .assign(own_mv=df_ah["ah03d"] == 1)
        .groupby("folio", as_index=False)["own_mv"]
        .any()
    )
    households_mv = mv[mv["own_mv"]][["folio"]]

    # Overall average household amount paid among households with recorded value
    crh_with_value = df_crh[(df_crh["crh03_1"] == 1) & (df_crh["crh03_2"].notna())]
    overall_avg = crh_with_value["crh03_2"].mean()

    # Households with positive amount paid exceeding overall average
    crh_exceed = crh_with_value[(crh_with_value["crh03_2"] > 0) & (crh_with_value["crh03_2"] > overall_avg)][["folio"]].drop_duplicates()

    # Individuals aged 25+ in motor-vehicle-owning households whose debts paid exceed overall average
    eligible_individuals = (
        df_portad.merge(households_mv, on="folio", how="inner")
        .merge(crh_exceed, on="folio", how="inner")
    )
    eligible_individuals = eligible_individuals[eligible_individuals["edad"].notna() & (eligible_individuals["edad"] >= 25)]

    avg_age = eligible_individuals["edad"].mean() if not eligible_individuals.empty else float("nan")

    return pd.DataFrame({"average_age": [avg_age]})