const express = require("express");
const path = require("path");
const axios = require("axios");

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || "http://backend-service:5000";

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.render("index", {
    message: null,
    error: null
  });
});

app.post("/submit", async (req, res) => {
  try {
    const payload = {
      first_name: req.body.first_name,
      last_name: req.body.last_name,
      email: req.body.email,
      phone: req.body.phone,
      address: req.body.address
    };

    const response = await axios.post(`${BACKEND_URL}/submit`, payload, {
      headers: {
        "Content-Type": "application/json"
      },
      timeout: 5000
    });

    res.render("index", {
      message: response.data.message || "Data submitted successfully",
      error: null
    });
  } catch (error) {
    let errMsg = "Failed to submit data";
    if (error.response && error.response.data && error.response.data.error) {
      errMsg = error.response.data.error;
    } else if (error.message) {
      errMsg = error.message;
    }

    res.render("index", {
      message: null,
      error: errMsg
    });
  }
});

app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok", service: "frontend" });
});

app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
});