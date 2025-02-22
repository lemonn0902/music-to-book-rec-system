document.addEventListener("DOMContentLoaded", function () {
    const manualForm = document.getElementById("manual-form");
    const addSongBtn = document.getElementById("add-song-btn");
    const songsContainer = document.getElementById("songs-container");
    const messageBox = document.getElementById("message-box");

    // Create a container for added songs
    const addedSongsContainer = document.createElement("div");
    addedSongsContainer.id = "added-songs";
    addedSongsContainer.className = "songs-list";
    addedSongsContainer.innerHTML = '<h3>Added Songs</h3><div id="songs-list-container"></div>';
    manualForm.parentNode.insertBefore(addedSongsContainer, manualForm.nextSibling);

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
            const response = await fetch(`/lastfm/track_metadata/?artist=${encodeURIComponent(artist)}&track=${encodeURIComponent(title)}`);
            if (!response.ok) {
                throw new Error("Failed to fetch metadata");
            }
            const data = await response.json();

            if (data) {
                showMessage("Metadata fetched successfully!", "success");
                console.log("Metadata:", data);

                // Remove existing metadata if any
                const existingMetadata = songDiv.querySelector('.metadata-fields');
                if (existingMetadata) {
                    existingMetadata.remove();
                }

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
    manualForm.querySelector("form").addEventListener("submit", async (event) => {
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

        console.log("Sending payload:", songs); // Debug log

        try {
            const response = await fetch("/songs/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(songs),
            });

            if (!response.ok) {
                throw new Error("Failed to submit songs");
            }

            const result = await response.json();
            console.log("API Response:", result); // Debug log

            showMessage("Songs added successfully!", "success");
            
            // Clear the form
            songsContainer.innerHTML = `
                <div class="song-input">
                    <div class="song-fields">
                        <input type="text" placeholder="Song title" class="song-title" required>
                        <input type="text" placeholder="Artist" class="song-artist" required>
                        <button type="button" class="fetch-metadata-btn">🔍 Fetch Metadata</button>
                    </div>
                    <button type="button" class="remove-song-btn">✕</button>
                </div>
            `;

            // Add the songs to the display list
            const songsListContainer = document.getElementById("songs-list-container");
            
            // Handle the response
            if (result.songs && Array.isArray(result.songs)) {
                result.songs.forEach(song => {
                    console.log("Song Object:", song); // Debug log
                    if (!song._id) {
                        console.error("Song ID is missing:", song);
                        return;
                    }
                    const songElement = document.createElement("div");
                    songElement.className = "song-item";
                    songElement.innerHTML = `
                        <div class="song-info">
                            <span class="song-title">${song.name || ''}</span> by 
                            <span class="song-artist">${song.artist || ''}</span>
                        </div>
                        <a href="/songs/view/${song._id}" class="btn recommendation-btn">
                            Get Book Recommendations
                        </a>
                    `;
                    songsListContainer.appendChild(songElement);
                });
            } else {
                console.error("Invalid response format:", result);
                showMessage("Failed to add songs. Invalid response from server.", "error");
            }

        } catch (error) {
            console.error("Error submitting songs:", error);
            console.error("Full error details:", error.message);
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