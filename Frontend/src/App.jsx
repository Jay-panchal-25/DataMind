import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import DatasetPage from "./components/DatasetPage";

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-900 text-white">
        <Sidebar />

        <div className="flex-1 overflow-auto ">
          <Routes>
            <Route path="/" element={<ChatWindow />} />
            <Route path="/dataset" element={<DatasetPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
