from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import timedelta
import pandas as pd
from .data_loader import get_dwell_dynamic, get_vessels, get_transactions, get_fish, get_fish_locations, get_pings


app = FastAPI(title="FishEye CatchNet API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




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
    selected_date = pd.Timestamp(date)
    arrival_date = selected_date - pd.Timedelta(days=1)

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
            arrival_time=lambda x: x["arrival_time"].astype(str)  # 👈 conversione chiave
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
        trans = get_transactions()  # your parquet loader
        fish = get_fish()
        selected_date = (pd.to_datetime(date) + pd.Timedelta(days=1)).date()

        # Filter exports for that port & date
        daily_exports = (
            trans[(trans["target_harbor"] == port)]
            .groupby(["date", "fish_id"], as_index=False)["qty_tons"]
            .sum()
            .rename(columns={"qty_tons": "exports_tons"})
        )
        print(daily_exports)
        daily_exports = daily_exports[
            pd.to_datetime(daily_exports["date"]).dt.date == selected_date
        ]        
        id_to_name = dict(zip(fish["id"], fish["entity_name"]))

        daily_exports["fish_name"] = daily_exports["fish_id"].map(id_to_name)
        illegal_fishes = ["Sockfish/Pisces foetida", "Offidiaa/Piscis osseus", "Helenaa/Pisces satis"]

        daily_exports["is_prohibited"] = daily_exports["fish_name"].isin(illegal_fishes)
        print(daily_exports)
        daily_exports = daily_exports.astype({
            "fish_id": "string",
            "exports_tons": "float"
        })
        daily_exports["date"] = daily_exports["date"].astype(str)
        selected_date = str(selected_date)
        # Convert to JSON-safe list of dicts

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
        arrival_date = selected_date - pd.Timedelta(days=1)


        dwell_dynamic["arrival_time"] = pd.to_datetime(dwell_dynamic["arrival_time"])
        dwell_dynamic = dwell_dynamic[
            (dwell_dynamic["arrival_time"].dt.date == arrival_date.date()) &
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

        # Nome del pesce
        id_to_name = dict(zip(fish["id"], fish["entity_name"]))
        daily_exports["fish_name"] = daily_exports["fish_id"].map(id_to_name)
        illegal_fishes = ["Sockfish/Pisces foetida", "Offidiaa/Piscis osseus", "Helenaa/Pisces satis"]

        daily_exports["is_prohibited"] = daily_exports["fish_name"].isin(illegal_fishes)


        def estimate_vessel_catch_by_habitat_with_cargo(daily_exports, dwell_dynamic, fish_locations):
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
                return pd.concat(results, ignore_index=True)
            else:
                return pd.DataFrame(columns=[
                    "cargo_id", "vessel_name", "fish_name", "location_name",
                    "dwell", "tonnage", "estimated_tons", "is_prohibited"
                ])

        vessel_catch = estimate_vessel_catch_by_habitat_with_cargo(
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
        ping = get_pings()  # or get_ping() if available

        # --- Filter for selected vessel ---
        print(ping)
        df_vessel = ping[ping["target"] == vessel].copy()
        print(df_vessel)
        if df_vessel.empty:
            return JSONResponse({
                "vessel": vessel,
                "segments": [],
                "message": "No records found for this vessel."
            })

        # --- Sort chronologically & compute start-end intervals ---
        df_vessel["time"] = pd.to_datetime(df_vessel["time"])
        df_vessel = df_vessel.sort_values("time")
        df_vessel["start"] = df_vessel["time"]
        df_vessel["end"] = df_vessel["time"] + pd.to_timedelta(df_vessel["dwell"], unit="s")

        # --- Classify kind ---
        def classify_kind(k):
            if "Preserve" in k or "Reserve" in k:
                return "Ecological Preserve"
            elif "Fishing" in k or "Shelf" in k or "Ground" in k:
                return "Fishing Ground"
            elif "City" in k or "Harbor" in k:
                return "city"
            elif "Buoy" in k:
                return "buoy"
            else:
                return "Other"

        df_vessel["kind"] = df_vessel["kind"].apply(classify_kind)

        # --- Clean up relevant fields ---
        df_vessel = df_vessel[["source", "kind", "start", "end"]]

        # --- Convert to JSON-safe ---
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
