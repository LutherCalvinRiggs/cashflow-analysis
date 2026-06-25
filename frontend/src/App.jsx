export default function App() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 p-4">
        <h1 className="text-lg font-semibold text-white mb-6">cashflow</h1>
        <nav className="space-y-1 text-sm text-gray-400">
          <div className="px-2 py-1 rounded hover:bg-gray-800 cursor-pointer">Ledger</div>
          <div className="px-2 py-1 rounded hover:bg-gray-800 cursor-pointer">Charts</div>
          <div className="px-2 py-1 rounded hover:bg-gray-800 cursor-pointer">Upload</div>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <p className="text-gray-500 text-sm">Main content area</p>
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
  )
}
