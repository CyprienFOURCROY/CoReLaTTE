import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh16a"]].copy()

    # Drop rows with missing key fields
    df_portad = df_portad.dropna(subset=["folio", "ent", "edad"])
    df_vlh = df_vlh.dropna(subset=["folio"])

    # Merge individuals with household victimization info
    df = df_portad.merge(df_vlh, on="folio", how="inner")

    # Normalize types
    # Convert 'ent' to nullable integer for grouping/mapping
    df["ent"] = pd.to_numeric(df["ent"], errors="coerce").astype("Int64")
    df["edad"] = pd.to_numeric(df["edad"], errors="coerce")
    df = df.dropna(subset=["ent", "edad"])

    # Create Yes/No status for parcel robbery since 2005
    df["robbery_since_2005"] = np.where(df["vlh16a"] == 1.0, "Yes",
                                 np.where(df["vlh16a"] == 3.0, "No", pd.NA))

    # Compute top 10 states by average age among households with Yes
    df_yes = df[df["robbery_since_2005"] == "Yes"]
    top_yes = (
        df_yes.groupby("ent", as_index=False)["edad"]
        .mean()
        .rename(columns={"edad": "avg_age_yes"})
        .sort_values("avg_age_yes", ascending=False)
        .head(10)
    )

    if top_yes.empty:
        return pd.DataFrame(
            {
                "state_code": pd.Series(dtype="Int64"),
                "state_name": pd.Series(dtype="object"),
                "robbery_since_2005": pd.Series(dtype="object"),
                "average_age": pd.Series(dtype="float64"),
                "respondent_count": pd.Series(dtype="int64"),
            }
        )

    top_ents = set(top_yes["ent"].tolist())

    # Aggregate stats for Yes and No within the selected states
    df_subset = df[df["ent"].isin(top_ents) & df["robbery_since_2005"].isin(["Yes", "No"])]
    stats = (
        df_subset.groupby(["ent", "robbery_since_2005"], as_index=False)
        .agg(average_age=("edad", "mean"), respondent_count=("edad", "size"))
    )

    # Map state codes to names
    ent_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas",
    }
    stats["state_name"] = stats["ent"].map(ent_map)

    # Order by the Yes average age for those states (descending), and within state show Yes first
    order_ref = top_yes[["ent", "avg_age_yes"]]
    stats = stats.merge(order_ref, on="ent", how="left")

    status_order = {"Yes": 0, "No": 1}
    stats["status_order"] = stats["robbery_since_2005"].map(status_order)

    stats = stats.sort_values(by=["avg_age_yes", "status_order"], ascending=[False, True]).drop(
        columns=["avg_age_yes", "status_order"]
    )

    # Rename ent to state_code and ensure dtypes
    stats = stats.rename(columns={"ent": "state_code"})

    # Reorder columns
    stats = stats[["state_code", "state_name", "robbery_since_2005", "average_age", "respondent_count"]]

    return stats