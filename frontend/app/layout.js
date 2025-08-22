// app/layout.js
import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "SwarmAid",
  description: "AI-powered Disaster Response Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-black text-gray-100">
        {/* Navbar */}
        <nav className="bg-gray backdrop-blur border-b border-gray-800 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="text-xl font-bold">SwarmAid</Link>
            <div className="flex gap-6 text-sm font-medium">
              <Link href="/" className="hover:text-blue-400">Dashboard</Link>
              <Link href="/about" className="hover:text-blue-400">About Us</Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        {children}
      </body>
    </html>
  );
}
