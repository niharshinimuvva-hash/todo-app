import { useEffect, useState } from "react";
import axios from "axios";

import "./App.css";

import ListToDoLists from "./ListToDoLists";
import ToDoList from "./ToDoList";
import Login from "./Login";
import Register from "./Register";

function App() {
  const [listSummaries, setListSummaries] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);

  const [loggedIn, setLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      axios.defaults.headers.common[
        "Authorization"
      ] = `Bearer ${token}`;

      setLoggedIn(true);
      reloadData();
    }
  }, []);

  async function reloadData() {
    try {
      const response = await axios.get("/api/lists");
      setListSummaries(response.data);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        handleLogout();
      }
    }
  }

  function handleLogin() {
    setLoggedIn(true);
    reloadData();
  }

  function handleLogout() {
    localStorage.removeItem("token");

    delete axios.defaults.headers.common[
      "Authorization"
    ];

    setLoggedIn(false);
    setSelectedItem(null);
    setListSummaries(null);
  }

  function handleNewToDoList(newName) {
    if (!newName.trim()) return;

    const updateData = async () => {
      await axios.post("/api/lists", {
        name: newName,
      });

      reloadData();
    };

    updateData();
  }

  function handleDeleteToDoList(id) {
    const updateData = async () => {
      await axios.delete(`/api/lists/${id}`);
      reloadData();
    };

    updateData();
  }

  function handleSelectList(id) {
    setSelectedItem(id);
  }

  function backToList() {
    setSelectedItem(null);
    reloadData();
  }

  if (!loggedIn) {
    return showRegister ? (
      <Register
        showLogin={() => setShowRegister(false)}
      />
    ) : (
      <Login
        onLogin={handleLogin}
        showRegister={() => setShowRegister(true)}
      />
    );
  }

  return (
    <div className="App">

      <div className="topBar">
        <h2>My ToDo App</h2>

        <button
          className="logout"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>

      {selectedItem === null ? (
        <ListToDoLists
          listSummaries={listSummaries}
          handleSelectList={handleSelectList}
          handleNewToDoList={handleNewToDoList}
          handleDeleteToDoList={handleDeleteToDoList}
        />
      ) : (
        <ToDoList
          listId={selectedItem}
          handleBackButton={backToList}
        />
      )}

    </div>
  );
}

export default App;