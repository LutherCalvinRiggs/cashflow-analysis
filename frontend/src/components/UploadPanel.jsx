import { useRef, useState } from "react";
import { uploadStatement } from "../api/client";

const STATES = { IDLE: "idle", UPLOADING: "uploading", SUCCESS: "success", ERROR: "error" };

export default function UploadPanel() {
  const [state, setState] = useState(STATES.IDLE);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  function reset() {
    setState(STATES.IDLE);
    setProgress(0);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  async function handleFile(file) {
    if (!file) return;
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are accepted.");
      setState(STATES.ERROR);
      return;
    }

    setState(STATES.UPLOADING);
    setProgress(0);

    try {
      const data = await uploadStatement(file, setProgress);
      setResult(data);
      setState(STATES.SUCCESS);
    } catch (err) {
      setError(err.message);
      setState(STATES.ERROR);
    }
  }

  function onFileChange(e) {
    handleFile(e.target.files?.[0]);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  function onDragOver(e) {
    e.preventDefault();
    setDragging(true);
  }

  function onDragLeave() {
    setDragging(false);
  }

  if (state === STATES.SUCCESS && result) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
        <div className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 text-lg">✓</div>
            <h2 className="text-white font-semibold">Statement uploaded</h2>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <Stat label="Transactions" value={result.transaction_count} />
            <Stat label="Merchants learned" value={result.new_map_entries} />
          </div>

          {result.warnings?.length > 0 && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 space-y-1">
              <p className="text-yellow-400 text-xs font-medium uppercase tracking-wide">Warnings</p>
              {result.warnings.map((w, i) => (
                <p key={i} className="text-yellow-300 text-sm">{w}</p>
              ))}
            </div>
          )}

          <button
            onClick={reset}
            className="w-full mt-2 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
          >
            Upload another statement
          </button>
        </div>
      </div>
    );
  }

  if (state === STATES.ERROR) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
        <div className="w-full max-w-md bg-gray-900 border border-red-900/50 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center text-red-400 text-lg">✕</div>
            <h2 className="text-white font-semibold">Upload failed</h2>
          </div>
          <p className="text-red-300 text-sm">{error}</p>
          <button
            onClick={reset}
            className="w-full py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm transition-colors"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (state === STATES.UPLOADING) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-6 px-8">
        <div className="w-full max-w-md space-y-4 text-center">
          <p className="text-gray-300 text-sm">Processing statement…</p>
          <div className="w-full bg-gray-800 rounded-full h-1.5">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-gray-600 text-xs">{progress < 100 ? `Uploading… ${progress}%` : "Extracting transactions…"}</p>
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
          className="hidden"
          onChange={onFileChange}
        />
        <p className="text-3xl mb-3">📄</p>
        <p className="text-gray-200 font-medium mb-1">Drop a PDF bank statement here</p>
        <p className="text-gray-500 text-sm">or click to browse</p>
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
