import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_ah = tables["ii_ah"].copy()

    # Household-level average age and state
    hh_age = (
        df_portad.groupby("folio", as_index=False)
        .agg(avg_age=("edad", "mean"), ent=("ent", "first"))
    )

    # Oaxaca households and overall Oaxaca household average age (mean of household averages)
    oax_hh = hh_age[hh_age["ent"] == 20]
    oax_overall_avg_age = oax_hh["avg_age"].mean()

    # Households in Oaxaca with avg age above Oaxaca overall avg
    high_age_oax = oax_hh[oax_hh["avg_age"] > oax_overall_avg_age][["folio"]]

    # Households that reported receiving Liconsa milk (in03a == 1)
    liconsa_hh = (
        df_in.assign(rec=lambda d: d["in03a"] == 1)
        .groupby("folio")["rec"]
        .any()
        .reset_index()
    )
    liconsa_hh = liconsa_hh[liconsa_hh["rec"]][["folio"]]

    # Total value of electronic devices per household
    elec_value = df_ah[["folio", "ah04e_2"]].copy()
    elec_value["ah04e_2"] = elec_value["ah04e_2"].fillna(0)
    elec_value = (
        elec_value.groupby("folio", as_index=False)
        .agg(total_electronic_value=("ah04e_2", "sum"))
    )

    # Eligible households: Oaxaca, high avg age, and received Liconsa
    eligible = high_age_oax.merge(liconsa_hh, on="folio", how="inner")
    eligible = eligible.merge(elec_value, on="folio", how="left")
    eligible["total_electronic_value"] = eligible["total_electronic_value"].fillna(0)

    avg_total_value = eligible["total_electronic_value"].mean() if not eligible.empty else float("nan")
    n_households = len(eligible)

    return pd.DataFrame(
        {
            "average_total_value_electronic_devices": [avg_total_value],
            "n_households": [n_households],
        }
    )