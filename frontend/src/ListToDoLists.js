import "./ListToDoLists.css";
import { useRef, useState } from "react";
import { BiSolidTrash } from "react-icons/bi";
import { BiSearch } from "react-icons/bi";

function ListToDoLists({
  listSummaries,
  handleSelectList,
  handleNewToDoList,
  handleDeleteToDoList,
}) {

  const labelRef = useRef();
  const [search, setSearch] = useState("");

  function createList() {
    if (!labelRef.current.value.trim()) return;

    handleNewToDoList(labelRef.current.value);

    labelRef.current.value = "";
  }

  if (listSummaries === null) {
    return (
      <div className="ListToDoLists loading">
        Loading To-Do Lists...
      </div>
    );
  }

  const filteredLists = listSummaries.filter((list) =>
    list.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="ListToDoLists">

      <h1>📋 My To-Do Lists</h1>

      <div className="toolbar">

        <div className="search-box">

          <BiSearch />

          <input
            type="text"
            placeholder="Search lists..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

        </div>

      </div>

      <div className="new-list">

        <input
          ref={labelRef}
          type="text"
          placeholder="New list name"
        />

        <button onClick={createList}>
          + Create List
        </button>

      </div>

      {filteredLists.length === 0 ? (

        <div className="empty">
          No matching lists found.
        </div>

      ) : (

        filteredLists.map((summary) => (

          <div
            key={summary.id}
            className="summary"
            onClick={() => handleSelectList(summary.id)}
          >

            <div>

              <div className="name">
                {summary.name}
              </div>

              <div className="count">
                {summary.item_count} Tasks
              </div>

            </div>

            <span className="flex"></span>

            <span
              className="trash"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteToDoList(summary.id);
              }}
            >
              <BiSolidTrash />
            </span>

          </div>

        ))

      )}

    </div>
  );
}

export default ListToDoLists;