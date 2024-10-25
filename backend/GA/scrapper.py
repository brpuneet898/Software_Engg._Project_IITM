from pytube import Playlist

# Replace with your playlist URL
playlist_url = 'https://www.youtube.com/playlist?list=PLZ2ps__7DhBYt5yvXrYAjjWtf5O399Xea'

# Create a Playlist object
playlist = Playlist(playlist_url)

# Extract and print video URLs
video_urls = [video.watch_url for video in playlist.videos]

# Print the video URLs
for url in video_urls:
    print(url)

print(len(video_urls))
