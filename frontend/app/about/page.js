// app/about/page.js
export default function About() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12 text-gray-200">
      <h1 className="text-4xl font-bold mb-8">About SwarmAid</h1>
      <p className="leading-relaxed mb-6">
        <span className="font-semibold text-blue-400">SwarmAid</span> is an
        AI-powered disaster response system created during our Hackathon project.  
        It demonstrates how multiple specialized AI agents – working like a human
        response team – can collaborate in real time to analyze crises, identify risks,
        and guide emergency operations.
      </p>

      <h2 className="text-2xl font-semibold mt-10 mb-4">🌍 Our Mission</h2>
      <p className="mb-6">
        Disasters strike without warning. Our mission is to harness AI and real-world
        data sources (satellite feeds, social media signals, routing APIs) to provide
        first responders, NGOs, and governments with actionable intelligence – faster,
        smarter, and more efficiently – to save lives.
      </p>

      <h2 className="text-2xl font-semibold mt-10 mb-4">🤖 The Agents</h2>
      <ul className="space-y-3">
        <li>
          👨‍💻 <span className="font-medium text-white">Data Analyst</span> – scans hazards and
          interprets damage zones from satellite and event data.
        </li>
        <li>
          🚑 <span className="font-medium text-white">Medic Coordinator</span> – analyzes
          social media reports to triage urgent medical needs.
        </li>
        <li>
          🚚 <span className="font-medium text-white">Logistics Manager</span> – plans safe
          supply routes and staging operations for aid delivery.
        </li>
        <li>
          🧐 <span className="font-medium text-white">Critic</span> – audits, validates, and
          strengthens the overall response plan.
        </li>
      </ul>

      <h2 className="text-2xl font-semibold mt-10 mb-4">🚀 Hackathon Context</h2>
      <p className="mb-6">
        SwarmAid was built as a <span className="text-blue-400">hackathon demo</span> to
        showcase the potential of multi-agent collaboration in emergency response.  
        Future iterations will deepen the integration with live data sources such as
        NASA EONET, OpenRouteService, and Twitter/X APIs, making the system closer to a
        real-time disaster intelligence platform.
      </p>
    </div>
  );
}
