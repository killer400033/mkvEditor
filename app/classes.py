class Track:
    def __init__(self, track_id):
        self.track_id = track_id
        self.track_type = None
        self.language = None
        self.default = "1"
        self.file_name = None

    def __repr__(self):
        return (f"Track(track_id={self.track_id}, track_type={self.track_type}, "
                f"language={self.language}, default={self.default})")
    
    def to_dict(self):
        return {
            "track_id": self.track_id,
            "track_type": self.track_type,
            "language": self.language,
            "default": self.default,
            "file_name": self.file_name
        }
    
    @staticmethod
    def from_dict(data):
        track = Track(track_id=data["track_id"])
        track.track_type=data["track_type"]
        track.language=data["language"]
        track.default=data["default"]
        track.file_name=data["file_name"]
        return track

class MkvFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tracks = None
    
    def __repr__(self):
        return (f"MkvFile(file_path={self.file_path}, tracks={self.tracks})")

    def to_dict(self):
        return {
            "file_path": self.file_path,
            "tracks": [track.to_dict() for track in self.tracks] if self.tracks else []
        }
    
    @staticmethod
    def from_dict(data):
        mkv_file = MkvFile(file_path=data["file_path"])
        mkv_file.tracks = [Track.from_dict(track) for track in data.get("tracks", [])]
        return mkv_file