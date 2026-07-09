import "./ToDoList.css";
import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { BiSolidTrash } from "react-icons/bi";

function ToDoList({ listId, handleBackButton }) {
  const labelRef = useRef();
  const dueDateRef = useRef();
  const dueTimeRef = useRef();
  const priorityRef = useRef();
  const categoryRef = useRef();

  const [listData, setListData] = useState(null);
  const [editItem, setEditItem] = useState(null);

  useEffect(() => {
    fetchData();
  }, [listId]);

  async function fetchData() {
    const response = await axios.get(`/api/lists/${listId}`);
    setListData(response.data);
  }

  function handleCreateItem(label) {
    if (!label.trim()) return;

    const updateData = async () => {
      const response = await axios.post(`/api/lists/${listData.id}/items/`, {
        label: label,
        due_date: dueDateRef.current.value || null,
        due_time: dueTimeRef.current.value || null,
        status: "Pending",
        priority: priorityRef.current.value,
        category: categoryRef.current.value,
      });

      setListData(response.data);

      labelRef.current.value = "";
      dueDateRef.current.value = "";
      dueTimeRef.current.value = "";
      priorityRef.current.value = "Medium";
      categoryRef.current.value = "Personal";
    };

    updateData();
  }

  function handleDeleteItem(id) {
    const updateData = async () => {
      const response = await axios.delete(
        `/api/lists/${listData.id}/items/${id}`
      );
      setListData(response.data);
    };

    updateData();
  }

  function handleCheckToggle(itemId, newState) {
    const updateData = async () => {
      const response = await axios.patch(
        `/api/lists/${listData.id}/checked_state`,
        {
          item_id: itemId,
          checked_state: newState,
        }
      );

      setListData(response.data);
    };

    updateData();
  }

  async function handleSaveEdit(id) {
    const response = await axios.patch(
      `/api/lists/${listData.id}/items/${id}`,
      editItem
    );

    setListData(response.data);
    setEditItem(null);
  }

  if (listData === null) {
    return (
      <div className="ToDoList loading">
        <button className="back" onClick={handleBackButton}>
          Back
        </button>
        Loading to-do list...
      </div>
    );
  }

  return (
    <div className="ToDoList">
      <button className="back" onClick={handleBackButton}>
        ← Back
      </button>

      <h1>{listData.name}</h1>

      <div className="box new-task">
        <input ref={labelRef} type="text" placeholder="Task name" />

        <input ref={dueDateRef} type="date" />

        <input ref={dueTimeRef} type="time" />

        <select ref={priorityRef} defaultValue="Medium">
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>

        <select ref={categoryRef} defaultValue="Personal">
          <option>Personal</option>
          <option>Study</option>
          <option>Work</option>
          <option>Shopping</option>
          <option>Other</option>
        </select>

        <button onClick={() => handleCreateItem(labelRef.current.value)}>
          Add Task
        </button>
      </div>

      {listData.items.length > 0 ? (
        listData.items.map((item) => (
          <div
            key={item.id}
            className={`item ${item.status
              .toLowerCase()
              .replace(/\s+/g, "")} ${item.checked ? "checked" : ""}`}
            onClick={() => handleCheckToggle(item.id, !item.checked)}
          >
            <span className="checkbox">{item.checked ? "✅" : "⬜"}</span>

            <div className="details">
              {editItem?.id === item.id ? (
                <div className="edit-box" onClick={(e) => e.stopPropagation()}>
                  <input
                    value={editItem.label}
                    onChange={(e) =>
                      setEditItem({
                        ...editItem,
                        label: e.target.value,
                      })
                    }
                  />

                  <input
                    type="date"
                    value={editItem.due_date || ""}
                    onChange={(e) =>
                      setEditItem({
                        ...editItem,
                        due_date: e.target.value,
                      })
                    }
                  />

                  <input
                    type="time"
                    value={editItem.due_time || ""}
                    onChange={(e) =>
                      setEditItem({
                        ...editItem,
                        due_time: e.target.value,
                      })
                    }
                  />

                  <select
                    value={editItem.priority}
                    onChange={(e) =>
                      setEditItem({
                        ...editItem,
                        priority: e.target.value,
                      })
                    }
                  >
                    <option>High</option>
                    <option>Medium</option>
                    <option>Low</option>
                  </select>

                  <select
                    value={editItem.category}
                    onChange={(e) =>
                      setEditItem({
                        ...editItem,
                        category: e.target.value,
                      })
                    }
                  >
                    <option>Personal</option>
                    <option>Study</option>
                    <option>Work</option>
                    <option>Shopping</option>
                    <option>Other</option>
                  </select>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSaveEdit(item.id);
                    }}
                  >
                    Save
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditItem(null);
                    }}
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="label">{item.label}</div>
              )}

              <div className="info">
                {item.due_date && <span>📅 {item.due_date}</span>}

                {item.due_time && <span>🕒 {item.due_time}</span>}
              </div>

              <div className="badges">
                <span
                  className={`badge priority ${item.priority.toLowerCase()}`}
                >
                  {item.priority}
                </span>

                <span className="badge category">{item.category}</span>
              </div>
            </div>

            <span className="flex"></span>

            {editItem?.id !== item.id && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setEditItem(item);
                }}
              >
                Edit
              </button>
            )}

            <span
              className="trash"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteItem(item.id);
              }}
            >
              <BiSolidTrash />
            </span>
          </div>
        ))
      ) : (
        <div className="box">There are currently no tasks.</div>
      )}
    </div>
  );
}

export default ToDoList;
