import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function FilterBar({ filters, onChange }) {
  const [categories, setCategories] = useState([]);
  const [periods, setPeriods] = useState([]); // ["2025-01", "2024-12", ...] desc

  useEffect(() => {
    api.request("/categories").then(setCategories).catch(() => {});
    api.request("/transactions/periods").then(setPeriods).catch(() => {});
  }, []);

  const years = useMemo(() => {
    return [...new Set(periods.map((p) => p.slice(0, 4)))].sort((a, b) => b.localeCompare(a));
  }, [periods]);

  const months = useMemo(() => {
    const relevant = filters.year ? periods.filter((p) => p.startsWith(filters.year)) : periods;
    return [...new Set(relevant.map((p) => p.slice(5, 7)))].sort();
  }, [periods, filters.year]);

  function set(key, value) {
    const next = { ...filters };
    if (value) {
      next[key] = value;
    } else {
      delete next[key];
    }
    onChange(next);
  }

  function setYear(value) {
    const next = { ...filters };
    if (value) {
      next.year = value;
    } else {
      delete next.year;
    }
    // Month may no longer be valid for the newly selected year — clear it rather
    // than silently keep filtering on a month/year combo with no data.
    delete next.month;
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

      {/* Year */}
      <select
        value={filters.year || ""}
        onChange={(e) => setYear(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500 cursor-pointer"
      >
        <option value="">All years</option>
        {years.map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>

      {/* Month */}
      <select
        value={filters.month || ""}
        onChange={(e) => set("month", e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500 cursor-pointer"
      >
        <option value="">All months</option>
        {months.map((m) => (
          <option key={m} value={m}>
            {MONTH_NAMES[Number(m) - 1]}
          </option>
        ))}
      </select>

      {/* Type */}
      <select
        value={filters.type || ""}
        onChange={(e) => set("type", e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-gray-200 focus:outline-none focus:border-gray-500 cursor-pointer"
      >
        <option value="">All types</option>
        <option value="debit">Debit</option>
        <option value="credit">Credit</option>
      </select>

      {/* Clear */}
      {hasFilters && (
        <button
          onClick={() => onChange({})}
          className="text-gray-500 hover:text-gray-300 transition-colors"
        >
          Clear filters
        </button>
      )}

      {/* Exclude transfers — always last, right-aligned */}
      <label className="ml-auto flex items-center gap-1.5 text-gray-400 cursor-pointer select-none">
        <input
          type="checkbox"
          checked={!!filters.exclude_transfers}
          onChange={(e) => set("exclude_transfers", e.target.checked ? true : "")}
          className="accent-gray-400"
        />
        Hide transfers
      </label>
    </div>
  );
}
