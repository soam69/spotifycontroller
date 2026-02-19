import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st

# load_dotenv()

# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]


sp = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-private user-read-playback-state user-modify-playback-state playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"
    )
)


def getIDfromLink(link : str) -> str:
    if "playlist" in link:
        return link.split("playlist/")[1].split("?")[0]
    return link

def getSongsUrl(playlistId : str) -> list:
    lst = []
    tracks = sp.playlist_items(playlistId)
    for item in tracks["items"]:
        lst.append(item["track"]["uri"])
    return lst

def checkDoubles(lst : list, dstId: str) -> list:
    dstTracks = []
    ans = []
    tracks = sp.playlist_items(dstId)
    for item in tracks["items"]:
        dstTracks.append(item["track"]["uri"])
    for l in lst:
        if l not in dstTracks:
            ans.append(l)
    return ans

def getPlaylistNameAndOwnerName(pid : str):
    playlist = sp.playlist(pid)
    return playlist["name"],playlist["owner"]["display_name"]


st.title("Welcome to Spotify Playlist Copier🎧")
st.caption("Copy songs from one playlist to another with one click 🖱️")
st.header("Source Playlist")
src_link = st.text_input(
    "Enter Source URL",
    placeholder="Enter the URL of ID of the Source playlist"
    )
srcId = getIDfromLink(src_link)

st.header("Destination Playlist")
dst_link = st.text_input(
    "Enter Destination URL",
    placeholder="Enter the URL of ID of the Destination playlist"
    )

dstId = getIDfromLink(dst_link)

if st.button("Copy It !!!"):
    if not src_link or not dst_link:
        st.error("Enter Source and Destination links or Ids")
    else:
        src_name,src_owner = getPlaylistNameAndOwnerName(srcId)
        dst_name,dst_owner = getPlaylistNameAndOwnerName(dstId)
        try:
            with st.spinner(f"📥 Copying from **{src_name}** (by {src_owner}) "
                            f"→ **{dst_name}** (by {dst_owner})"):
                combinedSongs = getSongsUrl(srcId)
                uniqueSongs = checkDoubles(combinedSongs,dstId)
                if uniqueSongs:
                    sp.playlist_add_items(
                        playlist_id=dstId,
                        items=uniqueSongs
                    )
                    st.success(f"Copied {len(uniqueSongs)} songs from **{src_name}** (by {src_owner}) → **{dst_name}** (by {dst_owner}) successfully")
                else:
                    st.info("No new songs to add!")
        except Exception as e:
            st.error(f"Error : {e}")