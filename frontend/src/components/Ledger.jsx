import { Fragment, useCallback, useEffect, useState } from "react";
import { api, updateTransactionCategory } from "../api/client";

const PAGE_SIZE = 50;

const TYPE_STYLE = {
  debit: { bg: "bg-red-900/40", text: "text-red-300" },
  credit: { bg: "bg-green-900/40", text: "text-green-300" },
};

function formatDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatAmount(amount, type) {
  const s = amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return type === "debit" ? `-$${s}` : `+$${s}`;
}

function buildQuery(filters, page, sort) {
  const params = new URLSearchParams({ page, page_size: PAGE_SIZE, sort });
  if (filters.category) params.set("category", filters.category);
  if (filters.type) params.set("type", filters.type);
  if (filters.year) params.set("year", filters.year);
  if (filters.month) params.set("month", filters.month);
  if (filters.exclude_transfers) params.set("exclude_transfers", "true");
  return `/transactions?${params}`;
}

export default function Ledger({ filters = {} }) {
  const [txns, setTxns] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState("desc");
  const [meta, setMeta] = useState({ total: 0, pages: 1 });
  const [expandedId, setExpandedId] = useState(null);
  const [editCategory, setEditCategory] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  const catColors = Object.fromEntries(categories.map((c) => [c.name, c.color]));

  useEffect(() => {
    api
      .request("/categories")
      .then(setCategories)
      .catch(() => {});
  }, []);

  useEffect(() => {
    setPage(1);
  }, [filters]);

  const loadTransactions = useCallback(() => {
    setLoading(true);
    setError(null);
    return api
      .request(buildQuery(filters, page, sort))
      .then((data) => {
        setTxns(data.items);
        setMeta({ total: data.total, pages: data.pages });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filters, page, sort]);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  function toggleSort() {
    setSort((s) => (s === "desc" ? "asc" : "desc"));
    setPage(1);
  }

  function toggleExpand(tx) {
    if (expandedId === tx.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(tx.id);
    setEditCategory(tx.category || "");
    setSaveError(null);
  }

  async function saveCategory(tx) {
    if (!editCategory || editCategory === tx.category) {
      setExpandedId(null);
      return;
    }
    setSaving(true);
    setSaveError(null);
    try {
      await updateTransactionCategory(tx.id, editCategory);
      await loadTransactions();
      setExpandedId(null);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (error) {
    return <div className="p-6 text-red-400 text-sm">Error: {error}</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-6 pt-5 pb-3 flex items-center justify-between border-b border-gray-800">
        <span className="text-xs text-gray-500">
          {loading ? "Loading…" : `${meta.total.toLocaleString()} transactions`}
        </span>
      </div>

      {!loading && txns.length === 0 ? (
        <div className="p-6 text-gray-500 text-sm">
          No transactions found. Upload a statement to get started.
        </div>
      ) : (
        <div className="flex-1 overflow-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-800 sticky top-0 bg-gray-950 z-10">
                <th className="px-6 py-3 font-medium whitespace-nowrap">
                  <button
                    onClick={toggleSort}
                    className="flex items-center gap-1 hover:text-gray-300 transition-colors"
                    title={sort === "desc" ? "Newest first — click for oldest first" : "Oldest first — click for newest first"}
                  >
                    Date
                    <span className="text-[10px]">{sort === "desc" ? "▼" : "▲"}</span>
                  </button>
                </th>
                <th className="pr-6 py-3 font-medium">Description</th>
                <th className="pr-6 py-3 font-medium text-right whitespace-nowrap">Amount</th>
                <th className="pr-6 py-3 font-medium whitespace-nowrap">Type</th>
                <th className="pr-6 py-3 font-medium">Category</th>
              </tr>
            </thead>
            <tbody>
              {txns.map((tx) => {
                const typeStyle = TYPE_STYLE[tx.type];
                const catColor = tx.category ? catColors[tx.category] : null;
                const isExpanded = expandedId === tx.id;
                return (
                  <Fragment key={tx.id}>
                    <tr
                      onClick={() => toggleExpand(tx)}
                      className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer"
                    >
                      <td className="px-6 py-2.5 text-gray-400 whitespace-nowrap">
                        {formatDate(tx.date)}
                      </td>
                      <td className="pr-6 py-2.5 text-gray-200 max-w-sm">
                        <span className="block truncate" title={tx.description}>
                          {tx.description}
                        </span>
                      </td>
                      <td
                        className={`pr-6 py-2.5 text-right font-mono whitespace-nowrap ${
                          tx.type === "debit" ? "text-red-400" : "text-green-400"
                        }`}
                      >
                        {formatAmount(tx.amount, tx.type)}
                      </td>
                      <td className="pr-6 py-2.5">
                        {typeStyle && (
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-medium ${typeStyle.bg} ${typeStyle.text}`}
                          >
                            {tx.type}
                          </span>
                        )}
                      </td>
                      <td className="pr-6 py-2.5">
                        {tx.category && (
                          <span
                            className="px-2 py-0.5 rounded text-xs font-medium"
                            style={
                              catColor
                                ? { color: catColor, backgroundColor: catColor + "26" }
                                : { color: "#9ca3af", backgroundColor: "#1f2937" }
                            }
                          >
                            {tx.category}
                          </span>
                        )}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="border-b border-gray-800/50 bg-gray-900/50">
                        <td colSpan={5} className="px-6 py-4">
                          <div
                            className="flex flex-wrap items-start gap-6 text-sm"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div>
                              <div className="text-xs text-gray-500 mb-1">Confidence</div>
                              <div className="text-gray-300">
                                {tx.confidence != null ? `${Math.round(tx.confidence * 100)}%` : "—"}
                              </div>
                            </div>
                            {tx.notes && (
                              <div className="max-w-md">
                                <div className="text-xs text-gray-500 mb-1">AI notes</div>
                                <div className="text-gray-300">{tx.notes}</div>
                              </div>
                            )}
                            <div>
                              <div className="text-xs text-gray-500 mb-1">Category</div>
                              <div className="flex items-center gap-2">
                                <select
                                  value={editCategory}
                                  onChange={(e) => setEditCategory(e.target.value)}
                                  className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-gray-200 text-sm"
                                >
                                  {categories.map((c) => (
                                    <option key={c.name} value={c.name}>
                                      {c.name}
                                    </option>
                                  ))}
                                </select>
                                <button
                                  onClick={() => saveCategory(tx)}
                                  disabled={saving}
                                  className="px-3 py-1 rounded bg-blue-700 hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium transition-colors"
                                >
                                  {saving ? "Saving…" : "Save"}
                                </button>
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                Applies to this merchant everywhere in your ledger.
                              </div>
                              {saveError && (
                                <div className="text-xs text-red-400 mt-1">{saveError}</div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {meta.pages > 1 && (
        <div className="px-6 py-3 border-t border-gray-800 flex items-center gap-3 text-sm text-gray-400 shrink-0">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            ← Prev
          </button>
          <span className="text-xs">
            Page {page} of {meta.pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(meta.pages, p + 1))}
            disabled={page === meta.pages}
            className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
