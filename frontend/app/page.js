"use client";
import { useState, useEffect } from "react";

export default function Home() {
  const [analysis, setAnalysis] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analyze")
      .then(res => res.json())
      .then(data => setAnalysis(data.analysis));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-6">🚨 SwarmAid Dashboard</h1>
      <p className="text-lg bg-gray-800 p-4 rounded-lg">
        {analysis || "Waiting for analysis..."}
      </p>
    </div>
  );
}
