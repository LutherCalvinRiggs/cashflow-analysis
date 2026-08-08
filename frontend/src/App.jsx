import { useState } from "react";
import FilterBar from "./components/FilterBar";
import Ledger from "./components/Ledger";
import UploadPanel from "./components/UploadPanel";

const NAV = [
  { id: "ledger", label: "Ledger" },
  { id: "charts", label: "Charts" },
  { id: "upload", label: "Upload" },
];

export default function App() {
  const [view, setView] = useState("upload");
  const [ledgerFilters, setLedgerFilters] = useState({});
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 p-4 flex flex-col">
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

        <button
          onClick={() => setChatOpen((open) => !open)}
          className="mt-4 w-full px-3 py-2 rounded border border-blue-500 text-blue-400 text-sm font-medium hover:bg-blue-500/10 transition-colors"
        >
          {chatOpen ? "Hide chat" : "Speak to Your Money"}
        </button>
      </aside>

      {/* Chat panel — slides out from behind the sidebar, its own fixed width once open */}
      <aside
        className={`shrink-0 bg-gray-900 overflow-hidden transition-all duration-300 ${
          chatOpen ? "w-80 border-r border-gray-800" : "w-0 border-r-0"
        }`}
      >
        <div className="w-80 h-full p-4 flex flex-col">
          <h2 className="text-sm font-medium text-gray-300 mb-4">Ask your finances</h2>
          <div className="flex-1 text-gray-600 text-sm">Conversation will appear here</div>
          <input
            className="mt-4 w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-gray-500"
            placeholder="Ask a question..."
          />
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {view === "upload" && <UploadPanel onViewLedger={() => setView("ledger")} />}
        {view === "ledger" && (
          <>
            <FilterBar filters={ledgerFilters} onChange={setLedgerFilters} />
            <div className="flex-1 min-h-0">
              <Ledger filters={ledgerFilters} />
            </div>
          </>
        )}
        {view === "charts" && (
          <div className="flex-1 p-6 text-gray-500 text-sm">Charts coming in Phase 3</div>
        )}
      </main>
    </div>
  );
}
