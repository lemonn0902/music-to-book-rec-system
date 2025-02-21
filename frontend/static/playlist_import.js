document.addEventListener("DOMContentLoaded", function () {
    const manualForm = document.getElementById("manual-form");
    const addSongBtn = document.getElementById("add-song-btn");
    const songsContainer = document.getElementById("songs-container");
    const messageBox = document.getElementById("message-box");

    // Add new song input fields dynamically
    addSongBtn.addEventListener("click", () => {
        const songDiv = document.createElement("div");
        songDiv.classList.add("song-input");
        songDiv.innerHTML = `
            <div class="song-fields">
                <input type="text" placeholder="Song title" class="song-title" required>
                <input type="text" placeholder="Artist" class="song-artist" required>
                <button type="button" class="fetch-metadata-btn">🔍 Fetch Metadata</button>
            </div>
            <button type="button" class="remove-song-btn">✕</button>
        `;
        songsContainer.appendChild(songDiv);

        // Add event listener to the new "Remove Song" button
        songDiv.querySelector(".remove-song-btn").addEventListener("click", () => {
            songDiv.remove();
        });

        // Add event listener to the new "Fetch Metadata" button
        songDiv.querySelector(".fetch-metadata-btn").addEventListener("click", async () => {
            const title = songDiv.querySelector(".song-title").value.trim();
            const artist = songDiv.querySelector(".song-artist").value.trim();
            if (!title || !artist) {
                showMessage("Please enter both song title and artist.", "error");
                return;
            }
            await fetchMetadata(title, artist, songDiv);
        });
    });

    // Fetch song metadata from your FastAPI backend
    async function fetchMetadata(title, artist, songDiv) {
        try {
            // Call the FastAPI backend endpoint to fetch metadata
            const response = await fetch(`/lastfm/track_metadata/?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(title)}`);
            if (!response.ok) {
                throw new Error("Failed to fetch metadata");
            }
            const data = await response.json();

            if (data) {
                showMessage("Metadata fetched successfully!", "success");
                console.log("Metadata:", data);

                // Update the UI with the fetched metadata
                const metadataFields = `
                    <div class="metadata-fields">
                        <p><strong>Album:</strong> ${data.album || "N/A"}</p>
                        <p><strong>Listeners:</strong> ${data.listeners || "N/A"}</p>
                        <p><strong>Play Count:</strong> ${data.playcount || "N/A"}</p>
                        <p><strong>Tags:</strong> ${data.tags ? data.tags.join(", ") : "N/A"}</p>
                        <p><strong>URL:</strong> <a href="${data.url}" target="_blank">${data.url || "N/A"}</a></p>
                    </div>
                `;
                songDiv.insertAdjacentHTML("beforeend", metadataFields);
            } else {
                showMessage("No metadata found.", "error");
            }
        } catch (error) {
            console.error("Error fetching metadata:", error);
            showMessage("Failed to fetch metadata. Please try again later.", "error");
        }
    }

    // Handle form submission
manualForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Collect all songs from the form
    const songs = [];
    document.querySelectorAll(".song-input").forEach((songDiv) => {
        const title = songDiv.querySelector(".song-title").value.trim();
        const artist = songDiv.querySelector(".song-artist").value.trim();
        if (title && artist) {
            songs.push({ title, artist });
        }
    });

    // Validate that at least one song is added
    if (songs.length === 0) {
        showMessage("Please add at least one song.", "error");
        return;
    }

    // Log the payload for debugging
    console.log("Sending payload:", songs);

    // Submit the songs to the backend
    try {
        const response = await fetch("/songs/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(songs),  // Send the array directly
        });

        if (!response.ok) {
            throw new Error("Failed to submit songs");
        }

        const result = await response.json();
        showMessage("Songs added successfully!", "success");
        console.log("Submission result:", result);
    } catch (error) {
        console.error("Error submitting songs:", error);
        showMessage("Failed to add songs. Please try again later.", "error");
    }
});

    // Show message
    function showMessage(message, type) {
        messageBox.textContent = message;
        messageBox.className = `message ${type}`;
        messageBox.classList.remove("hidden");
        setTimeout(() => messageBox.classList.add("hidden"), 5000);
    }
});