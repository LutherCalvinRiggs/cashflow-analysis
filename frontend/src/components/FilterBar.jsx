import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function FilterBar({ filters, onChange }) {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api.request("/categories").then(setCategories).catch(() => {});
  }, []);

  function set(key, value) {
    const next = { ...filters };
    if (value) {
      next[key] = value;
    } else {
      delete next[key];
    }
    onChange(next);
  }

  const hasFilters = Object.keys(filters).length > 0;

  return (
    <div className="px-6 py-2.5 border-b border-gray-800 flex flex-wrap items-center gap-3 text-xs shrink-0">
      {/* Category */}
      <select
        value={filters.category || ""}
        onChange={(e) => set("category", e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500 cursor-pointer"
      >
        <option value="">All categories</option>
        {categories.map((c) => (
          <option key={c.id} value={c.name}>
            {c.name}
          </option>
        ))}
      </select>

      {/* Type segmented control */}
      <div className="flex rounded overflow-hidden border border-gray-700">
        {[
          { value: "", label: "All" },
          { value: "debit", label: "Debit" },
          { value: "credit", label: "Credit" },
        ].map(({ value, label }) => (
          <button
            key={label}
            onClick={() => set("type", value)}
            className={`px-3 py-1.5 transition-colors ${
              (filters.type || "") === value
                ? "bg-gray-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Date range */}
      <div className="flex items-center gap-1.5 text-gray-500">
        <input
          type="date"
          value={filters.date_from || ""}
          onChange={(e) => set("date_from", e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500"
        />
        <span>–</span>
        <input
          type="date"
          value={filters.date_to || ""}
          onChange={(e) => set("date_to", e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500"
        />
      </div>

      {/* Exclude transfers */}
      <label className="flex items-center gap-1.5 text-gray-400 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={!!filters.exclude_transfers}
          onChange={(e) => set("exclude_transfers", e.target.checked ? true : "")}
          className="accent-gray-400"
        />
        Hide transfers
      </label>

      {/* Clear */}
      {hasFilters && (
        <button
          onClick={() => onChange({})}
          className="ml-auto text-gray-500 hover:text-gray-300 transition-colors"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
