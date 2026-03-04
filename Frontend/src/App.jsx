import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import DatasetPage from "./components/DatasetPage";
import GraphPage from "./components/GraphPage";

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-neutral-950 text-neutral-100">
        <Sidebar />

        <div className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<ChatWindow />} />
            <Route path="/dataset" element={<DatasetPage />} />
            <Route path="/graph" element={<GraphPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;

