import { useRef, useState } from "react";
import { uploadStatement } from "../api/client";

const FILE_STATUS = { PENDING: "pending", UPLOADING: "uploading", SUCCESS: "success", ERROR: "error" };
const AUTO_REDIRECT_KEY = "cashflow.autoRedirectToLedger";

function readAutoRedirect() {
  try {
    return localStorage.getItem(AUTO_REDIRECT_KEY) === "true";
  } catch {
    return false;
  }
}

function makeEntry(file) {
  return {
    id: `${file.name}-${file.size}-${file.lastModified}-${Math.random().toString(36).slice(2)}`,
    file,
    status: FILE_STATUS.PENDING,
    progress: 0,
    result: null,
    error: null,
  };
}

export default function UploadPanel({ onViewLedger }) {
  const [entries, setEntries] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [autoRedirect, setAutoRedirect] = useState(readAutoRedirect);
  const inputRef = useRef(null);

  function toggleAutoRedirect(e) {
    const value = e.target.checked;
    setAutoRedirect(value);
    try {
      localStorage.setItem(AUTO_REDIRECT_KEY, String(value));
    } catch {
      // localStorage unavailable — toggle still works for this session
    }
  }

  function reset() {
    setEntries([]);
    setProcessing(false);
    if (inputRef.current) inputRef.current.value = "";
  }

  function updateEntry(id, patch) {
    setEntries((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)));
  }

  async function processFiles(fileList) {
    const files = Array.from(fileList || []);
    if (files.length === 0) return;

    const newEntries = files.map(makeEntry);
    setEntries(newEntries);
    setProcessing(true);

    let succeeded = 0;
    for (const entry of newEntries) {
      const isPdf = entry.file.type === "application/pdf" || entry.file.name.toLowerCase().endsWith(".pdf");
      if (!isPdf) {
        updateEntry(entry.id, { status: FILE_STATUS.ERROR, error: "Only PDF files are accepted." });
        continue;
      }
      updateEntry(entry.id, { status: FILE_STATUS.UPLOADING });
      try {
        const data = await uploadStatement(entry.file, (pct) => updateEntry(entry.id, { progress: pct }));
        updateEntry(entry.id, { status: FILE_STATUS.SUCCESS, result: data });
        succeeded += 1;
      } catch (err) {
        updateEntry(entry.id, { status: FILE_STATUS.ERROR, error: err.message });
      }
    }

    setProcessing(false);
    if (succeeded > 0 && autoRedirect && onViewLedger) {
      onViewLedger();
    }
  }

  function onFileChange(e) {
    processFiles(e.target.files);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    processFiles(e.dataTransfer.files);
  }

  function onDragOver(e) {
    e.preventDefault();
    setDragging(true);
  }

  function onDragLeave() {
    setDragging(false);
  }

  if (entries.length > 0) {
    const successEntries = entries.filter((e) => e.status === FILE_STATUS.SUCCESS);
    const errorEntries = entries.filter((e) => e.status === FILE_STATUS.ERROR);
    const allDone = entries.every((e) => e.status === FILE_STATUS.SUCCESS || e.status === FILE_STATUS.ERROR);
    const totalTransactions = successEntries.reduce((sum, e) => sum + (e.result?.transaction_count || 0), 0);
    const totalNewMerchants = successEntries.reduce((sum, e) => sum + (e.result?.new_map_entries || 0), 0);
    const allWarnings = successEntries.flatMap((e) => e.result?.warnings || []);

    return (
      <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
        <div className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-lg ${
                allDone
                  ? errorEntries.length > 0 && successEntries.length === 0
                    ? "bg-red-500/20 text-red-400"
                    : "bg-green-500/20 text-green-400"
                  : "bg-blue-500/20 text-blue-400"
              }`}
            >
              {allDone ? (errorEntries.length > 0 && successEntries.length === 0 ? "✕" : "✓") : "⋯"}
            </div>
            <h2 className="text-white font-semibold">
              {allDone
                ? entries.length > 1
                  ? `${successEntries.length} of ${entries.length} statements uploaded`
                  : successEntries.length
                  ? "Statement uploaded"
                  : "Upload failed"
                : "Processing statements…"}
            </h2>
          </div>

          <ul className="space-y-1.5 max-h-56 overflow-auto">
            {entries.map((entry) => (
              <li
                key={entry.id}
                className="flex items-center justify-between gap-3 text-sm bg-gray-800/60 rounded-lg px-3 py-2"
              >
                <span className="text-gray-300 truncate" title={entry.file.name}>
                  {entry.file.name}
                </span>
                {entry.status === FILE_STATUS.PENDING && <span className="text-gray-600 text-xs shrink-0">Waiting…</span>}
                {entry.status === FILE_STATUS.UPLOADING && (
                  <span className="text-blue-400 text-xs shrink-0">{entry.progress < 100 ? `${entry.progress}%` : "Extracting…"}</span>
                )}
                {entry.status === FILE_STATUS.SUCCESS && (
                  <span className="text-green-400 text-xs shrink-0">{entry.result.transaction_count} txns</span>
                )}
                {entry.status === FILE_STATUS.ERROR && (
                  <span className="text-red-400 text-xs shrink-0 truncate max-w-[10rem]" title={entry.error}>
                    {entry.error}
                  </span>
                )}
              </li>
            ))}
          </ul>

          {allDone && successEntries.length > 0 && (
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Stat label="Transactions" value={totalTransactions} />
              <Stat label="Merchants learned" value={totalNewMerchants} />
            </div>
          )}

          {allWarnings.length > 0 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 space-y-1">
              <p className="text-yellow-400 text-xs font-medium uppercase tracking-wide">Warnings</p>
              {allWarnings.map((w, i) => (
                <p key={i} className="text-yellow-300 text-sm">{w}</p>
              ))}
            </div>
          )}

          {allDone && (
            <>
              {successEntries.length > 0 && (
                <button
                  onClick={onViewLedger}
                  className="w-full py-2 rounded-lg bg-blue-700 hover:bg-blue-600 text-white text-sm font-medium transition-colors"
                >
                  View Ledger
                </button>
              )}
              <button
                onClick={reset}
                className="w-full py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
              >
                Upload {entries.length > 1 ? "more statements" : "another statement"}
              </button>

              <div>
                <label className="flex items-center gap-1.5 text-gray-400 text-xs cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={autoRedirect}
                    onChange={toggleAutoRedirect}
                    className="accent-gray-400"
                  />
                  Automatically go to the ledger after a successful upload
                </label>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => inputRef.current?.click()}
        className={`w-full max-w-md border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
          dragging
            ? "border-blue-500 bg-blue-500/5"
            : "border-gray-700 hover:border-gray-600 hover:bg-gray-900/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          multiple
          className="hidden"
          onChange={onFileChange}
        />
        <p className="text-3xl mb-3">📄</p>
        <p className="text-gray-200 font-medium mb-1">Drop PDF bank statements here</p>
        <p className="text-gray-500 text-sm">or click to browse — you can select more than one</p>
      </div>

      <p className="text-gray-600 text-xs max-w-md text-center">
        Your file is processed locally. Nothing is sent to a third party — only the extracted text goes to your configured AI provider.
      </p>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <p className="text-gray-500 text-xs mb-1">{label}</p>
      <p className="text-white text-xl font-semibold">{value}</p>
    </div>
  );
}
