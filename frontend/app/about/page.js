// app/about/page.js
export default function About() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-6">About SwarmAid</h1>
      <p className="text-gray-300 leading-relaxed mb-6">
        SwarmAid is an AI-powered disaster response system built during our Hackathon project. 
        It simulates how multiple specialized AI agents – Data Analyst, Medic Coordinator, Logistics Manager, and Critic –
        can collaborate to analyze crises in real-time.
      </p>

      <h2 className="text-2xl font-semibold mt-10 mb-4">Our Mission</h2>
      <p className="text-gray-300 mb-6">
        Disasters strike without warning. Our mission is to use cutting-edge AI and real-world data 
        (satellite imagery, social media, routing APIs) to assist first responders, NGOs, and governments 
        in saving lives more efficiently.
      </p>

      <h2 className="text-2xl font-semibold mt-10 mb-4">The Team</h2>
      <ul className="space-y-2 text-gray-300">
        <li>👨‍💻 <span className="font-medium">Data Analyst Agent</span> – interprets disaster zones.</li>
        <li>🚑 <span className="font-medium">Medic Coordinator Agent</span> – triages urgent medical needs.</li>
        <li>🚚 <span className="font-medium">Logistics Manager Agent</span> – plans safe delivery routes.</li>
        <li>🧐 <span className="font-medium">Critic Agent</span> – validates and improves the response plan.</li>
      </ul>

      <h2 className="text-2xl font-semibold mt-10 mb-4">Hackathon Context</h2>
      <p className="text-gray-300">
        This project was built to demonstrate the power of multi-agent collaboration in crisis response. 
        Future versions will integrate live data sources such as NASA disaster feeds, OpenRouteService, 
        and Twitter/X APIs for fully automated emergency intelligence.
      </p>
    </div>
  );
}
