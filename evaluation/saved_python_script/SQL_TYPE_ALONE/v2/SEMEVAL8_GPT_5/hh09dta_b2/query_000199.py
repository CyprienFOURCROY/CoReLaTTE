import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_ah = tables["ii_ah"].copy()
    df_in = tables["ii_in"].copy()

    # Household-level: has at least one member aged 60+ and state (ent)
    port = df_portad[["folio", "ent", "edad"]].copy()
    port["age60"] = port["edad"] >= 60
    has60 = port.groupby("folio", as_index=False)["age60"].any().rename(columns={"age60": "has60"})
    ent_per = port.dropna(subset=["ent"]).groupby("folio", as_index=False)["ent"].first()
    hh_chars = has60.merge(ent_per, on="folio", how="left")
    hh_chars = hh_chars[hh_chars["has60"]]

    # Electronic devices owned with positive stated value; take max value per household
    ah = df_ah[["folio", "ah03e", "ah04e_2"]].copy()
    ah_cond = (ah["ah03e"] == 1) & (ah["ah04e_2"].notna()) & (ah["ah04e_2"] > 0)
    ah_max = ah[ah_cond].groupby("folio", as_index=False)["ah04e_2"].max().rename(columns={"ah04e_2": "max_electronic_value"})

    # Positive direct amount from Other Government Program
    in_pos = df_in[["folio", "in02a10"]].copy()
    in_pos = in_pos[(in_pos["in02a10"].notna()) & (in_pos["in02a10"] > 0)][["folio"]].drop_duplicates()

    # Eligible households
    eligible = hh_chars.merge(ah_max, on="folio", how="inner").merge(in_pos, on="folio", how="inner")
    eligible = eligible.dropna(subset=["ent"])
    try:
        eligible["ent"] = eligible["ent"].astype("int64")
    except Exception:
        pass

    result = (
        eligible.groupby("ent", as_index=False)
        .agg(
            avg_max_electronic_value=("max_electronic_value", "mean"),
            households_included=("folio", "nunique"),
        )
        .sort_values("ent")
        .reset_index(drop=True)
    )

    return result