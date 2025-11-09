from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import timedelta
import pandas as pd
from .data_loader import get_dwell_dynamic, get_vessels, get_transactions


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
        selected_date = pd.to_datetime(date).date()

        # Filter exports for that port & date
        daily_exports = (
            trans[(trans["target_harbor"] == port) &
                  (pd.to_datetime(trans["date"]).dt.date == selected_date)]
            .groupby("fish_id", as_index=False)["qty_tons"]
            .sum()
            .rename(columns={"qty_tons": "exports_tons"})
        )

        # convert to serializable dict
        daily_exports_json = daily_exports.to_dict(orient="records")

        return JSONResponse({
            "port": port,
            "date": date,
            "daily_exports": daily_exports_json
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )
