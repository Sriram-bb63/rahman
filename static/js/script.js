document.addEventListener('DOMContentLoaded', () => {
    const audioPlayer = document.getElementById('audio-player');
    const songList = document.getElementById('song-list');
    const searchBar = document.getElementById('search-bar');
    const downloadForm = document.getElementById('download-form');
    const downloadButton = document.getElementById('download-button');
    const youtubeUrlInput = document.getElementById('youtube-url');
    const downloadStatus = document.getElementById('download-status');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const nowPlayingText = document.getElementById('now-playing');

    const fetchSongs = async () => {
        songList.innerHTML = '<li class="list-group-item">Loading...</li>';
        try {
            const response = await fetch('/get_songs');
            const songs = await response.json();
            songList.innerHTML = songs.length
                ? songs.map(song => createSongElement(song)).join('')
                : '<li class="list-group-item">No songs found.</li>';
        } catch (error) {
            songList.innerHTML = '<li class="list-group-item text-danger">Error loading songs</li>';
        }
    };

    const createSongElement = (song) => {
        return `<li class="list-group-item d-flex justify-content-between align-items-center" 
                    data-file="${song.filename}" data-display-name="${song.display_name}">
                    <span>${song.display_name}</span>
                    <button class="btn btn-sm btn-warning rename-button">Rename</button>
                </li>`;
    };



    const renameSong = async (oldFileName) => {
        const songElement = document.querySelector(`[data-file="${oldFileName}"]`);
        const oldDisplayName = songElement.dataset.displayName;
        const newName = prompt("Enter new name:", oldDisplayName);

        if (!newName || newName.trim() === "") return;

        try {
            const response = await fetch('/rename_song', {
                method: 'POST',
                body: new URLSearchParams({ old_name: oldFileName, new_name: newName.trim() })
            });
            const data = await response.json();
            alert(data.success ? `Renamed to: ${data.new_name}` : `Error: ${data.message}`);
            fetchSongs();
        } catch (error) {
            alert('An error occurred while renaming.');
        }
    };



    const playSong = (songElement) => {
        const fileName = songElement.dataset.file;  // Get full filename
        audioPlayer.src = `/static/music/${encodeURIComponent(fileName)}`;
        audioPlayer.play();
        nowPlayingText.textContent = `Now Playing: ${songElement.dataset.displayName}`;
    };

    songList.addEventListener('click', (event) => {
        if (event.target.classList.contains('rename-button')) {
            const songItem = event.target.closest('li');
            renameSong(songItem.dataset.file);
        } else if (event.target.tagName === 'SPAN') {
            playSong(event.target.closest('li'));
        }
    });


    searchBar.addEventListener('input', () => {
        const query = searchBar.value.toLowerCase();
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.classList.toggle('d-none', !item.textContent.toLowerCase().includes(query));
        });
    });

    darkModeToggle.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });

    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    downloadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const youtubeUrl = youtubeUrlInput.value.trim();
        if (!youtubeUrl) return showDownloadStatus('Please enter a YouTube URL.', 'alert-warning');

        downloadButton.disabled = true;
        document.getElementById('download-spinner').classList.remove('d-none');
        showDownloadStatus('Downloading... Please wait.', 'alert-info');

        try {
            const response = await fetch('/download', {
                method: 'POST',
                body: new URLSearchParams({ youtube_url: youtubeUrl }),
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            const data = await response.json();
            showDownloadStatus(data.success ? `Successfully downloaded: ${data.filename}` : `Error: ${data.message}`, data.success ? 'alert-success' : 'alert-danger');
            youtubeUrlInput.value = '';
            fetchSongs();
        } catch (error) {
            showDownloadStatus('An error occurred. Please try again.', 'alert-danger');
        } finally {
            downloadButton.disabled = false;
            document.getElementById('download-spinner').classList.add('d-none');
        }
    });

    const showDownloadStatus = (message, alertClass) => {
        downloadStatus.className = `alert ${alertClass} mt-3`;
        downloadStatus.textContent = message;
        downloadStatus.classList.remove('d-none');
    };

    fetchSongs();
});
