from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import timedelta
import pandas as pd
import numpy as np
from .data_loader import get_dwell_dynamic, get_vessels, get_transactions, get_fish, get_fish_locations, get_pings


app = FastAPI(title="FishEye CatchNet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _classify_kind(k):
    if isinstance(k, str):
        if "Preserve" in k or "Reserve" in k:
            return "Protected"
        if "Fishing" in k or "Shelf" in k:
            return "Non-protected"
    return "Transit / Other"



@app.get("/")
def root():
    return {"message": "✅ API running!"}

@app.get("/api/ports")
def get_ports():
    dwell_dynamic = get_dwell_dynamic()
    ports = sorted(dwell_dynamic["arrival_port"].dropna().unique().tolist())
    return {"ports": ports}

@app.get("/api/vessels")
def get_vessels_list():
    dwell_dynamic = get_dwell_dynamic()
    vessels = sorted(dwell_dynamic["vessel_name"].dropna().unique().tolist())
    return {"vessels": vessels}

@app.get("/api/locations")
def get_locations_list():
    pings = get_pings()
    locations = sorted(pings["source"].dropna().unique().tolist())
    return {"locations": locations}


@app.get("/api/dates")
def get_dates():
    dwell_dynamic = get_dwell_dynamic()
    dates = (
        pd.to_datetime(dwell_dynamic["arrival_time"])
        .dt.date
        .dropna()
        .unique()
    )
    dates = sorted([d.strftime("%Y-%m-%d") for d in dates])
    return {"dates": dates}


@app.get("/api/daily_view")
def get_daily_view(port: str, date: str):
    dwell_dynamic = get_dwell_dynamic()
    vessels = get_vessels()

    selected_port = port
    selected_date = pd.Timestamp(date) - pd.Timedelta(days=1)
    arrival_date = selected_date 
    dwell_dynamic["arrival_time"] = pd.to_datetime(dwell_dynamic["arrival_time"])
    dwell_dynamic = dwell_dynamic[
        (dwell_dynamic["arrival_time"].dt.date == arrival_date.date()) &
        (dwell_dynamic["arrival_port"] == selected_port)
    ].copy()

    vessel_info = vessels[["vessel_id", "tonnage"]].rename(columns={"vessel_id": "vessel_name"})
    dwell_dynamic = dwell_dynamic.merge(vessel_info, on="vessel_name", how="left")

    def classify_kind(k):
        if "Preserve" in k or "Reserve" in k:
            return "Protected"
        elif "Fishing" in k or "Shelf" in k:
            return "Non-protected"
        else:
            return "Transit / Other"
    dwell_dynamic["area_type"] = dwell_dynamic["kind"].apply(classify_kind)

    scatter_data = (
        dwell_dynamic[[
            "vessel_name", "location_name", "dwell", "area_type", "arrival_time", "tonnage"
        ]]
        .assign(
            dwell=lambda x: x["dwell"].astype(float),
            tonnage=lambda x: x["tonnage"].astype(float),
            arrival_time=lambda x: x["arrival_time"].astype(str) 
        )
        .to_dict(orient="records")
    )

    summary = {
        "num_vessels": int(dwell_dynamic["vessel_name"].nunique()),
        "num_locations": int(dwell_dynamic["location_name"].nunique()),
        "total_dwell": float(dwell_dynamic["dwell"].sum())
    }

    return JSONResponse({
        "date": date,
        "port": port,
        "summary": summary,
        "scatter_data": scatter_data
    })

@app.get("/api/daily_exports_view")
def get_daily_exports(port: str, date: str):
    try:
        trans = get_transactions()  
        fish = get_fish()
        selected_date = pd.to_datetime(date)

        daily_exports = (
        trans[(trans["target_harbor"] == port) &
            (trans["date"].dt.date == selected_date.date())]
        .rename(columns={"source": "cargo_id", "qty_tons": "exports_tons"})
        [["cargo_id", "fish_id", "exports_tons", "target_harbor", "date"]]
        )
        id_to_name = dict(zip(fish["id"], fish["entity_name"]))

        daily_exports["fish_name"] = daily_exports["fish_id"].map(id_to_name)
        illegal_fishes = ["Sockfish/Pisces foetida", "Offidiaa/Piscis osseus", "Helenaa/Pisces satis"]

        daily_exports["is_prohibited"] = daily_exports["fish_name"].isin(illegal_fishes)
        daily_exports = daily_exports.astype({
            "fish_id": "string",
            "exports_tons": "float"
        })
        daily_exports["date"] = daily_exports["date"].astype(str)
        selected_date = str(selected_date)


        daily_exports_json = daily_exports.to_dict(orient="records")

        return JSONResponse({
            "port": port,
            "date": selected_date,
            "daily_exports": daily_exports_json
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )


@app.get("/api/vessel_catch_view")
def get_vessel_catch(port: str, date: str):
    try:
        # --- Carica i dataset ---
        dwell_dynamic = get_dwell_dynamic()
        vessels = get_vessels()
        trans = get_transactions()
        fish = get_fish()
        fish_locations = get_fish_locations()

        # --- Parametri di riferimento ---
        selected_port = port
        selected_date = pd.Timestamp(date) 
        arrival_date = selected_date  - pd.Timedelta(days=1)


        dwell_dynamic["arrival_time"] = pd.to_datetime(dwell_dynamic["arrival_time"])
        dwell_dynamic = dwell_dynamic[
            (dwell_dynamic["arrival_time"].dt.date == arrival_date.date()
            ) &
            (dwell_dynamic["arrival_port"] == selected_port)
        ].copy()
        vessel_info = vessels[["vessel_id", "tonnage"]].rename(columns={"vessel_id": "vessel_name"})
        dwell_dynamic = dwell_dynamic.merge(vessel_info, on="vessel_name", how="left")

        trans["date"] = pd.to_datetime(trans["date"])
        daily_exports = (
            trans[(trans["target_harbor"] == selected_port) &
                  (trans["date"].dt.date == selected_date.date())]
            .rename(columns={"source": "cargo_id", "qty_tons": "exports_tons"})
            [["cargo_id", "fish_id", "exports_tons", "target_harbor", "date"]]
        )
        id_to_name = dict(zip(fish["id"], fish["entity_name"]))
        daily_exports["fish_name"] = daily_exports["fish_id"].map(id_to_name)
        illegal_fishes = ["Sockfish/Pisces foetida", "Offidiaa/Piscis osseus", "Helenaa/Pisces satis"]

        daily_exports["is_prohibited"] = daily_exports["fish_name"].isin(illegal_fishes)



        def _estimate_vessel_catch_by_habitat_with_cargo(daily_exports, dwell_dynamic, fish_locations):
            results = []
            if daily_exports.empty or dwell_dynamic.empty:
                return pd.DataFrame(columns=[
                    "cargo_id", "vessel_name", "fish_name", "location_name",
                    "dwell", "tonnage", "estimated_tons"
                ])

            fish_to_locations = (
                fish_locations.groupby("entity_name")["location_id"]
                .apply(list)
                .to_dict()
            )

            for _, row in daily_exports.iterrows():
                fish_name = row["fish_name"]

                exports_tons = row["exports_tons"]
                cargo_id = row["cargo_id"]
                is_prohibited = row["is_prohibited"]
                habitats = fish_to_locations.get(fish_name, [])
                if not habitats:
                    continue

                candidates = dwell_dynamic[dwell_dynamic["location_name"].isin(habitats)].copy()
                if candidates.empty:
                    continue

                candidates["weight"] = candidates["tonnage"] * candidates["dwell"]
                total_weight = candidates["weight"].sum()
                if total_weight == 0:
                    continue

                candidates["estimated_tons"] = exports_tons * (candidates["weight"] / total_weight)
                candidates["fish_name"] = fish_name
                candidates["cargo_id"] = cargo_id
                candidates["is_prohibited"]=is_prohibited

                results.append(
                    candidates[["cargo_id", "vessel_name", "fish_name", "location_name",
                                "dwell", "tonnage", "estimated_tons", "is_prohibited"]]
                )

            if results:
                df = pd.concat(results, ignore_index=True)
                return df
            else:
                return pd.DataFrame(columns=[
                    "cargo_id", "vessel_name", "fish_name", "location_name",
                    "dwell", "tonnage", "estimated_tons", "is_prohibited"
                ])

        vessel_catch = _estimate_vessel_catch_by_habitat_with_cargo(
            daily_exports, dwell_dynamic, fish_locations
        )
        # Aggiungi percentuali per cargo_id
        vessel_catch["share_percent"] = (
            vessel_catch.groupby("cargo_id")["estimated_tons"]
            .transform(lambda x: 100 * x / x.sum())
        )

        # Serializza per JSON
        vessel_catch_json = vessel_catch.assign(
            dwell=lambda x: x["dwell"].astype(float),
            tonnage=lambda x: x["tonnage"].astype(float),
            estimated_tons=lambda x: x["estimated_tons"].astype(float),
            share_percent=lambda x: x["share_percent"].astype(float),
        ).to_dict(orient="records")

        return JSONResponse({
            "date": date,
            "port": port,
            "num_cargo": int(vessel_catch["cargo_id"].nunique()),
            "num_vessels": int(vessel_catch["vessel_name"].nunique()),
            "vessel_catch": vessel_catch_json
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/vessel_routine_view")
def get_vessel_routine(vessel: str):
    """
    Returns the chronological routine of a selected vessel:
    includes start/end times, area kind, and visited sources.
    """
    try:
        ping = get_pings() 

        df_vessel = ping[ping["target"] == vessel].copy()
        if df_vessel.empty:
            return JSONResponse({
                "vessel": vessel,
                "segments": [],
                "message": "No records found for this vessel."
            })

        df_vessel["time"] = pd.to_datetime(df_vessel["time"])
        df_vessel = df_vessel.sort_values("time")
        df_vessel["start"] = df_vessel["time"]
        df_vessel["end"] = df_vessel["time"] + pd.to_timedelta(df_vessel["dwell"], unit="s")


        df_vessel["kind"] = df_vessel["kind"].apply(_classify_kind)

        df_vessel = df_vessel[["source", "kind", "start", "end"]]

        segments_json = df_vessel.assign(
            start=lambda x: x["start"].astype(str),
            end=lambda x: x["end"].astype(str)
        ).to_dict(orient="records")

        return JSONResponse({
            "vessel": vessel,
            "num_segments": len(df_vessel),
            "segments": segments_json
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/dwell_comparison_view")
def get_dwell_comparison(vessel: str = None):
    """
    Restituisce dwell medio e safe zone per ciascuna location.
    La safe zone è calcolata come [25° percentile, 75° percentile] (più robusta della std).
    """
    import numpy as np
    import pandas as pd
    from fastapi.responses import JSONResponse

    try:
        ping = get_pings()
        ping["time"] = pd.to_datetime(ping["time"], errors="coerce")

        if not {"source", "target", "dwell"}.issubset(ping.columns):
            raise ValueError("Ping dataset must contain 'source', 'target' and 'dwell' columns")

        baseline = (
            ping.groupby("source")["dwell"]
            .agg(
                mean_dwell="mean",
                q25=lambda x: np.nanpercentile(x, 25),
                q75=lambda x: np.nanpercentile(x, 75),
                count="count"
            )
            .reset_index()
            .rename(columns={"source": "location_name"})
        )

        baseline["safe_low"] = baseline["q25"].clip(lower=0)
        baseline["safe_high"] = baseline["q75"]

        vessel_data = None
        if vessel and vessel.strip():
            vessel_df = ping[ping["target"] == vessel]
            vessel_data = (
                vessel_df.groupby("source")["dwell"]
                .mean()
                .reset_index()
                .rename(columns={"source": "location_name", "dwell": "vessel_dwell"})
            )


        merged = baseline.copy()
        if vessel_data is not None and not vessel_data.empty:
            merged = merged.merge(vessel_data, on="location_name", how="left", validate="one_to_one")
        else:
            merged["vessel_dwell"] = np.nan


        merged = merged.replace([np.inf, -np.inf], np.nan).replace({np.nan: None})

        json_data = merged.to_dict(orient="records")

        return JSONResponse({
            "num_locations": len(merged),
            "has_vessel": bool(vessel and vessel.strip()),
            "vessel": vessel or None,
            "dwell_comparison": json_data,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/dwell_location_view")
def get_dwell_location_view(
    location: str,
    vessel: str = None,
):
    """
    Restituisce dwell medio, quantili e confronto con eventuale nave specifica
    limitandosi alle location richieste (separate da virgola) e, opzionalmente,
    a una nave specificata.
    """
    try:
        ping = get_pings()
        ping["time"] = pd.to_datetime(ping["time"], errors="coerce")

        required_cols = {"source", "target", "dwell", "kind"}
        missing = required_cols - set(ping.columns)
        if missing:
            raise ValueError(f"Ping dataset missing required columns: {missing}")

        ping["area_type"] = ping["kind"].apply(_classify_kind)

        selected_locations = [loc.strip() for loc in location.split(",") if loc.strip()]
        if not selected_locations:
            raise ValueError("Parameter 'location' must include at least one value.")

        ping = ping[ping["source"].isin(selected_locations)]

        if ping.empty:
            stats = pd.DataFrame(
                columns=[
                    "location_name",
                    "area_type",
                    "mean_dwell",
                    "q25",
                    "q75",
                    "count",
                    "safe_low",
                    "safe_high",
                ]
            )
        else:
            stats = (
                ping.groupby(["source", "area_type"])["dwell"]
                .agg(
                    mean_dwell="mean",
                    q25=lambda x: np.nanpercentile(x, 25),
                    q75=lambda x: np.nanpercentile(x, 75),
                    count="count",
                )
                .reset_index()
                .rename(columns={"source": "location_name"})
            )
            stats["safe_low"] = stats["q25"].clip(lower=0)
            stats["safe_high"] = stats["q75"]

        vessel_data = None
        if vessel and vessel.strip():
            vessel_df = ping[ping["target"] == vessel]
            if not vessel_df.empty:
                vessel_data = (
                    vessel_df.groupby("source")["dwell"]
                    .mean()
                    .reset_index()
                    .rename(
                        columns={
                            "source": "location_name",
                            "dwell": "vessel_dwell",
                        }
                    )
                )

        merged = stats.copy()
        if vessel_data is not None and not vessel_data.empty:
            merged = merged.merge(
                vessel_data, on="location_name", how="left", validate="one_to_one"
            )
        else:
            merged["vessel_dwell"] = np.nan

        merged = merged.replace([np.inf, -np.inf], np.nan).replace({np.nan: None})
        json_data = merged.to_dict(orient="records")

        return JSONResponse(
            {
                "num_locations": len(json_data),
                "selected_locations": selected_locations,
                "has_vessel": bool(vessel and vessel.strip()),
                "vessel": vessel or None,
                "dwell_summary": json_data,
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/weekly_dwell")
def get_weekly_dwell(location: str | None = None):
    """
    Returns the average dwell per location, aggregated by calendar day.
    Optional query param 'location' filters to a specific location.
    """

    ping = get_pings()
    ping["time"] = pd.to_datetime(ping["time"], errors="coerce")
    ping["date"] = ping["time"].dt.date

    # --- Optional filter ---
    if location:
        ping = ping[ping["source"] == location]

    # --- Validate required columns ---
    if not {"source", "dwell", "date"}.issubset(ping.columns):
        raise ValueError("Ping dataset must contain 'source', 'dwell', and 'date' columns")

    # --- Aggregate by day ---
    daily_avg = (
        ping.groupby(["date", "source"])["dwell"]
        .mean()
        .reset_index()
        .rename(columns={"source": "location_name", "dwell": "avg_dwell"})
        .sort_values(["date"])
    )

    daily_avg["avg_dwell"] = daily_avg["avg_dwell"].round(2)
    daily_avg["date"] = daily_avg["date"].astype(str)

    result = []
    for loc, group in daily_avg.groupby("location_name"):
        result.append({
            "location_name": loc,
            "dates": group["date"].tolist(),
            "avg_dwell": group["avg_dwell"].tolist()
        })

    return {"data": result}
