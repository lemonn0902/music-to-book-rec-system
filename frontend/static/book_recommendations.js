document.addEventListener('DOMContentLoaded', function() {
    // Extract song ID from URL parameters
    const pathSegments = window.location.pathname.split('/');
    const songId = pathSegments[pathSegments.length - 1]; // Last segment is the song ID
    console.log("Song ID:", songId);  // Debug log
    if (!songId) {
        document.getElementById('song-details').innerHTML = '<p class="error">No song selected. Please go back and select a song.</p>';
        document.getElementById('get-recommendations-btn').disabled = true;
        return;
    }
    
    // Fetch song details
    fetchSongDetails(songId);
    
    // Add event listener to the recommendations button
    document.getElementById('get-recommendations-btn').addEventListener('click', function() {
        fetchBookRecommendations(songId);
    });
});

// Function to fetch song details
async function fetchSongDetails(songId) {
    try {
        const response = await fetch(`/songs/${songId}`);

        if (!response.ok) {
            throw new Error('Failed to fetch song details');
        }
        
        const song = await response.json();
        displaySongDetails(song);
    } catch (error) {
        console.error('Error fetching song details:', error);
        document.getElementById('song-details').innerHTML = `
            <p class="error">Error loading song details: ${error.message}</p>
        `;
    }
}

// Function to display song details
function displaySongDetails(song) {
    const songDetails = document.getElementById('song-details');
    
    // Create tags HTML
    const tagsHtml = song.tags && song.tags.length 
        ? song.tags.map(tag => `<span class="genre-tag">${tag}</span>`).join('') 
        : '<span class="genre-tag">No genres available</span>';
    
    songDetails.innerHTML = `
        <div class="song-info">
            <h3>${song.name || 'Unknown Track'}</h3>
            <p class="song-artist">by ${song.artist || 'Unknown Artist'}</p>
            ${song.album ? `<p>Album: ${song.album}</p>` : ''}
            <div class="genre-tags">
                ${tagsHtml}
            </div>
            ${song.url ? `<p><a href="${song.url}" target="_blank">View on Last.fm</a></p>` : ''}
        </div>
    `;
}

// Function to fetch book recommendations
async function fetchBookRecommendations(songId) {
    // Show loading state
    document.getElementById('no-recommendations').classList.add('hidden');
    document.getElementById('recommendations-loading').classList.remove('hidden');
    document.getElementById('recommendations-error').classList.add('hidden');
    document.getElementById('recommendations-results').classList.add('hidden');
    
    try {
        const response = await fetch(`/api/books/recommendations/${songId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch recommendations');
        }
        
        const data = await response.json();
        displayBookRecommendations(data);
    } catch (error) {
        console.error('Error fetching book recommendations:', error);
        document.getElementById('recommendations-loading').classList.add('hidden');
        document.getElementById('recommendations-error').classList.remove('hidden');
        document.getElementById('recommendations-error').innerHTML = `
            <p class="error">Error loading recommendations: ${error.message}</p>
            <button id="retry-btn" class="secondary-btn">Try Again</button>
        `;
        
        // Add retry button functionality
        document.getElementById('retry-btn').addEventListener('click', function() {
            fetchBookRecommendations(songId);
        });
    }
}

// Function to display book recommendations
function displayBookRecommendations(data) {
    // Hide loading state
    document.getElementById('recommendations-loading').classList.add('hidden');
    
    // Display genre mapping
    const genreMapping = document.getElementById('genre-mapping');
    genreMapping.innerHTML = `
        <p>Music genre <strong>${data.music_genre}</strong> has been matched to 
        book genre <strong>${data.mapped_book_genre}</strong></p>
    `;
    
    // Display book recommendations
    const booksGrid = document.getElementById('books-grid');
    booksGrid.innerHTML = '';
    
    if (data.recommendations && data.recommendations.length > 0) {
        data.recommendations.forEach(book => {
            const bookCard = document.createElement('div');
            bookCard.className = 'book-card';
            
            // Create cover image or placeholder
            let coverHtml;
            if (book.cover_url) {
                coverHtml = `<img src="${book.cover_url}" alt="Cover of ${book.title}" class="book-cover">`;
            } else {
                coverHtml = `
                    <div class="placeholder-cover">
                        <span>${book.title.charAt(0)}</span>
                    </div>
                `;
            }
            
            // Create rating HTML if available
            const ratingHtml = book.rating 
                ? `<div class="book-rating">Rating: ${book.rating} ★</div>` 
                : '';
            
            // Truncate description if needed
            const description = book.description 
                ? (book.description.length > 120 ? book.description.substring(0, 120) + '...' : book.description)
                : 'No description available';
            
            bookCard.innerHTML = `
                ${coverHtml}
                <h5>${book.title}</h5>
                <p class="book-author">by ${book.author}</p>
                ${ratingHtml}
                <p class="book-description">${description}</p>
            `;
            
            booksGrid.appendChild(bookCard);
        });
    } else {
        booksGrid.innerHTML = '<p>No book recommendations found for this song.</p>';
    }
    
    // Show results section
    document.getElementById('recommendations-results').classList.remove('hidden');
}