import { BrowserRouter, Route, Routes } from "react-router-dom";
import CreatePage from "./pages/CreatePage";
import PreviewPage from "./pages/PreviewPage";
import HistoryPage from "./pages/HistoryPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CreatePage />} />
        <Route path="/preview/:id" element={<PreviewPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </BrowserRouter>
  );
}
