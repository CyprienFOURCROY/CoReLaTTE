import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Households with positive direct amount from '70 y más'
    hh_pos = df_in.loc[df_in["in02a11"].notna() & (df_in["in02a11"] > 0), ["folio"]].drop_duplicates()

    if hh_pos.empty:
        return pd.DataFrame({"ent": [], "hh_with_70plus": [], "hh_without_70plus": []})

    # Determine if household has at least one member aged 70+
    port = df_portad[["folio", "ent", "edad"]].copy()
    port["edad_ge_70"] = port["edad"] >= 70
    hh_age = (
        port.groupby("folio")
        .agg(ent=("ent", "first"), has_70plus=("edad_ge_70", "any"))
        .reset_index()
    )

    merged = hh_pos.merge(hh_age, on="folio", how="left")
    merged = merged[merged["ent"].notna()].copy()
    merged["has_70plus"] = merged["has_70plus"].fillna(False)

    out = (
        merged.groupby("ent")
        .agg(
            hh_with_70plus=("has_70plus", lambda x: int(x.sum())),
            total_hh=("folio", "nunique"),
        )
        .reset_index()
    )
    out["hh_without_70plus"] = out["total_hh"] - out["hh_with_70plus"]
    out = out.drop(columns=["total_hh"]).sort_values("ent").reset_index(drop=True)

    return out