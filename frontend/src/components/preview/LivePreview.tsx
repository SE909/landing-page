import { useEffect, useState } from "react";

interface Props {
  html: string;
}

type Viewport = "desktop" | "tablet" | "mobile";
type ViewMode = "preview" | "code";

export default function LivePreview({ html }: Props) {
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [viewMode, setViewMode] = useState<ViewMode>("preview");
  const [copied, setCopied] = useState(false);
  const [frameHeight, setFrameHeight] = useState(900);

  useEffect(() => {
    setFrameHeight(900);
  }, [html, viewport]);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getViewportWidth = () => {
    switch (viewport) {
      case "mobile":
        return "w-[375px]";
      case "tablet":
        return "w-[768px]";
      default:
        return "w-full";
    }
  };

  const resizePreviewFrame = (frame: HTMLIFrameElement) => {
    const document = frame.contentDocument;
    if (!document) return;

    const height = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight,
      document.body.offsetHeight,
      document.documentElement.offsetHeight
    );
    setFrameHeight(Math.max(height, 600));
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-[#e7ddd0] bg-[#f7f1eb] shadow-sm">
      {/* Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#e7ddd0] bg-white px-4 py-3">
        {/* View Mode Toggle */}
        <div className="flex items-center rounded-lg bg-gray-100 p-1 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setViewMode("preview")}
            className={`rounded-md px-3 py-1.5 transition ${
              viewMode === "preview"
                ? "bg-white coral-text shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            👁️ Aperçu Visuel
          </button>
          <button
            type="button"
            onClick={() => setViewMode("code")}
            className={`rounded-md px-3 py-1.5 transition ${
              viewMode === "code"
                ? "bg-white coral-text shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            💻 Code HTML
          </button>
        </div>

        {/* Viewport Toggles (only in preview mode) */}
        {viewMode === "preview" && (
          <div className="flex items-center gap-1.5 rounded-lg bg-gray-100 p-1 text-xs font-medium">
            <button
              type="button"
              onClick={() => setViewport("desktop")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "desktop"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🖥️ Ordi (100%)
            </button>
            <button
              type="button"
              onClick={() => setViewport("tablet")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "tablet"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📱 Tablette (768px)
            </button>
            <button
              type="button"
              onClick={() => setViewport("mobile")}
              className={`rounded-md px-2.5 py-1 transition ${
                viewport === "mobile"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              📲 Mobile (375px)
            </button>
          </div>
        )}

        {/* Copy Code button */}
        {viewMode === "code" && (
          <button
            type="button"
            onClick={handleCopyCode}
            className="coral-soft inline-flex items-center gap-1.5 rounded-full border border-[#f0c5b0] px-3 py-1.5 text-xs font-semibold hover:bg-[#fbe8de]"
          >
            {copied ? "✓ Copié !" : "📋 Copier le HTML"}
          </button>
        )}
      </div>

      {/* Main Content Viewer */}
      <div className="flex min-h-[75vh] justify-center bg-[#f7f1eb] p-4">
        {viewMode === "preview" ? (
          <div
            className={`transition-all duration-300 ${getViewportWidth()} overflow-hidden rounded-xl border border-[#e7ddd0] bg-white shadow-lg`}
          >
            <iframe
              srcDoc={html}
              sandbox="allow-same-origin"
              title="Landing Page Preview"
              className="w-full border-0"
              style={{ height: `${frameHeight}px` }}
              onLoad={(event) => {
                const frame = event.currentTarget;
                resizePreviewFrame(frame);
                window.setTimeout(() => resizePreviewFrame(frame), 300);
                window.setTimeout(() => resizePreviewFrame(frame), 1200);
              }}
            />
          </div>
        ) : (
          <div className="w-full max-w-5xl rounded-lg bg-gray-900 p-4 text-gray-100 overflow-auto max-h-[75vh] font-mono text-xs leading-relaxed">
            <pre>{html}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
