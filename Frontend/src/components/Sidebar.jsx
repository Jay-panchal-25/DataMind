export default function Sidebar() {
  return (
    <div className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <button className="w-full bg-gray-800 hover:bg-gray-700 p-2 rounded-md">
          + New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        <div className="p-2 hover:bg-gray-800 rounded cursor-pointer">
          Chat 1
        </div>
        <div className="p-2 hover:bg-gray-800 rounded cursor-pointer">
          Chat 2
        </div>
      </div>
    </div>
  );
}
