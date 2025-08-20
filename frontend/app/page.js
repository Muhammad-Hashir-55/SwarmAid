"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import ReactMarkdown from "react-markdown";
import { useMap } from "react-leaflet";

/**
 * IMPORTANT
 *  - FastAPI must have CORS enabled for http://localhost:3000
 *  - This page renders Leaflet client-side via dynamic imports.
 */
const MapContainer = dynamic(
  () => import("react-leaflet").then((m) => m.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((m) => m.TileLayer),
  { ssr: false }
);
const Polyline = dynamic(
  () => import("react-leaflet").then((m) => m.Polyline),
  { ssr: false }
);
const Circle = dynamic(
  () => import("react-leaflet").then((m) => m.Circle),
  { ssr: false }
);
const Popup = dynamic(
  () => import("react-leaflet").then((m) => m.Popup),
  { ssr: false }
);

/* --- Reset map view to fit all features --- */
function ResetView({ features }) {
  const map = useMap();

  useEffect(() => {
    if (!features || features.length === 0) return;

    const bounds = [];
    features.forEach((f) => {
      if (f.geometry.type === "Point") {
        bounds.push([f.geometry.coordinates[1], f.geometry.coordinates[0]]);
      } else if (f.geometry.type === "LineString") {
        f.geometry.coordinates.forEach((c) => bounds.push([c[1], c[0]]));
      }
    });

    if (bounds.length > 0) {
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [features, map]);

  return null;
}

export default function Page() {
  const [scenario, setScenario] = useState("Tokyo earthquake");
  const [data, setData] = useState(null);
  const [fetching, setFetching] = useState(false);
  const [err, setErr] = useState("");

  /* --- Run simulation API --- */
  const runSimulate = async () => {
    setErr("");
    setFetching(true);
    try {
      const url = `http://127.0.0.1:8000/simulate?scenario=${encodeURIComponent(
        scenario
      )}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      setErr(
        `Could not fetch simulation. ${
          e?.message || e
        }. Check FastAPI & CORS.`
      );
    } finally {
      setFetching(false);
    }
  };

  /* --- Run once on load --- */
  useEffect(() => {
    runSimulate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const features = data?.geojson?.features || [];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header / Controls */}
      <header className="sticky top-0 z-10 bg-gray-900/70 backdrop-blur border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <h1 className="text-2xl md:text-3xl font-bold">SwarmAid Dashboard</h1>

          <div className="flex gap-2">
            <input
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              placeholder="Enter a scenario e.g. 'Tokyo earthquake'"
              className="px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-sm w-72 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={runSimulate}
              disabled={fetching}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-sm font-medium"
            >
              {fetching ? "Running..." : "Run Simulation"}
            </button>
          </div>
        </div>
      </header>

      {/* Main layout */}
      <main className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Map */}
        <section className="lg:col-span-7 xl:col-span-8 h-[70vh] rounded-2xl overflow-hidden border border-gray-800 bg-gray-900">
          <div className="h-full w-full">
            <MapContainer
              center={[20, 0]} // default world view
              zoom={2}
              scrollWheelZoom={true}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
                url="https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              />


              {features.map((f, i) => {
                if (f.geometry.type === "Point") {
                  const [lon, lat] = f.geometry.coordinates;
                  const severity = f.properties?.severity;
                  const color =
                    severity === "severe"
                      ? "#ef4444"
                      : severity === "moderate"
                      ? "#f59e0b"
                      : "#3b82f6";
                  return (
                    <Circle
                      key={`pt-${i}`}
                      center={[lat, lon]}
                      radius={1000}
                      pathOptions={{ color }}
                    >
                      <Popup>
                        <div className="text-sm">
                          <div className="font-semibold">{f.properties?.name}</div>
                          <div>{severity || "Cluster"}</div>
                        </div>
                      </Popup>
                    </Circle>
                  );
                } else if (f.geometry.type === "LineString") {
                  const coords = f.geometry.coordinates.map((c) => [c[1], c[0]]);
                  return (
                    <Polyline
                      key={`ln-${i}`}
                      positions={coords}
                      pathOptions={{ color: "#3b82f6" }}
                    >
                      <Popup>
                        <div className="text-sm font-semibold">
                          {f.properties?.name || "Safe Route"}
                        </div>
                      </Popup>
                    </Polyline>
                  );
                }
                return null;
              })}

              <ResetView features={features} />
            </MapContainer>
          </div>
        </section>

        {/* Agent Logs */}
        <aside className="lg:col-span-5 xl:col-span-4 space-y-4">
          <div className="rounded-2xl border border-gray-800 bg-gray-900">
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Agent Logs</h2>
              <span className="text-xs text-gray-400">
                {data?.scenario ? `Scenario: ${data.scenario}` : "No scenario yet"}
              </span>
            </div>

            {err && (
              <div className="px-4 py-3 text-sm text-red-400 border-b border-gray-800">
                {err}
              </div>
            )}

            {!data && !err && (
              <div className="px-4 py-6 text-sm text-gray-400">
                Waiting for results…
              </div>
            )}

            {data && (
              <ul className="divide-y divide-gray-800">
                {data.logs?.map((log, idx) => (
                  <li key={idx} className="p-4">
                    <div className="text-sm uppercase tracking-wide text-gray-400 mb-1">
                      {log.agent}
                    </div>
                    <div className="prose prose-invert max-w-none text-sm leading-relaxed">
                      <ReactMarkdown>{log.response}</ReactMarkdown>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}
