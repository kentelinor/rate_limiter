import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [timestamp, setTimestamp] = useState(new Date().toISOString());
  const [response, setResponse] = useState(null);

  const handleButtonClick = async () => {
    try {
      const res = await axios.post("http://localhost:8000/rate_limit", { time: timestamp });
      setResponse(res.data.allowed ? "Request Approved" : "Request Denied");
    } catch (error) {
      console.error("Error sending request:", error);
      setResponse("An error occurred.");
    }
  };

  const updateTime = () => {
    setTimestamp(new Date().toISOString());
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <button onClick={handleButtonClick}>
        {timestamp} <br />
        Send Request
      </button>
      {response && <p>{response}</p>}
      <div style={{ marginTop: "20px" }}>
        <button onClick={updateTime}>Update Time</button>
      </div>
    </div>
  );
};

export default App;
