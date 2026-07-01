import { useState } from "react";
import UploadPanel from "./components/UploadPanel";

const NAV = [
  { id: "ledger", label: "Ledger" },
  { id: "charts", label: "Charts" },
  { id: "upload", label: "Upload" },
];

export default function App() {
  const [view, setView] = useState("upload");

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 p-4">
        <h1 className="text-lg font-semibold text-white mb-6">cashflow</h1>
        <nav className="space-y-1 text-sm">
          {NAV.map((item) => (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full text-left px-2 py-1 rounded transition-colors ${
                view === item.id
                  ? "bg-gray-800 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {view === "upload" && <UploadPanel />}
        {view === "ledger" && (
          <div className="p-6 text-gray-500 text-sm">Ledger coming in Phase 2</div>
        )}
        {view === "charts" && (
          <div className="p-6 text-gray-500 text-sm">Charts coming in Phase 3</div>
        )}
      </main>

      {/* Chat panel */}
      <aside className="w-80 shrink-0 bg-gray-900 border-l border-gray-800 p-4 flex flex-col">
        <h2 className="text-sm font-medium text-gray-300 mb-4">Ask your finances</h2>
        <div className="flex-1 text-gray-600 text-sm">Conversation will appear here</div>
        <input
          className="mt-4 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-gray-500"
          placeholder="Ask a question..."
        />
      </aside>
    </div>
  );
}
