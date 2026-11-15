const API_BASE = "/api";

export async function scanStorage() {
  const response = await fetch(`${API_BASE}/files/scan`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Storage scan failed");
  }

  return response.json();
}

export async function getFiles() {
  const response = await fetch(`${API_BASE}/files/`);

  if (!response.ok) {
    throw new Error("Unable to retrieve files");
  }

  return response.json();
}
