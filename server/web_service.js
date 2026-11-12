const express = require("express");
const multer = require("multer");
const { DatabaseSync } = require("node:sqlite");
const path = require("path");
const fs = require("fs");

const HOST = process.env.FLASK_HOST || process.env.HOST || "0.0.0.0";
const PORT = process.env.FLASK_PORT || process.env.PORT || 8000;

const UPLOADS_DIR = path.join(__dirname, "uploads");
const DB_PATH = path.join(__dirname, "videos.db");

if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

const db = new DatabaseSync(DB_PATH);
db.exec("PRAGMA journal_mode = WAL;");
db.exec("PRAGMA busy_timeout = 5000;");

db.exec(`
  CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    video_url TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
`);

function sanitizeFilename(name) {
  return name.trim().replace(/[^a-zA-Z0-9_-]/g, "_");
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, UPLOADS_DIR);
  },
  filename: (req, file, cb) => {
    const companyName = req.body.company_name || "unknown";
    const ext = path.extname(file.originalname) || ".webm";
    const safeName = `${sanitizeFilename(companyName)}${ext}`;
    cb(null, safeName);
  },
});

const upload = multer({ storage });
const app = express();

app.post("/upload", upload.single("file"), (req, res) => {
  const companyName = req.body.company_name;

  if (!companyName || !req.file) {
    return res
      .status(400)
      .json({ error: "Both company_name and file are required" });
  }

  const filePath = path.resolve(req.file.path);
  const protocol = req.protocol;
  const host = req.get("host");
  const videoUrl = `${protocol}://${host}/media/${req.file.filename}`;

  try {
    const stmt = db.prepare(`
      INSERT INTO videos (company_name, file_path, video_url, created_at, updated_at)
      VALUES (?, ?, ?, datetime('now'), datetime('now'))
      ON CONFLICT(company_name) DO UPDATE SET
        file_path = excluded.file_path,
        video_url = excluded.video_url,
        updated_at = datetime('now')
    `);

    stmt.run(companyName, filePath, videoUrl);

    return res.status(200).json({
      company_name: companyName,
      video_url: videoUrl,
    });
  } catch (err) {
    console.error("Database error:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/get_video_url", (req, res) => {
  const companyName = req.query.company_name;

  if (!companyName) {
    return res
      .status(400)
      .json({ error: "company_name query parameter is required" });
  }

  const stmt = db.prepare(
    "SELECT company_name, video_url FROM videos WHERE company_name = ?",
  );
  const row = stmt.get(companyName);

  if (!row) {
    return res.status(404).json({ error: "Company not found" });
  }

  return res.status(200).json({
    company_name: row.company_name,
    video_url: row.video_url,
  });
});

app.use("/media", express.static(UPLOADS_DIR));

app.get("/videos", (req, res) => {
  const rows = db
    .prepare("SELECT * FROM videos ORDER BY updated_at DESC")
    .all();
  res.status(200).json(rows);
});

app.listen(PORT, HOST, () => {
  console.log(`Web service running at http://${HOST}:${PORT}`);
});
